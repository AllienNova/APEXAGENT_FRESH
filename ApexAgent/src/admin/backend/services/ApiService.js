/**
 * API Service for Aideon AI Lite Admin Dashboard
 * 
 * This service provides functionality for managing API credentials, tracking usage,
 * configuring rate limits, and proxying API requests.
 */

const express = require('express');
const router = express.Router();
const crypto = require('crypto');
const { body, validationResult } = require('express-validator');
const { authenticate, authorize } = require('../middleware/auth');

// Database models
const ApiCredential = require('../models/ApiCredential');
const ApiUsage = require('../models/ApiUsage');
const ApiRateLimit = require('../models/ApiRateLimit');

/**
 * API Service class
 */
class ApiService {
  /**
   * Initialize the API Service
   * @param {Object} core - Reference to the AideonCore instance
   */
  constructor(core) {
    this.core = core;
    this.logger = core.logManager.getLogger('api-service');
    this.config = core.configManager.getConfig().apiService || {};
    this.encryptionKey = this.config.encryptionKey || process.env.API_ENCRYPTION_KEY;
    
    if (!this.encryptionKey) {
      throw new Error('API encryption key is required for secure credential storage');
    }
    
    this.router = this._setupRoutes();
    
    this.logger.info('API Service initialized');
  }
  
  /**
   * Set up API routes
   * @returns {Object} Express router
   * @private
   */
  _setupRoutes() {
    // Get all API providers
    router.get('/providers', authenticate, async (req, res) => {
      try {
        const providers = await this._getAllProviders();
        res.json({ success: true, data: providers });
      } catch (error) {
        this.logger.error('Error getting API providers:', error);
        res.status(500).json({ success: false, error: 'Failed to get API providers' });
      }
    });
    
    // Get a specific API provider
    router.get('/providers/:id', authenticate, async (req, res) => {
      try {
        const provider = await this._getProviderById(req.params.id);
        
        if (!provider) {
          return res.status(404).json({ success: false, error: 'API provider not found' });
        }
        
        res.json({ success: true, data: provider });
      } catch (error) {
        this.logger.error(`Error getting API provider ${req.params.id}:`, error);
        res.status(500).json({ success: false, error: 'Failed to get API provider' });
      }
    });
    
    // Create a new API provider
    router.post('/providers', 
      authenticate, 
      authorize(['super_admin', 'admin', 'api_manager']),
      [
        body('name').notEmpty().withMessage('Name is required'),
        body('type').notEmpty().withMessage('Type is required'),
        body('baseUrl').optional(),
        body('credentials').optional(),
        body('isActive').isBoolean().optional(),
        body('rateLimit').optional()
      ],
      async (req, res) => {
        const errors = validationResult(req);
        if (!errors.isEmpty()) {
          return res.status(400).json({ success: false, errors: errors.array() });
        }
        
        try {
          const provider = await this._createProvider(req.body);
          res.status(201).json({ success: true, data: provider });
        } catch (error) {
          this.logger.error('Error creating API provider:', error);
          res.status(500).json({ success: false, error: 'Failed to create API provider' });
        }
      }
    );
    
    // Update an API provider
    router.put('/providers/:id', 
      authenticate, 
      authorize(['super_admin', 'admin', 'api_manager']),
      [
        body('name').optional(),
        body('type').optional(),
        body('baseUrl').optional(),
        body('credentials').optional(),
        body('isActive').isBoolean().optional(),
        body('rateLimit').optional()
      ],
      async (req, res) => {
        const errors = validationResult(req);
        if (!errors.isEmpty()) {
          return res.status(400).json({ success: false, errors: errors.array() });
        }
        
        try {
          const provider = await this._updateProvider(req.params.id, req.body);
          
          if (!provider) {
            return res.status(404).json({ success: false, error: 'API provider not found' });
          }
          
          res.json({ success: true, data: provider });
        } catch (error) {
          this.logger.error(`Error updating API provider ${req.params.id}:`, error);
          res.status(500).json({ success: false, error: 'Failed to update API provider' });
        }
      }
    );
    
    // Delete an API provider
    router.delete('/providers/:id', 
      authenticate, 
      authorize(['super_admin', 'admin']),
      async (req, res) => {
        try {
          const result = await this._deleteProvider(req.params.id);
          
          if (!result) {
            return res.status(404).json({ success: false, error: 'API provider not found' });
          }
          
          res.json({ success: true, message: 'API provider deleted successfully' });
        } catch (error) {
          this.logger.error(`Error deleting API provider ${req.params.id}:`, error);
          res.status(500).json({ success: false, error: 'Failed to delete API provider' });
        }
      }
    );
    
    // Get API usage statistics
    router.get('/usage', authenticate, async (req, res) => {
      try {
        const { providerId, startDate, endDate, interval } = req.query;
        const usage = await this._getApiUsage(providerId, startDate, endDate, interval);
        res.json({ success: true, data: usage });
      } catch (error) {
        this.logger.error('Error getting API usage:', error);
        res.status(500).json({ success: false, error: 'Failed to get API usage' });
      }
    });
    
    // Get API rate limits
    router.get('/rate-limits', authenticate, async (req, res) => {
      try {
        const rateLimits = await this._getRateLimits(req.query.providerId);
        res.json({ success: true, data: rateLimits });
      } catch (error) {
        this.logger.error('Error getting API rate limits:', error);
        res.status(500).json({ success: false, error: 'Failed to get API rate limits' });
      }
    });
    
    // Update API rate limits
    router.put('/rate-limits/:id', 
      authenticate, 
      authorize(['super_admin', 'admin', 'api_manager']),
      [
        body('requestsPerMinute').isInt().optional(),
        body('requestsPerHour').isInt().optional(),
        body('requestsPerDay').isInt().optional(),
        body('concurrentRequests').isInt().optional()
      ],
      async (req, res) => {
        const errors = validationResult(req);
        if (!errors.isEmpty()) {
          return res.status(400).json({ success: false, errors: errors.array() });
        }
        
        try {
          const rateLimit = await this._updateRateLimit(req.params.id, req.body);
          
          if (!rateLimit) {
            return res.status(404).json({ success: false, error: 'Rate limit not found' });
          }
          
          res.json({ success: true, data: rateLimit });
        } catch (error) {
          this.logger.error(`Error updating rate limit ${req.params.id}:`, error);
          res.status(500).json({ success: false, error: 'Failed to update rate limit' });
        }
      }
    );
    
    // Test API connection
    router.post('/test-connection', 
      authenticate, 
      authorize(['super_admin', 'admin', 'api_manager']),
      [
        body('providerId').notEmpty().withMessage('Provider ID is required')
      ],
      async (req, res) => {
        const errors = validationResult(req);
        if (!errors.isEmpty()) {
          return res.status(400).json({ success: false, errors: errors.array() });
        }
        
        try {
          const result = await this._testApiConnection(req.body.providerId);
          res.json({ success: true, data: result });
        } catch (error) {
          this.logger.error(`Error testing API connection for provider ${req.body.providerId}:`, error);
          res.status(500).json({ success: false, error: 'Failed to test API connection', details: error.message });
        }
      }
    );
    
    return router;
  }
  
  /**
   * Get all API providers
   * @returns {Promise<Array>} List of API providers
   * @private
   */
  async _getAllProviders() {
    try {
      const providers = await ApiCredential.find().select('-credentials');
      return providers;
    } catch (error) {
      this.logger.error('Error getting all providers:', error);
      throw error;
    }
  }
  
  /**
   * Get API provider by ID
   * @param {string} id - Provider ID
   * @returns {Promise<Object>} API provider
   * @private
   */
  async _getProviderById(id) {
    try {
      const provider = await ApiCredential.findById(id);
      
      if (!provider) {
        return null;
      }
      
      // Don't return raw credentials
      const result = provider.toObject();
      delete result.credentials;
      
      return result;
    } catch (error) {
      this.logger.error(`Error getting provider ${id}:`, error);
      throw error;
    }
  }
  
  /**
   * Create a new API provider
   * @param {Object} data - Provider data
   * @returns {Promise<Object>} Created provider
   * @private
   */
  async _createProvider(data) {
    try {
      // Encrypt credentials if provided
      if (data.credentials) {
        data.credentials = this._encryptCredentials(data.credentials);
      }
      
      const provider = new ApiCredential(data);
      await provider.save();
      
      // Create default rate limit if not provided
      if (!data.rateLimit) {
        const defaultRateLimit = {
          providerId: provider._id,
          requestsPerMinute: 60,
          requestsPerHour: 3600,
          requestsPerDay: 86400,
          concurrentRequests: 10
        };
        
        const rateLimit = new ApiRateLimit(defaultRateLimit);
        await rateLimit.save();
      }
      
      // Don't return raw credentials
      const result = provider.toObject();
      delete result.credentials;
      
      return result;
    } catch (error) {
      this.logger.error('Error creating provider:', error);
      throw error;
    }
  }
  
  /**
   * Update an API provider
   * @param {string} id - Provider ID
   * @param {Object} data - Updated provider data
   * @returns {Promise<Object>} Updated provider
   * @private
   */
  async _updateProvider(id, data) {
    try {
      // Encrypt credentials if provided
      if (data.credentials) {
        data.credentials = this._encryptCredentials(data.credentials);
      }
      
      const provider = await ApiCredential.findByIdAndUpdate(id, data, { new: true });
      
      if (!provider) {
        return null;
      }
      
      // Update rate limit if provided
      if (data.rateLimit) {
        await ApiRateLimit.findOneAndUpdate({ providerId: id }, data.rateLimit, { new: true, upsert: true });
      }
      
      // Don't return raw credentials
      const result = provider.toObject();
      delete result.credentials;
      
      return result;
    } catch (error) {
      this.logger.error(`Error updating provider ${id}:`, error);
      throw error;
    }
  }
  
  /**
   * Delete an API provider
   * @param {string} id - Provider ID
   * @returns {Promise<boolean>} Success status
   * @private
   */
  async _deleteProvider(id) {
    try {
      const provider = await ApiCredential.findByIdAndDelete(id);
      
      if (!provider) {
        return false;
      }
      
      // Delete related rate limits
      await ApiRateLimit.deleteMany({ providerId: id });
      
      // Note: We keep usage history for reporting purposes
      
      return true;
    } catch (error) {
      this.logger.error(`Error deleting provider ${id}:`, error);
      throw error;
    }
  }
  
  /**
   * Get API usage statistics
   * @param {string} providerId - Provider ID (optional)
   * @param {string} startDate - Start date (optional)
   * @param {string} endDate - End date (optional)
   * @param {string} interval - Interval for aggregation (optional)
   * @returns {Promise<Object>} Usage statistics
   * @private
   */
  async _getApiUsage(providerId, startDate, endDate, interval = 'day') {
    try {
      const query = {};
      
      if (providerId) {
        query.providerId = providerId;
      }
      
      if (startDate) {
        query.timestamp = { $gte: new Date(startDate) };
      }
      
      if (endDate) {
        if (!query.timestamp) {
          query.timestamp = {};
        }
        query.timestamp.$lte = new Date(endDate);
      }
      
      // Determine grouping based on interval
      let groupBy = {};
      switch (interval) {
        case 'hour':
          groupBy = {
            year: { $year: '$timestamp' },
            month: { $month: '$timestamp' },
            day: { $dayOfMonth: '$timestamp' },
            hour: { $hour: '$timestamp' }
          };
          break;
        case 'day':
          groupBy = {
            year: { $year: '$timestamp' },
            month: { $month: '$timestamp' },
            day: { $dayOfMonth: '$timestamp' }
          };
          break;
        case 'month':
          groupBy = {
            year: { $year: '$timestamp' },
            month: { $month: '$timestamp' }
          };
          break;
        default:
          groupBy = {
            year: { $year: '$timestamp' },
            month: { $month: '$timestamp' },
            day: { $dayOfMonth: '$timestamp' }
          };
      }
      
      const usage = await ApiUsage.aggregate([
        { $match: query },
        {
          $group: {
            _id: {
              providerId: '$providerId',
              ...groupBy
            },
            count: { $sum: 1 },
            successCount: { $sum: { $cond: [{ $eq: ['$success', true] }, 1, 0] } },
            errorCount: { $sum: { $cond: [{ $eq: ['$success', false] }, 1, 0] } },
            totalLatency: { $sum: '$latency' },
            totalCost: { $sum: '$cost' }
          }
        },
        {
          $project: {
            providerId: '$_id.providerId',
            year: '$_id.year',
            month: '$_id.month',
            day: '$_id.day',
            hour: '$_id.hour',
            count: 1,
            successCount: 1,
            errorCount: 1,
            averageLatency: { $divide: ['$totalLatency', '$count'] },
            totalCost: 1,
            _id: 0
          }
        },
        { $sort: { year: 1, month: 1, day: 1, hour: 1 } }
      ]);
      
      // Get provider details for each usage entry
      const providers = await ApiCredential.find().select('_id name type');
      const providerMap = {};
      providers.forEach(provider => {
        providerMap[provider._id] = {
          name: provider.name,
          type: provider.type
        };
      });
      
      // Enhance usage data with provider details
      usage.forEach(entry => {
        if (providerMap[entry.providerId]) {
          entry.providerName = providerMap[entry.providerId].name;
          entry.providerType = providerMap[entry.providerId].type;
        }
      });
      
      return usage;
    } catch (error) {
      this.logger.error('Error getting API usage:', error);
      throw error;
    }
  }
  
  /**
   * Get API rate limits
   * @param {string} providerId - Provider ID (optional)
   * @returns {Promise<Array>} Rate limits
   * @private
   */
  async _getRateLimits(providerId) {
    try {
      const query = {};
      
      if (providerId) {
        query.providerId = providerId;
      }
      
      const rateLimits = await ApiRateLimit.find(query);
      
      // Get provider details for each rate limit
      const providers = await ApiCredential.find().select('_id name type');
      const providerMap = {};
      providers.forEach(provider => {
        providerMap[provider._id] = {
          name: provider.name,
          type: provider.type
        };
      });
      
      // Enhance rate limit data with provider details
      const enhancedRateLimits = rateLimits.map(rateLimit => {
        const result = rateLimit.toObject();
        if (providerMap[result.providerId]) {
          result.providerName = providerMap[result.providerId].name;
          result.providerType = providerMap[result.providerId].type;
        }
        return result;
      });
      
      return enhancedRateLimits;
    } catch (error) {
      this.logger.error('Error getting API rate limits:', error);
      throw error;
    }
  }
  
  /**
   * Update API rate limit
   * @param {string} id - Rate limit ID
   * @param {Object} data - Updated rate limit data
   * @returns {Promise<Object>} Updated rate limit
   * @private
   */
  async _updateRateLimit(id, data) {
    try {
      const rateLimit = await ApiRateLimit.findByIdAndUpdate(id, data, { new: true });
      
      if (!rateLimit) {
        return null;
      }
      
      return rateLimit;
    } catch (error) {
      this.logger.error(`Error updating rate limit ${id}:`, error);
      throw error;
    }
  }
  
  /**
   * Test API connection
   * @param {string} providerId - Provider ID
   * @returns {Promise<Object>} Test result
   * @private
   */
  async _testApiConnection(providerId) {
    try {
      const provider = await ApiCredential.findById(providerId);
      
      if (!provider) {
        throw new Error('API provider not found');
      }
      
      // Decrypt credentials
      const credentials = this._decryptCredentials(provider.credentials);
      
      // Test connection based on provider type
      let result;
      switch (provider.type) {
        case 'openai':
          result = await this._testOpenAIConnection(provider.baseUrl, credentials);
          break;
        case 'anthropic':
          result = await this._testAnthropicConnection(provider.baseUrl, credentials);
          break;
        case 'google':
          result = await this._testGoogleConnection(provider.baseUrl, credentials);
          break;
        default:
          result = await this._testGenericConnection(provider.baseUrl, credentials);
      }
      
      return result;
    } catch (error) {
      this.logger.error(`Error testing API connection for provider ${providerId}:`, error);
      throw error;
    }
  }
  
  /**
   * Test OpenAI API connection
   * @param {string} baseUrl - Base URL
   * @param {Object} credentials - API credentials
   * @returns {Promise<Object>} Test result
   * @private
   */
  async _testOpenAIConnection(baseUrl, credentials) {
    try {
      const axios = require('axios');
      
      const url = baseUrl || 'https://api.openai.com/v1';
      const response = await axios.get(`${url}/models`, {
        headers: {
          'Authorization': `Bearer ${credentials.apiKey}`,
          'Content-Type': 'application/json'
        }
      });
      
      return {
        success: true,
        statusCode: response.status,
        models: response.data.data.length,
        message: 'Successfully connected to OpenAI API'
      };
    } catch (error) {
      return {
        success: false,
        statusCode: error.response?.status || 500,
        message: error.response?.data?.error?.message || error.message
      };
    }
  }
  
  /**
   * Test Anthropic API connection
   * @param {string} baseUrl - Base URL
   * @param {Object} credentials - API credentials
   * @returns {Promise<Object>} Test result
   * @private
   */
  async _testAnthropicConnection(baseUrl, credentials) {
    try {
      const axios = require('axios');
      
      const url = baseUrl || 'https://api.anthropic.com/v1';
      const response = await axios.post(`${url}/messages`, {
        model: 'claude-3-haiku-20240307',
        max_tokens: 10,
        messages: [{ role: 'user', content: 'Hello' }]
      }, {
        headers: {
          'x-api-key': credentials.apiKey,
          'anthropic-version': '2023-06-01',
          'Content-Type': 'application/json'
        }
      });
      
      return {
        success: true,
        statusCode: response.status,
        message: 'Successfully connected to Anthropic API'
      };
    } catch (error) {
      return {
        success: false,
        statusCode: error.response?.status || 500,
        message: error.response?.data?.error?.message || error.message
      };
    }
  }
  
  /**
   * Test Google API connection
   * @param {string} baseUrl - Base URL
   * @param {Object} credentials - API credentials
   * @returns {Promise<Object>} Test result
   * @private
   */
  async _testGoogleConnection(baseUrl, credentials) {
    try {
      const axios = require('axios');
      
      // Test with a simple search query
      const url = 'https://www.googleapis.com/customsearch/v1';
      const response = await axios.get(url, {
        params: {
          key: credentials.apiKey,
          cx: credentials.searchEngineId,
          q: 'test'
        }
      });
      
      return {
        success: true,
        statusCode: response.status,
        results: response.data.searchInformation.totalResults,
        message: 'Successfully connected to Google API'
      };
    } catch (error) {
      return {
        success: false,
        statusCode: error.response?.status || 500,
        message: error.response?.data?.error?.message || error.message
      };
    }
  }
  
  /**
   * Test generic API connection
   * @param {string} baseUrl - Base URL
   * @param {Object} credentials - API credentials
   * @returns {Promise<Object>} Test result
   * @private
   */
  async _testGenericConnection(baseUrl, credentials) {
    try {
      const axios = require('axios');
      
      if (!baseUrl) {
        throw new Error('Base URL is required for generic API connection test');
      }
      
      // Determine authentication method based on available credentials
      let headers = {};
      
      if (credentials.apiKey) {
        headers['Authorization'] = `Bearer ${credentials.apiKey}`;
      } else if (credentials.username && credentials.password) {
        const auth = Buffer.from(`${credentials.username}:${credentials.password}`).toString('base64');
        headers['Authorization'] = `Basic ${auth}`;
      }
      
      const response = await axios.get(baseUrl, { headers });
      
      return {
        success: true,
        statusCode: response.status,
        message: 'Successfully connected to API'
      };
    } catch (error) {
      return {
        success: false,
        statusCode: error.response?.status || 500,
        message: error.response?.data?.error?.message || error.message
      };
    }
  }
  
  /**
   * Encrypt API credentials
   * @param {Object} credentials - API credentials
   * @returns {string} Encrypted credentials
   * @private
   */
  _encryptCredentials(credentials) {
    try {
      const iv = crypto.randomBytes(16);
      const cipher = crypto.createCipheriv('aes-256-gcm', Buffer.from(this.encryptionKey, 'hex'), iv);
      
      let encrypted = cipher.update(JSON.stringify(credentials), 'utf8', 'hex');
      encrypted += cipher.final('hex');
      
      const authTag = cipher.getAuthTag().toString('hex');
      
      return {
        iv: iv.toString('hex'),
        encrypted,
        authTag
      };
    } catch (error) {
      this.logger.error('Error encrypting credentials:', error);
      throw new Error('Failed to encrypt API credentials');
    }
  }
  
  /**
   * Decrypt API credentials
   * @param {Object} encryptedData - Encrypted credentials data
   * @returns {Object} Decrypted credentials
   * @private
   */
  _decryptCredentials(encryptedData) {
    try {
      const { iv, encrypted, authTag } = encryptedData;
      
      const decipher = crypto.createDecipheriv(
        'aes-256-gcm',
        Buffer.from(this.encryptionKey, 'hex'),
        Buffer.from(iv, 'hex')
      );
      
      decipher.setAuthTag(Buffer.from(authTag, 'hex'));
      
      let decrypted = decipher.update(encrypted, 'hex', 'utf8');
      decrypted += decipher.final('utf8');
      
      return JSON.parse(decrypted);
    } catch (error) {
      this.logger.error('Error decrypting credentials:', error);
      throw new Error('Failed to decrypt API credentials');
    }
  }
  
  /**
   * Record API usage
   * @param {string} providerId - Provider ID
   * @param {string} endpoint - API endpoint
   * @param {boolean} success - Success status
   * @param {number} latency - Request latency in ms
   * @param {number} cost - Request cost
   * @returns {Promise<void>}
   */
  async recordApiUsage(providerId, endpoint, success, latency, cost = 0) {
    try {
      const usage = new ApiUsage({
        providerId,
        endpoint,
        success,
        latency,
        cost,
        timestamp: new Date()
      });
      
      await usage.save();
    } catch (error) {
      this.logger.error('Error recording API usage:', error);
      // Don't throw, just log the error
    }
  }
  
  /**
   * Get API router
   * @returns {Object} Express router
   */
  getRouter() {
    return this.router;
  }
  
  /**
   * Get API credentials
   * @param {string} providerId - Provider ID
   * @returns {Promise<Object>} API credentials
   */
  async getApiCredentials(providerId) {
    try {
      const provider = await ApiCredential.findById(providerId);
      
      if (!provider) {
        throw new Error('API provider not found');
      }
      
      return this._decryptCredentials(provider.credentials);
    } catch (error) {
      this.logger.error(`Error getting API credentials for provider ${providerId}:`, error);
      throw error;
    }
  }
  
  /**
   * Check rate limit
   * @param {string} providerId - Provider ID
   * @returns {Promise<boolean>} Whether request is allowed
   */
  async checkRateLimit(providerId) {
    try {
      const rateLimit = await ApiRateLimit.findOne({ providerId });
      
      if (!rateLimit) {
        // No rate limit defined, allow the request
        return true;
      }
      
      // Get current usage counts
      const now = new Date();
      const minuteAgo = new Date(now.getTime() - 60000);
      const hourAgo = new Date(now.getTime() - 3600000);
      const dayAgo = new Date(now.getTime() - 86400000);
      
      const [minuteCount, hourCount, dayCount, concurrentCount] = await Promise.all([
        ApiUsage.countDocuments({
          providerId,
          timestamp: { $gte: minuteAgo }
        }),
        ApiUsage.countDocuments({
          providerId,
          timestamp: { $gte: hourAgo }
        }),
        ApiUsage.countDocuments({
          providerId,
          timestamp: { $gte: dayAgo }
        }),
        ApiUsage.countDocuments({
          providerId,
          completed: false
        })
      ]);
      
      // Check if any limits are exceeded
      if (
        (rateLimit.requestsPerMinute && minuteCount >= rateLimit.requestsPerMinute) ||
        (rateLimit.requestsPerHour && hourCount >= rateLimit.requestsPerHour) ||
        (rateLimit.requestsPerDay && dayCount >= rateLimit.requestsPerDay) ||
        (rateLimit.concurrentRequests && concurrentCount >= rateLimit.concurrentRequests)
      ) {
        return false;
      }
      
      return true;
    } catch (error) {
      this.logger.error(`Error checking rate limit for provider ${providerId}:`, error);
      // In case of error, allow the request
      return true;
    }
  }
}

module.exports = ApiService;
