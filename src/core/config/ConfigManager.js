/**
 * Configuration Manager for Aideon AI Lite
 * 
 * Manages the configuration system for Aideon AI Lite.
 * Handles loading, validation, and access to configuration settings.
 */

const EventEmitter = require('events');
const fs = require('fs').promises;
const path = require('path');
const yaml = require('js-yaml');
const deepmerge = require('deepmerge');
const Ajv = require('ajv');

class ConfigManager extends EventEmitter {
  /**
   * Initialize the Configuration Manager
   * @param {Object} options - Configuration options
   */
  constructor(options = {}) {
    super();
    
    this.options = options;
    this.initialized = false;
    this.config = {};
    this.schemas = {};
    
    this.configPath = options.configPath || path.join(process.cwd(), 'config');
    this.configFile = options.configFile || 'config.yaml';
    this.envPrefix = options.envPrefix || 'AIDEON_';
    
    this.validator = new Ajv({
      allErrors: true,
      useDefaults: true,
      coerceTypes: true
    });
  }
  
  /**
   * Initialize the configuration manager
   * @returns {Promise<void>}
   */
  async initialize() {
    if (this.initialized) {
      return;
    }
    
    try {
      // Ensure config directory exists
      await fs.mkdir(this.configPath, { recursive: true });
      
      // Load configuration schemas
      await this._loadSchemas();
      
      // Load configuration files
      await this._loadConfigurations();
      
      // Apply environment variable overrides
      this._applyEnvironmentOverrides();
      
      // Validate configuration
      this._validateConfiguration();
      
      this.initialized = true;
    } catch (error) {
      throw new Error(`Failed to initialize configuration manager: ${error.message}`);
    }
  }
  
  /**
   * Get the entire configuration object
   * @returns {Object} The complete configuration object
   */
  getConfig() {
    return this.config;
  }
  
  /**
   * Get the data directory path
   * @returns {string} The data directory path
   */
  getDataDir() {
    const dataDir = this.get('system.dataDir', './data');
    
    // If path is relative, resolve it against the current working directory
    if (!path.isAbsolute(dataDir)) {
      return path.resolve(process.cwd(), dataDir);
    }
    
    return dataDir;
  }
  
  /**
   * Get the temporary directory path
   * @returns {string} The temporary directory path
   */
  getTempDir() {
    const tempDir = this.get('system.tempDir', './temp');
    
    // If path is relative, resolve it against the current working directory
    if (!path.isAbsolute(tempDir)) {
      return path.resolve(process.cwd(), tempDir);
    }
    
    return tempDir;
  }
  
  /**
   * Get the workspace directory path
   * @returns {string} The workspace directory path
   */
  getWorkspacePath() {
    const workspacePath = this.get('system.workspacePath', './workspace');
    
    // If path is relative, resolve it against the current working directory
    if (!path.isAbsolute(workspacePath)) {
      return path.resolve(process.cwd(), workspacePath);
    }
    
    return workspacePath;
  }
  
  /**
   * Load configuration schemas
   * @returns {Promise<void>}
   * @private
   */
  async _loadSchemas() {
    const schemaPath = path.join(this.configPath, 'schemas');
    
    try {
      // Check if schemas directory exists
      await fs.access(schemaPath);
      
      // Get all schema files
      const files = await fs.readdir(schemaPath);
      
      for (const file of files) {
        if (file.endsWith('.json') || file.endsWith('.yaml') || file.endsWith('.yml')) {
          const filePath = path.join(schemaPath, file);
          const content = await fs.readFile(filePath, 'utf8');
          
          let schema;
          if (file.endsWith('.json')) {
            schema = JSON.parse(content);
          } else {
            schema = yaml.load(content);
          }
          
          const name = path.basename(file, path.extname(file));
          this.schemas[name] = schema;
          
          // Add schema to validator
          this.validator.addSchema(schema, name);
        }
      }
    } catch (error) {
      // If schemas directory doesn't exist, use default schemas
      this._loadDefaultSchemas();
    }
  }
  
  /**
   * Load default schemas
   * @private
   */
  _loadDefaultSchemas() {
    // Core schema
    this.schemas.core = {
      type: 'object',
      properties: {
        system: {
          type: 'object',
          properties: {
            name: { type: 'string', default: 'Aideon AI Lite' },
            version: { type: 'string', default: '1.0.0' },
            description: { type: 'string', default: 'Intelligence Everywhere, Limits Nowhere' },
            logLevel: { type: 'string', enum: ['debug', 'info', 'warn', 'error'], default: 'info' },
            dataDir: { type: 'string', default: './data' },
            tempDir: { type: 'string', default: './temp' },
            workspacePath: { type: 'string', default: './workspace' },
            maxConcurrency: { type: 'integer', minimum: 1, default: 4 }
          },
          additionalProperties: false
        }
      },
      required: ['system'],
      additionalProperties: true
    };
    
    // Add schema to validator
    this.validator.addSchema(this.schemas.core, 'core');
  }
  
  /**
   * Load configuration files
   * @returns {Promise<void>}
   * @private
   */
  async _loadConfigurations() {
    // Start with default configuration
    this.config = this._getDefaultConfig();
    
    // Load base configuration file
    const baseConfigPath = path.join(this.configPath, this.configFile);
    
    try {
      await fs.access(baseConfigPath);
      const content = await fs.readFile(baseConfigPath, 'utf8');
      const baseConfig = yaml.load(content);
      
      // Merge with defaults
      this.config = deepmerge(this.config, baseConfig);
    } catch (error) {
      // If base config doesn't exist, create it with defaults
      await this._saveConfiguration();
    }
    
    // Load environment-specific configuration
    const env = process.env.NODE_ENV || 'development';
    const envConfigPath = path.join(this.configPath, `config.${env}.yaml`);
    
    try {
      await fs.access(envConfigPath);
      const content = await fs.readFile(envConfigPath, 'utf8');
      const envConfig = yaml.load(content);
      
      // Merge with base config
      this.config = deepmerge(this.config, envConfig);
    } catch (error) {
      // Environment-specific config is optional
    }
    
    // Load local overrides (not committed to version control)
    const localConfigPath = path.join(this.configPath, 'config.local.yaml');
    
    try {
      await fs.access(localConfigPath);
      const content = await fs.readFile(localConfigPath, 'utf8');
      const localConfig = yaml.load(content);
      
      // Merge with current config
      this.config = deepmerge(this.config, localConfig);
    } catch (error) {
      // Local config is optional
    }
  }
  
  /**
   * Get default configuration
   * @returns {Object} Default configuration
   * @private
   */
  _getDefaultConfig() {
    return {
      system: {
        name: 'Aideon AI Lite',
        version: '1.0.0',
        description: 'Intelligence Everywhere, Limits Nowhere',
        logLevel: 'info',
        dataDir: './data',
        tempDir: './temp',
        workspacePath: './workspace',
        maxConcurrency: 4
      },
      agents: {
        planner: {
          enabled: true,
          model: 'gpt-4-turbo',
          temperature: 0.2,
          maxTokens: 4096
        },
        execution: {
          enabled: true,
          model: 'gpt-4-turbo',
          temperature: 0.5,
          maxTokens: 8192
        },
        verification: {
          enabled: true,
          model: 'gpt-4-turbo',
          temperature: 0.3,
          maxTokens: 4096
        },
        security: {
          enabled: true,
          model: 'gpt-4-turbo',
          temperature: 0.1,
          maxTokens: 4096
        },
        optimization: {
          enabled: true,
          model: 'gpt-4-turbo',
          temperature: 0.4,
          maxTokens: 4096
        },
        learning: {
          enabled: true,
          model: 'gpt-4-turbo',
          temperature: 0.6,
          maxTokens: 8192
        }
      },
      memory: {
        persistencePath: './data/memory',
        autoSave: true,
        autoSaveInterval: 60000,
        maxHistoryLength: 1000
      },
      tasks: {
        maxConcurrentTasks: 5,
        taskTimeout: 300000,
        retryLimit: 3
      },
      tools: {
        toolsPath: './tools',
        customToolsPath: './custom_tools'
      },
      api: {
        enabled: true,
        port: 3000,
        host: 'localhost',
        cors: {
          enabled: true,
          origin: '*'
        },
        rateLimit: {
          enabled: true,
          windowMs: 60000,
          max: 100
        }
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
        },
        permissions: {
          enabled: true,
          defaultPolicy: 'deny'
        }
      },
      ui: {
        enabled: true,
        port: 8080,
        host: 'localhost',
        theme: 'dark'
      },
      logging: {
        console: {
          enabled: true,
          level: 'info',
          format: 'pretty'
        },
        file: {
          enabled: true,
          level: 'debug',
          path: './logs',
          maxSize: '10m',
          maxFiles: 5
        }
      },
      telemetry: {
        enabled: false,
        anonymized: true
      }
    };
  }
  
  /**
   * Apply environment variable overrides
   * @private
   */
  _applyEnvironmentOverrides() {
    // Get all environment variables with the specified prefix
    const envVars = Object.keys(process.env)
      .filter(key => key.startsWith(this.envPrefix))
      .reduce((obj, key) => {
        obj[key] = process.env[key];
        return obj;
      }, {});
    
    // Apply overrides
    for (const [key, value] of Object.entries(envVars)) {
      // Remove prefix and convert to path
      const configPath = key
        .substring(this.envPrefix.length)
        .toLowerCase()
        .split('_');
      
      // Set value in config
      this._setNestedValue(this.config, configPath, this._parseValue(value));
    }
  }
  
  /**
   * Set a nested value in an object
   * @param {Object} obj - Target object
   * @param {Array<string>} path - Path to the value
   * @param {any} value - Value to set
   * @private
   */
  _setNestedValue(obj, path, value) {
    if (path.length === 1) {
      obj[path[0]] = value;
      return;
    }
    
    const key = path[0];
    
    if (!obj[key]) {
      obj[key] = {};
    }
    
    this._setNestedValue(obj[key], path.slice(1), value);
  }
  
  /**
   * Parse a string value to the appropriate type
   * @param {string} value - Value to parse
   * @returns {any} Parsed value
   * @private
   */
  _parseValue(value) {
    // Boolean
    if (value.toLowerCase() === 'true') return true;
    if (value.toLowerCase() === 'false') return false;
    
    // Number
    if (!isNaN(value) && value.trim() !== '') {
      if (value.includes('.')) {
        return parseFloat(value);
      }
      return parseInt(value, 10);
    }
    
    // JSON
    try {
      return JSON.parse(value);
    } catch (e) {
      // Not JSON, return as string
      return value;
    }
  }
  
  /**
   * Validate configuration against schemas
   * @private
   */
  _validateConfiguration() {
    // Validate core configuration
    const validateCore = this.validator.getSchema('core');
    
    if (!validateCore) {
      throw new Error('Core configuration schema not found');
    }
    
    const valid = validateCore(this.config);
    
    if (!valid) {
      const errors = validateCore.errors.map(error => {
        return `${error.instancePath} ${error.message}`;
      }).join(', ');
      
      throw new Error(`Configuration validation failed: ${errors}`);
    }
    
    // Validate other sections if schemas exist
    for (const [name, schema] of Object.entries(this.schemas)) {
      if (name === 'core') continue;
      
      if (this.config[name]) {
        const validate = this.validator.getSchema(name);
        
        if (validate) {
          const valid = validate(this.config[name]);
          
          if (!valid) {
            const errors = validate.errors.map(error => {
              return `${name}${error.instancePath} ${error.message}`;
            }).join(', ');
            
            throw new Error(`Configuration validation failed: ${errors}`);
          }
        }
      }
    }
  }
  
  /**
   * Save current configuration to file
   * @returns {Promise<void>}
   * @private
   */
  async _saveConfiguration() {
    const configPath = path.join(this.configPath, this.configFile);
    const yamlStr = yaml.dump(this.config);
    
    await fs.writeFile(configPath, yamlStr, 'utf8');
  }
  
  /**
   * Get configuration value
   * @param {string} path - Configuration path (dot notation)
   * @param {any} defaultValue - Default value if path not found
   * @returns {any} Configuration value
   */
  get(path, defaultValue) {
    if (!path) {
      return this.config;
    }
    
    const parts = path.split('.');
    let current = this.config;
    
    for (const part of parts) {
      if (current === undefined || current === null) {
        return defaultValue;
      }
      
      current = current[part];
    }
    
    return current !== undefined ? current : defaultValue;
  }
  
  /**
   * Set configuration value
   * @param {string} path - Configuration path (dot notation)
   * @param {any} value - Value to set
   * @returns {boolean} Success status
   */
  set(path, value) {
    if (!path) {
      return false;
    }
    
    const parts = path.split('.');
    const _setNestedValue = (obj, pathParts, val) => {
      const part = pathParts[0];
      
      if (pathParts.length === 1) {
        obj[part] = val;
        return true;
      }
      
      if (!obj[part] || typeof obj[part] !== 'object') {
        obj[part] = {};
      }
      
      return _setNestedValue(obj[part], pathParts.slice(1), val);
    };
    
    const result = _setNestedValue(this.config, parts, value);
    
    // Validate after setting
    try {
      this._validateConfiguration();
    } catch (error) {
      // Revert change if validation fails
      this._loadConfigurations().catch(() => {});
      throw error;
    }
    
    // Emit change event
    this.emit('config:changed', { path, value });
    
    return result;
  }
  
  /**
   * Save configuration changes
   * @returns {Promise<boolean>} Success status
   */
  async save() {
    try {
      await this._saveConfiguration();
      return true;
    } catch (error) {
      this.emit('error', new Error(`Failed to save configuration: ${error.message}`));
      return false;
    }
  }
  
  /**
   * Reset configuration to defaults
   * @returns {Promise<boolean>} Success status
   */
  async reset() {
    try {
      this.config = this._getDefaultConfig();
      await this._saveConfiguration();
      
      this.emit('config:reset');
      
      return true;
    } catch (error) {
      this.emit('error', new Error(`Failed to reset configuration: ${error.message}`));
      return false;
    }
  }
}

module.exports = { ConfigManager };
