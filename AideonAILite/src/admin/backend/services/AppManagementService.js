/**
 * App Management Service for Aideon AI Lite Admin Dashboard
 * 
 * This service provides functionality for managing application configuration,
 * resource allocation, deployment management, and version control.
 */

const express = require('express');
const router = express.Router();
const { body, validationResult } = require('express-validator');
const { authenticate, authorize } = require('../middleware/auth');
const fs = require('fs').promises;
const path = require('path');
const os = require('os');

// Database models
const AppConfig = require('../models/AppConfig');
const ResourceAllocation = require('../models/ResourceAllocation');
const DeploymentHistory = require('../models/DeploymentHistory');
const SystemVersion = require('../models/SystemVersion');

/**
 * App Management Service class
 */
class AppManagementService {
  /**
   * Initialize the App Management Service
   * @param {Object} core - Reference to the AideonCore instance
   */
  constructor(core) {
    this.core = core;
    this.logger = core.logManager.getLogger('app-management-service');
    this.config = core.configManager.getConfig().appManagement || {};
    this.configPath = this.config.configPath || path.join(process.cwd(), 'config');
    
    this.router = this._setupRoutes();
    
    this.logger.info('App Management Service initialized');
  }
  
  /**
   * Set up API routes
   * @returns {Object} Express router
   * @private
   */
  _setupRoutes() {
    // Get system information
    router.get('/system-info', authenticate, async (req, res) => {
      try {
        const systemInfo = await this._getSystemInfo();
        res.json({ success: true, data: systemInfo });
      } catch (error) {
        this.logger.error('Error getting system information:', error);
        res.status(500).json({ success: false, error: 'Failed to get system information' });
      }
    });
    
    // Get application configuration
    router.get('/config', authenticate, async (req, res) => {
      try {
        const config = await this._getAppConfig();
        res.json({ success: true, data: config });
      } catch (error) {
        this.logger.error('Error getting application configuration:', error);
        res.status(500).json({ success: false, error: 'Failed to get application configuration' });
      }
    });
    
    // Update application configuration
    router.put('/config/:id', 
      authenticate, 
      authorize(['super_admin', 'admin']),
      [
        body('key').optional(),
        body('value').optional(),
        body('description').optional(),
        body('category').optional()
      ],
      async (req, res) => {
        const errors = validationResult(req);
        if (!errors.isEmpty()) {
          return res.status(400).json({ success: false, errors: errors.array() });
        }
        
        try {
          const config = await this._updateAppConfig(req.params.id, req.body);
          
          if (!config) {
            return res.status(404).json({ success: false, error: 'Configuration not found' });
          }
          
          res.json({ success: true, data: config });
        } catch (error) {
          this.logger.error(`Error updating configuration ${req.params.id}:`, error);
          res.status(500).json({ success: false, error: 'Failed to update configuration' });
        }
      }
    );
    
    // Create application configuration
    router.post('/config', 
      authenticate, 
      authorize(['super_admin', 'admin']),
      [
        body('key').notEmpty().withMessage('Key is required'),
        body('value').notEmpty().withMessage('Value is required'),
        body('description').optional(),
        body('category').optional()
      ],
      async (req, res) => {
        const errors = validationResult(req);
        if (!errors.isEmpty()) {
          return res.status(400).json({ success: false, errors: errors.array() });
        }
        
        try {
          const config = await this._createAppConfig(req.body);
          res.status(201).json({ success: true, data: config });
        } catch (error) {
          this.logger.error('Error creating configuration:', error);
          res.status(500).json({ success: false, error: 'Failed to create configuration' });
        }
      }
    );
    
    // Delete application configuration
    router.delete('/config/:id', 
      authenticate, 
      authorize(['super_admin', 'admin']),
      async (req, res) => {
        try {
          const result = await this._deleteAppConfig(req.params.id);
          
          if (!result) {
            return res.status(404).json({ success: false, error: 'Configuration not found' });
          }
          
          res.json({ success: true, message: 'Configuration deleted successfully' });
        } catch (error) {
          this.logger.error(`Error deleting configuration ${req.params.id}:`, error);
          res.status(500).json({ success: false, error: 'Failed to delete configuration' });
        }
      }
    );
    
    // Get resource allocation
    router.get('/resources', authenticate, async (req, res) => {
      try {
        const resources = await this._getResourceAllocation();
        res.json({ success: true, data: resources });
      } catch (error) {
        this.logger.error('Error getting resource allocation:', error);
        res.status(500).json({ success: false, error: 'Failed to get resource allocation' });
      }
    });
    
    // Update resource allocation
    router.put('/resources/:id', 
      authenticate, 
      authorize(['super_admin', 'admin']),
      [
        body('resourceType').optional(),
        body('maxAllocation').isNumeric().optional(),
        body('priority').isNumeric().optional(),
        body('autoScale').isBoolean().optional()
      ],
      async (req, res) => {
        const errors = validationResult(req);
        if (!errors.isEmpty()) {
          return res.status(400).json({ success: false, errors: errors.array() });
        }
        
        try {
          const resource = await this._updateResourceAllocation(req.params.id, req.body);
          
          if (!resource) {
            return res.status(404).json({ success: false, error: 'Resource allocation not found' });
          }
          
          res.json({ success: true, data: resource });
        } catch (error) {
          this.logger.error(`Error updating resource allocation ${req.params.id}:`, error);
          res.status(500).json({ success: false, error: 'Failed to update resource allocation' });
        }
      }
    );
    
    // Get deployment history
    router.get('/deployments', authenticate, async (req, res) => {
      try {
        const { limit, skip } = req.query;
        const deployments = await this._getDeploymentHistory(parseInt(limit) || 10, parseInt(skip) || 0);
        res.json({ success: true, data: deployments });
      } catch (error) {
        this.logger.error('Error getting deployment history:', error);
        res.status(500).json({ success: false, error: 'Failed to get deployment history' });
      }
    });
    
    // Create deployment record
    router.post('/deployments', 
      authenticate, 
      authorize(['super_admin', 'admin']),
      [
        body('version').notEmpty().withMessage('Version is required'),
        body('environment').notEmpty().withMessage('Environment is required'),
        body('changes').optional(),
        body('deployedBy').optional()
      ],
      async (req, res) => {
        const errors = validationResult(req);
        if (!errors.isEmpty()) {
          return res.status(400).json({ success: false, errors: errors.array() });
        }
        
        try {
          const deployment = await this._createDeployment(req.body);
          res.status(201).json({ success: true, data: deployment });
        } catch (error) {
          this.logger.error('Error creating deployment record:', error);
          res.status(500).json({ success: false, error: 'Failed to create deployment record' });
        }
      }
    );
    
    // Get system versions
    router.get('/versions', authenticate, async (req, res) => {
      try {
        const versions = await this._getSystemVersions();
        res.json({ success: true, data: versions });
      } catch (error) {
        this.logger.error('Error getting system versions:', error);
        res.status(500).json({ success: false, error: 'Failed to get system versions' });
      }
    });
    
    // Create system version
    router.post('/versions', 
      authenticate, 
      authorize(['super_admin', 'admin']),
      [
        body('version').notEmpty().withMessage('Version is required'),
        body('releaseDate').isISO8601().withMessage('Valid release date is required'),
        body('changes').optional(),
        body('isActive').isBoolean().optional()
      ],
      async (req, res) => {
        const errors = validationResult(req);
        if (!errors.isEmpty()) {
          return res.status(400).json({ success: false, errors: errors.array() });
        }
        
        try {
          const version = await this._createSystemVersion(req.body);
          res.status(201).json({ success: true, data: version });
        } catch (error) {
          this.logger.error('Error creating system version:', error);
          res.status(500).json({ success: false, error: 'Failed to create system version' });
        }
      }
    );
    
    // Update system version
    router.put('/versions/:id', 
      authenticate, 
      authorize(['super_admin', 'admin']),
      [
        body('version').optional(),
        body('releaseDate').isISO8601().optional(),
        body('changes').optional(),
        body('isActive').isBoolean().optional()
      ],
      async (req, res) => {
        const errors = validationResult(req);
        if (!errors.isEmpty()) {
          return res.status(400).json({ success: false, errors: errors.array() });
        }
        
        try {
          const version = await this._updateSystemVersion(req.params.id, req.body);
          
          if (!version) {
            return res.status(404).json({ success: false, error: 'System version not found' });
          }
          
          res.json({ success: true, data: version });
        } catch (error) {
          this.logger.error(`Error updating system version ${req.params.id}:`, error);
          res.status(500).json({ success: false, error: 'Failed to update system version' });
        }
      }
    );
    
    // Restart application
    router.post('/restart', 
      authenticate, 
      authorize(['super_admin', 'admin']),
      async (req, res) => {
        try {
          // Send response before restarting
          res.json({ success: true, message: 'Application restart initiated' });
          
          // Log the restart
          this.logger.info(`Application restart initiated by user ${req.user.id}`);
          
          // Schedule restart after a short delay
          setTimeout(() => {
            this._restartApplication();
          }, 1000);
        } catch (error) {
          this.logger.error('Error restarting application:', error);
          res.status(500).json({ success: false, error: 'Failed to restart application' });
        }
      }
    );
    
    // Apply configuration changes
    router.post('/apply-config', 
      authenticate, 
      authorize(['super_admin', 'admin']),
      async (req, res) => {
        try {
          await this._applyConfigChanges();
          res.json({ success: true, message: 'Configuration changes applied successfully' });
        } catch (error) {
          this.logger.error('Error applying configuration changes:', error);
          res.status(500).json({ success: false, error: 'Failed to apply configuration changes' });
        }
      }
    );
    
    return router;
  }
  
  /**
   * Get system information
   * @returns {Promise<Object>} System information
   * @private
   */
  async _getSystemInfo() {
    try {
      const cpuInfo = os.cpus();
      const totalMemory = os.totalmem();
      const freeMemory = os.freemem();
      const uptime = os.uptime();
      const loadAvg = os.loadavg();
      
      // Get disk usage
      const diskUsage = await this._getDiskUsage();
      
      // Get process information
      const processInfo = {
        pid: process.pid,
        uptime: process.uptime(),
        memoryUsage: process.memoryUsage(),
        cpuUsage: process.cpuUsage()
      };
      
      // Get active connections
      const activeConnections = await this._getActiveConnections();
      
      return {
        os: {
          platform: os.platform(),
          release: os.release(),
          type: os.type(),
          arch: os.arch()
        },
        cpu: {
          model: cpuInfo[0].model,
          cores: cpuInfo.length,
          speed: cpuInfo[0].speed,
          loadAvg
        },
        memory: {
          total: totalMemory,
          free: freeMemory,
          used: totalMemory - freeMemory,
          usedPercentage: ((totalMemory - freeMemory) / totalMemory) * 100
        },
        disk: diskUsage,
        system: {
          hostname: os.hostname(),
          uptime
        },
        process: processInfo,
        network: {
          interfaces: os.networkInterfaces(),
          activeConnections
        }
      };
    } catch (error) {
      this.logger.error('Error getting system information:', error);
      throw error;
    }
  }
  
  /**
   * Get disk usage
   * @returns {Promise<Object>} Disk usage information
   * @private
   */
  async _getDiskUsage() {
    try {
      // This is a simplified implementation
      // In a production environment, you would use a library like diskusage
      // or execute system commands to get accurate disk usage
      
      // For now, we'll return placeholder data
      return {
        total: 1000000000000, // 1 TB
        free: 500000000000,   // 500 GB
        used: 500000000000,   // 500 GB
        usedPercentage: 50
      };
    } catch (error) {
      this.logger.error('Error getting disk usage:', error);
      throw error;
    }
  }
  
  /**
   * Get active connections
   * @returns {Promise<number>} Number of active connections
   * @private
   */
  async _getActiveConnections() {
    try {
      // This is a simplified implementation
      // In a production environment, you would get this from your HTTP server
      
      // For now, we'll return a placeholder value
      return 42;
    } catch (error) {
      this.logger.error('Error getting active connections:', error);
      throw error;
    }
  }
  
  /**
   * Get application configuration
   * @returns {Promise<Array>} Application configuration
   * @private
   */
  async _getAppConfig() {
    try {
      const config = await AppConfig.find().sort({ category: 1, key: 1 });
      return config;
    } catch (error) {
      this.logger.error('Error getting application configuration:', error);
      throw error;
    }
  }
  
  /**
   * Create application configuration
   * @param {Object} data - Configuration data
   * @returns {Promise<Object>} Created configuration
   * @private
   */
  async _createAppConfig(data) {
    try {
      // Check if configuration with the same key already exists
      const existingConfig = await AppConfig.findOne({ key: data.key });
      
      if (existingConfig) {
        throw new Error(`Configuration with key '${data.key}' already exists`);
      }
      
      const config = new AppConfig(data);
      await config.save();
      
      // Update in-memory configuration
      this.core.configManager.setConfig(data.key, data.value);
      
      return config;
    } catch (error) {
      this.logger.error('Error creating application configuration:', error);
      throw error;
    }
  }
  
  /**
   * Update application configuration
   * @param {string} id - Configuration ID
   * @param {Object} data - Updated configuration data
   * @returns {Promise<Object>} Updated configuration
   * @private
   */
  async _updateAppConfig(id, data) {
    try {
      const config = await AppConfig.findByIdAndUpdate(id, data, { new: true });
      
      if (!config) {
        return null;
      }
      
      // Update in-memory configuration
      this.core.configManager.setConfig(config.key, config.value);
      
      return config;
    } catch (error) {
      this.logger.error(`Error updating configuration ${id}:`, error);
      throw error;
    }
  }
  
  /**
   * Delete application configuration
   * @param {string} id - Configuration ID
   * @returns {Promise<boolean>} Success status
   * @private
   */
  async _deleteAppConfig(id) {
    try {
      const config = await AppConfig.findByIdAndDelete(id);
      
      if (!config) {
        return false;
      }
      
      // Remove from in-memory configuration
      this.core.configManager.removeConfig(config.key);
      
      return true;
    } catch (error) {
      this.logger.error(`Error deleting configuration ${id}:`, error);
      throw error;
    }
  }
  
  /**
   * Get resource allocation
   * @returns {Promise<Array>} Resource allocation
   * @private
   */
  async _getResourceAllocation() {
    try {
      const resources = await ResourceAllocation.find();
      return resources;
    } catch (error) {
      this.logger.error('Error getting resource allocation:', error);
      throw error;
    }
  }
  
  /**
   * Update resource allocation
   * @param {string} id - Resource allocation ID
   * @param {Object} data - Updated resource allocation data
   * @returns {Promise<Object>} Updated resource allocation
   * @private
   */
  async _updateResourceAllocation(id, data) {
    try {
      const resource = await ResourceAllocation.findByIdAndUpdate(id, data, { new: true });
      
      if (!resource) {
        return null;
      }
      
      // Apply resource allocation changes
      this._applyResourceAllocation(resource);
      
      return resource;
    } catch (error) {
      this.logger.error(`Error updating resource allocation ${id}:`, error);
      throw error;
    }
  }
  
  /**
   * Apply resource allocation changes
   * @param {Object} resource - Resource allocation
   * @private
   */
  _applyResourceAllocation(resource) {
    try {
      // This is where you would apply resource allocation changes to the system
      // For example, adjusting memory limits, CPU allocation, etc.
      
      this.logger.info(`Applied resource allocation changes for ${resource.resourceType}`);
    } catch (error) {
      this.logger.error(`Error applying resource allocation changes for ${resource.resourceType}:`, error);
      throw error;
    }
  }
  
  /**
   * Get deployment history
   * @param {number} limit - Maximum number of records to return
   * @param {number} skip - Number of records to skip
   * @returns {Promise<Array>} Deployment history
   * @private
   */
  async _getDeploymentHistory(limit = 10, skip = 0) {
    try {
      const deployments = await DeploymentHistory.find()
        .sort({ deploymentDate: -1 })
        .skip(skip)
        .limit(limit);
      
      const total = await DeploymentHistory.countDocuments();
      
      return {
        deployments,
        pagination: {
          total,
          limit,
          skip,
          hasMore: total > skip + limit
        }
      };
    } catch (error) {
      this.logger.error('Error getting deployment history:', error);
      throw error;
    }
  }
  
  /**
   * Create deployment record
   * @param {Object} data - Deployment data
   * @returns {Promise<Object>} Created deployment record
   * @private
   */
  async _createDeployment(data) {
    try {
      const deployment = new DeploymentHistory({
        ...data,
        deploymentDate: new Date(),
        status: 'completed'
      });
      
      await deployment.save();
      
      return deployment;
    } catch (error) {
      this.logger.error('Error creating deployment record:', error);
      throw error;
    }
  }
  
  /**
   * Get system versions
   * @returns {Promise<Array>} System versions
   * @private
   */
  async _getSystemVersions() {
    try {
      const versions = await SystemVersion.find().sort({ releaseDate: -1 });
      return versions;
    } catch (error) {
      this.logger.error('Error getting system versions:', error);
      throw error;
    }
  }
  
  /**
   * Create system version
   * @param {Object} data - Version data
   * @returns {Promise<Object>} Created system version
   * @private
   */
  async _createSystemVersion(data) {
    try {
      // If this version is set as active, deactivate all other versions
      if (data.isActive) {
        await SystemVersion.updateMany({}, { isActive: false });
      }
      
      const version = new SystemVersion(data);
      await version.save();
      
      return version;
    } catch (error) {
      this.logger.error('Error creating system version:', error);
      throw error;
    }
  }
  
  /**
   * Update system version
   * @param {string} id - Version ID
   * @param {Object} data - Updated version data
   * @returns {Promise<Object>} Updated system version
   * @private
   */
  async _updateSystemVersion(id, data) {
    try {
      // If this version is set as active, deactivate all other versions
      if (data.isActive) {
        await SystemVersion.updateMany({ _id: { $ne: id } }, { isActive: false });
      }
      
      const version = await SystemVersion.findByIdAndUpdate(id, data, { new: true });
      
      if (!version) {
        return null;
      }
      
      return version;
    } catch (error) {
      this.logger.error(`Error updating system version ${id}:`, error);
      throw error;
    }
  }
  
  /**
   * Restart application
   * @private
   */
  _restartApplication() {
    try {
      this.logger.info('Restarting application...');
      
      // In a production environment, this would be handled by a process manager like PM2
      // For now, we'll just exit the process and let the process manager restart it
      process.exit(0);
    } catch (error) {
      this.logger.error('Error restarting application:', error);
      throw error;
    }
  }
  
  /**
   * Apply configuration changes
   * @returns {Promise<void>}
   * @private
   */
  async _applyConfigChanges() {
    try {
      this.logger.info('Applying configuration changes...');
      
      // Get all configuration
      const configs = await AppConfig.find();
      
      // Update in-memory configuration
      configs.forEach(config => {
        this.core.configManager.setConfig(config.key, config.value);
      });
      
      // Write configuration to file
      await this._writeConfigToFile(configs);
      
      this.logger.info('Configuration changes applied successfully');
    } catch (error) {
      this.logger.error('Error applying configuration changes:', error);
      throw error;
    }
  }
  
  /**
   * Write configuration to file
   * @param {Array} configs - Configuration array
   * @returns {Promise<void>}
   * @private
   */
  async _writeConfigToFile(configs) {
    try {
      // Ensure config directory exists
      await fs.mkdir(this.configPath, { recursive: true });
      
      // Group configs by category
      const configsByCategory = {};
      configs.forEach(config => {
        const category = config.category || 'default';
        if (!configsByCategory[category]) {
          configsByCategory[category] = {};
        }
        configsByCategory[category][config.key] = config.value;
      });
      
      // Write each category to a separate file
      for (const [category, categoryConfigs] of Object.entries(configsByCategory)) {
        const filePath = path.join(this.configPath, `${category}.json`);
        await fs.writeFile(filePath, JSON.stringify(categoryConfigs, null, 2));
      }
      
      this.logger.info('Configuration written to files successfully');
    } catch (error) {
      this.logger.error('Error writing configuration to file:', error);
      throw error;
    }
  }
  
  /**
   * Get API router
   * @returns {Object} Express router
   */
  getRouter() {
    return this.router;
  }
}

module.exports = AppManagementService;
