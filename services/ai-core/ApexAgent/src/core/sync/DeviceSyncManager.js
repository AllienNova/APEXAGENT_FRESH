/**
 * DeviceSyncManager.js
 * 
 * Provides seamless synchronization of work and data across multiple devices (desktop, mobile, tablet).
 * Enables real-time updates, conflict resolution, and continuity features for starting tasks on one device
 * and continuing on another.
 * 
 * @author Aideon AI Team
 * @version 1.0.0
 */

const EventEmitter = require('events');
const crypto = require('crypto');
const fs = require('fs').promises;
const path = require('path');
const { v4: uuidv4 } = require('uuid');
const WebSocket = require('ws');
const axios = require('axios');

class DeviceSyncManager extends EventEmitter {
  /**
   * Creates a new DeviceSyncManager instance
   * 
   * @param {Object} core - The Aideon core instance
   */
  constructor(core) {
    super();
    this.core = core;
    this.logger = core.logManager.getLogger('sync:device');
    this.configManager = core.configManager;
    this.securityManager = core.securityManager;
    
    // Device identification
    this.deviceId = null;
    this.deviceType = null;
    this.deviceName = null;
    
    // Connection management
    this.syncServer = null;
    this.wsConnection = null;
    this.connectionStatus = 'disconnected';
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 10;
    this.reconnectDelay = 1000; // Start with 1 second, will increase exponentially
    
    // Data management
    this.syncQueue = [];
    this.pendingOperations = new Map();
    this.lastSyncTimestamp = null;
    this.syncInProgress = false;
    
    // Conflict resolution strategies
    this.conflictResolutionStrategies = new Map();
    
    // Device discovery
    this.knownDevices = new Map();
    this.discoveryInterval = null;
    
    // Continuity features
    this.activeContexts = new Map();
    this.continuityHandlers = new Map();
  }
  
  /**
   * Initializes the DeviceSyncManager
   * 
   * @returns {Promise<boolean>} True if initialization was successful
   */
  async initialize() {
    try {
      this.logger.info('Initializing DeviceSyncManager');
      
      // Load configuration
      const config = this.configManager.getConfig().deviceSync || {};
      this.syncServer = config.syncServer || 'wss://sync.aideon.ai';
      this.maxReconnectAttempts = config.maxReconnectAttempts || 10;
      
      // Initialize device identity
      await this._initializeDeviceIdentity();
      
      // Register default conflict resolution strategies
      this._registerDefaultConflictStrategies();
      
      // Register default continuity handlers
      this._registerDefaultContinuityHandlers();
      
      // Create sync directory if it doesn't exist
      const syncDir = path.join(this.configManager.getDataDir(), 'device_sync');
      await fs.mkdir(syncDir, { recursive: true });
      
      // Start device discovery
      this._startDeviceDiscovery();
      
      // Connect to sync server if configured for auto-connect
      if (config.autoConnect !== false) {
        await this.connect();
      }
      
      this.logger.info('DeviceSyncManager initialized successfully');
      return true;
    } catch (error) {
      this.logger.error(`Failed to initialize DeviceSyncManager: ${error.message}`, error);
      return false;
    }
  }
  
  /**
   * Connects to the sync server
   * 
   * @returns {Promise<boolean>} True if connection was successful
   */
  async connect() {
    if (this.connectionStatus === 'connected' || this.connectionStatus === 'connecting') {
      this.logger.debug('Already connected or connecting to sync server');
      return this.connectionStatus === 'connected';
    }
    
    try {
      this.connectionStatus = 'connecting';
      this.logger.info(`Connecting to sync server: ${this.syncServer}`);
      
      // Get authentication token
      const authToken = await this._getAuthToken();
      
      // Create WebSocket connection with authentication
      return new Promise((resolve, reject) => {
        const ws = new WebSocket(this.syncServer, {
          headers: {
            'Authorization': `Bearer ${authToken}`,
            'X-Device-ID': this.deviceId,
            'X-Device-Type': this.deviceType,
            'X-Device-Name': this.deviceName
          }
        });
        
        // Set connection timeout
        const connectionTimeout = setTimeout(() => {
          ws.terminate();
          this.connectionStatus = 'disconnected';
          reject(new Error('Connection timeout'));
        }, 10000);
        
        ws.on('open', () => {
          clearTimeout(connectionTimeout);
          this.wsConnection = ws;
          this.connectionStatus = 'connected';
          this.reconnectAttempts = 0;
          this.reconnectDelay = 1000;
          this.logger.info('Connected to sync server');
          
          // Process any queued sync operations
          this._processSyncQueue();
          
          // Emit connected event
          this.emit('connected');
          resolve(true);
        });
        
        ws.on('message', (data) => {
          this._handleIncomingMessage(data);
        });
        
        ws.on('error', (error) => {
          this.logger.error(`WebSocket error: ${error.message}`, error);
          if (this.connectionStatus === 'connecting') {
            clearTimeout(connectionTimeout);
            reject(error);
          }
        });
        
        ws.on('close', (code, reason) => {
          this.logger.info(`WebSocket closed: ${code} - ${reason}`);
          this.connectionStatus = 'disconnected';
          this.wsConnection = null;
          
          // Attempt reconnection if not explicitly disconnected
          if (code !== 1000) {
            this._scheduleReconnect();
          }
          
          // Emit disconnected event
          this.emit('disconnected', { code, reason });
        });
      });
    } catch (error) {
      this.connectionStatus = 'disconnected';
      this.logger.error(`Failed to connect to sync server: ${error.message}`, error);
      this._scheduleReconnect();
      return false;
    }
  }
  
  /**
   * Disconnects from the sync server
   * 
   * @returns {Promise<boolean>} True if disconnection was successful
   */
  async disconnect() {
    if (this.connectionStatus === 'disconnected') {
      return true;
    }
    
    try {
      if (this.wsConnection) {
        this.wsConnection.close(1000, 'Client disconnected');
      }
      
      this.connectionStatus = 'disconnected';
      this.wsConnection = null;
      this.logger.info('Disconnected from sync server');
      return true;
    } catch (error) {
      this.logger.error(`Error during disconnect: ${error.message}`, error);
      return false;
    }
  }
  
  /**
   * Synchronizes data with other devices
   * 
   * @param {string} dataType - Type of data being synchronized
   * @param {Object} data - The data to synchronize
   * @param {Object} options - Synchronization options
   * @returns {Promise<Object>} Result of the synchronization operation
   */
  async syncData(dataType, data, options = {}) {
    const operationId = uuidv4();
    const timestamp = Date.now();
    
    const syncOperation = {
      id: operationId,
      type: 'sync',
      dataType,
      data,
      timestamp,
      deviceId: this.deviceId,
      options
    };
    
    // Add to pending operations
    this.pendingOperations.set(operationId, {
      operation: syncOperation,
      status: 'pending',
      timestamp
    });
    
    // If connected, send immediately, otherwise queue
    if (this.connectionStatus === 'connected' && !this.syncInProgress) {
      return this._sendSyncOperation(syncOperation);
    } else {
      this.syncQueue.push(syncOperation);
      this.logger.debug(`Queued sync operation ${operationId} for later processing`);
      return {
        success: true,
        status: 'queued',
        operationId
      };
    }
  }
  
  /**
   * Retrieves synchronized data from other devices
   * 
   * @param {string} dataType - Type of data to retrieve
   * @param {Object} query - Query parameters to filter the data
   * @param {Object} options - Retrieval options
   * @returns {Promise<Object>} The retrieved data
   */
  async retrieveData(dataType, query = {}, options = {}) {
    const operationId = uuidv4();
    const timestamp = Date.now();
    
    const retrieveOperation = {
      id: operationId,
      type: 'retrieve',
      dataType,
      query,
      timestamp,
      deviceId: this.deviceId,
      options
    };
    
    // Add to pending operations
    this.pendingOperations.set(operationId, {
      operation: retrieveOperation,
      status: 'pending',
      timestamp
    });
    
    // If connected, send immediately, otherwise return error
    if (this.connectionStatus === 'connected') {
      return new Promise((resolve, reject) => {
        // Set timeout for the retrieve operation
        const timeout = setTimeout(() => {
          this.pendingOperations.get(operationId).status = 'timeout';
          reject(new Error('Retrieve operation timed out'));
        }, options.timeout || 30000);
        
        // Set up one-time listener for this operation's response
        const responseHandler = (response) => {
          if (response.operationId === operationId) {
            clearTimeout(timeout);
            this.removeListener('retrieveResponse', responseHandler);
            
            if (response.success) {
              resolve(response.data);
            } else {
              reject(new Error(response.error || 'Unknown error during retrieve operation'));
            }
          }
        };
        
        this.on('retrieveResponse', responseHandler);
        
        // Send the retrieve operation
        this._sendMessage(retrieveOperation)
          .catch(error => {
            clearTimeout(timeout);
            this.removeListener('retrieveResponse', responseHandler);
            reject(error);
          });
      });
    } else {
      throw new Error('Cannot retrieve data while disconnected from sync server');
    }
  }
  
  /**
   * Registers a continuity handler for a specific context type
   * 
   * @param {string} contextType - Type of context to handle
   * @param {Function} handler - Handler function for the context
   */
  registerContinuityHandler(contextType, handler) {
    if (typeof handler !== 'function') {
      throw new Error('Continuity handler must be a function');
    }
    
    this.continuityHandlers.set(contextType, handler);
    this.logger.debug(`Registered continuity handler for context type: ${contextType}`);
  }
  
  /**
   * Starts a continuity context that can be resumed on another device
   * 
   * @param {string} contextType - Type of context being started
   * @param {Object} contextData - Data associated with the context
   * @returns {Promise<string>} ID of the created context
   */
  async startContinuityContext(contextType, contextData) {
    const contextId = uuidv4();
    const timestamp = Date.now();
    
    const context = {
      id: contextId,
      type: contextType,
      data: contextData,
      deviceId: this.deviceId,
      deviceType: this.deviceType,
      deviceName: this.deviceName,
      timestamp,
      status: 'active'
    };
    
    // Store locally
    this.activeContexts.set(contextId, context);
    
    // Sync to server if connected
    if (this.connectionStatus === 'connected') {
      await this.syncData('continuity_context', context, { priority: 'high' });
    }
    
    this.logger.debug(`Started continuity context: ${contextId} of type: ${contextType}`);
    return contextId;
  }
  
  /**
   * Updates an existing continuity context
   * 
   * @param {string} contextId - ID of the context to update
   * @param {Object} contextData - Updated data for the context
   * @returns {Promise<boolean>} True if update was successful
   */
  async updateContinuityContext(contextId, contextData) {
    if (!this.activeContexts.has(contextId)) {
      throw new Error(`Continuity context not found: ${contextId}`);
    }
    
    const context = this.activeContexts.get(contextId);
    context.data = contextData;
    context.timestamp = Date.now();
    
    // Store locally
    this.activeContexts.set(contextId, context);
    
    // Sync to server if connected
    if (this.connectionStatus === 'connected') {
      await this.syncData('continuity_context', context, { priority: 'high' });
    }
    
    this.logger.debug(`Updated continuity context: ${contextId}`);
    return true;
  }
  
  /**
   * Ends a continuity context
   * 
   * @param {string} contextId - ID of the context to end
   * @returns {Promise<boolean>} True if ending the context was successful
   */
  async endContinuityContext(contextId) {
    if (!this.activeContexts.has(contextId)) {
      throw new Error(`Continuity context not found: ${contextId}`);
    }
    
    const context = this.activeContexts.get(contextId);
    context.status = 'completed';
    context.endTimestamp = Date.now();
    
    // Sync to server if connected
    if (this.connectionStatus === 'connected') {
      await this.syncData('continuity_context', context, { priority: 'high' });
    }
    
    // Remove from active contexts
    this.activeContexts.delete(contextId);
    
    this.logger.debug(`Ended continuity context: ${contextId}`);
    return true;
  }
  
  /**
   * Resumes a continuity context from another device
   * 
   * @param {string} contextId - ID of the context to resume
   * @returns {Promise<Object>} The resumed context data
   */
  async resumeContinuityContext(contextId) {
    // Check if we already have this context locally
    if (this.activeContexts.has(contextId)) {
      const context = this.activeContexts.get(contextId);
      return context.data;
    }
    
    // Retrieve from server
    try {
      const context = await this.retrieveData('continuity_context', { id: contextId });
      
      if (!context) {
        throw new Error(`Continuity context not found: ${contextId}`);
      }
      
      // Store locally
      this.activeContexts.set(contextId, {
        ...context,
        status: 'resumed',
        resumeTimestamp: Date.now(),
        resumeDeviceId: this.deviceId
      });
      
      // Notify the server that we've resumed this context
      if (this.connectionStatus === 'connected') {
        await this._sendMessage({
          type: 'context_resumed',
          contextId,
          deviceId: this.deviceId,
          timestamp: Date.now()
        });
      }
      
      // Execute the appropriate continuity handler
      if (this.continuityHandlers.has(context.type)) {
        const handler = this.continuityHandlers.get(context.type);
        handler(context.data, context);
      }
      
      this.logger.debug(`Resumed continuity context: ${contextId}`);
      return context.data;
    } catch (error) {
      this.logger.error(`Failed to resume continuity context: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Lists available continuity contexts
   * 
   * @param {Object} filters - Filters to apply to the list
   * @returns {Promise<Array>} List of available continuity contexts
   */
  async listContinuityContexts(filters = {}) {
    try {
      // Retrieve from server
      const contexts = await this.retrieveData('continuity_contexts', filters);
      
      // Sort by timestamp (newest first)
      return contexts.sort((a, b) => b.timestamp - a.timestamp);
    } catch (error) {
      this.logger.error(`Failed to list continuity contexts: ${error.message}`, error);
      
      // If disconnected, return only local contexts
      if (this.connectionStatus !== 'connected') {
        const localContexts = Array.from(this.activeContexts.values());
        return localContexts.filter(context => {
          // Apply filters
          for (const [key, value] of Object.entries(filters)) {
            if (context[key] !== value) {
              return false;
            }
          }
          return true;
        }).sort((a, b) => b.timestamp - a.timestamp);
      }
      
      throw error;
    }
  }
  
  /**
   * Registers a conflict resolution strategy for a specific data type
   * 
   * @param {string} dataType - Type of data to register strategy for
   * @param {Function} strategyFn - Strategy function to resolve conflicts
   */
  registerConflictStrategy(dataType, strategyFn) {
    if (typeof strategyFn !== 'function') {
      throw new Error('Conflict resolution strategy must be a function');
    }
    
    this.conflictResolutionStrategies.set(dataType, strategyFn);
    this.logger.debug(`Registered conflict resolution strategy for data type: ${dataType}`);
  }
  
  /**
   * Gets information about known devices
   * 
   * @returns {Array} List of known devices
   */
  getKnownDevices() {
    return Array.from(this.knownDevices.values());
  }
  
  /**
   * Gets the connection status
   * 
   * @returns {string} Current connection status
   */
  getConnectionStatus() {
    return this.connectionStatus;
  }
  
  /**
   * Gets the current device information
   * 
   * @returns {Object} Current device information
   */
  getDeviceInfo() {
    return {
      id: this.deviceId,
      type: this.deviceType,
      name: this.deviceName
    };
  }
  
  /**
   * Initializes the device identity
   * 
   * @private
   */
  async _initializeDeviceIdentity() {
    const config = this.configManager.getConfig().deviceSync || {};
    const identityPath = path.join(this.configManager.getDataDir(), 'device_identity.json');
    
    try {
      // Try to load existing identity
      const identityData = await fs.readFile(identityPath, 'utf8');
      const identity = JSON.parse(identityData);
      
      this.deviceId = identity.deviceId;
      this.deviceType = identity.deviceType;
      this.deviceName = identity.deviceName;
      
      this.logger.debug(`Loaded existing device identity: ${this.deviceId}`);
    } catch (error) {
      // Create new identity
      this.deviceId = uuidv4();
      
      // Determine device type
      if (process.platform === 'darwin') {
        this.deviceType = process.platform.includes('darwin') ? 'macos' : 'desktop';
      } else if (process.platform === 'win32') {
        this.deviceType = 'windows';
      } else if (process.platform === 'linux') {
        this.deviceType = 'linux';
      } else {
        this.deviceType = 'desktop';
      }
      
      // Generate device name
      const osInfo = await this._getOSInfo();
      this.deviceName = config.deviceName || `${osInfo.hostname} (${this.deviceType})`;
      
      // Save identity
      const identity = {
        deviceId: this.deviceId,
        deviceType: this.deviceType,
        deviceName: this.deviceName,
        created: Date.now()
      };
      
      await fs.writeFile(identityPath, JSON.stringify(identity, null, 2), 'utf8');
      this.logger.info(`Created new device identity: ${this.deviceId}`);
    }
  }
  
  /**
   * Gets OS information
   * 
   * @private
   * @returns {Promise<Object>} OS information
   */
  async _getOSInfo() {
    const os = require('os');
    return {
      platform: os.platform(),
      release: os.release(),
      hostname: os.hostname()
    };
  }
  
  /**
   * Gets authentication token for sync server
   * 
   * @private
   * @returns {Promise<string>} Authentication token
   */
  async _getAuthToken() {
    try {
      // Use security manager to get token
      if (this.securityManager && typeof this.securityManager.getAuthToken === 'function') {
        return await this.securityManager.getAuthToken('device_sync');
      }
      
      // Fallback to config
      const config = this.configManager.getConfig().deviceSync || {};
      if (config.authToken) {
        return config.authToken;
      }
      
      throw new Error('No authentication token available');
    } catch (error) {
      this.logger.error(`Failed to get auth token: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Schedules a reconnection attempt
   * 
   * @private
   */
  _scheduleReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      this.logger.warn(`Maximum reconnect attempts (${this.maxReconnectAttempts}) reached`);
      return;
    }
    
    // Exponential backoff
    const delay = Math.min(30000, this.reconnectDelay * Math.pow(1.5, this.reconnectAttempts));
    this.reconnectAttempts++;
    
    this.logger.debug(`Scheduling reconnect attempt ${this.reconnectAttempts} in ${delay}ms`);
    
    setTimeout(async () => {
      if (this.connectionStatus === 'disconnected') {
        try {
          await this.connect();
        } catch (error) {
          this.logger.error(`Reconnect attempt failed: ${error.message}`);
        }
      }
    }, delay);
    
    // Increase delay for next attempt
    this.reconnectDelay = delay;
  }
  
  /**
   * Processes the sync queue
   * 
   * @private
   */
  async _processSyncQueue() {
    if (this.syncInProgress || this.syncQueue.length === 0 || this.connectionStatus !== 'connected') {
      return;
    }
    
    this.syncInProgress = true;
    
    try {
      // Sort queue by priority
      this.syncQueue.sort((a, b) => {
        const priorityA = a.options?.priority === 'high' ? 0 : 1;
        const priorityB = b.options?.priority === 'high' ? 0 : 1;
        return priorityA - priorityB;
      });
      
      // Process queue items
      while (this.syncQueue.length > 0 && this.connectionStatus === 'connected') {
        const operation = this.syncQueue.shift();
        await this._sendSyncOperation(operation);
      }
    } catch (error) {
      this.logger.error(`Error processing sync queue: ${error.message}`, error);
    } finally {
      this.syncInProgress = false;
    }
  }
  
  /**
   * Sends a sync operation to the server
   * 
   * @private
   * @param {Object} operation - The sync operation to send
   * @returns {Promise<Object>} Result of the operation
   */
  async _sendSyncOperation(operation) {
    try {
      await this._sendMessage(operation);
      
      // Update operation status
      if (this.pendingOperations.has(operation.id)) {
        this.pendingOperations.get(operation.id).status = 'sent';
      }
      
      this.lastSyncTimestamp = Date.now();
      
      return {
        success: true,
        status: 'sent',
        operationId: operation.id
      };
    } catch (error) {
      // Update operation status
      if (this.pendingOperations.has(operation.id)) {
        this.pendingOperations.get(operation.id).status = 'failed';
        this.pendingOperations.get(operation.id).error = error.message;
      }
      
      // Re-queue the operation for later retry
      this.syncQueue.push(operation);
      
      this.logger.error(`Failed to send sync operation: ${error.message}`, error);
      
      return {
        success: false,
        status: 'failed',
        operationId: operation.id,
        error: error.message
      };
    }
  }
  
  /**
   * Sends a message to the sync server
   * 
   * @private
   * @param {Object} message - The message to send
   * @returns {Promise<void>}
   */
  async _sendMessage(message) {
    if (this.connectionStatus !== 'connected' || !this.wsConnection) {
      throw new Error('Not connected to sync server');
    }
    
    return new Promise((resolve, reject) => {
      try {
        this.wsConnection.send(JSON.stringify(message), (error) => {
          if (error) {
            this.logger.error(`WebSocket send error: ${error.message}`, error);
            reject(error);
          } else {
            resolve();
          }
        });
      } catch (error) {
        this.logger.error(`Error preparing message: ${error.message}`, error);
        reject(error);
      }
    });
  }
  
  /**
   * Handles incoming messages from the sync server
   * 
   * @private
   * @param {string|Buffer} data - The incoming message data
   */
  _handleIncomingMessage(data) {
    try {
      const message = JSON.parse(data.toString());
      
      switch (message.type) {
        case 'sync':
          this._handleSyncMessage(message);
          break;
        
        case 'retrieve_response':
          this.emit('retrieveResponse', message);
          break;
        
        case 'device_discovered':
          this._handleDeviceDiscovered(message);
          break;
        
        case 'context_available':
          this._handleContextAvailable(message);
          break;
        
        case 'conflict':
          this._handleConflict(message);
          break;
        
        case 'ping':
          this._sendMessage({ type: 'pong', timestamp: Date.now() });
          break;
        
        default:
          this.logger.debug(`Received unknown message type: ${message.type}`);
      }
    } catch (error) {
      this.logger.error(`Error handling incoming message: ${error.message}`, error);
    }
  }
  
  /**
   * Handles sync messages from other devices
   * 
   * @private
   * @param {Object} message - The sync message
   */
  async _handleSyncMessage(message) {
    try {
      // Check if this is our own message
      if (message.deviceId === this.deviceId) {
        return;
      }
      
      this.logger.debug(`Received sync message for data type: ${message.dataType}`);
      
      // Handle continuity contexts specially
      if (message.dataType === 'continuity_context') {
        await this._handleContinuityContextSync(message);
        return;
      }
      
      // Emit sync event for other components to handle
      this.emit('sync', {
        dataType: message.dataType,
        data: message.data,
        sourceDeviceId: message.deviceId,
        timestamp: message.timestamp
      });
      
      // Acknowledge receipt
      await this._sendMessage({
        type: 'sync_ack',
        syncId: message.id,
        deviceId: this.deviceId,
        timestamp: Date.now()
      });
    } catch (error) {
      this.logger.error(`Error handling sync message: ${error.message}`, error);
    }
  }
  
  /**
   * Handles continuity context sync messages
   * 
   * @private
   * @param {Object} message - The sync message
   */
  async _handleContinuityContextSync(message) {
    const context = message.data;
    
    // Store or update the context locally
    this.activeContexts.set(context.id, context);
    
    // Notify about available context if it's active
    if (context.status === 'active' && context.deviceId !== this.deviceId) {
      this.emit('contextAvailable', context);
    }
  }
  
  /**
   * Handles device discovery messages
   * 
   * @private
   * @param {Object} message - The device discovery message
   */
  _handleDeviceDiscovered(message) {
    const device = message.device;
    
    // Skip our own device
    if (device.id === this.deviceId) {
      return;
    }
    
    // Update known devices
    this.knownDevices.set(device.id, {
      ...device,
      lastSeen: Date.now()
    });
    
    this.logger.debug(`Discovered device: ${device.name} (${device.id})`);
    this.emit('deviceDiscovered', device);
  }
  
  /**
   * Handles context available messages
   * 
   * @private
   * @param {Object} message - The context available message
   */
  _handleContextAvailable(message) {
    const context = message.context;
    
    // Skip contexts from this device
    if (context.deviceId === this.deviceId) {
      return;
    }
    
    this.logger.debug(`Context available: ${context.id} (${context.type})`);
    this.emit('contextAvailable', context);
  }
  
  /**
   * Handles conflict messages
   * 
   * @private
   * @param {Object} message - The conflict message
   */
  async _handleConflict(message) {
    const { dataType, localData, remoteData, conflictId } = message;
    
    try {
      let resolvedData;
      
      // Check if we have a strategy for this data type
      if (this.conflictResolutionStrategies.has(dataType)) {
        const strategy = this.conflictResolutionStrategies.get(dataType);
        resolvedData = await strategy(localData, remoteData);
      } else {
        // Default strategy: newest wins
        resolvedData = localData.timestamp > remoteData.timestamp ? localData : remoteData;
      }
      
      // Send resolution
      await this._sendMessage({
        type: 'conflict_resolution',
        conflictId,
        dataType,
        resolvedData,
        deviceId: this.deviceId,
        timestamp: Date.now()
      });
    } catch (error) {
      this.logger.error(`Error handling conflict: ${error.message}`, error);
    }
  }
  
  /**
   * Starts device discovery
   * 
   * @private
   */
  _startDeviceDiscovery() {
    // Clear any existing interval
    if (this.discoveryInterval) {
      clearInterval(this.discoveryInterval);
    }
    
    // Broadcast device info immediately
    this._broadcastDeviceInfo();
    
    // Set up regular broadcasts
    this.discoveryInterval = setInterval(() => {
      this._broadcastDeviceInfo();
    }, 60000); // Every minute
  }
  
  /**
   * Broadcasts device information to other devices
   * 
   * @private
   */
  async _broadcastDeviceInfo() {
    if (this.connectionStatus !== 'connected') {
      return;
    }
    
    try {
      const deviceInfo = {
        id: this.deviceId,
        type: this.deviceType,
        name: this.deviceName,
        capabilities: this._getDeviceCapabilities(),
        timestamp: Date.now()
      };
      
      await this._sendMessage({
        type: 'device_info',
        device: deviceInfo
      });
    } catch (error) {
      this.logger.error(`Error broadcasting device info: ${error.message}`, error);
    }
  }
  
  /**
   * Gets device capabilities
   * 
   * @private
   * @returns {Object} Device capabilities
   */
  _getDeviceCapabilities() {
    return {
      continuity: true,
      fileSync: true,
      mediaSync: true,
      notifications: true
    };
  }
  
  /**
   * Registers default conflict resolution strategies
   * 
   * @private
   */
  _registerDefaultConflictStrategies() {
    // Default strategy for most data types: newest wins
    const newestWinsStrategy = (localData, remoteData) => {
      return localData.timestamp > remoteData.timestamp ? localData : remoteData;
    };
    
    // Strategy for documents: merge changes if possible
    const documentMergeStrategy = async (localData, remoteData) => {
      // If document formats are compatible, try to merge
      if (localData.format === remoteData.format) {
        try {
          // In a real implementation, this would use a proper diff/merge algorithm
          // For now, we'll use a simple timestamp-based approach
          return localData.timestamp > remoteData.timestamp ? localData : remoteData;
        } catch (error) {
          this.logger.error(`Failed to merge documents: ${error.message}`, error);
          // Fall back to newest wins
          return localData.timestamp > remoteData.timestamp ? localData : remoteData;
        }
      } else {
        // Different formats, use newest
        return localData.timestamp > remoteData.timestamp ? localData : remoteData;
      }
    };
    
    // Register strategies
    this.registerConflictStrategy('default', newestWinsStrategy);
    this.registerConflictStrategy('document', documentMergeStrategy);
    this.registerConflictStrategy('settings', newestWinsStrategy);
    this.registerConflictStrategy('user_preferences', newestWinsStrategy);
  }
  
  /**
   * Registers default continuity handlers
   * 
   * @private
   */
  _registerDefaultContinuityHandlers() {
    // Document editing continuity
    this.registerContinuityHandler('document_editing', (contextData, context) => {
      this.logger.info(`Resuming document editing for: ${contextData.documentName}`);
      this.emit('resumeDocumentEditing', contextData);
    });
    
    // Web browsing continuity
    this.registerContinuityHandler('web_browsing', (contextData, context) => {
      this.logger.info(`Resuming web browsing session for: ${contextData.url}`);
      this.emit('resumeWebBrowsing', contextData);
    });
    
    // Task continuity
    this.registerContinuityHandler('task', (contextData, context) => {
      this.logger.info(`Resuming task: ${contextData.taskName}`);
      this.emit('resumeTask', contextData);
    });
  }
}

module.exports = { DeviceSyncManager };
