/**
 * BaseToolProvider.js
 * 
 * Base class for all domain-specific tool providers in Aideon AI Lite.
 * 
 * @author Aideon AI Team
 * @version 1.0.0
 */

class BaseToolProvider {
  /**
   * Create a new BaseToolProvider instance
   * @param {Object} core - Reference to the AideonCore instance
   * @param {string} domain - Domain identifier for this provider
   */
  constructor(core, domain) {
    if (new.target === BaseToolProvider) {
      throw new Error('BaseToolProvider is an abstract class and cannot be instantiated directly');
    }
    
    this.core = core;
    this.domain = domain;
    this.logger = core?.logManager?.getLogger(`tools:${domain}`) || console;
  }
  
  /**
   * Initialize the tool provider
   * @returns {Promise<boolean>} - True if initialization was successful
   */
  async initialize() {
    throw new Error('Method initialize() must be implemented by subclass');
  }
  
  /**
   * Get all tools provided by this provider
   * @returns {Promise<Array<Object>>} - Array of tool definitions
   */
  async getTools() {
    throw new Error('Method getTools() must be implemented by subclass');
  }
  
  /**
   * Shutdown the tool provider
   * @returns {Promise<void>}
   */
  async shutdown() {
    // Default implementation - can be overridden by subclasses
    if (this.logger.debug) {
      this.logger.debug(`Shutting down ${this.domain} tool provider`);
    } else {
      console.log(`Shutting down ${this.domain} tool provider`);
    }
    return true;
  }
}

module.exports = { BaseToolProvider };
