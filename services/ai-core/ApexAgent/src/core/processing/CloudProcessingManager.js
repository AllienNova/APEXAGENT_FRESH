/**
 * CloudProcessingManager.js
 * 
 * Manages cloud processing capabilities for Aideon AI Lite.
 * Handles API connections, request management, and optimization
 * for tasks that are executed in the cloud.
 * 
 * @author Aideon AI Team
 * @version 1.0.0
 */

const EventEmitter = require('events');
const axios = require('axios');
const { v4: uuidv4 } = require('uuid');

/**
 * CloudProcessingManager class for managing cloud processing capabilities
 */
class CloudProcessingManager extends EventEmitter {
  /**
   * Create a new CloudProcessingManager instance
   * @param {Object} config - Configuration options
   */
  constructor(config = {}) {
    super();
    
    this.config = {
      enabled: config.enabled !== undefined ? config.enabled : true,
      apiEndpoint: config.apiEndpoint || process.env.CLOUD_API_ENDPOINT || 'https://api.aideon.ai',
      apiKey: config.apiKey || process.env.CLOUD_API_KEY,
      maxConcurrentRequests: config.maxConcurrentRequests || 10,
      requestTimeout: config.requestTimeout || 60000, // 1 minute
      retryLimit: config.retryLimit || 3,
      retryDelay: config.retryDelay || 1000, // 1 second
      priorityLevels: config.priorityLevels || {
        low: 0,
        normal: 1,
        high: 2,
        critical: 3
      },
      ...config
    };
    
    // Initialize request tracking
    this.requests = new Map();
    this.activeRequests = 0;
    
    // Initialize request queue
    this.requestQueue = [];
    
    // Initialize metrics
    this.metrics = {
      requestsProcessed: 0,
      requestsSucceeded: 0,
      requestsFailed: 0,
      averageProcessingTime: 0,
      totalBytesUploaded: 0,
      totalBytesDownloaded: 0,
      peakConcurrency: 0
    };
    
    // Initialize HTTP client
    this.client = axios.create({
      baseURL: this.config.apiEndpoint,
      timeout: this.config.requestTimeout,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'User-Agent': 'AideonAILite/1.0.0'
      }
    });
    
    // Add API key if available
    if (this.config.apiKey) {
      this.client.defaults.headers.common['Authorization'] = `Bearer ${this.config.apiKey}`;
    }
    
    // Add request interceptor for metrics
    this.client.interceptors.request.use((config) => {
      // Track request size
      if (config.data) {
        const size = typeof config.data === 'string' 
          ? config.data.length 
          : JSON.stringify(config.data).length;
        
        this.metrics.totalBytesUploaded += size;
      }
      
      return config;
    });
    
    // Add response interceptor for metrics
    this.client.interceptors.response.use((response) => {
      // Track response size
      if (response.data) {
        const size = typeof response.data === 'string'
          ? response.data.length
          : JSON.stringify(response.data).length;
        
        this.metrics.totalBytesDownloaded += size;
      }
      
      return response;
    });
    
    console.log('CloudProcessingManager initialized');
  }
  
  /**
   * Initialize the CloudProcessingManager
   * @returns {Promise<boolean>} Success status
   */
  async initialize() {
    if (!this.config.enabled) {
      console.log('Cloud processing is disabled');
      return false;
    }
    
    try {
      console.log('Initializing CloudProcessingManager');
      
      // Test API connection
      const connectionStatus = await this._testConnection();
      
      if (!connectionStatus.success) {
        console.warn(`Cloud API connection failed: ${connectionStatus.error}`);
        return false;
      }
      
      console.log('CloudProcessingManager initialized successfully');
      
      return true;
    } catch (error) {
      console.error('Error initializing CloudProcessingManager:', error);
      throw error;
    }
  }
  
  /**
   * Test the connection to the cloud API
   * @private
   * @returns {Promise<Object>} Connection status
   */
  async _testConnection() {
    try {
      const response = await this.client.get('/status');
      
      if (response.status === 200) {
        return {
          success: true,
          status: response.data
        };
      } else {
        return {
          success: false,
          error: `Unexpected status code: ${response.status}`
        };
      }
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }
  
  /**
   * Process a task in the cloud
   * @param {Object} task - Task to process
   * @param {Object} options - Processing options
   * @returns {Promise<Object>} Task result
   */
  async processTask(task, options = {}) {
    if (!this.config.enabled) {
      throw new Error('Cloud processing is disabled');
    }
    
    // Generate request ID if not provided
    const requestId = options.requestId || uuidv4();
    
    // Set default priority if not provided
    const priority = options.priority || 'normal';
    const priorityLevel = this.config.priorityLevels[priority] || this.config.priorityLevels.normal;
    
    // Create request promise
    const requestPromise = new Promise((resolve, reject) => {
      // Create request info
      const requestInfo = {
        id: requestId,
        task,
        options,
        priority,
        priorityLevel,
        status: 'queued',
        progress: 0,
        startTime: Date.now(),
        endTime: null,
        processingTime: null,
        result: null,
        error: null,
        retries: 0,
        resolve,
        reject
      };
      
      // Add to request queue
      this._addToRequestQueue(requestInfo);
      
      // Emit request queued event
      this.emit('request:queued', {
        requestId,
        priority,
        queueLength: this.requestQueue.length
      });
      
      // Process next request if possible
      this._processNextRequest();
    });
    
    return requestPromise;
  }
  
  /**
   * Add a request to the queue
   * @param {Object} requestInfo - Request information
   * @private
   */
  _addToRequestQueue(requestInfo) {
    // Find position in queue based on priority
    let insertIndex = this.requestQueue.length;
    
    for (let i = 0; i < this.requestQueue.length; i++) {
      if (requestInfo.priorityLevel > this.requestQueue[i].priorityLevel) {
        insertIndex = i;
        break;
      }
    }
    
    // Insert request at the appropriate position
    this.requestQueue.splice(insertIndex, 0, requestInfo);
  }
  
  /**
   * Process the next request in the queue
   * @private
   */
  _processNextRequest() {
    // Check if we're at max concurrent requests
    if (this.activeRequests >= this.config.maxConcurrentRequests) {
      return;
    }
    
    // Check if there are requests in the queue
    if (this.requestQueue.length === 0) {
      return;
    }
    
    // Get next request
    const requestInfo = this.requestQueue.shift();
    
    // Update request info
    requestInfo.status = 'processing';
    requestInfo.startTime = Date.now();
    
    // Add to active requests
    this.requests.set(requestInfo.id, requestInfo);
    this.activeRequests++;
    
    // Update metrics
    const currentConcurrency = this.activeRequests;
    if (currentConcurrency > this.metrics.peakConcurrency) {
      this.metrics.peakConcurrency = currentConcurrency;
    }
    
    // Emit request started event
    this.emit('request:started', {
      requestId: requestInfo.id,
      concurrency: this.activeRequests
    });
    
    // Process the request
    this._executeRequest(requestInfo);
  }
  
  /**
   * Execute a request
   * @param {Object} requestInfo - Request information
   * @private
   */
  async _executeRequest(requestInfo) {
    try {
      // Prepare request data
      const requestData = {
        task: requestInfo.task,
        options: {
          ...requestInfo.options,
          requestId: requestInfo.id
        }
      };
      
      // Send request to cloud API
      const response = await this.client.post('/process', requestData);
      
      // Handle response
      if (response.status === 200) {
        this._handleRequestSuccess(requestInfo, response.data);
      } else {
        throw new Error(`Unexpected status code: ${response.status}`);
      }
    } catch (error) {
      // Check if we should retry
      if (requestInfo.retries < this.config.retryLimit) {
        this._handleRequestRetry(requestInfo, error);
      } else {
        this._handleRequestFailure(requestInfo, error);
      }
    }
  }
  
  /**
   * Handle successful request
   * @param {Object} requestInfo - Request information
   * @param {Object} result - Request result
   * @private
   */
  _handleRequestSuccess(requestInfo, result) {
    // Update request info
    requestInfo.status = 'completed';
    requestInfo.result = result;
    requestInfo.endTime = Date.now();
    requestInfo.processingTime = requestInfo.endTime - requestInfo.startTime;
    
    // Update metrics
    this.metrics.requestsProcessed++;
    this.metrics.requestsSucceeded++;
    this.metrics.averageProcessingTime = (
      (this.metrics.averageProcessingTime * (this.metrics.requestsProcessed - 1)) +
      requestInfo.processingTime
    ) / this.metrics.requestsProcessed;
    
    // Resolve request promise
    requestInfo.resolve(result);
    
    // Remove from active requests
    this.requests.delete(requestInfo.id);
    this.activeRequests--;
    
    // Emit request completed event
    this.emit('request:completed', {
      requestId: requestInfo.id,
      processingTime: requestInfo.processingTime,
      result
    });
    
    // Process next request
    this._processNextRequest();
  }
  
  /**
   * Handle request retry
   * @param {Object} requestInfo - Request information
   * @param {Error} error - Error that caused the retry
   * @private
   */
  _handleRequestRetry(requestInfo, error) {
    // Update request info
    requestInfo.retries++;
    
    // Calculate retry delay with exponential backoff
    const retryDelay = this.config.retryDelay * Math.pow(2, requestInfo.retries - 1);
    
    console.log(`Retrying request ${requestInfo.id} (${requestInfo.retries}/${this.config.retryLimit}) after ${retryDelay}ms: ${error.message}`);
    
    // Emit request retry event
    this.emit('request:retry', {
      requestId: requestInfo.id,
      retries: requestInfo.retries,
      retryDelay,
      error: error.message
    });
    
    // Schedule retry
    setTimeout(() => {
      this._executeRequest(requestInfo);
    }, retryDelay);
  }
  
  /**
   * Handle request failure
   * @param {Object} requestInfo - Request information
   * @param {Error} error - Error that caused the failure
   * @private
   */
  _handleRequestFailure(requestInfo, error) {
    // Update request info
    requestInfo.status = 'failed';
    requestInfo.error = error.message;
    requestInfo.endTime = Date.now();
    requestInfo.processingTime = requestInfo.endTime - requestInfo.startTime;
    
    // Update metrics
    this.metrics.requestsProcessed++;
    this.metrics.requestsFailed++;
    
    // Reject request promise
    requestInfo.reject(error);
    
    // Remove from active requests
    this.requests.delete(requestInfo.id);
    this.activeRequests--;
    
    // Emit request failed event
    this.emit('request:failed', {
      requestId: requestInfo.id,
      error: error.message,
      retries: requestInfo.retries
    });
    
    // Process next request
    this._processNextRequest();
  }
  
  /**
   * Cancel a request
   * @param {string} requestId - ID of the request to cancel
   * @returns {boolean} Whether the request was cancelled
   */
  cancelRequest(requestId) {
    // Check if request is in queue
    const queueIndex = this.requestQueue.findIndex(request => request.id === requestId);
    
    if (queueIndex !== -1) {
      // Remove from queue
      const requestInfo = this.requestQueue.splice(queueIndex, 1)[0];
      
      // Reject request promise
      requestInfo.reject(new Error('Request cancelled'));
      
      // Emit request cancelled event
      this.emit('request:cancelled', {
        requestId,
        status: 'queued'
      });
      
      return true;
    }
    
    // Check if request is active
    const requestInfo = this.requests.get(requestId);
    
    if (requestInfo) {
      // Send cancel request to cloud API
      this.client.post(`/cancel/${requestId}`)
        .catch(error => {
          console.warn(`Error cancelling request ${requestId}:`, error.message);
        });
      
      // Update request info
      requestInfo.status = 'cancelled';
      requestInfo.endTime = Date.now();
      requestInfo.processingTime = requestInfo.endTime - requestInfo.startTime;
      
      // Reject request promise
      requestInfo.reject(new Error('Request cancelled'));
      
      // Remove from active requests
      this.requests.delete(requestId);
      this.activeRequests--;
      
      // Emit request cancelled event
      this.emit('request:cancelled', {
        requestId,
        status: 'processing'
      });
      
      // Process next request
      this._processNextRequest();
      
      return true;
    }
    
    return false;
  }
  
  /**
   * Get request status
   * @param {string} requestId - ID of the request
   * @returns {Promise<Object|null>} Request status or null if not found
   */
  async getRequestStatus(requestId) {
    // Check active requests
    const activeRequest = this.requests.get(requestId);
    
    if (activeRequest) {
      return {
        id: activeRequest.id,
        status: activeRequest.status,
        progress: activeRequest.progress,
        startTime: activeRequest.startTime,
        processingTime: Date.now() - activeRequest.startTime,
        retries: activeRequest.retries
      };
    }
    
    // Check queued requests
    const queuedRequest = this.requestQueue.find(request => request.id === requestId);
    
    if (queuedRequest) {
      return {
        id: queuedRequest.id,
        status: 'queued',
        priority: queuedRequest.priority,
        queuePosition: this.requestQueue.indexOf(queuedRequest) + 1,
        queuedTime: Date.now() - queuedRequest.startTime
      };
    }
    
    // Check with cloud API
    try {
      const response = await this.client.get(`/status/${requestId}`);
      
      if (response.status === 200) {
        return response.data;
      }
    } catch (error) {
      console.warn(`Error getting status for request ${requestId}:`, error.message);
    }
    
    return null;
  }
  
  /**
   * Get status of all requests
   * @returns {Object} Status of all requests
   */
  getAllRequestStatus() {
    return {
      queued: this.requestQueue.length,
      active: this.activeRequests,
      queuedRequests: this.requestQueue.map((request, index) => ({
        id: request.id,
        status: 'queued',
        priority: request.priority,
        queuePosition: index + 1,
        queuedTime: Date.now() - request.startTime
      })),
      activeRequests: Array.from(this.requests.values()).map(request => ({
        id: request.id,
        status: request.status,
        progress: request.progress,
        startTime: request.startTime,
        processingTime: Date.now() - request.startTime,
        retries: request.retries
      }))
    };
  }
  
  /**
   * Get cloud API status
   * @returns {Promise<Object>} API status
   */
  async getApiStatus() {
    try {
      const response = await this.client.get('/status');
      
      if (response.status === 200) {
        return {
          success: true,
          status: response.data
        };
      } else {
        return {
          success: false,
          error: `Unexpected status code: ${response.status}`
        };
      }
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }
  
  /**
   * Get processing metrics
   * @returns {Object} Processing metrics
   */
  getMetrics() {
    return this.metrics;
  }
  
  /**
   * Get overall status
   * @returns {Object} Overall status
   */
  getStatus() {
    return {
      enabled: this.config.enabled,
      apiEndpoint: this.config.apiEndpoint,
      requests: {
        queued: this.requestQueue.length,
        active: this.activeRequests,
        processed: this.metrics.requestsProcessed,
        succeeded: this.metrics.requestsSucceeded,
        failed: this.metrics.requestsFailed
      },
      metrics: this.metrics
    };
  }
  
  /**
   * Shutdown the CloudProcessingManager
   * @returns {Promise<void>}
   */
  async shutdown() {
    try {
      console.log('Shutting down CloudProcessingManager');
      
      // Cancel all queued requests
      while (this.requestQueue.length > 0) {
        const requestInfo = this.requestQueue.shift();
        requestInfo.reject(new Error('CloudProcessingManager shutting down'));
      }
      
      // Cancel all active requests
      const cancelPromises = [];
      
      for (const [requestId, requestInfo] of this.requests.entries()) {
        // Send cancel request to cloud API
        cancelPromises.push(
          this.client.post(`/cancel/${requestId}`)
            .catch(error => {
              console.warn(`Error cancelling request ${requestId}:`, error.message);
            })
        );
        
        // Reject request promise
        requestInfo.reject(new Error('CloudProcessingManager shutting down'));
      }
      
      // Wait for all cancel requests to complete
      await Promise.allSettled(cancelPromises);
      
      this.requests.clear();
      this.activeRequests = 0;
      
      console.log('CloudProcessingManager shutdown complete');
    } catch (error) {
      console.error('Error shutting down CloudProcessingManager:', error);
      throw error;
    }
  }
}

module.exports = { CloudProcessingManager };
