/**
 * OfflineCapabilityManager.js
 * 
 * Enables offline capabilities for Aideon AI Lite tools.
 * Manages local model caching, data synchronization, and graceful degradation
 * when internet connectivity is limited or unavailable.
 * 
 * @author Aideon AI Team
 * @version 1.0.0
 */

const EventEmitter = require('events');
const path = require('path');
const fs = require('fs').promises;
const os = require('os');

/**
 * Offline Capability Manager for Aideon AI Lite
 */
class OfflineCapabilityManager extends EventEmitter {
  /**
   * Creates a new OfflineCapabilityManager instance
   * 
   * @param {Object} core - The Aideon core instance
   */
  constructor(core) {
    super();
    
    this.core = core;
    this.logger = core.getLogManager().getLogger('offline-capability');
    this.configManager = core.getConfigManager();
    
    this.isInitialized = false;
    this.isOnline = true;
    this.connectivityCheckInterval = null;
    this.syncQueue = [];
    this.offlineModels = new Map();
    this.offlineData = new Map();
    this.toolOfflineStatus = new Map();
    
    // Bind methods
    this._checkConnectivity = this._checkConnectivity.bind(this);
    this._handleConnectivityChange = this._handleConnectivityChange.bind(this);
    this._processSyncQueue = this._processSyncQueue.bind(this);
  }
  
  /**
   * Initializes the offline capability manager
   * 
   * @param {Object} options - Initialization options
   * @returns {Promise<boolean>} True if initialization was successful
   */
  async initialize(options = {}) {
    try {
      this.logger.info('Initializing Offline Capability Manager');
      
      // Set options
      this.options = {
        connectivityCheckInterval: 30000, // 30 seconds
        maxSyncQueueSize: 1000,
        offlineDataDir: path.join(this.configManager.getDataDir(), 'offline'),
        offlineModelDir: path.join(this.configManager.getDataDir(), 'offline-models'),
        ...options
      };
      
      // Create offline directories if they don't exist
      await this._ensureDirectories();
      
      // Load offline models
      await this._loadOfflineModels();
      
      // Load offline data
      await this._loadOfflineData();
      
      // Initialize tool offline status
      await this._initializeToolOfflineStatus();
      
      // Start connectivity monitoring
      this._startConnectivityMonitoring();
      
      this.isInitialized = true;
      this.logger.info('Offline Capability Manager initialized successfully');
      
      return true;
    } catch (error) {
      this.logger.error(`Failed to initialize Offline Capability Manager: ${error.message}`, error);
      return false;
    }
  }
  
  /**
   * Checks if a tool can operate offline
   * 
   * @param {string} toolId - Tool ID
   * @returns {boolean} True if tool can operate offline
   */
  canOperateOffline(toolId) {
    return this.toolOfflineStatus.get(toolId) || false;
  }
  
  /**
   * Gets all tools that can operate offline
   * 
   * @returns {Array<string>} Array of tool IDs that can operate offline
   */
  getOfflineCapableTools() {
    return Array.from(this.toolOfflineStatus.entries())
      .filter(([_, canOperate]) => canOperate)
      .map(([toolId, _]) => toolId);
  }
  
  /**
   * Gets current connectivity status
   * 
   * @returns {boolean} True if online, false if offline
   */
  isConnected() {
    return this.isOnline;
  }
  
  /**
   * Gets an offline model
   * 
   * @param {string} modelId - Model ID
   * @returns {Object|null} Offline model or null if not available
   */
  getOfflineModel(modelId) {
    return this.offlineModels.get(modelId) || null;
  }
  
  /**
   * Gets all available offline models
   * 
   * @returns {Map<string, Object>} Map of model ID to model
   */
  getAllOfflineModels() {
    return new Map(this.offlineModels);
  }
  
  /**
   * Gets offline data
   * 
   * @param {string} key - Data key
   * @returns {any|null} Offline data or null if not available
   */
  getOfflineData(key) {
    return this.offlineData.get(key) || null;
  }
  
  /**
   * Sets offline data
   * 
   * @param {string} key - Data key
   * @param {any} data - Data to store
   * @returns {Promise<boolean>} True if data was stored
   */
  async setOfflineData(key, data) {
    try {
      if (!this.isInitialized) {
        throw new Error('Offline Capability Manager not initialized');
      }
      
      this.offlineData.set(key, data);
      
      // Save to disk
      await this._saveOfflineData(key, data);
      
      return true;
    } catch (error) {
      this.logger.error(`Failed to set offline data: ${error.message}`, error);
      return false;
    }
  }
  
  /**
   * Downloads a model for offline use
   * 
   * @param {string} modelId - Model ID
   * @param {Object} options - Download options
   * @returns {Promise<boolean>} True if model was downloaded
   */
  async downloadModelForOffline(modelId, options = {}) {
    try {
      if (!this.isInitialized) {
        throw new Error('Offline Capability Manager not initialized');
      }
      
      if (!this.isOnline) {
        throw new Error('Cannot download model while offline');
      }
      
      this.logger.info(`Downloading model ${modelId} for offline use`);
      
      // Get model manager
      const modelManager = this.core.getModelManager();
      
      if (!modelManager) {
        throw new Error('Model Manager not available');
      }
      
      // Check if model exists
      const model = await modelManager.getModel(modelId);
      
      if (!model) {
        throw new Error(`Model ${modelId} not found`);
      }
      
      // Check if model supports offline use
      if (!model.supportsOffline) {
        throw new Error(`Model ${modelId} does not support offline use`);
      }
      
      // Download model
      const modelPath = path.join(this.options.offlineModelDir, `${modelId}.bin`);
      const metadataPath = path.join(this.options.offlineModelDir, `${modelId}.json`);
      
      // Emit download start event
      this.emit('model:download:start', {
        modelId,
        timestamp: new Date()
      });
      
      // Download model file
      await modelManager.downloadModel(modelId, modelPath, options);
      
      // Save metadata
      const metadata = {
        id: model.id,
        name: model.name,
        version: model.version,
        modality: model.modality,
        capabilities: model.capabilities,
        parameters: model.parameters,
        quantization: options.quantization || 'none',
        downloadedAt: new Date(),
        filePath: modelPath
      };
      
      await fs.writeFile(metadataPath, JSON.stringify(metadata, null, 2));
      
      // Add to offline models
      this.offlineModels.set(modelId, {
        ...metadata,
        downloadedAt: new Date(metadata.downloadedAt)
      });
      
      // Emit download complete event
      this.emit('model:download:complete', {
        modelId,
        timestamp: new Date(),
        metadata
      });
      
      this.logger.info(`Model ${modelId} downloaded successfully for offline use`);
      
      return true;
    } catch (error) {
      this.logger.error(`Failed to download model for offline use: ${error.message}`, error);
      
      // Emit download error event
      this.emit('model:download:error', {
        modelId,
        timestamp: new Date(),
        error: error.message
      });
      
      return false;
    }
  }
  
  /**
   * Removes an offline model
   * 
   * @param {string} modelId - Model ID
   * @returns {Promise<boolean>} True if model was removed
   */
  async removeOfflineModel(modelId) {
    try {
      if (!this.isInitialized) {
        throw new Error('Offline Capability Manager not initialized');
      }
      
      if (!this.offlineModels.has(modelId)) {
        throw new Error(`Model ${modelId} not available offline`);
      }
      
      this.logger.info(`Removing offline model ${modelId}`);
      
      // Get model metadata
      const model = this.offlineModels.get(modelId);
      
      // Delete model file
      if (model.filePath) {
        await fs.unlink(model.filePath).catch(err => {
          this.logger.warn(`Failed to delete model file: ${err.message}`);
        });
      }
      
      // Delete metadata file
      const metadataPath = path.join(this.options.offlineModelDir, `${modelId}.json`);
      await fs.unlink(metadataPath).catch(err => {
        this.logger.warn(`Failed to delete metadata file: ${err.message}`);
      });
      
      // Remove from offline models
      this.offlineModels.delete(modelId);
      
      // Emit model removed event
      this.emit('model:offline:removed', {
        modelId,
        timestamp: new Date()
      });
      
      this.logger.info(`Offline model ${modelId} removed successfully`);
      
      return true;
    } catch (error) {
      this.logger.error(`Failed to remove offline model: ${error.message}`, error);
      return false;
    }
  }
  
  /**
   * Adds an operation to the sync queue
   * 
   * @param {Object} operation - Operation to queue
   * @returns {boolean} True if operation was queued
   */
  queueSyncOperation(operation) {
    try {
      if (!this.isInitialized) {
        throw new Error('Offline Capability Manager not initialized');
      }
      
      if (!operation || !operation.type || !operation.data) {
        throw new Error('Invalid sync operation');
      }
      
      // Check queue size
      if (this.syncQueue.length >= this.options.maxSyncQueueSize) {
        throw new Error('Sync queue is full');
      }
      
      // Add operation to queue
      this.syncQueue.push({
        ...operation,
        timestamp: new Date(),
        id: `sync-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
      });
      
      this.logger.debug(`Queued sync operation: ${operation.type}`);
      
      // If online, process queue
      if (this.isOnline) {
        this._processSyncQueue();
      }
      
      return true;
    } catch (error) {
      this.logger.error(`Failed to queue sync operation: ${error.message}`, error);
      return false;
    }
  }
  
  /**
   * Registers a tool for offline capability
   * 
   * @param {string} toolId - Tool ID
   * @param {boolean} canOperateOffline - Whether tool can operate offline
   * @returns {boolean} True if tool was registered
   */
  registerToolOfflineCapability(toolId, canOperateOffline) {
    try {
      if (!this.isInitialized) {
        throw new Error('Offline Capability Manager not initialized');
      }
      
      if (!toolId) {
        throw new Error('Tool ID is required');
      }
      
      this.toolOfflineStatus.set(toolId, !!canOperateOffline);
      
      this.logger.info(`Registered tool ${toolId} with offline capability: ${canOperateOffline}`);
      
      // Save tool offline status
      this._saveToolOfflineStatus();
      
      return true;
    } catch (error) {
      this.logger.error(`Failed to register tool offline capability: ${error.message}`, error);
      return false;
    }
  }
  
  /**
   * Forces a connectivity check
   * 
   * @returns {Promise<boolean>} True if online, false if offline
   */
  async checkConnectivity() {
    return this._checkConnectivity();
  }
  
  /**
   * Ensures required directories exist
   * 
   * @private
   * @returns {Promise<void>}
   */
  async _ensureDirectories() {
    try {
      // Create offline data directory
      await fs.mkdir(this.options.offlineDataDir, { recursive: true });
      
      // Create offline model directory
      await fs.mkdir(this.options.offlineModelDir, { recursive: true });
      
      this.logger.debug('Offline directories created');
    } catch (error) {
      this.logger.error(`Failed to create offline directories: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Loads offline models
   * 
   * @private
   * @returns {Promise<void>}
   */
  async _loadOfflineModels() {
    try {
      // Get all JSON files in offline model directory
      const files = await fs.readdir(this.options.offlineModelDir);
      const metadataFiles = files.filter(file => file.endsWith('.json'));
      
      for (const file of metadataFiles) {
        try {
          // Read and parse metadata
          const metadataPath = path.join(this.options.offlineModelDir, file);
          const content = await fs.readFile(metadataPath, 'utf8');
          const metadata = JSON.parse(content);
          
          // Check if model file exists
          const modelPath = metadata.filePath;
          const modelExists = await fs.stat(modelPath).catch(() => null);
          
          if (!modelExists) {
            this.logger.warn(`Model file not found for ${metadata.id}, skipping`);
            continue;
          }
          
          // Add to offline models
          this.offlineModels.set(metadata.id, {
            ...metadata,
            downloadedAt: new Date(metadata.downloadedAt)
          });
          
          this.logger.debug(`Loaded offline model: ${metadata.id}`);
        } catch (err) {
          this.logger.warn(`Failed to load offline model from ${file}: ${err.message}`);
        }
      }
      
      this.logger.info(`Loaded ${this.offlineModels.size} offline models`);
    } catch (error) {
      this.logger.error(`Failed to load offline models: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Loads offline data
   * 
   * @private
   * @returns {Promise<void>}
   */
  async _loadOfflineData() {
    try {
      // Get all JSON files in offline data directory
      const files = await fs.readdir(this.options.offlineDataDir);
      const dataFiles = files.filter(file => file.endsWith('.json'));
      
      for (const file of dataFiles) {
        try {
          // Read and parse data
          const dataPath = path.join(this.options.offlineDataDir, file);
          const content = await fs.readFile(dataPath, 'utf8');
          const data = JSON.parse(content);
          
          // Extract key from filename
          const key = file.replace('.json', '');
          
          // Add to offline data
          this.offlineData.set(key, data);
          
          this.logger.debug(`Loaded offline data: ${key}`);
        } catch (err) {
          this.logger.warn(`Failed to load offline data from ${file}: ${err.message}`);
        }
      }
      
      this.logger.info(`Loaded ${this.offlineData.size} offline data items`);
    } catch (error) {
      this.logger.error(`Failed to load offline data: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Initializes tool offline status
   * 
   * @private
   * @returns {Promise<void>}
   */
  async _initializeToolOfflineStatus() {
    try {
      const statusPath = path.join(this.options.offlineDataDir, 'tool-offline-status.json');
      
      // Check if file exists
      const exists = await fs.stat(statusPath).catch(() => null);
      
      if (!exists) {
        this.logger.info('No tool offline status found');
        return;
      }
      
      // Read and parse file
      const content = await fs.readFile(statusPath, 'utf8');
      const status = JSON.parse(content);
      
      // Convert to Map
      this.toolOfflineStatus = new Map(Object.entries(status));
      
      this.logger.info(`Loaded offline status for ${this.toolOfflineStatus.size} tools`);
    } catch (error) {
      this.logger.error(`Failed to initialize tool offline status: ${error.message}`, error);
    }
  }
  
  /**
   * Saves tool offline status
   * 
   * @private
   * @returns {Promise<void>}
   */
  async _saveToolOfflineStatus() {
    try {
      const statusPath = path.join(this.options.offlineDataDir, 'tool-offline-status.json');
      
      // Convert Map to object
      const status = Object.fromEntries(this.toolOfflineStatus);
      
      // Write to file
      await fs.writeFile(statusPath, JSON.stringify(status, null, 2));
      
      this.logger.debug(`Saved offline status for ${this.toolOfflineStatus.size} tools`);
    } catch (error) {
      this.logger.error(`Failed to save tool offline status: ${error.message}`, error);
    }
  }
  
  /**
   * Saves offline data
   * 
   * @private
   * @param {string} key - Data key
   * @param {any} data - Data to save
   * @returns {Promise<void>}
   */
  async _saveOfflineData(key, data) {
    try {
      const dataPath = path.join(this.options.offlineDataDir, `${key}.json`);
      
      // Write to file
      await fs.writeFile(dataPath, JSON.stringify(data, null, 2));
      
      this.logger.debug(`Saved offline data: ${key}`);
    } catch (error) {
      this.logger.error(`Failed to save offline data: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Starts connectivity monitoring
   * 
   * @private
   */
  _startConnectivityMonitoring() {
    // Initial connectivity check
    this._checkConnectivity();
    
    // Start periodic checks
    this.connectivityCheckInterval = setInterval(
      this._checkConnectivity,
      this.options.connectivityCheckInterval
    );
    
    this.logger.info('Connectivity monitoring started');
  }
  
  /**
   * Stops connectivity monitoring
   * 
   * @private
   */
  _stopConnectivityMonitoring() {
    if (this.connectivityCheckInterval) {
      clearInterval(this.connectivityCheckInterval);
      this.connectivityCheckInterval = null;
      
      this.logger.info('Connectivity monitoring stopped');
    }
  }
  
  /**
   * Checks internet connectivity
   * 
   * @private
   * @returns {Promise<boolean>} True if online, false if offline
   */
  async _checkConnectivity() {
    try {
      // Try to connect to multiple reliable endpoints
      const endpoints = [
        'https://www.google.com',
        'https://www.cloudflare.com',
        'https://www.microsoft.com'
      ];
      
      // Use fetch with a short timeout
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);
      
      // Try each endpoint
      for (const endpoint of endpoints) {
        try {
          const response = await fetch(endpoint, {
            method: 'HEAD',
            signal: controller.signal
          });
          
          if (response.ok) {
            clearTimeout(timeoutId);
            
            // We're online
            const wasOffline = !this.isOnline;
            
            if (wasOffline) {
              this._handleConnectivityChange(true);
            }
            
            return true;
          }
        } catch (err) {
          // Continue to next endpoint
        }
      }
      
      clearTimeout(timeoutId);
      
      // All endpoints failed, we're offline
      const wasOnline = this.isOnline;
      
      if (wasOnline) {
        this._handleConnectivityChange(false);
      }
      
      return false;
    } catch (error) {
      this.logger.error(`Connectivity check error: ${error.message}`, error);
      
      // Assume offline on error
      const wasOnline = this.isOnline;
      
      if (wasOnline) {
        this._handleConnectivityChange(false);
      }
      
      return false;
    }
  }
  
  /**
   * Handles connectivity change
   * 
   * @private
   * @param {boolean} isOnline - Whether we're online
   */
  _handleConnectivityChange(isOnline) {
    const previousState = this.isOnline;
    this.isOnline = isOnline;
    
    if (previousState !== isOnline) {
      if (isOnline) {
        this.logger.info('Connectivity restored, now online');
        
        // Process sync queue
        this._processSyncQueue();
        
        // Emit online event
        this.emit('connectivity:online', {
          timestamp: new Date()
        });
      } else {
        this.logger.info('Connectivity lost, now offline');
        
        // Emit offline event
        this.emit('connectivity:offline', {
          timestamp: new Date()
        });
      }
    }
  }
  
  /**
   * Processes the sync queue
   * 
   * @private
   * @returns {Promise<void>}
   */
  async _processSyncQueue() {
    if (!this.isOnline || this.syncQueue.length === 0) {
      return;
    }
    
    this.logger.info(`Processing sync queue (${this.syncQueue.length} operations)`);
    
    // Process operations in order
    const operations = [...this.syncQueue];
    this.syncQueue = [];
    
    for (const operation of operations) {
      try {
        this.logger.debug(`Processing sync operation: ${operation.type} (${operation.id})`);
        
        // Emit sync start event
        this.emit('sync:operation:start', {
          operationId: operation.id,
          type: operation.type,
          timestamp: new Date()
        });
        
        // Process based on operation type
        switch (operation.type) {
          case 'data:update':
            await this._processSyncDataUpdate(operation);
            break;
            
          case 'model:usage':
            await this._processSyncModelUsage(operation);
            break;
            
          case 'tool:usage':
            await this._processSyncToolUsage(operation);
            break;
            
          default:
            this.logger.warn(`Unknown sync operation type: ${operation.type}`);
            break;
        }
        
        // Emit sync complete event
        this.emit('sync:operation:complete', {
          operationId: operation.id,
          type: operation.type,
          timestamp: new Date()
        });
      } catch (error) {
        this.logger.error(`Failed to process sync operation: ${error.message}`, error);
        
        // Emit sync error event
        this.emit('sync:operation:error', {
          operationId: operation.id,
          type: operation.type,
          timestamp: new Date(),
          error: error.message
        });
        
        // Re-queue operation for later retry
        this.syncQueue.push(operation);
      }
    }
    
    this.logger.info('Sync queue processing complete');
  }
  
  /**
   * Processes a data update sync operation
   * 
   * @private
   * @param {Object} operation - Sync operation
   * @returns {Promise<void>}
   */
  async _processSyncDataUpdate(operation) {
    try {
      const { key, data, endpoint } = operation.data;
      
      if (!endpoint) {
        throw new Error('Sync endpoint not specified');
      }
      
      // Send data to endpoint
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          key,
          data,
          timestamp: new Date()
        })
      });
      
      if (!response.ok) {
        throw new Error(`Sync request failed: ${response.status} ${response.statusText}`);
      }
      
      this.logger.debug(`Data sync successful for key: ${key}`);
    } catch (error) {
      this.logger.error(`Data sync failed: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Processes a model usage sync operation
   * 
   * @private
   * @param {Object} operation - Sync operation
   * @returns {Promise<void>}
   */
  async _processSyncModelUsage(operation) {
    try {
      const { modelId, usage } = operation.data;
      
      // Get model manager
      const modelManager = this.core.getModelManager();
      
      if (!modelManager) {
        throw new Error('Model Manager not available');
      }
      
      // Record usage
      await modelManager.recordUsage(modelId, usage);
      
      this.logger.debug(`Model usage sync successful for model: ${modelId}`);
    } catch (error) {
      this.logger.error(`Model usage sync failed: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Processes a tool usage sync operation
   * 
   * @private
   * @param {Object} operation - Sync operation
   * @returns {Promise<void>}
   */
  async _processSyncToolUsage(operation) {
    try {
      const { toolId, usage } = operation.data;
      
      // Get tool manager
      const toolManager = this.core.getToolManager();
      
      if (!toolManager) {
        throw new Error('Tool Manager not available');
      }
      
      // Record usage
      await toolManager.recordUsage(toolId, usage);
      
      this.logger.debug(`Tool usage sync successful for tool: ${toolId}`);
    } catch (error) {
      this.logger.error(`Tool usage sync failed: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Cleans up resources
   * 
   * @returns {Promise<void>}
   */
  async cleanup() {
    try {
      this._stopConnectivityMonitoring();
      
      // Process any remaining sync operations if online
      if (this.isOnline && this.syncQueue.length > 0) {
        await this._processSyncQueue();
      }
      
      this.logger.info('Offline Capability Manager cleaned up');
    } catch (error) {
      this.logger.error(`Cleanup error: ${error.message}`, error);
    }
  }
}

module.exports = { OfflineCapabilityManager };
