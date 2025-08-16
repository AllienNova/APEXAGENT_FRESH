/**
 * Admin Dashboard Integration Module for Aideon AI Lite
 * 
 * This module integrates the admin dashboard with the core system,
 * providing a unified interface for managing all aspects of the platform.
 */

const express = require('express');
const path = require('path');
const cors = require('cors');
const helmet = require('helmet');
const compression = require('compression');
const rateLimit = require('express-rate-limit');
const { createProxyMiddleware } = require('http-proxy-middleware');

// Import services
const ApiService = require('./services/ApiService');
const AppManagementService = require('./services/AppManagementService');
const HealthMonitoringService = require('./services/HealthMonitoringService');
const AuthService = require('./services/AuthService');
const UserManagementService = require('./services/UserManagementService');

// Import middleware
const { authenticate, authorize } = require('./middleware/auth');
const errorHandler = require('./middleware/errorHandler');
const requestLogger = require('./middleware/requestLogger');

/**
 * Admin Dashboard Integration class
 */
class AdminDashboardIntegration {
  /**
   * Initialize the Admin Dashboard Integration
   * @param {Object} core - Reference to the AideonCore instance
   * @param {Object} options - Configuration options
   */
  constructor(core, options = {}) {
    this.core = core;
    this.logger = core.logManager.getLogger('admin-dashboard');
    this.config = core.configManager.getConfig().adminDashboard || {};
    
    this.options = {
      port: options.port || this.config.port || 3000,
      apiPrefix: options.apiPrefix || this.config.apiPrefix || '/api/admin',
      staticPath: options.staticPath || this.config.staticPath || path.join(__dirname, '../frontend/build'),
      corsOrigins: options.corsOrigins || this.config.corsOrigins || ['http://localhost:3000'],
      rateLimit: options.rateLimit || this.config.rateLimit || {
        windowMs: 15 * 60 * 1000, // 15 minutes
        max: 100 // limit each IP to 100 requests per windowMs
      }
    };
    
    // Initialize services
    this.apiService = new ApiService(core);
    this.appManagementService = new AppManagementService(core);
    this.healthMonitoringService = new HealthMonitoringService(core);
    this.authService = new AuthService(core);
    this.userManagementService = new UserManagementService(core);
    
    // Initialize Express app
    this.app = this._setupExpressApp();
    
    this.logger.info('Admin Dashboard Integration initialized');
  }
  
  /**
   * Set up Express app
   * @returns {Object} Express app
   * @private
   */
  _setupExpressApp() {
    const app = express();
    
    // Apply middleware
    app.use(helmet({
      contentSecurityPolicy: {
        directives: {
          defaultSrc: ["'self'"],
          scriptSrc: ["'self'", "'unsafe-inline'", "'unsafe-eval'"],
          styleSrc: ["'self'", "'unsafe-inline'", 'https://fonts.googleapis.com'],
          fontSrc: ["'self'", 'https://fonts.gstatic.com'],
          imgSrc: ["'self'", 'data:', 'blob:'],
          connectSrc: ["'self'", ...this.options.corsOrigins]
        }
      }
    }));
    app.use(compression());
    app.use(express.json({ limit: '10mb' }));
    app.use(express.urlencoded({ extended: true, limit: '10mb' }));
    
    // Set up CORS
    app.use(cors({
      origin: (origin, callback) => {
        if (!origin || this.options.corsOrigins.includes(origin) || this.options.corsOrigins.includes('*')) {
          callback(null, true);
        } else {
          callback(new Error('Not allowed by CORS'));
        }
      },
      credentials: true
    }));
    
    // Set up rate limiting
    const limiter = rateLimit(this.options.rateLimit);
    app.use(this.options.apiPrefix, limiter);
    
    // Request logging
    app.use(requestLogger(this.logger));
    
    // Set up API routes
    this._setupApiRoutes(app);
    
    // Serve static files for admin dashboard frontend
    app.use(express.static(this.options.staticPath));
    
    // Handle SPA routing
    app.get('*', (req, res) => {
      res.sendFile(path.join(this.options.staticPath, 'index.html'));
    });
    
    // Error handling
    app.use(errorHandler(this.logger));
    
    return app;
  }
  
  /**
   * Set up API routes
   * @param {Object} app - Express app
   * @private
   */
  _setupApiRoutes(app) {
    const apiRouter = express.Router();
    
    // Auth routes
    apiRouter.use('/auth', this.authService.getRouter());
    
    // Protected routes
    apiRouter.use('/api-management', authenticate, this.apiService.getRouter());
    apiRouter.use('/app-management', authenticate, this.appManagementService.getRouter());
    apiRouter.use('/health', authenticate, this.healthMonitoringService.getRouter());
    apiRouter.use('/users', authenticate, this.userManagementService.getRouter());
    
    // System info route
    apiRouter.get('/system-info', authenticate, async (req, res) => {
      try {
        const systemInfo = {
          version: this.core.version,
          uptime: process.uptime(),
          environment: process.env.NODE_ENV || 'development',
          nodeVersion: process.version,
          platform: process.platform,
          memory: process.memoryUsage(),
          cpuUsage: process.cpuUsage()
        };
        
        res.json({ success: true, data: systemInfo });
      } catch (error) {
        this.logger.error('Error getting system info:', error);
        res.status(500).json({ success: false, error: 'Failed to get system info' });
      }
    });
    
    // Core system routes
    apiRouter.use('/core', authenticate, authorize(['super_admin', 'admin']), (req, res, next) => {
      // Proxy requests to core system API
      const coreApiProxy = createProxyMiddleware({
        target: `http://localhost:${this.core.config.apiPort || 8000}`,
        changeOrigin: true,
        pathRewrite: {
          [`^${this.options.apiPrefix}/core`]: '/api'
        },
        onProxyReq: (proxyReq, req) => {
          // Add admin token to proxied request
          proxyReq.setHeader('Authorization', `Bearer ${this.core.generateAdminToken()}`);
        },
        logLevel: 'warn',
        logProvider: () => this.logger
      });
      
      coreApiProxy(req, res, next);
    });
    
    // Mount API router
    app.use(this.options.apiPrefix, apiRouter);
  }
  
  /**
   * Start the admin dashboard server
   * @returns {Promise<void>}
   */
  async start() {
    return new Promise((resolve) => {
      this.server = this.app.listen(this.options.port, () => {
        this.logger.info(`Admin dashboard server listening on port ${this.options.port}`);
        
        // Start health monitoring service
        this.healthMonitoringService.start();
        
        resolve();
      });
    });
  }
  
  /**
   * Stop the admin dashboard server
   * @returns {Promise<void>}
   */
  async stop() {
    return new Promise((resolve) => {
      if (this.server) {
        // Stop health monitoring service
        this.healthMonitoringService.stop();
        
        this.server.close(() => {
          this.logger.info('Admin dashboard server stopped');
          resolve();
        });
      } else {
        resolve();
      }
    });
  }
  
  /**
   * Get the admin dashboard URL
   * @returns {string} Admin dashboard URL
   */
  getUrl() {
    return `http://localhost:${this.options.port}`;
  }
}

module.exports = AdminDashboardIntegration;
