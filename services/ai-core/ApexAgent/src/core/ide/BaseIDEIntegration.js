/**
 * BaseIDEIntegration.js
 * 
 * Base class for all IDE integrations in Aideon AI Lite.
 * Defines the common interface and functionality that all IDE integrations must implement.
 * 
 * @author Aideon AI Team
 * @version 1.0.0
 */

class BaseIDEIntegration {
  constructor(core) {
    if (new.target === BaseIDEIntegration) {
      throw new Error('BaseIDEIntegration is an abstract class and cannot be instantiated directly');
    }
    
    this.core = core;
    this.logger = core.logManager.getLogger(`ide:${this.getIDEName().toLowerCase()}`);
    this.config = core.configManager.getConfig().ide || {};
    this.eventHandlers = new Map();
  }

  /**
   * Get the name of the IDE
   * @returns {string} IDE name
   */
  getIDEName() {
    throw new Error('getIDEName() must be implemented by subclass');
  }

  /**
   * Get the version of the integration
   * @returns {string} Version string
   */
  getVersion() {
    return '1.0.0';
  }

  /**
   * Get the capabilities of this IDE integration
   * @returns {Object} Capabilities object
   */
  getCapabilities() {
    return {
      fileAccess: false,
      projectManagement: false,
      debugging: false,
      terminalAccess: false,
      codeCompletion: false,
      codeNavigation: false,
      refactoring: false,
      versionControl: false,
      extensionManagement: false
    };
  }

  /**
   * Connect to the IDE
   * @param {Object} options - Connection options
   * @returns {Promise<Object>} Connection object
   */
  async connect(options) {
    throw new Error('connect() must be implemented by subclass');
  }

  /**
   * Disconnect from the IDE
   * @param {Object} connection - Connection object
   * @returns {Promise<boolean>} Success status
   */
  async disconnect(connection) {
    throw new Error('disconnect() must be implemented by subclass');
  }

  /**
   * Check if a command is supported
   * @param {string} command - Command name
   * @returns {boolean} Whether the command is supported
   */
  supportsCommand(command) {
    return false;
  }

  /**
   * Execute a command in the IDE
   * @param {Object} connection - Connection object
   * @param {string} command - Command name
   * @param {Object} params - Command parameters
   * @returns {Promise<Object>} Command result
   */
  async executeCommand(connection, command, params) {
    throw new Error(`Command ${command} not supported`);
  }

  /**
   * Start a server for IDE extension communication
   * @param {number} port - Port to listen on
   * @returns {Promise<Object>} Server object
   */
  async startServer(port) {
    throw new Error('startServer() not implemented for this IDE');
  }

  /**
   * Install the IDE extension
   * @param {Object} options - Installation options
   * @returns {Promise<Object>} Installation result
   */
  async installExtension(options) {
    throw new Error('installExtension() not implemented for this IDE');
  }

  /**
   * Register an event handler
   * @param {Object} connection - Connection object
   * @param {string} eventType - Event type
   * @param {Function} handler - Event handler function
   */
  registerEventHandler(connection, eventType, handler) {
    if (!this.eventHandlers.has(connection.id)) {
      this.eventHandlers.set(connection.id, new Map());
    }
    
    const connectionHandlers = this.eventHandlers.get(connection.id);
    
    if (!connectionHandlers.has(eventType)) {
      connectionHandlers.set(eventType, []);
    }
    
    connectionHandlers.get(eventType).push(handler);
  }

  /**
   * Trigger an event
   * @param {Object} connection - Connection object
   * @param {string} eventType - Event type
   * @param {Object} eventData - Event data
   * @protected
   */
  _triggerEvent(connection, eventType, eventData) {
    if (!this.eventHandlers.has(connection.id)) {
      return;
    }
    
    const connectionHandlers = this.eventHandlers.get(connection.id);
    
    if (!connectionHandlers.has(eventType)) {
      return;
    }
    
    for (const handler of connectionHandlers.get(eventType)) {
      try {
        handler(eventData);
      } catch (error) {
        this.logger.error(`Error in event handler for ${eventType}: ${error.message}`);
      }
    }
  }

  /**
   * Clean up resources
   * @protected
   */
  _cleanup() {
    this.eventHandlers.clear();
  }
}

module.exports = BaseIDEIntegration;
