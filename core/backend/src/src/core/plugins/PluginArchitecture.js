/**
 * PluginArchitecture.js
 * 
 * Unified plugin architecture for Aideon AI Lite.
 * Provides a framework for third-party developers to extend Aideon's capabilities
 * through standardized interfaces and lifecycle management.
 * 
 * @author Aideon AI Team
 * @version 1.0.0
 */

const EventEmitter = require('events');
const path = require('path');
const fs = require('fs').promises;
const { v4: uuidv4 } = require('uuid');
const semver = require('semver');

/**
 * Core plugin architecture class that manages plugin lifecycle and integration
 */
class PluginArchitecture extends EventEmitter {
  /**
   * Creates a new PluginArchitecture instance
   * 
   * @param {Object} core - The Aideon core instance
   */
  constructor(core) {
    super();
    
    this.core = core;
    this.logger = core.getLogManager().getLogger('plugin-architecture');
    this.configManager = core.getConfigManager();
    
    this.plugins = new Map();
    this.hooks = new Map();
    this.extensionPoints = new Map();
    
    this.pluginDirectories = [];
    this.isInitialized = false;
  }
  
  /**
   * Initializes the plugin architecture
   * 
   * @param {Object} options - Initialization options
   * @returns {Promise<boolean>} True if initialization was successful
   */
  async initialize(options = {}) {
    try {
      this.logger.info('Initializing Plugin Architecture');
      
      // Set plugin directories
      this.pluginDirectories = [
        // Built-in plugins
        path.join(this.configManager.getAppDir(), 'plugins'),
        
        // User plugins
        path.join(this.configManager.getDataDir(), 'plugins'),
        
        // Additional directories from options
        ...(options.additionalDirectories || [])
      ];
      
      // Create plugin directories if they don't exist
      for (const dir of this.pluginDirectories) {
        await fs.mkdir(dir, { recursive: true });
      }
      
      // Register core extension points
      this._registerCoreExtensionPoints();
      
      // Load plugins
      await this._loadPlugins();
      
      this.isInitialized = true;
      this.logger.info(`Plugin Architecture initialized with ${this.plugins.size} plugins`);
      
      // Emit initialization event
      this.emit('initialized', { pluginCount: this.plugins.size });
      
      return true;
    } catch (error) {
      this.logger.error(`Failed to initialize Plugin Architecture: ${error.message}`, error);
      return false;
    }
  }
  
  /**
   * Registers a new plugin
   * 
   * @param {Object} pluginInfo - Plugin information
   * @returns {Promise<string>} Plugin ID if registration was successful
   */
  async registerPlugin(pluginInfo) {
    try {
      if (!this.isInitialized) {
        throw new Error('Plugin Architecture not initialized');
      }
      
      // Validate plugin info
      this._validatePluginInfo(pluginInfo);
      
      // Generate plugin ID if not provided
      const pluginId = pluginInfo.id || `plugin-${uuidv4()}`;
      
      // Check if plugin with this ID already exists
      if (this.plugins.has(pluginId)) {
        throw new Error(`Plugin with ID ${pluginId} already exists`);
      }
      
      // Create plugin instance
      const plugin = {
        id: pluginId,
        name: pluginInfo.name,
        version: pluginInfo.version,
        description: pluginInfo.description,
        author: pluginInfo.author,
        main: pluginInfo.main,
        dependencies: pluginInfo.dependencies || {},
        extensionPoints: pluginInfo.extensionPoints || [],
        hooks: pluginInfo.hooks || [],
        instance: null,
        status: 'registered',
        registeredAt: new Date(),
        path: pluginInfo.path
      };
      
      // Register plugin
      this.plugins.set(pluginId, plugin);
      
      this.logger.info(`Plugin ${plugin.name} (${pluginId}) registered`);
      
      // Emit plugin registered event
      this.emit('plugin:registered', { pluginId, plugin });
      
      return pluginId;
    } catch (error) {
      this.logger.error(`Failed to register plugin: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Loads a plugin
   * 
   * @param {string} pluginId - Plugin ID
   * @returns {Promise<boolean>} True if plugin was loaded successfully
   */
  async loadPlugin(pluginId) {
    try {
      if (!this.isInitialized) {
        throw new Error('Plugin Architecture not initialized');
      }
      
      // Get plugin
      const plugin = this.plugins.get(pluginId);
      
      if (!plugin) {
        throw new Error(`Plugin ${pluginId} not found`);
      }
      
      // Check if plugin is already loaded
      if (plugin.status === 'loaded' || plugin.status === 'activated') {
        this.logger.info(`Plugin ${plugin.name} (${pluginId}) already loaded`);
        return true;
      }
      
      // Check dependencies
      await this._checkDependencies(plugin);
      
      // Load plugin module
      const pluginModule = require(path.join(plugin.path, plugin.main));
      
      // Create plugin instance
      if (typeof pluginModule.default === 'function') {
        plugin.instance = new pluginModule.default(this.core, this);
      } else if (typeof pluginModule === 'function') {
        plugin.instance = new pluginModule(this.core, this);
      } else {
        throw new Error(`Plugin ${pluginId} does not export a constructor`);
      }
      
      // Update plugin status
      plugin.status = 'loaded';
      plugin.loadedAt = new Date();
      
      this.logger.info(`Plugin ${plugin.name} (${pluginId}) loaded`);
      
      // Emit plugin loaded event
      this.emit('plugin:loaded', { pluginId, plugin });
      
      return true;
    } catch (error) {
      this.logger.error(`Failed to load plugin ${pluginId}: ${error.message}`, error);
      
      // Update plugin status
      const plugin = this.plugins.get(pluginId);
      if (plugin) {
        plugin.status = 'error';
        plugin.error = error.message;
      }
      
      // Emit plugin error event
      this.emit('plugin:error', { pluginId, error: error.message });
      
      return false;
    }
  }
  
  /**
   * Activates a plugin
   * 
   * @param {string} pluginId - Plugin ID
   * @returns {Promise<boolean>} True if plugin was activated successfully
   */
  async activatePlugin(pluginId) {
    try {
      if (!this.isInitialized) {
        throw new Error('Plugin Architecture not initialized');
      }
      
      // Get plugin
      const plugin = this.plugins.get(pluginId);
      
      if (!plugin) {
        throw new Error(`Plugin ${pluginId} not found`);
      }
      
      // Check if plugin is already activated
      if (plugin.status === 'activated') {
        this.logger.info(`Plugin ${plugin.name} (${pluginId}) already activated`);
        return true;
      }
      
      // Check if plugin is loaded
      if (plugin.status !== 'loaded') {
        await this.loadPlugin(pluginId);
      }
      
      // Activate plugin
      if (plugin.instance && typeof plugin.instance.activate === 'function') {
        await plugin.instance.activate();
      }
      
      // Register plugin hooks
      await this._registerPluginHooks(plugin);
      
      // Register plugin extension points
      await this._registerPluginExtensionPoints(plugin);
      
      // Update plugin status
      plugin.status = 'activated';
      plugin.activatedAt = new Date();
      
      this.logger.info(`Plugin ${plugin.name} (${pluginId}) activated`);
      
      // Emit plugin activated event
      this.emit('plugin:activated', { pluginId, plugin });
      
      return true;
    } catch (error) {
      this.logger.error(`Failed to activate plugin ${pluginId}: ${error.message}`, error);
      
      // Update plugin status
      const plugin = this.plugins.get(pluginId);
      if (plugin) {
        plugin.status = 'error';
        plugin.error = error.message;
      }
      
      // Emit plugin error event
      this.emit('plugin:error', { pluginId, error: error.message });
      
      return false;
    }
  }
  
  /**
   * Deactivates a plugin
   * 
   * @param {string} pluginId - Plugin ID
   * @returns {Promise<boolean>} True if plugin was deactivated successfully
   */
  async deactivatePlugin(pluginId) {
    try {
      if (!this.isInitialized) {
        throw new Error('Plugin Architecture not initialized');
      }
      
      // Get plugin
      const plugin = this.plugins.get(pluginId);
      
      if (!plugin) {
        throw new Error(`Plugin ${pluginId} not found`);
      }
      
      // Check if plugin is activated
      if (plugin.status !== 'activated') {
        this.logger.info(`Plugin ${plugin.name} (${pluginId}) is not activated`);
        return true;
      }
      
      // Unregister plugin hooks
      await this._unregisterPluginHooks(plugin);
      
      // Unregister plugin extension points
      await this._unregisterPluginExtensionPoints(plugin);
      
      // Deactivate plugin
      if (plugin.instance && typeof plugin.instance.deactivate === 'function') {
        await plugin.instance.deactivate();
      }
      
      // Update plugin status
      plugin.status = 'loaded';
      plugin.deactivatedAt = new Date();
      
      this.logger.info(`Plugin ${plugin.name} (${pluginId}) deactivated`);
      
      // Emit plugin deactivated event
      this.emit('plugin:deactivated', { pluginId, plugin });
      
      return true;
    } catch (error) {
      this.logger.error(`Failed to deactivate plugin ${pluginId}: ${error.message}`, error);
      
      // Emit plugin error event
      this.emit('plugin:error', { pluginId, error: error.message });
      
      return false;
    }
  }
  
  /**
   * Unloads a plugin
   * 
   * @param {string} pluginId - Plugin ID
   * @returns {Promise<boolean>} True if plugin was unloaded successfully
   */
  async unloadPlugin(pluginId) {
    try {
      if (!this.isInitialized) {
        throw new Error('Plugin Architecture not initialized');
      }
      
      // Get plugin
      const plugin = this.plugins.get(pluginId);
      
      if (!plugin) {
        throw new Error(`Plugin ${pluginId} not found`);
      }
      
      // Check if plugin is activated
      if (plugin.status === 'activated') {
        await this.deactivatePlugin(pluginId);
      }
      
      // Unload plugin
      if (plugin.instance && typeof plugin.instance.unload === 'function') {
        await plugin.instance.unload();
      }
      
      // Clear plugin instance
      plugin.instance = null;
      
      // Update plugin status
      plugin.status = 'registered';
      plugin.unloadedAt = new Date();
      
      // Clear module from require cache
      const modulePath = path.join(plugin.path, plugin.main);
      delete require.cache[require.resolve(modulePath)];
      
      this.logger.info(`Plugin ${plugin.name} (${pluginId}) unloaded`);
      
      // Emit plugin unloaded event
      this.emit('plugin:unloaded', { pluginId, plugin });
      
      return true;
    } catch (error) {
      this.logger.error(`Failed to unload plugin ${pluginId}: ${error.message}`, error);
      
      // Emit plugin error event
      this.emit('plugin:error', { pluginId, error: error.message });
      
      return false;
    }
  }
  
  /**
   * Unregisters a plugin
   * 
   * @param {string} pluginId - Plugin ID
   * @returns {Promise<boolean>} True if plugin was unregistered successfully
   */
  async unregisterPlugin(pluginId) {
    try {
      if (!this.isInitialized) {
        throw new Error('Plugin Architecture not initialized');
      }
      
      // Get plugin
      const plugin = this.plugins.get(pluginId);
      
      if (!plugin) {
        throw new Error(`Plugin ${pluginId} not found`);
      }
      
      // Check if plugin is loaded or activated
      if (plugin.status === 'loaded' || plugin.status === 'activated') {
        await this.unloadPlugin(pluginId);
      }
      
      // Unregister plugin
      this.plugins.delete(pluginId);
      
      this.logger.info(`Plugin ${plugin.name} (${pluginId}) unregistered`);
      
      // Emit plugin unregistered event
      this.emit('plugin:unregistered', { pluginId, plugin });
      
      return true;
    } catch (error) {
      this.logger.error(`Failed to unregister plugin ${pluginId}: ${error.message}`, error);
      
      // Emit plugin error event
      this.emit('plugin:error', { pluginId, error: error.message });
      
      return false;
    }
  }
  
  /**
   * Gets a plugin by ID
   * 
   * @param {string} pluginId - Plugin ID
   * @returns {Object|null} Plugin object or null if not found
   */
  getPlugin(pluginId) {
    return this.plugins.get(pluginId) || null;
  }
  
  /**
   * Gets all plugins
   * 
   * @returns {Array<Object>} Array of plugin objects
   */
  getAllPlugins() {
    return Array.from(this.plugins.values());
  }
  
  /**
   * Gets active plugins
   * 
   * @returns {Array<Object>} Array of active plugin objects
   */
  getActivePlugins() {
    return Array.from(this.plugins.values())
      .filter(plugin => plugin.status === 'activated');
  }
  
  /**
   * Registers a hook
   * 
   * @param {string} hookName - Hook name
   * @param {Function} callback - Hook callback function
   * @param {Object} options - Hook options
   * @returns {string} Hook ID
   */
  registerHook(hookName, callback, options = {}) {
    try {
      if (!this.isInitialized) {
        throw new Error('Plugin Architecture not initialized');
      }
      
      // Generate hook ID
      const hookId = `hook-${uuidv4()}`;
      
      // Get or create hook array
      if (!this.hooks.has(hookName)) {
        this.hooks.set(hookName, []);
      }
      
      const hooks = this.hooks.get(hookName);
      
      // Add hook
      hooks.push({
        id: hookId,
        callback,
        priority: options.priority || 10,
        pluginId: options.pluginId
      });
      
      // Sort hooks by priority (higher priority first)
      hooks.sort((a, b) => b.priority - a.priority);
      
      this.logger.debug(`Hook ${hookName} registered with ID ${hookId}`);
      
      return hookId;
    } catch (error) {
      this.logger.error(`Failed to register hook ${hookName}: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Unregisters a hook
   * 
   * @param {string} hookId - Hook ID
   * @returns {boolean} True if hook was unregistered
   */
  unregisterHook(hookId) {
    try {
      if (!this.isInitialized) {
        throw new Error('Plugin Architecture not initialized');
      }
      
      // Find hook
      for (const [hookName, hooks] of this.hooks.entries()) {
        const index = hooks.findIndex(hook => hook.id === hookId);
        
        if (index !== -1) {
          // Remove hook
          hooks.splice(index, 1);
          
          this.logger.debug(`Hook ${hookId} unregistered from ${hookName}`);
          
          return true;
        }
      }
      
      return false;
    } catch (error) {
      this.logger.error(`Failed to unregister hook ${hookId}: ${error.message}`, error);
      return false;
    }
  }
  
  /**
   * Applies hooks
   * 
   * @param {string} hookName - Hook name
   * @param {*} value - Value to pass to hooks
   * @param {Object} context - Hook context
   * @returns {Promise<*>} Modified value after all hooks have been applied
   */
  async applyHooks(hookName, value, context = {}) {
    try {
      if (!this.isInitialized) {
        throw new Error('Plugin Architecture not initialized');
      }
      
      // Get hooks
      const hooks = this.hooks.get(hookName) || [];
      
      // Apply hooks
      let result = value;
      
      for (const hook of hooks) {
        try {
          result = await hook.callback(result, context);
        } catch (error) {
          this.logger.error(`Error in hook ${hook.id} for ${hookName}: ${error.message}`, error);
        }
      }
      
      return result;
    } catch (error) {
      this.logger.error(`Failed to apply hooks for ${hookName}: ${error.message}`, error);
      return value;
    }
  }
  
  /**
   * Registers an extension point
   * 
   * @param {string} name - Extension point name
   * @param {Object} definition - Extension point definition
   * @returns {boolean} True if extension point was registered
   */
  registerExtensionPoint(name, definition) {
    try {
      if (!this.isInitialized) {
        throw new Error('Plugin Architecture not initialized');
      }
      
      // Check if extension point already exists
      if (this.extensionPoints.has(name)) {
        throw new Error(`Extension point ${name} already exists`);
      }
      
      // Validate definition
      if (!definition || typeof definition !== 'object') {
        throw new Error('Extension point definition must be an object');
      }
      
      if (!definition.schema) {
        throw new Error('Extension point definition must include a schema');
      }
      
      // Register extension point
      this.extensionPoints.set(name, {
        name,
        schema: definition.schema,
        description: definition.description || '',
        extensions: [],
        pluginId: definition.pluginId
      });
      
      this.logger.info(`Extension point ${name} registered`);
      
      // Emit extension point registered event
      this.emit('extensionPoint:registered', { name, definition });
      
      return true;
    } catch (error) {
      this.logger.error(`Failed to register extension point ${name}: ${error.message}`, error);
      return false;
    }
  }
  
  /**
   * Unregisters an extension point
   * 
   * @param {string} name - Extension point name
   * @returns {boolean} True if extension point was unregistered
   */
  unregisterExtensionPoint(name) {
    try {
      if (!this.isInitialized) {
        throw new Error('Plugin Architecture not initialized');
      }
      
      // Check if extension point exists
      if (!this.extensionPoints.has(name)) {
        return false;
      }
      
      // Unregister extension point
      this.extensionPoints.delete(name);
      
      this.logger.info(`Extension point ${name} unregistered`);
      
      // Emit extension point unregistered event
      this.emit('extensionPoint:unregistered', { name });
      
      return true;
    } catch (error) {
      this.logger.error(`Failed to unregister extension point ${name}: ${error.message}`, error);
      return false;
    }
  }
  
  /**
   * Registers an extension
   * 
   * @param {string} extensionPointName - Extension point name
   * @param {Object} extension - Extension data
   * @param {Object} options - Extension options
   * @returns {string} Extension ID
   */
  registerExtension(extensionPointName, extension, options = {}) {
    try {
      if (!this.isInitialized) {
        throw new Error('Plugin Architecture not initialized');
      }
      
      // Check if extension point exists
      const extensionPoint = this.extensionPoints.get(extensionPointName);
      
      if (!extensionPoint) {
        throw new Error(`Extension point ${extensionPointName} not found`);
      }
      
      // Validate extension against schema
      this._validateExtension(extension, extensionPoint.schema);
      
      // Generate extension ID
      const extensionId = `extension-${uuidv4()}`;
      
      // Add extension
      extensionPoint.extensions.push({
        id: extensionId,
        data: extension,
        pluginId: options.pluginId,
        priority: options.priority || 10
      });
      
      // Sort extensions by priority (higher priority first)
      extensionPoint.extensions.sort((a, b) => b.priority - a.priority);
      
      this.logger.debug(`Extension registered for ${extensionPointName} with ID ${extensionId}`);
      
      // Emit extension registered event
      this.emit('extension:registered', { 
        extensionPointName, 
        extensionId, 
        extension 
      });
      
      return extensionId;
    } catch (error) {
      this.logger.error(`Failed to register extension for ${extensionPointName}: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Unregisters an extension
   * 
   * @param {string} extensionId - Extension ID
   * @returns {boolean} True if extension was unregistered
   */
  unregisterExtension(extensionId) {
    try {
      if (!this.isInitialized) {
        throw new Error('Plugin Architecture not initialized');
      }
      
      // Find extension
      for (const [extensionPointName, extensionPoint] of this.extensionPoints.entries()) {
        const index = extensionPoint.extensions.findIndex(ext => ext.id === extensionId);
        
        if (index !== -1) {
          // Remove extension
          extensionPoint.extensions.splice(index, 1);
          
          this.logger.debug(`Extension ${extensionId} unregistered from ${extensionPointName}`);
          
          // Emit extension unregistered event
          this.emit('extension:unregistered', { 
            extensionPointName, 
            extensionId 
          });
          
          return true;
        }
      }
      
      return false;
    } catch (error) {
      this.logger.error(`Failed to unregister extension ${extensionId}: ${error.message}`, error);
      return false;
    }
  }
  
  /**
   * Gets extensions for an extension point
   * 
   * @param {string} extensionPointName - Extension point name
   * @returns {Array<Object>} Array of extensions
   */
  getExtensions(extensionPointName) {
    try {
      if (!this.isInitialized) {
        throw new Error('Plugin Architecture not initialized');
      }
      
      // Check if extension point exists
      const extensionPoint = this.extensionPoints.get(extensionPointName);
      
      if (!extensionPoint) {
        return [];
      }
      
      // Return extensions
      return extensionPoint.extensions.map(ext => ({
        id: ext.id,
        data: ext.data,
        pluginId: ext.pluginId
      }));
    } catch (error) {
      this.logger.error(`Failed to get extensions for ${extensionPointName}: ${error.message}`, error);
      return [];
    }
  }
  
  /**
   * Loads all plugins from plugin directories
   * 
   * @private
   * @returns {Promise<void>}
   */
  async _loadPlugins() {
    try {
      this.logger.info('Loading plugins from directories');
      
      // Get plugin directories
      for (const dir of this.pluginDirectories) {
        try {
          // Check if directory exists
          const stats = await fs.stat(dir).catch(() => null);
          
          if (!stats || !stats.isDirectory()) {
            continue;
          }
          
          // Get plugin directories
          const entries = await fs.readdir(dir, { withFileTypes: true });
          const pluginDirs = entries.filter(entry => entry.isDirectory());
          
          // Load plugins
          for (const pluginDir of pluginDirs) {
            const pluginPath = path.join(dir, pluginDir.name);
            
            try {
              // Check for plugin manifest
              const manifestPath = path.join(pluginPath, 'plugin.json');
              const manifestExists = await fs.stat(manifestPath).catch(() => null);
              
              if (!manifestExists) {
                continue;
              }
              
              // Read plugin manifest
              const manifestContent = await fs.readFile(manifestPath, 'utf8');
              const manifest = JSON.parse(manifestContent);
              
              // Add plugin path
              manifest.path = pluginPath;
              
              // Register plugin
              const pluginId = await this.registerPlugin(manifest);
              
              // Check if plugin should be activated
              const config = this.configManager.getConfig();
              const pluginsConfig = config.plugins || {};
              
              if (pluginsConfig[pluginId]?.autoActivate !== false) {
                // Load and activate plugin
                await this.loadPlugin(pluginId);
                await this.activatePlugin(pluginId);
              }
            } catch (error) {
              this.logger.error(`Failed to load plugin from ${pluginPath}: ${error.message}`, error);
            }
          }
        } catch (error) {
          this.logger.error(`Failed to read plugin directory ${dir}: ${error.message}`, error);
        }
      }
    } catch (error) {
      this.logger.error(`Failed to load plugins: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Registers core extension points
   * 
   * @private
   */
  _registerCoreExtensionPoints() {
    // Register core extension points
    this.registerExtensionPoint('core.tools', {
      description: 'Register additional tools for Aideon AI Lite',
      schema: {
        type: 'object',
        required: ['id', 'name', 'description', 'category', 'handler'],
        properties: {
          id: { type: 'string' },
          name: { type: 'string' },
          description: { type: 'string' },
          category: { type: 'string' },
          handler: { instanceof: 'Function' }
        }
      }
    });
    
    this.registerExtensionPoint('core.models', {
      description: 'Register additional AI models for Aideon AI Lite',
      schema: {
        type: 'object',
        required: ['id', 'name', 'provider', 'capabilities', 'handler'],
        properties: {
          id: { type: 'string' },
          name: { type: 'string' },
          provider: { type: 'string' },
          capabilities: { 
            type: 'array',
            items: { type: 'string' }
          },
          handler: { instanceof: 'Function' }
        }
      }
    });
    
    this.registerExtensionPoint('core.ui.components', {
      description: 'Register additional UI components for Aideon AI Lite',
      schema: {
        type: 'object',
        required: ['id', 'name', 'component'],
        properties: {
          id: { type: 'string' },
          name: { type: 'string' },
          component: { instanceof: 'Function' },
          mountPoint: { type: 'string' }
        }
      }
    });
    
    this.registerExtensionPoint('core.commands', {
      description: 'Register additional commands for Aideon AI Lite',
      schema: {
        type: 'object',
        required: ['id', 'name', 'handler'],
        properties: {
          id: { type: 'string' },
          name: { type: 'string' },
          description: { type: 'string' },
          handler: { instanceof: 'Function' },
          keybinding: { type: 'string' }
        }
      }
    });
    
    this.registerExtensionPoint('core.settings', {
      description: 'Register additional settings for Aideon AI Lite',
      schema: {
        type: 'object',
        required: ['id', 'name', 'settings'],
        properties: {
          id: { type: 'string' },
          name: { type: 'string' },
          description: { type: 'string' },
          settings: { 
            type: 'array',
            items: {
              type: 'object',
              required: ['id', 'name', 'type'],
              properties: {
                id: { type: 'string' },
                name: { type: 'string' },
                description: { type: 'string' },
                type: { type: 'string' },
                default: {}
              }
            }
          }
        }
      }
    });
  }
  
  /**
   * Validates plugin information
   * 
   * @private
   * @param {Object} pluginInfo - Plugin information
   */
  _validatePluginInfo(pluginInfo) {
    if (!pluginInfo) {
      throw new Error('Plugin info is required');
    }
    
    if (!pluginInfo.name) {
      throw new Error('Plugin name is required');
    }
    
    if (!pluginInfo.version) {
      throw new Error('Plugin version is required');
    }
    
    if (!pluginInfo.main) {
      throw new Error('Plugin main file is required');
    }
    
    if (!pluginInfo.path) {
      throw new Error('Plugin path is required');
    }
  }
  
  /**
   * Validates an extension against a schema
   * 
   * @private
   * @param {Object} extension - Extension data
   * @param {Object} schema - Schema to validate against
   */
  _validateExtension(extension, schema) {
    // Simple schema validation
    if (schema.type === 'object') {
      if (typeof extension !== 'object' || extension === null) {
        throw new Error(`Extension must be an object`);
      }
      
      // Check required properties
      if (schema.required) {
        for (const prop of schema.required) {
          if (!(prop in extension)) {
            throw new Error(`Extension is missing required property: ${prop}`);
          }
        }
      }
      
      // Check property types
      if (schema.properties) {
        for (const [prop, propSchema] of Object.entries(schema.properties)) {
          if (prop in extension) {
            if (propSchema.type === 'string' && typeof extension[prop] !== 'string') {
              throw new Error(`Property ${prop} must be a string`);
            } else if (propSchema.type === 'number' && typeof extension[prop] !== 'number') {
              throw new Error(`Property ${prop} must be a number`);
            } else if (propSchema.type === 'boolean' && typeof extension[prop] !== 'boolean') {
              throw new Error(`Property ${prop} must be a boolean`);
            } else if (propSchema.type === 'array' && !Array.isArray(extension[prop])) {
              throw new Error(`Property ${prop} must be an array`);
            } else if (propSchema.type === 'object' && (typeof extension[prop] !== 'object' || extension[prop] === null)) {
              throw new Error(`Property ${prop} must be an object`);
            } else if (propSchema.instanceof === 'Function' && typeof extension[prop] !== 'function') {
              throw new Error(`Property ${prop} must be a function`);
            }
            
            // Validate array items
            if (propSchema.type === 'array' && propSchema.items && Array.isArray(extension[prop])) {
              for (let i = 0; i < extension[prop].length; i++) {
                const item = extension[prop][i];
                
                if (propSchema.items.type === 'string' && typeof item !== 'string') {
                  throw new Error(`Item ${i} in ${prop} must be a string`);
                } else if (propSchema.items.type === 'number' && typeof item !== 'number') {
                  throw new Error(`Item ${i} in ${prop} must be a number`);
                } else if (propSchema.items.type === 'boolean' && typeof item !== 'boolean') {
                  throw new Error(`Item ${i} in ${prop} must be a boolean`);
                } else if (propSchema.items.type === 'object' && (typeof item !== 'object' || item === null)) {
                  throw new Error(`Item ${i} in ${prop} must be an object`);
                }
              }
            }
          }
        }
      }
    }
  }
  
  /**
   * Checks plugin dependencies
   * 
   * @private
   * @param {Object} plugin - Plugin object
   * @returns {Promise<void>}
   */
  async _checkDependencies(plugin) {
    if (!plugin.dependencies || Object.keys(plugin.dependencies).length === 0) {
      return;
    }
    
    for (const [depId, versionRange] of Object.entries(plugin.dependencies)) {
      // Check if dependency exists
      const dependency = this.plugins.get(depId);
      
      if (!dependency) {
        throw new Error(`Dependency ${depId} not found`);
      }
      
      // Check version
      if (!semver.satisfies(dependency.version, versionRange)) {
        throw new Error(`Dependency ${depId} version ${dependency.version} does not satisfy required range ${versionRange}`);
      }
      
      // Check if dependency is loaded
      if (dependency.status !== 'loaded' && dependency.status !== 'activated') {
        await this.loadPlugin(depId);
      }
      
      // Check if dependency is activated
      if (dependency.status !== 'activated') {
        await this.activatePlugin(depId);
      }
    }
  }
  
  /**
   * Registers plugin hooks
   * 
   * @private
   * @param {Object} plugin - Plugin object
   * @returns {Promise<void>}
   */
  async _registerPluginHooks(plugin) {
    if (!plugin.hooks || plugin.hooks.length === 0) {
      return;
    }
    
    for (const hook of plugin.hooks) {
      if (!hook.name || typeof hook.name !== 'string') {
        this.logger.warn(`Invalid hook name in plugin ${plugin.id}`);
        continue;
      }
      
      if (!hook.handler && plugin.instance) {
        // Try to get handler from plugin instance
        const handlerName = typeof hook.handler === 'string' ? hook.handler : `on${hook.name.charAt(0).toUpperCase()}${hook.name.slice(1)}`;
        
        if (typeof plugin.instance[handlerName] === 'function') {
          hook.handler = plugin.instance[handlerName].bind(plugin.instance);
        }
      }
      
      if (typeof hook.handler !== 'function') {
        this.logger.warn(`Invalid hook handler for ${hook.name} in plugin ${plugin.id}`);
        continue;
      }
      
      // Register hook
      this.registerHook(hook.name, hook.handler, {
        priority: hook.priority,
        pluginId: plugin.id
      });
    }
  }
  
  /**
   * Unregisters plugin hooks
   * 
   * @private
   * @param {Object} plugin - Plugin object
   * @returns {Promise<void>}
   */
  async _unregisterPluginHooks(plugin) {
    // Find all hooks for this plugin
    for (const [hookName, hooks] of this.hooks.entries()) {
      const pluginHooks = hooks.filter(hook => hook.pluginId === plugin.id);
      
      for (const hook of pluginHooks) {
        this.unregisterHook(hook.id);
      }
    }
  }
  
  /**
   * Registers plugin extension points
   * 
   * @private
   * @param {Object} plugin - Plugin object
   * @returns {Promise<void>}
   */
  async _registerPluginExtensionPoints(plugin) {
    if (!plugin.extensionPoints || plugin.extensionPoints.length === 0) {
      return;
    }
    
    for (const extPoint of plugin.extensionPoints) {
      if (!extPoint.name || typeof extPoint.name !== 'string') {
        this.logger.warn(`Invalid extension point name in plugin ${plugin.id}`);
        continue;
      }
      
      if (!extPoint.schema) {
        this.logger.warn(`Missing schema for extension point ${extPoint.name} in plugin ${plugin.id}`);
        continue;
      }
      
      // Register extension point
      this.registerExtensionPoint(extPoint.name, {
        schema: extPoint.schema,
        description: extPoint.description,
        pluginId: plugin.id
      });
    }
    
    // Register extensions if plugin provides them
    if (plugin.instance && typeof plugin.instance.getExtensions === 'function') {
      const extensions = await plugin.instance.getExtensions();
      
      if (extensions && typeof extensions === 'object') {
        for (const [extPointName, extData] of Object.entries(extensions)) {
          if (Array.isArray(extData)) {
            for (const ext of extData) {
              try {
                this.registerExtension(extPointName, ext, {
                  pluginId: plugin.id,
                  priority: ext.priority
                });
              } catch (error) {
                this.logger.error(`Failed to register extension for ${extPointName} from plugin ${plugin.id}: ${error.message}`, error);
              }
            }
          } else {
            try {
              this.registerExtension(extPointName, extData, {
                pluginId: plugin.id,
                priority: extData.priority
              });
            } catch (error) {
              this.logger.error(`Failed to register extension for ${extPointName} from plugin ${plugin.id}: ${error.message}`, error);
            }
          }
        }
      }
    }
  }
  
  /**
   * Unregisters plugin extension points
   * 
   * @private
   * @param {Object} plugin - Plugin object
   * @returns {Promise<void>}
   */
  async _unregisterPluginExtensionPoints(plugin) {
    // Unregister extensions
    for (const [extPointName, extPoint] of this.extensionPoints.entries()) {
      const pluginExts = extPoint.extensions.filter(ext => ext.pluginId === plugin.id);
      
      for (const ext of pluginExts) {
        this.unregisterExtension(ext.id);
      }
    }
    
    // Unregister extension points
    const pluginExtPoints = Array.from(this.extensionPoints.entries())
      .filter(([name, extPoint]) => extPoint.pluginId === plugin.id)
      .map(([name]) => name);
    
    for (const extPointName of pluginExtPoints) {
      this.unregisterExtensionPoint(extPointName);
    }
  }
}

module.exports = { PluginArchitecture };
