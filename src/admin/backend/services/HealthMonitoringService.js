/**
 * Health Monitoring Service for Aideon AI Lite Admin Dashboard
 * 
 * This service provides functionality for monitoring system health, collecting metrics,
 * generating alerts, and storing historical performance data.
 */

const express = require('express');
const router = express.Router();
const { body, validationResult } = require('express-validator');
const { authenticate, authorize } = require('../middleware/auth');
const os = require('os');
const { EventEmitter } = require('events');

// Database models
const SystemMetric = require('../models/SystemMetric');
const Alert = require('../models/Alert');
const AlertConfig = require('../models/AlertConfig');
const PerformanceSnapshot = require('../models/PerformanceSnapshot');

/**
 * Health Monitoring Service class
 */
class HealthMonitoringService extends EventEmitter {
  /**
   * Initialize the Health Monitoring Service
   * @param {Object} core - Reference to the AideonCore instance
   */
  constructor(core) {
    super();
    this.core = core;
    this.logger = core.logManager.getLogger('health-monitoring-service');
    this.config = core.configManager.getConfig().healthMonitoring || {};
    
    // Metrics collection interval in milliseconds
    this.metricsInterval = this.config.metricsInterval || 60000; // Default: 1 minute
    
    // Alert check interval in milliseconds
    this.alertCheckInterval = this.config.alertCheckInterval || 30000; // Default: 30 seconds
    
    // Performance snapshot interval in milliseconds
    this.snapshotInterval = this.config.snapshotInterval || 3600000; // Default: 1 hour
    
    // Metrics retention period in days
    this.metricsRetention = this.config.metricsRetention || 30; // Default: 30 days
    
    // Initialize metrics collection
    this.metricsCollector = null;
    this.alertChecker = null;
    this.snapshotCollector = null;
    
    this.router = this._setupRoutes();
    
    this.logger.info('Health Monitoring Service initialized');
  }
  
  /**
   * Start the health monitoring service
   */
  start() {
    this._startMetricsCollection();
    this._startAlertChecking();
    this._startSnapshotCollection();
    this._scheduleDataRetention();
    
    this.logger.info('Health monitoring started');
  }
  
  /**
   * Stop the health monitoring service
   */
  stop() {
    if (this.metricsCollector) {
      clearInterval(this.metricsCollector);
      this.metricsCollector = null;
    }
    
    if (this.alertChecker) {
      clearInterval(this.alertChecker);
      this.alertChecker = null;
    }
    
    if (this.snapshotCollector) {
      clearInterval(this.snapshotCollector);
      this.snapshotCollector = null;
    }
    
    this.logger.info('Health monitoring stopped');
  }
  
  /**
   * Set up API routes
   * @returns {Object} Express router
   * @private
   */
  _setupRoutes() {
    // Get current system metrics
    router.get('/metrics/current', authenticate, async (req, res) => {
      try {
        const metrics = await this._getCurrentMetrics();
        res.json({ success: true, data: metrics });
      } catch (error) {
        this.logger.error('Error getting current metrics:', error);
        res.status(500).json({ success: false, error: 'Failed to get current metrics' });
      }
    });
    
    // Get historical system metrics
    router.get('/metrics/history', authenticate, async (req, res) => {
      try {
        const { metricType, startTime, endTime, interval } = req.query;
        const metrics = await this._getHistoricalMetrics(metricType, startTime, endTime, interval);
        res.json({ success: true, data: metrics });
      } catch (error) {
        this.logger.error('Error getting historical metrics:', error);
        res.status(500).json({ success: false, error: 'Failed to get historical metrics' });
      }
    });
    
    // Get active alerts
    router.get('/alerts/active', authenticate, async (req, res) => {
      try {
        const alerts = await this._getActiveAlerts();
        res.json({ success: true, data: alerts });
      } catch (error) {
        this.logger.error('Error getting active alerts:', error);
        res.status(500).json({ success: false, error: 'Failed to get active alerts' });
      }
    });
    
    // Get alert history
    router.get('/alerts/history', authenticate, async (req, res) => {
      try {
        const { startTime, endTime, severity, limit, skip } = req.query;
        const alerts = await this._getAlertHistory(
          startTime, 
          endTime, 
          severity, 
          parseInt(limit) || 50, 
          parseInt(skip) || 0
        );
        res.json({ success: true, data: alerts });
      } catch (error) {
        this.logger.error('Error getting alert history:', error);
        res.status(500).json({ success: false, error: 'Failed to get alert history' });
      }
    });
    
    // Acknowledge alert
    router.post('/alerts/:id/acknowledge', 
      authenticate, 
      authorize(['super_admin', 'admin', 'api_manager']),
      async (req, res) => {
        try {
          const result = await this._acknowledgeAlert(req.params.id, req.user.id);
          
          if (!result) {
            return res.status(404).json({ success: false, error: 'Alert not found' });
          }
          
          res.json({ success: true, data: result });
        } catch (error) {
          this.logger.error(`Error acknowledging alert ${req.params.id}:`, error);
          res.status(500).json({ success: false, error: 'Failed to acknowledge alert' });
        }
      }
    );
    
    // Resolve alert
    router.post('/alerts/:id/resolve', 
      authenticate, 
      authorize(['super_admin', 'admin', 'api_manager']),
      async (req, res) => {
        try {
          const result = await this._resolveAlert(req.params.id, req.user.id);
          
          if (!result) {
            return res.status(404).json({ success: false, error: 'Alert not found' });
          }
          
          res.json({ success: true, data: result });
        } catch (error) {
          this.logger.error(`Error resolving alert ${req.params.id}:`, error);
          res.status(500).json({ success: false, error: 'Failed to resolve alert' });
        }
      }
    );
    
    // Get alert configurations
    router.get('/alert-configs', authenticate, async (req, res) => {
      try {
        const configs = await this._getAlertConfigs();
        res.json({ success: true, data: configs });
      } catch (error) {
        this.logger.error('Error getting alert configurations:', error);
        res.status(500).json({ success: false, error: 'Failed to get alert configurations' });
      }
    });
    
    // Create alert configuration
    router.post('/alert-configs', 
      authenticate, 
      authorize(['super_admin', 'admin']),
      [
        body('name').notEmpty().withMessage('Name is required'),
        body('metricType').notEmpty().withMessage('Metric type is required'),
        body('condition').notEmpty().withMessage('Condition is required'),
        body('threshold').isNumeric().withMessage('Threshold must be a number'),
        body('severity').isIn(['info', 'warning', 'error', 'critical']).withMessage('Invalid severity'),
        body('enabled').isBoolean().optional(),
        body('description').optional()
      ],
      async (req, res) => {
        const errors = validationResult(req);
        if (!errors.isEmpty()) {
          return res.status(400).json({ success: false, errors: errors.array() });
        }
        
        try {
          const config = await this._createAlertConfig(req.body);
          res.status(201).json({ success: true, data: config });
        } catch (error) {
          this.logger.error('Error creating alert configuration:', error);
          res.status(500).json({ success: false, error: 'Failed to create alert configuration' });
        }
      }
    );
    
    // Update alert configuration
    router.put('/alert-configs/:id', 
      authenticate, 
      authorize(['super_admin', 'admin']),
      [
        body('name').optional(),
        body('metricType').optional(),
        body('condition').optional(),
        body('threshold').isNumeric().optional(),
        body('severity').isIn(['info', 'warning', 'error', 'critical']).optional(),
        body('enabled').isBoolean().optional(),
        body('description').optional()
      ],
      async (req, res) => {
        const errors = validationResult(req);
        if (!errors.isEmpty()) {
          return res.status(400).json({ success: false, errors: errors.array() });
        }
        
        try {
          const config = await this._updateAlertConfig(req.params.id, req.body);
          
          if (!config) {
            return res.status(404).json({ success: false, error: 'Alert configuration not found' });
          }
          
          res.json({ success: true, data: config });
        } catch (error) {
          this.logger.error(`Error updating alert configuration ${req.params.id}:`, error);
          res.status(500).json({ success: false, error: 'Failed to update alert configuration' });
        }
      }
    );
    
    // Delete alert configuration
    router.delete('/alert-configs/:id', 
      authenticate, 
      authorize(['super_admin', 'admin']),
      async (req, res) => {
        try {
          const result = await this._deleteAlertConfig(req.params.id);
          
          if (!result) {
            return res.status(404).json({ success: false, error: 'Alert configuration not found' });
          }
          
          res.json({ success: true, message: 'Alert configuration deleted successfully' });
        } catch (error) {
          this.logger.error(`Error deleting alert configuration ${req.params.id}:`, error);
          res.status(500).json({ success: false, error: 'Failed to delete alert configuration' });
        }
      }
    );
    
    // Get performance snapshots
    router.get('/snapshots', authenticate, async (req, res) => {
      try {
        const { startTime, endTime, limit, skip } = req.query;
        const snapshots = await this._getPerformanceSnapshots(
          startTime, 
          endTime, 
          parseInt(limit) || 24, 
          parseInt(skip) || 0
        );
        res.json({ success: true, data: snapshots });
      } catch (error) {
        this.logger.error('Error getting performance snapshots:', error);
        res.status(500).json({ success: false, error: 'Failed to get performance snapshots' });
      }
    });
    
    // Get system health score
    router.get('/health-score', authenticate, async (req, res) => {
      try {
        const healthScore = await this._calculateHealthScore();
        res.json({ success: true, data: healthScore });
      } catch (error) {
        this.logger.error('Error calculating health score:', error);
        res.status(500).json({ success: false, error: 'Failed to calculate health score' });
      }
    });
    
    // Run system health check
    router.post('/health-check', 
      authenticate, 
      authorize(['super_admin', 'admin', 'api_manager']),
      async (req, res) => {
        try {
          const healthCheck = await this._runHealthCheck();
          res.json({ success: true, data: healthCheck });
        } catch (error) {
          this.logger.error('Error running health check:', error);
          res.status(500).json({ success: false, error: 'Failed to run health check' });
        }
      }
    );
    
    return router;
  }
  
  /**
   * Start metrics collection
   * @private
   */
  _startMetricsCollection() {
    if (this.metricsCollector) {
      clearInterval(this.metricsCollector);
    }
    
    // Collect initial metrics
    this._collectMetrics();
    
    // Set up interval for regular collection
    this.metricsCollector = setInterval(() => {
      this._collectMetrics();
    }, this.metricsInterval);
    
    this.logger.info(`Metrics collection started with interval of ${this.metricsInterval}ms`);
  }
  
  /**
   * Start alert checking
   * @private
   */
  _startAlertChecking() {
    if (this.alertChecker) {
      clearInterval(this.alertChecker);
    }
    
    // Check alerts initially
    this._checkAlerts();
    
    // Set up interval for regular checking
    this.alertChecker = setInterval(() => {
      this._checkAlerts();
    }, this.alertCheckInterval);
    
    this.logger.info(`Alert checking started with interval of ${this.alertCheckInterval}ms`);
  }
  
  /**
   * Start performance snapshot collection
   * @private
   */
  _startSnapshotCollection() {
    if (this.snapshotCollector) {
      clearInterval(this.snapshotCollector);
    }
    
    // Collect initial snapshot
    this._collectPerformanceSnapshot();
    
    // Set up interval for regular collection
    this.snapshotCollector = setInterval(() => {
      this._collectPerformanceSnapshot();
    }, this.snapshotInterval);
    
    this.logger.info(`Performance snapshot collection started with interval of ${this.snapshotInterval}ms`);
  }
  
  /**
   * Schedule data retention tasks
   * @private
   */
  _scheduleDataRetention() {
    // Run data retention daily at midnight
    const now = new Date();
    const midnight = new Date(now);
    midnight.setHours(24, 0, 0, 0);
    
    const timeUntilMidnight = midnight.getTime() - now.getTime();
    
    setTimeout(() => {
      this._performDataRetention();
      
      // Schedule subsequent runs daily
      setInterval(() => {
        this._performDataRetention();
      }, 24 * 60 * 60 * 1000);
    }, timeUntilMidnight);
    
    this.logger.info(`Data retention scheduled to run in ${Math.round(timeUntilMidnight / 1000 / 60)} minutes`);
  }
  
  /**
   * Perform data retention
   * @private
   */
  async _performDataRetention() {
    try {
      this.logger.info('Performing data retention...');
      
      const retentionDate = new Date();
      retentionDate.setDate(retentionDate.getDate() - this.metricsRetention);
      
      // Delete old metrics
      const metricsResult = await SystemMetric.deleteMany({
        timestamp: { $lt: retentionDate }
      });
      
      // Delete old resolved alerts
      const alertsResult = await Alert.deleteMany({
        status: 'resolved',
        resolvedAt: { $lt: retentionDate }
      });
      
      // Delete old performance snapshots
      const snapshotsResult = await PerformanceSnapshot.deleteMany({
        timestamp: { $lt: retentionDate }
      });
      
      this.logger.info(`Data retention completed: ${metricsResult.deletedCount} metrics, ${alertsResult.deletedCount} alerts, ${snapshotsResult.deletedCount} snapshots deleted`);
    } catch (error) {
      this.logger.error('Error performing data retention:', error);
    }
  }
  
  /**
   * Collect system metrics
   * @private
   */
  async _collectMetrics() {
    try {
      const metrics = await this._gatherSystemMetrics();
      
      // Save metrics to database
      for (const [type, value] of Object.entries(metrics)) {
        const metric = new SystemMetric({
          type,
          value,
          timestamp: new Date()
        });
        
        await metric.save();
      }
      
      // Emit metrics event for real-time updates
      this.emit('metrics', metrics);
      
      this.logger.debug('System metrics collected successfully');
    } catch (error) {
      this.logger.error('Error collecting system metrics:', error);
    }
  }
  
  /**
   * Gather system metrics
   * @returns {Promise<Object>} System metrics
   * @private
   */
  async _gatherSystemMetrics() {
    try {
      // CPU usage
      const cpuUsage = os.loadavg()[0] / os.cpus().length * 100;
      
      // Memory usage
      const totalMemory = os.totalmem();
      const freeMemory = os.freemem();
      const memoryUsage = ((totalMemory - freeMemory) / totalMemory) * 100;
      
      // Process memory usage
      const processMemory = process.memoryUsage();
      const heapUsage = (processMemory.heapUsed / processMemory.heapTotal) * 100;
      
      // API metrics
      const apiMetrics = await this._getApiMetrics();
      
      // Task metrics
      const taskMetrics = await this._getTaskMetrics();
      
      // Database metrics
      const dbMetrics = await this._getDatabaseMetrics();
      
      return {
        'cpu.usage': cpuUsage,
        'memory.usage': memoryUsage,
        'memory.free': freeMemory,
        'memory.total': totalMemory,
        'process.heap.usage': heapUsage,
        'process.memory.rss': processMemory.rss,
        'process.uptime': process.uptime(),
        'system.uptime': os.uptime(),
        ...apiMetrics,
        ...taskMetrics,
        ...dbMetrics
      };
    } catch (error) {
      this.logger.error('Error gathering system metrics:', error);
      throw error;
    }
  }
  
  /**
   * Get API metrics
   * @returns {Promise<Object>} API metrics
   * @private
   */
  async _getApiMetrics() {
    try {
      // This would typically come from your API monitoring system
      // For now, we'll return placeholder data
      return {
        'api.requests.total': 1000,
        'api.requests.success': 980,
        'api.requests.error': 20,
        'api.latency.avg': 120, // ms
        'api.throughput': 16.7 // requests per second
      };
    } catch (error) {
      this.logger.error('Error getting API metrics:', error);
      return {};
    }
  }
  
  /**
   * Get task metrics
   * @returns {Promise<Object>} Task metrics
   * @private
   */
  async _getTaskMetrics() {
    try {
      // This would typically come from your task management system
      // For now, we'll return placeholder data
      return {
        'tasks.active': 5,
        'tasks.queued': 12,
        'tasks.completed': 450,
        'tasks.failed': 3,
        'tasks.processing_time.avg': 2300 // ms
      };
    } catch (error) {
      this.logger.error('Error getting task metrics:', error);
      return {};
    }
  }
  
  /**
   * Get database metrics
   * @returns {Promise<Object>} Database metrics
   * @private
   */
  async _getDatabaseMetrics() {
    try {
      // This would typically come from your database monitoring system
      // For now, we'll return placeholder data
      return {
        'db.connections': 25,
        'db.queries.per_second': 45,
        'db.latency.avg': 5, // ms
        'db.size': 256000000 // bytes
      };
    } catch (error) {
      this.logger.error('Error getting database metrics:', error);
      return {};
    }
  }
  
  /**
   * Check alerts based on current metrics
   * @private
   */
  async _checkAlerts() {
    try {
      // Get current metrics
      const metrics = await this._getCurrentMetrics();
      
      // Get alert configurations
      const alertConfigs = await AlertConfig.find({ enabled: true });
      
      for (const config of alertConfigs) {
        const metricValue = metrics[config.metricType];
        
        if (metricValue === undefined) {
          continue;
        }
        
        let isTriggered = false;
        
        // Check if alert condition is met
        switch (config.condition) {
          case 'gt':
            isTriggered = metricValue > config.threshold;
            break;
          case 'gte':
            isTriggered = metricValue >= config.threshold;
            break;
          case 'lt':
            isTriggered = metricValue < config.threshold;
            break;
          case 'lte':
            isTriggered = metricValue <= config.threshold;
            break;
          case 'eq':
            isTriggered = metricValue === config.threshold;
            break;
          case 'neq':
            isTriggered = metricValue !== config.threshold;
            break;
        }
        
        if (isTriggered) {
          // Check if there's already an active alert for this configuration
          const existingAlert = await Alert.findOne({
            configId: config._id,
            status: { $in: ['active', 'acknowledged'] }
          });
          
          if (!existingAlert) {
            // Create new alert
            const alert = new Alert({
              configId: config._id,
              name: config.name,
              description: config.description,
              metricType: config.metricType,
              metricValue,
              threshold: config.threshold,
              condition: config.condition,
              severity: config.severity,
              status: 'active',
              createdAt: new Date()
            });
            
            await alert.save();
            
            // Emit alert event for real-time updates
            this.emit('alert', alert);
            
            this.logger.info(`Alert triggered: ${config.name}, ${config.metricType} = ${metricValue}`);
          }
        } else {
          // Check if there's an active alert that should be auto-resolved
          const existingAlert = await Alert.findOne({
            configId: config._id,
            status: { $in: ['active', 'acknowledged'] }
          });
          
          if (existingAlert && config.autoResolve) {
            existingAlert.status = 'resolved';
            existingAlert.resolvedAt = new Date();
            existingAlert.resolvedBy = 'system';
            existingAlert.resolution = 'Auto-resolved: metric value returned to normal range';
            
            await existingAlert.save();
            
            // Emit alert update event for real-time updates
            this.emit('alertUpdate', existingAlert);
            
            this.logger.info(`Alert auto-resolved: ${config.name}, ${config.metricType} = ${metricValue}`);
          }
        }
      }
    } catch (error) {
      this.logger.error('Error checking alerts:', error);
    }
  }
  
  /**
   * Collect performance snapshot
   * @private
   */
  async _collectPerformanceSnapshot() {
    try {
      // Get current metrics
      const metrics = await this._getCurrentMetrics();
      
      // Get active alerts
      const activeAlerts = await Alert.countDocuments({
        status: { $in: ['active', 'acknowledged'] }
      });
      
      // Calculate health score
      const healthScore = await this._calculateHealthScore();
      
      // Create snapshot
      const snapshot = new PerformanceSnapshot({
        timestamp: new Date(),
        metrics,
        activeAlerts,
        healthScore
      });
      
      await snapshot.save();
      
      this.logger.debug('Performance snapshot collected successfully');
    } catch (error) {
      this.logger.error('Error collecting performance snapshot:', error);
    }
  }
  
  /**
   * Get current system metrics
   * @returns {Promise<Object>} Current system metrics
   * @private
   */
  async _getCurrentMetrics() {
    try {
      return await this._gatherSystemMetrics();
    } catch (error) {
      this.logger.error('Error getting current metrics:', error);
      throw error;
    }
  }
  
  /**
   * Get historical system metrics
   * @param {string} metricType - Metric type (optional)
   * @param {string} startTime - Start time (optional)
   * @param {string} endTime - End time (optional)
   * @param {string} interval - Aggregation interval (optional)
   * @returns {Promise<Array>} Historical metrics
   * @private
   */
  async _getHistoricalMetrics(metricType, startTime, endTime, interval = 'hour') {
    try {
      const query = {};
      
      if (metricType) {
        query.type = metricType;
      }
      
      if (startTime) {
        query.timestamp = { $gte: new Date(startTime) };
      }
      
      if (endTime) {
        if (!query.timestamp) {
          query.timestamp = {};
        }
        query.timestamp.$lte = new Date(endTime);
      }
      
      // Determine time grouping based on interval
      let timeGroup = {};
      switch (interval) {
        case 'minute':
          timeGroup = {
            year: { $year: '$timestamp' },
            month: { $month: '$timestamp' },
            day: { $dayOfMonth: '$timestamp' },
            hour: { $hour: '$timestamp' },
            minute: { $minute: '$timestamp' }
          };
          break;
        case 'hour':
          timeGroup = {
            year: { $year: '$timestamp' },
            month: { $month: '$timestamp' },
            day: { $dayOfMonth: '$timestamp' },
            hour: { $hour: '$timestamp' }
          };
          break;
        case 'day':
          timeGroup = {
            year: { $year: '$timestamp' },
            month: { $month: '$timestamp' },
            day: { $dayOfMonth: '$timestamp' }
          };
          break;
        default:
          timeGroup = {
            year: { $year: '$timestamp' },
            month: { $month: '$timestamp' },
            day: { $dayOfMonth: '$timestamp' },
            hour: { $hour: '$timestamp' }
          };
      }
      
      const metrics = await SystemMetric.aggregate([
        { $match: query },
        {
          $group: {
            _id: {
              type: '$type',
              ...timeGroup
            },
            avgValue: { $avg: '$value' },
            minValue: { $min: '$value' },
            maxValue: { $max: '$value' },
            count: { $sum: 1 }
          }
        },
        {
          $project: {
            type: '$_id.type',
            year: '$_id.year',
            month: '$_id.month',
            day: '$_id.day',
            hour: '$_id.hour',
            minute: '$_id.minute',
            avgValue: 1,
            minValue: 1,
            maxValue: 1,
            count: 1,
            _id: 0
          }
        },
        { $sort: { type: 1, year: 1, month: 1, day: 1, hour: 1, minute: 1 } }
      ]);
      
      return metrics;
    } catch (error) {
      this.logger.error('Error getting historical metrics:', error);
      throw error;
    }
  }
  
  /**
   * Get active alerts
   * @returns {Promise<Array>} Active alerts
   * @private
   */
  async _getActiveAlerts() {
    try {
      const alerts = await Alert.find({
        status: { $in: ['active', 'acknowledged'] }
      }).sort({ severity: 1, createdAt: -1 });
      
      return alerts;
    } catch (error) {
      this.logger.error('Error getting active alerts:', error);
      throw error;
    }
  }
  
  /**
   * Get alert history
   * @param {string} startTime - Start time (optional)
   * @param {string} endTime - End time (optional)
   * @param {string} severity - Alert severity (optional)
   * @param {number} limit - Maximum number of alerts to return
   * @param {number} skip - Number of alerts to skip
   * @returns {Promise<Object>} Alert history with pagination
   * @private
   */
  async _getAlertHistory(startTime, endTime, severity, limit = 50, skip = 0) {
    try {
      const query = {};
      
      if (startTime) {
        query.createdAt = { $gte: new Date(startTime) };
      }
      
      if (endTime) {
        if (!query.createdAt) {
          query.createdAt = {};
        }
        query.createdAt.$lte = new Date(endTime);
      }
      
      if (severity) {
        query.severity = severity;
      }
      
      const alerts = await Alert.find(query)
        .sort({ createdAt: -1 })
        .skip(skip)
        .limit(limit);
      
      const total = await Alert.countDocuments(query);
      
      return {
        alerts,
        pagination: {
          total,
          limit,
          skip,
          hasMore: total > skip + limit
        }
      };
    } catch (error) {
      this.logger.error('Error getting alert history:', error);
      throw error;
    }
  }
  
  /**
   * Acknowledge alert
   * @param {string} id - Alert ID
   * @param {string} userId - User ID
   * @returns {Promise<Object>} Updated alert
   * @private
   */
  async _acknowledgeAlert(id, userId) {
    try {
      const alert = await Alert.findById(id);
      
      if (!alert) {
        return null;
      }
      
      if (alert.status !== 'active') {
        throw new Error(`Alert is not active (current status: ${alert.status})`);
      }
      
      alert.status = 'acknowledged';
      alert.acknowledgedAt = new Date();
      alert.acknowledgedBy = userId;
      
      await alert.save();
      
      // Emit alert update event for real-time updates
      this.emit('alertUpdate', alert);
      
      return alert;
    } catch (error) {
      this.logger.error(`Error acknowledging alert ${id}:`, error);
      throw error;
    }
  }
  
  /**
   * Resolve alert
   * @param {string} id - Alert ID
   * @param {string} userId - User ID
   * @returns {Promise<Object>} Updated alert
   * @private
   */
  async _resolveAlert(id, userId) {
    try {
      const alert = await Alert.findById(id);
      
      if (!alert) {
        return null;
      }
      
      if (!['active', 'acknowledged'].includes(alert.status)) {
        throw new Error(`Alert cannot be resolved (current status: ${alert.status})`);
      }
      
      alert.status = 'resolved';
      alert.resolvedAt = new Date();
      alert.resolvedBy = userId;
      
      await alert.save();
      
      // Emit alert update event for real-time updates
      this.emit('alertUpdate', alert);
      
      return alert;
    } catch (error) {
      this.logger.error(`Error resolving alert ${id}:`, error);
      throw error;
    }
  }
  
  /**
   * Get alert configurations
   * @returns {Promise<Array>} Alert configurations
   * @private
   */
  async _getAlertConfigs() {
    try {
      const configs = await AlertConfig.find().sort({ severity: 1, name: 1 });
      return configs;
    } catch (error) {
      this.logger.error('Error getting alert configurations:', error);
      throw error;
    }
  }
  
  /**
   * Create alert configuration
   * @param {Object} data - Alert configuration data
   * @returns {Promise<Object>} Created alert configuration
   * @private
   */
  async _createAlertConfig(data) {
    try {
      const config = new AlertConfig({
        ...data,
        enabled: data.enabled !== undefined ? data.enabled : true,
        autoResolve: data.autoResolve !== undefined ? data.autoResolve : true
      });
      
      await config.save();
      
      return config;
    } catch (error) {
      this.logger.error('Error creating alert configuration:', error);
      throw error;
    }
  }
  
  /**
   * Update alert configuration
   * @param {string} id - Alert configuration ID
   * @param {Object} data - Updated alert configuration data
   * @returns {Promise<Object>} Updated alert configuration
   * @private
   */
  async _updateAlertConfig(id, data) {
    try {
      const config = await AlertConfig.findByIdAndUpdate(id, data, { new: true });
      
      if (!config) {
        return null;
      }
      
      return config;
    } catch (error) {
      this.logger.error(`Error updating alert configuration ${id}:`, error);
      throw error;
    }
  }
  
  /**
   * Delete alert configuration
   * @param {string} id - Alert configuration ID
   * @returns {Promise<boolean>} Success status
   * @private
   */
  async _deleteAlertConfig(id) {
    try {
      const config = await AlertConfig.findByIdAndDelete(id);
      
      if (!config) {
        return false;
      }
      
      return true;
    } catch (error) {
      this.logger.error(`Error deleting alert configuration ${id}:`, error);
      throw error;
    }
  }
  
  /**
   * Get performance snapshots
   * @param {string} startTime - Start time (optional)
   * @param {string} endTime - End time (optional)
   * @param {number} limit - Maximum number of snapshots to return
   * @param {number} skip - Number of snapshots to skip
   * @returns {Promise<Object>} Performance snapshots with pagination
   * @private
   */
  async _getPerformanceSnapshots(startTime, endTime, limit = 24, skip = 0) {
    try {
      const query = {};
      
      if (startTime) {
        query.timestamp = { $gte: new Date(startTime) };
      }
      
      if (endTime) {
        if (!query.timestamp) {
          query.timestamp = {};
        }
        query.timestamp.$lte = new Date(endTime);
      }
      
      const snapshots = await PerformanceSnapshot.find(query)
        .sort({ timestamp: -1 })
        .skip(skip)
        .limit(limit);
      
      const total = await PerformanceSnapshot.countDocuments(query);
      
      return {
        snapshots,
        pagination: {
          total,
          limit,
          skip,
          hasMore: total > skip + limit
        }
      };
    } catch (error) {
      this.logger.error('Error getting performance snapshots:', error);
      throw error;
    }
  }
  
  /**
   * Calculate system health score
   * @returns {Promise<Object>} Health score details
   * @private
   */
  async _calculateHealthScore() {
    try {
      // Get current metrics
      const metrics = await this._getCurrentMetrics();
      
      // Get active alerts
      const activeAlerts = await Alert.find({
        status: { $in: ['active', 'acknowledged'] }
      });
      
      // Calculate component scores
      const cpuScore = 100 - Math.min(100, metrics['cpu.usage']);
      const memoryScore = 100 - Math.min(100, metrics['memory.usage']);
      const apiScore = (metrics['api.requests.success'] / Math.max(1, metrics['api.requests.total'])) * 100;
      
      // Calculate alert penalty
      let alertPenalty = 0;
      for (const alert of activeAlerts) {
        switch (alert.severity) {
          case 'critical':
            alertPenalty += 25;
            break;
          case 'error':
            alertPenalty += 15;
            break;
          case 'warning':
            alertPenalty += 5;
            break;
          case 'info':
            alertPenalty += 1;
            break;
        }
      }
      
      // Calculate overall score
      let overallScore = (cpuScore * 0.3) + (memoryScore * 0.3) + (apiScore * 0.4);
      overallScore = Math.max(0, overallScore - alertPenalty);
      
      // Determine status based on score
      let status;
      if (overallScore >= 90) {
        status = 'excellent';
      } else if (overallScore >= 75) {
        status = 'good';
      } else if (overallScore >= 50) {
        status = 'fair';
      } else if (overallScore >= 25) {
        status = 'poor';
      } else {
        status = 'critical';
      }
      
      return {
        score: overallScore,
        status,
        components: {
          cpu: cpuScore,
          memory: memoryScore,
          api: apiScore
        },
        alertPenalty,
        activeAlerts: activeAlerts.length
      };
    } catch (error) {
      this.logger.error('Error calculating health score:', error);
      throw error;
    }
  }
  
  /**
   * Run system health check
   * @returns {Promise<Object>} Health check results
   * @private
   */
  async _runHealthCheck() {
    try {
      // Get current metrics
      const metrics = await this._getCurrentMetrics();
      
      // Check core services
      const coreServices = await this._checkCoreServices();
      
      // Check database connection
      const database = await this._checkDatabase();
      
      // Check external API connections
      const externalApis = await this._checkExternalApis();
      
      // Calculate health score
      const healthScore = await this._calculateHealthScore();
      
      return {
        timestamp: new Date(),
        metrics,
        coreServices,
        database,
        externalApis,
        healthScore
      };
    } catch (error) {
      this.logger.error('Error running health check:', error);
      throw error;
    }
  }
  
  /**
   * Check core services
   * @returns {Promise<Object>} Core services status
   * @private
   */
  async _checkCoreServices() {
    try {
      // This would check the status of core system services
      // For now, we'll return placeholder data
      return {
        apiService: { status: 'ok', responseTime: 5 },
        taskManager: { status: 'ok', responseTime: 8 },
        agentManager: { status: 'ok', responseTime: 12 },
        modelManager: { status: 'ok', responseTime: 15 }
      };
    } catch (error) {
      this.logger.error('Error checking core services:', error);
      return {
        error: error.message
      };
    }
  }
  
  /**
   * Check database connection
   * @returns {Promise<Object>} Database status
   * @private
   */
  async _checkDatabase() {
    try {
      // This would check the database connection and performance
      // For now, we'll return placeholder data
      return {
        status: 'ok',
        responseTime: 3,
        connections: 25,
        size: 256000000 // bytes
      };
    } catch (error) {
      this.logger.error('Error checking database:', error);
      return {
        status: 'error',
        error: error.message
      };
    }
  }
  
  /**
   * Check external API connections
   * @returns {Promise<Object>} External APIs status
   * @private
   */
  async _checkExternalApis() {
    try {
      // This would check connections to external APIs
      // For now, we'll return placeholder data
      return {
        openai: { status: 'ok', responseTime: 250 },
        anthropic: { status: 'ok', responseTime: 320 },
        google: { status: 'ok', responseTime: 180 }
      };
    } catch (error) {
      this.logger.error('Error checking external APIs:', error);
      return {
        error: error.message
      };
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

module.exports = HealthMonitoringService;
