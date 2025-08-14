/**
 * APIManager.js
 * 
 * Manages API connections and endpoints for Aideon AI Lite.
 * Provides a unified interface for internal and external API interactions,
 * request handling, authentication, and rate limiting.
 * 
 * @author Aideon AI Team
 * @version 1.0.0
 */

const EventEmitter = require('events');
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const compression = require('compression');
const rateLimit = require('express-rate-limit');
const cookieParser = require('cookie-parser');
const http = require('http');
const https = require('https');
const fs = require('fs');
const path = require('path');
const { v4: uuidv4 } = require('uuid');

/**
 * APIManager class for managing API connections and endpoints
 */
class APIManager extends EventEmitter {
  /**
   * Create a new APIManager instance
   * @param {Object} config - Configuration options
   */
  constructor(config = {}) {
    super();
    
    this.config = {
      enabled: config.enabled !== undefined ? config.enabled : true,
      port: config.port || process.env.API_PORT || 3000,
      host: config.host || process.env.API_HOST || 'localhost',
      basePath: config.basePath || '/api/v1',
      cors: {
        enabled: config.cors?.enabled !== undefined ? config.cors.enabled : true,
        origin: config.cors?.origin || '*',
        methods: config.cors?.methods || ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
        allowedHeaders: config.cors?.allowedHeaders || ['Content-Type', 'Authorization'],
        credentials: config.cors?.credentials !== undefined ? config.cors.credentials : true
      },
      rateLimit: {
        enabled: config.rateLimit?.enabled !== undefined ? config.rateLimit.enabled : true,
        windowMs: config.rateLimit?.windowMs || 60000, // 1 minute
        max: config.rateLimit?.max || 100, // 100 requests per minute
        standardHeaders: config.rateLimit?.standardHeaders !== undefined ? config.rateLimit.standardHeaders : true,
        legacyHeaders: config.rateLimit?.legacyHeaders !== undefined ? config.rateLimit.legacyHeaders : false
      },
      ssl: {
        enabled: config.ssl?.enabled !== undefined ? config.ssl.enabled : false,
        key: config.ssl?.key || null,
        cert: config.ssl?.cert || null,
        ca: config.ssl?.ca || null
      },
      auth: {
        enabled: config.auth?.enabled !== undefined ? config.auth.enabled : true,
        methods: config.auth?.methods || ['jwt', 'api_key'],
        jwtSecret: config.auth?.jwtSecret || process.env.JWT_SECRET || 'aideon-ai-lite-secret'
      },
      logging: {
        enabled: config.logging?.enabled !== undefined ? config.logging.enabled : true,
        level: config.logging?.level || 'info'
      },
      ...config
    };
    
    // Initialize Express app
    this.app = express();
    this.server = null;
    this.isRunning = false;
    
    // Initialize API endpoints
    this.endpoints = new Map();
    
    // Initialize metrics
    this.metrics = {
      requestsTotal: 0,
      requestsSuccess: 0,
      requestsError: 0,
      averageResponseTime: 0,
      endpointUsage: new Map()
    };
    
    console.log('APIManager initialized');
  }
  
  /**
   * Initialize the APIManager
   * @returns {Promise<boolean>} Success status
   */
  async initialize() {
    if (!this.config.enabled) {
      console.log('API server is disabled');
      return false;
    }
    
    try {
      console.log('Initializing APIManager');
      
      // Configure Express middleware
      this._configureMiddleware();
      
      // Configure API routes
      this._configureRoutes();
      
      // Configure error handling
      this._configureErrorHandling();
      
      console.log('APIManager initialized successfully');
      
      return true;
    } catch (error) {
      console.error('Error initializing APIManager:', error);
      throw error;
    }
  }
  
  /**
   * Configure Express middleware
   * @private
   */
  _configureMiddleware() {
    // Basic middleware
    this.app.use(express.json({ limit: '50mb' }));
    this.app.use(express.urlencoded({ extended: true, limit: '50mb' }));
    this.app.use(cookieParser());
    
    // Security middleware
    this.app.use(helmet());
    
    // Compression middleware
    this.app.use(compression());
    
    // CORS middleware
    if (this.config.cors.enabled) {
      this.app.use(cors({
        origin: this.config.cors.origin,
        methods: this.config.cors.methods,
        allowedHeaders: this.config.cors.allowedHeaders,
        credentials: this.config.cors.credentials
      }));
    }
    
    // Rate limiting middleware
    if (this.config.rateLimit.enabled) {
      const limiter = rateLimit({
        windowMs: this.config.rateLimit.windowMs,
        max: this.config.rateLimit.max,
        standardHeaders: this.config.rateLimit.standardHeaders,
        legacyHeaders: this.config.rateLimit.legacyHeaders
      });
      
      this.app.use(limiter);
    }
    
    // Request logging middleware
    this.app.use((req, res, next) => {
      const requestId = uuidv4();
      const startTime = Date.now();
      
      // Add request ID to request object
      req.id = requestId;
      
      // Log request
      if (this.config.logging.enabled) {
        console.log(`[${new Date().toISOString()}] ${req.method} ${req.url} - Request ID: ${requestId}`);
      }
      
      // Track metrics on response
      res.on('finish', () => {
        const endTime = Date.now();
        const responseTime = endTime - startTime;
        
        // Update metrics
        this.metrics.requestsTotal++;
        
        if (res.statusCode >= 200 && res.statusCode < 400) {
          this.metrics.requestsSuccess++;
        } else {
          this.metrics.requestsError++;
        }
        
        // Update average response time
        this.metrics.averageResponseTime = (
          (this.metrics.averageResponseTime * (this.metrics.requestsTotal - 1)) +
          responseTime
        ) / this.metrics.requestsTotal;
        
        // Update endpoint usage
        const endpoint = `${req.method} ${req.route?.path || req.path}`;
        
        if (!this.metrics.endpointUsage.has(endpoint)) {
          this.metrics.endpointUsage.set(endpoint, {
            count: 0,
            averageResponseTime: 0
          });
        }
        
        const endpointMetrics = this.metrics.endpointUsage.get(endpoint);
        endpointMetrics.count++;
        endpointMetrics.averageResponseTime = (
          (endpointMetrics.averageResponseTime * (endpointMetrics.count - 1)) +
          responseTime
        ) / endpointMetrics.count;
        
        // Log response
        if (this.config.logging.enabled) {
          console.log(`[${new Date().toISOString()}] ${req.method} ${req.url} - ${res.statusCode} - ${responseTime}ms - Request ID: ${requestId}`);
        }
        
        // Emit request completed event
        this.emit('request:completed', {
          requestId,
          method: req.method,
          url: req.url,
          statusCode: res.statusCode,
          responseTime
        });
      });
      
      next();
    });
    
    // Authentication middleware
    if (this.config.auth.enabled) {
      this.app.use((req, res, next) => {
        // Skip authentication for certain routes
        const skipAuthRoutes = [
          `${this.config.basePath}/status`,
          `${this.config.basePath}/auth/login`,
          `${this.config.basePath}/auth/register`
        ];
        
        if (skipAuthRoutes.includes(req.path)) {
          return next();
        }
        
        // Check for authentication
        const authHeader = req.headers.authorization;
        
        if (!authHeader) {
          return res.status(401).json({
            error: 'Authentication required'
          });
        }
        
        // Handle different authentication methods
        if (authHeader.startsWith('Bearer ')) {
          // JWT authentication
          const token = authHeader.substring(7);
          
          try {
            // In a real implementation, this would verify the JWT
            // For now, we'll just accept any token
            req.user = {
              id: '1',
              username: 'admin',
              roles: ['admin']
            };
            
            next();
          } catch (error) {
            return res.status(401).json({
              error: 'Invalid token'
            });
          }
        } else if (authHeader.startsWith('ApiKey ')) {
          // API key authentication
          const apiKey = authHeader.substring(7);
          
          // In a real implementation, this would verify the API key
          // For now, we'll just accept any API key
          req.user = {
            id: '1',
            username: 'api',
            roles: ['api']
          };
          
          next();
        } else {
          return res.status(401).json({
            error: 'Unsupported authentication method'
          });
        }
      });
    }
  }
  
  /**
   * Configure API routes
   * @private
   */
  _configureRoutes() {
    const router = express.Router();
    
    // Status endpoint
    router.get('/status', (req, res) => {
      res.json({
        status: 'ok',
        version: '1.0.0',
        timestamp: new Date().toISOString()
      });
    });
    
    // Authentication endpoints
    router.post('/auth/login', (req, res) => {
      const { username, password } = req.body;
      
      // In a real implementation, this would verify credentials
      // For now, we'll just accept any credentials
      if (username && password) {
        res.json({
          success: true,
          token: 'dummy-jwt-token',
          user: {
            id: '1',
            username,
            roles: ['user']
          }
        });
      } else {
        res.status(400).json({
          error: 'Username and password required'
        });
      }
    });
    
    router.post('/auth/register', (req, res) => {
      const { username, password, email } = req.body;
      
      // In a real implementation, this would create a new user
      // For now, we'll just return success
      if (username && password && email) {
        res.json({
          success: true,
          user: {
            id: uuidv4(),
            username,
            email
          }
        });
      } else {
        res.status(400).json({
          error: 'Username, password, and email required'
        });
      }
    });
    
    // Task endpoints
    router.post('/tasks', (req, res) => {
      const { description, type, options } = req.body;
      
      // In a real implementation, this would create a new task
      // For now, we'll just return a dummy task
      const taskId = uuidv4();
      
      res.json({
        success: true,
        task: {
          id: taskId,
          description,
          type,
          options,
          status: 'pending',
          createdAt: new Date().toISOString(),
          createdBy: req.user.id
        }
      });
    });
    
    router.get('/tasks/:id', (req, res) => {
      const { id } = req.params;
      
      // In a real implementation, this would retrieve a task
      // For now, we'll just return a dummy task
      res.json({
        success: true,
        task: {
          id,
          description: 'Dummy task',
          type: 'general',
          status: 'completed',
          createdAt: new Date().toISOString(),
          completedAt: new Date().toISOString(),
          createdBy: req.user.id
        }
      });
    });
    
    // Tool endpoints
    router.get('/tools', (req, res) => {
      // In a real implementation, this would retrieve available tools
      // For now, we'll just return dummy tools
      res.json({
        success: true,
        tools: [
          {
            id: 'tool1',
            name: 'Tool 1',
            description: 'A dummy tool',
            category: 'general',
            domain: 'software_development'
          },
          {
            id: 'tool2',
            name: 'Tool 2',
            description: 'Another dummy tool',
            category: 'analysis',
            domain: 'data_science'
          }
        ]
      });
    });
    
    router.post('/tools/:id/execute', (req, res) => {
      const { id } = req.params;
      const { params, context } = req.body;
      
      // In a real implementation, this would execute a tool
      // For now, we'll just return a dummy result
      res.json({
        success: true,
        result: {
          toolId: id,
          output: `Executed tool ${id} with params: ${JSON.stringify(params)}`,
          timestamp: new Date().toISOString()
        }
      });
    });
    
    // Mount router
    this.app.use(this.config.basePath, router);
  }
  
  /**
   * Configure error handling
   * @private
   */
  _configureErrorHandling() {
    // 404 handler
    this.app.use((req, res, next) => {
      res.status(404).json({
        error: 'Not found'
      });
    });
    
    // Error handler
    this.app.use((err, req, res, next) => {
      console.error('API error:', err);
      
      res.status(err.status || 500).json({
        error: err.message || 'Internal server error'
      });
      
      // Emit error event
      this.emit('error', {
        error: err,
        request: {
          id: req.id,
          method: req.method,
          url: req.url
        }
      });
    });
  }
  
  /**
   * Start the API server
   * @returns {Promise<boolean>} Success status
   */
  async start() {
    if (!this.config.enabled) {
      console.log('API server is disabled');
      return false;
    }
    
    if (this.isRunning) {
      console.log('API server is already running');
      return true;
    }
    
    try {
      return new Promise((resolve, reject) => {
        // Create HTTP or HTTPS server
        if (this.config.ssl.enabled && this.config.ssl.key && this.config.ssl.cert) {
          const sslOptions = {
            key: fs.readFileSync(this.config.ssl.key),
            cert: fs.readFileSync(this.config.ssl.cert)
          };
          
          if (this.config.ssl.ca) {
            sslOptions.ca = fs.readFileSync(this.config.ssl.ca);
          }
          
          this.server = https.createServer(sslOptions, this.app);
        } else {
          this.server = http.createServer(this.app);
        }
        
        // Start server
        this.server.listen(this.config.port, this.config.host, () => {
          this.isRunning = true;
          
          const protocol = this.config.ssl.enabled ? 'https' : 'http';
          console.log(`API server running at ${protocol}://${this.config.host}:${this.config.port}${this.config.basePath}`);
          
          // Emit started event
          this.emit('started', {
            host: this.config.host,
            port: this.config.port,
            basePath: this.config.basePath,
            protocol
          });
          
          resolve(true);
        });
        
        // Handle server errors
        this.server.on('error', (error) => {
          console.error('API server error:', error);
          
          // Emit error event
          this.emit('error', {
            error
          });
          
          reject(error);
        });
      });
    } catch (error) {
      console.error('Error starting API server:', error);
      throw error;
    }
  }
  
  /**
   * Stop the API server
   * @returns {Promise<boolean>} Success status
   */
  async stop() {
    if (!this.isRunning || !this.server) {
      console.log('API server is not running');
      return true;
    }
    
    try {
      return new Promise((resolve, reject) => {
        this.server.close((error) => {
          if (error) {
            console.error('Error stopping API server:', error);
            reject(error);
            return;
          }
          
          this.isRunning = false;
          this.server = null;
          
          console.log('API server stopped');
          
          // Emit stopped event
          this.emit('stopped');
          
          resolve(true);
        });
      });
    } catch (error) {
      console.error('Error stopping API server:', error);
      throw error;
    }
  }
  
  /**
   * Register an API endpoint
   * @param {string} method - HTTP method
   * @param {string} path - Endpoint path
   * @param {Function} handler - Request handler
   * @param {Object} options - Endpoint options
   * @returns {boolean} Success status
   */
  registerEndpoint(method, path, handler, options = {}) {
    try {
      method = method.toUpperCase();
      
      // Check if method is valid
      const validMethods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD'];
      
      if (!validMethods.includes(method)) {
        throw new Error(`Invalid HTTP method: ${method}`);
      }
      
      // Check if path is valid
      if (!path || typeof path !== 'string') {
        throw new Error('Invalid endpoint path');
      }
      
      // Check if handler is valid
      if (!handler || typeof handler !== 'function') {
        throw new Error('Invalid endpoint handler');
      }
      
      // Generate endpoint ID
      const endpointId = `${method}:${path}`;
      
      // Check if endpoint already exists
      if (this.endpoints.has(endpointId)) {
        console.warn(`Endpoint already registered: ${method} ${path}`);
        return false;
      }
      
      // Create endpoint info
      const endpointInfo = {
        id: endpointId,
        method,
        path,
        handler,
        options: {
          auth: options.auth !== undefined ? options.auth : true,
          rateLimit: options.rateLimit !== undefined ? options.rateLimit : true,
          ...options
        }
      };
      
      // Register endpoint
      this.endpoints.set(endpointId, endpointInfo);
      
      // Register with Express
      const routePath = path.startsWith('/') ? path : `/${path}`;
      const fullPath = `${this.config.basePath}${routePath}`;
      
      // Create middleware chain
      const middlewares = [];
      
      // Add authentication middleware if required
      if (endpointInfo.options.auth && this.config.auth.enabled) {
        middlewares.push((req, res, next) => {
          // Check for authentication
          const authHeader = req.headers.authorization;
          
          if (!authHeader) {
            return res.status(401).json({
              error: 'Authentication required'
            });
          }
          
          // Handle different authentication methods
          if (authHeader.startsWith('Bearer ')) {
            // JWT authentication
            const token = authHeader.substring(7);
            
            try {
              // In a real implementation, this would verify the JWT
              // For now, we'll just accept any token
              req.user = {
                id: '1',
                username: 'admin',
                roles: ['admin']
              };
              
              next();
            } catch (error) {
              return res.status(401).json({
                error: 'Invalid token'
              });
            }
          } else if (authHeader.startsWith('ApiKey ')) {
            // API key authentication
            const apiKey = authHeader.substring(7);
            
            // In a real implementation, this would verify the API key
            // For now, we'll just accept any API key
            req.user = {
              id: '1',
              username: 'api',
              roles: ['api']
            };
            
            next();
          } else {
            return res.status(401).json({
              error: 'Unsupported authentication method'
            });
          }
        });
      }
      
      // Add rate limiting middleware if required
      if (endpointInfo.options.rateLimit && this.config.rateLimit.enabled) {
        const limit = endpointInfo.options.rateLimit === true
          ? this.config.rateLimit.max
          : endpointInfo.options.rateLimit;
        
        const limiter = rateLimit({
          windowMs: this.config.rateLimit.windowMs,
          max: limit,
          standardHeaders: this.config.rateLimit.standardHeaders,
          legacyHeaders: this.config.rateLimit.legacyHeaders
        });
        
        middlewares.push(limiter);
      }
      
      // Add handler
      middlewares.push(async (req, res, next) => {
        try {
          await handler(req, res, next);
        } catch (error) {
          next(error);
        }
      });
      
      // Register with Express
      this.app[method.toLowerCase()](fullPath, ...middlewares);
      
      console.log(`Registered endpoint: ${method} ${fullPath}`);
      
      // Initialize metrics for this endpoint
      if (!this.metrics.endpointUsage.has(endpointId)) {
        this.metrics.endpointUsage.set(endpointId, {
          count: 0,
          averageResponseTime: 0
        });
      }
      
      // Emit endpoint registered event
      this.emit('endpoint:registered', {
        method,
        path: fullPath,
        options: endpointInfo.options
      });
      
      return true;
    } catch (error) {
      console.error('Error registering endpoint:', error);
      throw error;
    }
  }
  
  /**
   * Unregister an API endpoint
   * @param {string} method - HTTP method
   * @param {string} path - Endpoint path
   * @returns {boolean} Success status
   */
  unregisterEndpoint(method, path) {
    try {
      method = method.toUpperCase();
      
      // Generate endpoint ID
      const endpointId = `${method}:${path}`;
      
      // Check if endpoint exists
      if (!this.endpoints.has(endpointId)) {
        console.warn(`Endpoint not registered: ${method} ${path}`);
        return false;
      }
      
      // Remove endpoint
      this.endpoints.delete(endpointId);
      
      console.log(`Unregistered endpoint: ${method} ${path}`);
      
      // Emit endpoint unregistered event
      this.emit('endpoint:unregistered', {
        method,
        path
      });
      
      // Note: Express doesn't provide a way to unregister routes
      // We'll need to restart the server to apply changes
      console.warn('Server restart required to apply endpoint changes');
      
      return true;
    } catch (error) {
      console.error('Error unregistering endpoint:', error);
      throw error;
    }
  }
  
  /**
   * Get all registered endpoints
   * @returns {Array<Object>} Registered endpoints
   */
  getEndpoints() {
    return Array.from(this.endpoints.values()).map(endpoint => ({
      method: endpoint.method,
      path: endpoint.path,
      options: endpoint.options
    }));
  }
  
  /**
   * Get API metrics
   * @returns {Object} API metrics
   */
  getMetrics() {
    return {
      ...this.metrics,
      endpointUsage: Array.from(this.metrics.endpointUsage.entries()).map(([endpoint, metrics]) => ({
        endpoint,
        count: metrics.count,
        averageResponseTime: metrics.averageResponseTime
      }))
    };
  }
  
  /**
   * Get API status
   * @returns {Object} API status
   */
  getStatus() {
    return {
      enabled: this.config.enabled,
      running: this.isRunning,
      host: this.config.host,
      port: this.config.port,
      basePath: this.config.basePath,
      ssl: this.config.ssl.enabled,
      endpoints: this.endpoints.size,
      metrics: {
        requestsTotal: this.metrics.requestsTotal,
        requestsSuccess: this.metrics.requestsSuccess,
        requestsError: this.metrics.requestsError,
        averageResponseTime: this.metrics.averageResponseTime
      }
    };
  }
  
  /**
   * Shutdown the APIManager
   * @returns {Promise<void>}
   */
  async shutdown() {
    try {
      console.log('Shutting down APIManager');
      
      // Stop API server
      if (this.isRunning) {
        await this.stop();
      }
      
      // Clear endpoints
      this.endpoints.clear();
      
      console.log('APIManager shutdown complete');
    } catch (error) {
      console.error('Error shutting down APIManager:', error);
      throw error;
    }
  }
}

module.exports = { APIManager };
