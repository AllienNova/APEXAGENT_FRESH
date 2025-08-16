/**
 * Admin Dashboard Validation Module for Aideon AI Lite
 * 
 * This module provides comprehensive validation and testing for the admin dashboard,
 * ensuring all components work correctly and meet performance requirements.
 */

const axios = require('axios');
const { performance } = require('perf_hooks');

/**
 * Admin Dashboard Validation class
 */
class AdminDashboardValidation {
  /**
   * Initialize the Admin Dashboard Validation
   * @param {Object} core - Reference to the AideonCore instance
   * @param {Object} options - Configuration options
   */
  constructor(core, options = {}) {
    this.core = core;
    this.logger = core.logManager.getLogger('admin-dashboard-validation');
    this.config = core.configManager.getConfig().adminDashboard || {};
    
    this.options = {
      baseUrl: options.baseUrl || `http://localhost:${this.config.port || 3000}`,
      apiPrefix: options.apiPrefix || this.config.apiPrefix || '/api/admin',
      adminCredentials: options.adminCredentials || {
        username: 'admin',
        password: 'admin123'
      },
      testTimeout: options.testTimeout || 30000 // 30 seconds
    };
    
    this.authToken = null;
    
    this.logger.info('Admin Dashboard Validation initialized');
  }
  
  /**
   * Run all validation tests
   * @returns {Promise<Object>} Validation results
   */
  async validateAll() {
    try {
      this.logger.info('Starting admin dashboard validation');
      
      const startTime = performance.now();
      
      // Authenticate
      await this._authenticate();
      
      // Run all validation tests
      const results = {
        auth: await this._validateAuth(),
        apiManagement: await this._validateApiManagement(),
        appManagement: await this._validateAppManagement(),
        healthMonitoring: await this._validateHealthMonitoring(),
        userManagement: await this._validateUserManagement(),
        performance: await this._validatePerformance(),
        security: await this._validateSecurity(),
        ui: await this._validateUI()
      };
      
      const endTime = performance.now();
      const duration = (endTime - startTime) / 1000;
      
      // Calculate overall status
      const overallStatus = this._calculateOverallStatus(results);
      
      const summary = {
        status: overallStatus.status,
        passRate: overallStatus.passRate,
        duration,
        timestamp: new Date(),
        results
      };
      
      this.logger.info(`Admin dashboard validation completed with status: ${overallStatus.status}`);
      
      return summary;
    } catch (error) {
      this.logger.error('Error during admin dashboard validation:', error);
      throw error;
    }
  }
  
  /**
   * Authenticate with the admin dashboard
   * @private
   */
  async _authenticate() {
    try {
      const response = await axios.post(`${this.options.baseUrl}${this.options.apiPrefix}/auth/login`, {
        username: this.options.adminCredentials.username,
        password: this.options.adminCredentials.password
      });
      
      if (response.data && response.data.success && response.data.data.token) {
        this.authToken = response.data.data.token;
        this.logger.debug('Authentication successful');
      } else {
        throw new Error('Authentication failed: Invalid response format');
      }
    } catch (error) {
      this.logger.error('Authentication failed:', error);
      throw new Error(`Authentication failed: ${error.message}`);
    }
  }
  
  /**
   * Validate authentication functionality
   * @returns {Promise<Object>} Validation results
   * @private
   */
  async _validateAuth() {
    const results = {
      tests: [],
      passed: 0,
      failed: 0,
      status: 'pending'
    };
    
    try {
      // Test login with valid credentials
      try {
        const response = await axios.post(`${this.options.baseUrl}${this.options.apiPrefix}/auth/login`, {
          username: this.options.adminCredentials.username,
          password: this.options.adminCredentials.password
        });
        
        results.tests.push({
          name: 'Login with valid credentials',
          status: response.data && response.data.success ? 'passed' : 'failed',
          details: response.data && response.data.success ? 'Successfully logged in' : 'Failed to log in'
        });
        
        if (response.data && response.data.success) {
          results.passed++;
        } else {
          results.failed++;
        }
      } catch (error) {
        results.tests.push({
          name: 'Login with valid credentials',
          status: 'failed',
          details: `Error: ${error.message}`
        });
        results.failed++;
      }
      
      // Test login with invalid credentials
      try {
        const response = await axios.post(`${this.options.baseUrl}${this.options.apiPrefix}/auth/login`, {
          username: 'invalid',
          password: 'invalid'
        });
        
        results.tests.push({
          name: 'Login with invalid credentials',
          status: !response.data.success ? 'passed' : 'failed',
          details: !response.data.success ? 'Correctly rejected invalid credentials' : 'Incorrectly accepted invalid credentials'
        });
        
        if (!response.data.success) {
          results.passed++;
        } else {
          results.failed++;
        }
      } catch (error) {
        if (error.response && error.response.status === 401) {
          results.tests.push({
            name: 'Login with invalid credentials',
            status: 'passed',
            details: 'Correctly rejected invalid credentials'
          });
          results.passed++;
        } else {
          results.tests.push({
            name: 'Login with invalid credentials',
            status: 'failed',
            details: `Error: ${error.message}`
          });
          results.failed++;
        }
      }
      
      // Test token validation
      try {
        const response = await axios.get(`${this.options.baseUrl}${this.options.apiPrefix}/auth/validate`, {
          headers: {
            Authorization: `Bearer ${this.authToken}`
          }
        });
        
        results.tests.push({
          name: 'Token validation',
          status: response.data && response.data.success ? 'passed' : 'failed',
          details: response.data && response.data.success ? 'Successfully validated token' : 'Failed to validate token'
        });
        
        if (response.data && response.data.success) {
          results.passed++;
        } else {
          results.failed++;
        }
      } catch (error) {
        results.tests.push({
          name: 'Token validation',
          status: 'failed',
          details: `Error: ${error.message}`
        });
        results.failed++;
      }
      
      // Test token refresh
      try {
        const response = await axios.post(`${this.options.baseUrl}${this.options.apiPrefix}/auth/refresh`, {}, {
          headers: {
            Authorization: `Bearer ${this.authToken}`
          }
        });
        
        results.tests.push({
          name: 'Token refresh',
          status: response.data && response.data.success && response.data.data.token ? 'passed' : 'failed',
          details: response.data && response.data.success && response.data.data.token ? 'Successfully refreshed token' : 'Failed to refresh token'
        });
        
        if (response.data && response.data.success && response.data.data.token) {
          this.authToken = response.data.data.token;
          results.passed++;
        } else {
          results.failed++;
        }
      } catch (error) {
        results.tests.push({
          name: 'Token refresh',
          status: 'failed',
          details: `Error: ${error.message}`
        });
        results.failed++;
      }
      
      // Test logout
      try {
        const response = await axios.post(`${this.options.baseUrl}${this.options.apiPrefix}/auth/logout`, {}, {
          headers: {
            Authorization: `Bearer ${this.authToken}`
          }
        });
        
        results.tests.push({
          name: 'Logout',
          status: response.data && response.data.success ? 'passed' : 'failed',
          details: response.data && response.data.success ? 'Successfully logged out' : 'Failed to log out'
        });
        
        if (response.data && response.data.success) {
          results.passed++;
        } else {
          results.failed++;
        }
        
        // Re-authenticate for subsequent tests
        await this._authenticate();
      } catch (error) {
        results.tests.push({
          name: 'Logout',
          status: 'failed',
          details: `Error: ${error.message}`
        });
        results.failed++;
        
        // Re-authenticate for subsequent tests
        await this._authenticate();
      }
      
      // Calculate status
      results.status = results.failed === 0 ? 'passed' : results.passed === 0 ? 'failed' : 'partial';
      
      return results;
    } catch (error) {
      this.logger.error('Error validating authentication:', error);
      
      results.status = 'error';
      results.error = error.message;
      
      return results;
    }
  }
  
  /**
   * Validate API management functionality
   * @returns {Promise<Object>} Validation results
   * @private
   */
  async _validateApiManagement() {
    const results = {
      tests: [],
      passed: 0,
      failed: 0,
      status: 'pending'
    };
    
    try {
      // Test getting API providers
      try {
        const response = await axios.get(`${this.options.baseUrl}${this.options.apiPrefix}/api-management/providers`, {
          headers: {
            Authorization: `Bearer ${this.authToken}`
          }
        });
        
        results.tests.push({
          name: 'Get API providers',
          status: response.data && response.data.success ? 'passed' : 'failed',
          details: response.data && response.data.success ? 'Successfully retrieved API providers' : 'Failed to retrieve API providers'
        });
        
        if (response.data && response.data.success) {
          results.passed++;
        } else {
          results.failed++;
        }
      } catch (error) {
        results.tests.push({
          name: 'Get API providers',
          status: 'failed',
          details: `Error: ${error.message}`
        });
        results.failed++;
      }
      
      // Test getting API credentials
      try {
        const response = await axios.get(`${this.options.baseUrl}${this.options.apiPrefix}/api-management/credentials`, {
          headers: {
            Authorization: `Bearer ${this.authToken}`
          }
        });
        
        results.tests.push({
          name: 'Get API credentials',
          status: response.data && response.data.success ? 'passed' : 'failed',
          details: response.data && response.data.success ? 'Successfully retrieved API credentials' : 'Failed to retrieve API credentials'
        });
        
        if (response.data && response.data.success) {
          results.passed++;
        } else {
          results.failed++;
        }
      } catch (error) {
        results.tests.push({
          name: 'Get API credentials',
          status: 'failed',
          details: `Error: ${error.message}`
        });
        results.failed++;
      }
      
      // Test creating API credential
      let createdCredentialId = null;
      try {
        const response = await axios.post(`${this.options.baseUrl}${this.options.apiPrefix}/api-management/credentials`, {
          provider: 'test-provider',
          name: 'Test Credential',
          apiKey: 'test-api-key',
          isActive: true
        }, {
          headers: {
            Authorization: `Bearer ${this.authToken}`
          }
        });
        
        results.tests.push({
          name: 'Create API credential',
          status: response.data && response.data.success ? 'passed' : 'failed',
          details: response.data && response.data.success ? 'Successfully created API credential' : 'Failed to create API credential'
        });
        
        if (response.data && response.data.success) {
          createdCredentialId = response.data.data._id;
          results.passed++;
        } else {
          results.failed++;
        }
      } catch (error) {
        results.tests.push({
          name: 'Create API credential',
          status: 'failed',
          details: `Error: ${error.message}`
        });
        results.failed++;
      }
      
      // Test updating API credential
      if (createdCredentialId) {
        try {
          const response = await axios.put(`${this.options.baseUrl}${this.options.apiPrefix}/api-management/credentials/${createdCredentialId}`, {
            name: 'Updated Test Credential',
            isActive: false
          }, {
            headers: {
              Authorization: `Bearer ${this.authToken}`
            }
          });
          
          results.tests.push({
            name: 'Update API credential',
            status: response.data && response.data.success ? 'passed' : 'failed',
            details: response.data && response.data.success ? 'Successfully updated API credential' : 'Failed to update API credential'
          });
          
          if (response.data && response.data.success) {
            results.passed++;
          } else {
            results.failed++;
          }
        } catch (error) {
          results.tests.push({
            name: 'Update API credential',
            status: 'failed',
            details: `Error: ${error.message}`
          });
          results.failed++;
        }
      }
      
      // Test deleting API credential
      if (createdCredentialId) {
        try {
          const response = await axios.delete(`${this.options.baseUrl}${this.options.apiPrefix}/api-management/credentials/${createdCredentialId}`, {
            headers: {
              Authorization: `Bearer ${this.authToken}`
            }
          });
          
          results.tests.push({
            name: 'Delete API credential',
            status: response.data && response.data.success ? 'passed' : 'failed',
            details: response.data && response.data.success ? 'Successfully deleted API credential' : 'Failed to delete API credential'
          });
          
          if (response.data && response.data.success) {
            results.passed++;
          } else {
            results.failed++;
          }
        } catch (error) {
          results.tests.push({
            name: 'Delete API credential',
            status: 'failed',
            details: `Error: ${error.message}`
          });
          results.failed++;
        }
      }
      
      // Test getting API usage
      try {
        const response = await axios.get(`${this.options.baseUrl}${this.options.apiPrefix}/api-management/usage`, {
          headers: {
            Authorization: `Bearer ${this.authToken}`
          }
        });
        
        results.tests.push({
          name: 'Get API usage',
          status: response.data && response.data.success ? 'passed' : 'failed',
          details: response.data && response.data.success ? 'Successfully retrieved API usage' : 'Failed to retrieve API usage'
        });
        
        if (response.data && response.data.success) {
          results.passed++;
        } else {
          results.failed++;
        }
      } catch (error) {
        results.tests.push({
          name: 'Get API usage',
          status: 'failed',
          details: `Error: ${error.message}`
        });
        results.failed++;
      }
      
      // Calculate status
      results.status = results.failed === 0 ? 'passed' : results.passed === 0 ? 'failed' : 'partial';
      
      return results;
    } catch (error) {
      this.logger.error('Error validating API management:', error);
      
      results.status = 'error';
      results.error = error.message;
      
      return results;
    }
  }
  
  /**
   * Validate app management functionality
   * @returns {Promise<Object>} Validation results
   * @private
   */
  async _validateAppManagement() {
    const results = {
      tests: [],
      passed: 0,
      failed: 0,
      status: 'pending'
    };
    
    try {
      // Test getting system info
      try {
        const response = await axios.get(`${this.options.baseUrl}${this.options.apiPrefix}/app-management/system-info`, {
          headers: {
            Authorization: `Bearer ${this.authToken}`
          }
        });
        
        results.tests.push({
          name: 'Get system info',
          status: response.data && response.data.success ? 'passed' : 'failed',
          details: response.data && response.data.success ? 'Successfully retrieved system info' : 'Failed to retrieve system info'
        });
        
        if (response.data && response.data.success) {
          results.passed++;
        } else {
          results.failed++;
        }
      } catch (error) {
        results.tests.push({
          name: 'Get system info',
          status: 'failed',
          details: `Error: ${error.message}`
        });
        results.failed++;
      }
      
      // Test getting app config
      try {
        const response = await axios.get(`${this.options.baseUrl}${this.options.apiPrefix}/app-management/config`, {
          headers: {
            Authorization: `Bearer ${this.authToken}`
          }
        });
        
        results.tests.push({
          name: 'Get app config',
          status: response.data && response.data.success ? 'passed' : 'failed',
          details: response.data && response.data.success ? 'Successfully retrieved app config' : 'Failed to retrieve app config'
        });
        
        if (response.data && response.data.success) {
          results.passed++;
        } else {
          results.failed++;
        }
      } catch (error) {
        results.tests.push({
          name: 'Get app config',
          status: 'failed',
          details: `Error: ${error.message}`
        });
        results.failed++;
      }
      
      // Test creating app config
      let createdConfigId = null;
      try {
        const response = await axios.post(`${this.options.baseUrl}${this.options.apiPrefix}/app-management/config`, {
          key: 'test.config',
          value: 'test-value',
          description: 'Test configuration',
          category: 'test'
        }, {
          headers: {
            Authorization: `Bearer ${this.authToken}`
          }
        });
        
        results.tests.push({
          name: 'Create app config',
          status: response.data && response.data.success ? 'passed' : 'failed',
          details: response.data && response.data.success ? 'Successfully created app config' : 'Failed to create app config'
        });
        
        if (response.data && response.data.success) {
          createdConfigId = response.data.data._id;
          results.passed++;
        } else {
          results.failed++;
        }
      } catch (error) {
        results.tests.push({
          name: 'Create app config',
          status: 'failed',
          details: `Error: ${error.message}`
        });
        results.failed++;
      }
      
      // Test updating app config
      if (createdConfigId) {
        try {
          const response = await axios.put(`${this.options.baseUrl}${this.options.apiPrefix}/app-management/config/${createdConfigId}`, {
            value: 'updated-test-value',
            description: 'Updated test configuration'
          }, {
            headers: {
              Authorization: `Bearer ${this.authToken}`
            }
          });
          
          results.tests.push({
            name: 'Update app config',
            status: response.data && response.data.success ? 'passed' : 'failed',
            details: response.data && response.data.success ? 'Successfully updated app config' : 'Failed to update app config'
          });
          
          if (response.data && response.data.success) {
            results.passed++;
          } else {
            results.failed++;
          }
        } catch (error) {
          results.tests.push({
            name: 'Update app config',
            status: 'failed',
            details: `Error: ${error.message}`
          });
          results.failed++;
        }
      }
      
      // Test deleting app config
      if (createdConfigId) {
        try {
          const response = await axios.delete(`${this.options.baseUrl}${this.options.apiPrefix}/app-management/config/${createdConfigId}`, {
            headers: {
              Authorization: `Bearer ${this.authToken}`
            }
          });
          
          results.tests.push({
            name: 'Delete app config',
            status: response.data && response.data.success ? 'passed' : 'failed',
            details: response.data && response.data.success ? 'Successfully deleted app config' : 'Failed to delete app config'
          });
          
          if (response.data && response.data.success) {
            results.passed++;
          } else {
            results.failed++;
          }
        } catch (error) {
          results.tests.push({
            name: 'Delete app config',
            status: 'failed',
            details: `Error: ${error.message}`
          });
          results.failed++;
        }
      }
      
      // Test getting resource allocation
      try {
        const response = await axios.get(`${this.options.baseUrl}${this.options.apiPrefix}/app-management/resources`, {
          headers: {
            Authorization: `Bearer ${this.authToken}`
          }
        });
        
        results.tests.push({
          name: 'Get resource allocation',
          status: response.data && response.data.success ? 'passed' : 'failed',
          details: response.data && response.data.success ? 'Successfully retrieved resource allocation' : 'Failed to retrieve resource allocation'
        });
        
        if (response.data && response.data.success) {
          results.passed++;
        } else {
          results.failed++;
        }
      } catch (error) {
        results.tests.push({
          name: 'Get resource allocation',
          status: 'failed',
          details: `Error: ${error.message}`
        });
        results.failed++;
      }
      
      // Calculate status
      results.status = results.failed === 0 ? 'passed' : results.passed === 0 ? 'failed' : 'partial';
      
      return results;
    } catch (error) {
      this.logger.error('Error validating app management:', error);
      
      results.status = 'error';
      results.error = error.message;
      
      return results;
    }
  }
  
  /**
   * Validate health monitoring functionality
   * @returns {Promise<Object>} Validation results
   * @private
   */
  async _validateHealthMonitoring() {
    const results = {
      tests: [],
      passed: 0,
      failed: 0,
      status: 'pending'
    };
    
    try {
      // Test getting current metrics
      try {
        const response = await axios.get(`${this.options.baseUrl}${this.options.apiPrefix}/health/metrics/current`, {
          headers: {
            Authorization: `Bearer ${this.authToken}`
          }
        });
        
        results.tests.push({
          name: 'Get current metrics',
          status: response.data && response.data.success ? 'passed' : 'failed',
          details: response.data && response.data.success ? 'Successfully retrieved current metrics' : 'Failed to retrieve current metrics'
        });
        
        if (response.data && response.data.success) {
          results.passed++;
        } else {
          results.failed++;
        }
      } catch (error) {
        results.tests.push({
          name: 'Get current metrics',
          status: 'failed',
          details: `Error: ${error.message}`
        });
        results.failed++;
      }
      
      // Test getting historical metrics
      try {
        const response = await axios.get(`${this.options.baseUrl}${this.options.apiPrefix}/health/metrics/history`, {
          headers: {
            Authorization: `Bearer ${this.authToken}`
          }
        });
        
        results.tests.push({
          name: 'Get historical metrics',
          status: response.data && response.data.success ? 'passed' : 'failed',
          details: response.data && response.data.success ? 'Successfully retrieved historical metrics' : 'Failed to retrieve historical metrics'
        });
        
        if (response.data && response.data.success) {
          results.passed++;
        } else {
          results.failed++;
        }
      } catch (error) {
        results.tests.push({
          name: 'Get historical metrics',
          status: 'failed',
          details: `Error: ${error.message}`
        });
        results.failed++;
      }
      
      // Test getting active alerts
      try {
        const response = await axios.get(`${this.options.baseUrl}${this.options.apiPrefix}/health/alerts/active`, {
          headers: {
            Authorization: `Bearer ${this.authToken}`
          }
        });
        
        results.tests.push({
          name: 'Get active alerts',
          status: response.data && response.data.success ? 'passed' : 'failed',
          details: response.data && response.data.success ? 'Successfully retrieved active alerts' : 'Failed to retrieve active alerts'
        });
        
        if (response.data && response.data.success) {
          results.passed++;
        } else {
          results.failed++;
        }
      } catch (error) {
        results.tests.push({
          name: 'Get active alerts',
          status: 'failed',
          details: `Error: ${error.message}`
        });
        results.failed++;
      }
      
      // Test getting alert history
      try {
        const response = await axios.get(`${this.options.baseUrl}${this.options.apiPrefix}/health/alerts/history`, {
          headers: {
            Authorization: `Bearer ${this.authToken}`
          }
        });
        
        results.tests.push({
          name: 'Get alert history',
          status: response.data && response.data.success ? 'passed' : 'failed',
          details: response.data && response.data.success ? 'Successfully retrieved alert history' : 'Failed to retrieve alert history'
        });
        
        if (response.data && response.data.success) {
          results.passed++;
        } else {
          results.failed++;
        }
      } catch (error) {
        results.tests.push({
          name: 'Get alert history',
          status: 'failed',
          details: `Error: ${error.message}`
        });
        results.failed++;
      }
      
      // Test getting alert configurations
      try {
        const response = await axios.get(`${this.options.baseUrl}${this.options.apiPrefix}/health/alert-configs`, {
          headers: {
            Authorization: `Bearer ${this.authToken}`
          }
        });
        
        results.tests.push({
          name: 'Get alert configurations',
          status: response.data && response.data.success ? 'passed' : 'failed',
          details: response.data && response.data.success ? 'Successfully retrieved alert configurations' : 'Failed to retrieve alert configurations'
        });
        
        if (response.data && response.data.success) {
          results.passed++;
        } else {
          results.failed++;
        }
      } catch (error) {
        results.tests.push({
          name: 'Get alert configurations',
          status: 'failed',
          details: `Error: ${error.message}`
        });
        results.failed++;
      }
      
      // Test creating alert configuration
      let createdAlertConfigId = null;
      try {
        const response = await axios.post(`${this.options.baseUrl}${this.options.apiPrefix}/health/alert-configs`, {
          name: 'Test Alert Config',
          metricType: 'cpu.usage',
          condition: 'gt',
          threshold: 90,
          severity: 'warning',
          description: 'Test alert configuration'
        }, {
          headers: {
            Authorization: `Bearer ${this.authToken}`
          }
        });
        
        results.tests.push({
          name: 'Create alert configuration',
          status: response.data && response.data.success ? 'passed' : 'failed',
          details: response.data && response.data.success ? 'Successfully created alert configuration' : 'Failed to create alert configuration'
        });
        
        if (response.data && response.data.success) {
          createdAlertConfigId = response.data.data._id;
          results.passed++;
        } else {
          results.failed++;
        }
      } catch (error) {
        results.tests.push({
          name: 'Create alert configuration',
          status: 'failed',
          details: `Error: ${error.message}`
        });
        results.failed++;
      }
      
      // Test updating alert configuration
      if (createdAlertConfigId) {
        try {
          const response = await axios.put(`${this.options.baseUrl}${this.options.apiPrefix}/health/alert-configs/${createdAlertConfigId}`, {
            threshold: 95,
            severity: 'error'
          }, {
            headers: {
              Authorization: `Bearer ${this.authToken}`
            }
          });
          
          results.tests.push({
            name: 'Update alert configuration',
            status: response.data && response.data.success ? 'passed' : 'failed',
            details: response.data && response.data.success ? 'Successfully updated alert configuration' : 'Failed to update alert configuration'
          });
          
          if (response.data && response.data.success) {
            results.passed++;
          } else {
            results.failed++;
          }
        } catch (error) {
          results.tests.push({
            name: 'Update alert configuration',
            status: 'failed',
            details: `Error: ${error.message}`
          });
          results.failed++;
        }
      }
      
      // Test deleting alert configuration
      if (createdAlertConfigId) {
        try {
          const response = await axios.delete(`${this.options.baseUrl}${this.options.apiPrefix}/health/alert-configs/${createdAlertConfigId}`, {
            headers: {
              Authorization: `Bearer ${this.authToken}`
            }
          });
          
          results.tests.push({
            name: 'Delete alert configuration',
            status: response.data && response.data.success ? 'passed' : 'failed',
            details: response.data && response.data.success ? 'Successfully deleted alert configuration' : 'Failed to delete alert configuration'
          });
          
          if (response.data && response.data.success) {
            results.passed++;
          } else {
            results.failed++;
          }
        } catch (error) {
          results.tests.push({
            name: 'Delete alert configuration',
            status: 'failed',
            details: `Error: ${error.message}`
          });
          results.failed++;
        }
      }
      
      // Test getting health score
      try {
        const response = await axios.get(`${this.options.baseUrl}${this.options.apiPrefix}/health/health-score`, {
          headers: {
            Authorization: `Bearer ${this.authToken}`
          }
        });
        
        results.tests.push({
          name: 'Get health score',
          status: response.data && response.data.success ? 'passed' : 'failed',
          details: response.data && response.data.success ? 'Successfully retrieved health score' : 'Failed to retrieve health score'
        });
        
        if (response.data && response.data.success) {
          results.passed++;
        } else {
          results.failed++;
        }
      } catch (error) {
        results.tests.push({
          name: 'Get health score',
          status: 'failed',
          details: `Error: ${error.message}`
        });
        results.failed++;
      }
      
      // Test running health check
      try {
        const response = await axios.post(`${this.options.baseUrl}${this.options.apiPrefix}/health/health-check`, {}, {
          headers: {
            Authorization: `Bearer ${this.authToken}`
          }
        });
        
        results.tests.push({
          name: 'Run health check',
          status: response.data && response.data.success ? 'passed' : 'failed',
          details: response.data && response.data.success ? 'Successfully ran health check' : 'Failed to run health check'
        });
        
        if (response.data && response.data.success) {
          results.passed++;
        } else {
          results.failed++;
        }
      } catch (error) {
        results.tests.push({
          name: 'Run health check',
          status: 'failed',
          details: `Error: ${error.message}`
        });
        results.failed++;
      }
      
      // Calculate status
      results.status = results.failed === 0 ? 'passed' : results.passed === 0 ? 'failed' : 'partial';
      
      return results;
    } catch (error) {
      this.logger.error('Error validating health monitoring:', error);
      
      results.status = 'error';
      results.error = error.message;
      
      return results;
    }
  }
  
  /**
   * Validate user management functionality
   * @returns {Promise<Object>} Validation results
   * @private
   */
  async _validateUserManagement() {
    const results = {
      tests: [],
      passed: 0,
      failed: 0,
      status: 'pending'
    };
    
    try {
      // Test getting users
      try {
        const response = await axios.get(`${this.options.baseUrl}${this.options.apiPrefix}/users`, {
          headers: {
            Authorization: `Bearer ${this.authToken}`
          }
        });
        
        results.tests.push({
          name: 'Get users',
          status: response.data && response.data.success ? 'passed' : 'failed',
          details: response.data && response.data.success ? 'Successfully retrieved users' : 'Failed to retrieve users'
        });
        
        if (response.data && response.data.success) {
          results.passed++;
        } else {
          results.failed++;
        }
      } catch (error) {
        results.tests.push({
          name: 'Get users',
          status: 'failed',
          details: `Error: ${error.message}`
        });
        results.failed++;
      }
      
      // Test creating user
      let createdUserId = null;
      try {
        const response = await axios.post(`${this.options.baseUrl}${this.options.apiPrefix}/users`, {
          username: `test-user-${Date.now()}`,
          email: `test-user-${Date.now()}@example.com`,
          password: 'Test123!',
          role: 'viewer',
          firstName: 'Test',
          lastName: 'User'
        }, {
          headers: {
            Authorization: `Bearer ${this.authToken}`
          }
        });
        
        results.tests.push({
          name: 'Create user',
          status: response.data && response.data.success ? 'passed' : 'failed',
          details: response.data && response.data.success ? 'Successfully created user' : 'Failed to create user'
        });
        
        if (response.data && response.data.success) {
          createdUserId = response.data.data._id;
          results.passed++;
        } else {
          results.failed++;
        }
      } catch (error) {
        results.tests.push({
          name: 'Create user',
          status: 'failed',
          details: `Error: ${error.message}`
        });
        results.failed++;
      }
      
      // Test updating user
      if (createdUserId) {
        try {
          const response = await axios.put(`${this.options.baseUrl}${this.options.apiPrefix}/users/${createdUserId}`, {
            firstName: 'Updated',
            lastName: 'User',
            role: 'api_manager'
          }, {
            headers: {
              Authorization: `Bearer ${this.authToken}`
            }
          });
          
          results.tests.push({
            name: 'Update user',
            status: response.data && response.data.success ? 'passed' : 'failed',
            details: response.data && response.data.success ? 'Successfully updated user' : 'Failed to update user'
          });
          
          if (response.data && response.data.success) {
            results.passed++;
          } else {
            results.failed++;
          }
        } catch (error) {
          results.tests.push({
            name: 'Update user',
            status: 'failed',
            details: `Error: ${error.message}`
          });
          results.failed++;
        }
      }
      
      // Test deleting user
      if (createdUserId) {
        try {
          const response = await axios.delete(`${this.options.baseUrl}${this.options.apiPrefix}/users/${createdUserId}`, {
            headers: {
              Authorization: `Bearer ${this.authToken}`
            }
          });
          
          results.tests.push({
            name: 'Delete user',
            status: response.data && response.data.success ? 'passed' : 'failed',
            details: response.data && response.data.success ? 'Successfully deleted user' : 'Failed to delete user'
          });
          
          if (response.data && response.data.success) {
            results.passed++;
          } else {
            results.failed++;
          }
        } catch (error) {
          results.tests.push({
            name: 'Delete user',
            status: 'failed',
            details: `Error: ${error.message}`
          });
          results.failed++;
        }
      }
      
      // Calculate status
      results.status = results.failed === 0 ? 'passed' : results.passed === 0 ? 'failed' : 'partial';
      
      return results;
    } catch (error) {
      this.logger.error('Error validating user management:', error);
      
      results.status = 'error';
      results.error = error.message;
      
      return results;
    }
  }
  
  /**
   * Validate performance
   * @returns {Promise<Object>} Validation results
   * @private
   */
  async _validatePerformance() {
    const results = {
      tests: [],
      passed: 0,
      failed: 0,
      status: 'pending'
    };
    
    try {
      // Test API response time
      try {
        const startTime = performance.now();
        
        await axios.get(`${this.options.baseUrl}${this.options.apiPrefix}/health/metrics/current`, {
          headers: {
            Authorization: `Bearer ${this.authToken}`
          }
        });
        
        const endTime = performance.now();
        const responseTime = endTime - startTime;
        
        const passed = responseTime < 1000; // Less than 1 second
        
        results.tests.push({
          name: 'API response time',
          status: passed ? 'passed' : 'failed',
          details: `Response time: ${responseTime.toFixed(2)}ms (target: <1000ms)`
        });
        
        if (passed) {
          results.passed++;
        } else {
          results.failed++;
        }
      } catch (error) {
        results.tests.push({
          name: 'API response time',
          status: 'failed',
          details: `Error: ${error.message}`
        });
        results.failed++;
      }
      
      // Test concurrent requests
      try {
        const concurrentRequests = 10;
        const startTime = performance.now();
        
        await Promise.all(Array(concurrentRequests).fill().map(() => 
          axios.get(`${this.options.baseUrl}${this.options.apiPrefix}/health/metrics/current`, {
            headers: {
              Authorization: `Bearer ${this.authToken}`
            }
          })
        ));
        
        const endTime = performance.now();
        const totalTime = endTime - startTime;
        const avgResponseTime = totalTime / concurrentRequests;
        
        const passed = avgResponseTime < 2000; // Less than 2 seconds per request on average
        
        results.tests.push({
          name: 'Concurrent requests',
          status: passed ? 'passed' : 'failed',
          details: `Average response time for ${concurrentRequests} concurrent requests: ${avgResponseTime.toFixed(2)}ms (target: <2000ms)`
        });
        
        if (passed) {
          results.passed++;
        } else {
          results.failed++;
        }
      } catch (error) {
        results.tests.push({
          name: 'Concurrent requests',
          status: 'failed',
          details: `Error: ${error.message}`
        });
        results.failed++;
      }
      
      // Calculate status
      results.status = results.failed === 0 ? 'passed' : results.passed === 0 ? 'failed' : 'partial';
      
      return results;
    } catch (error) {
      this.logger.error('Error validating performance:', error);
      
      results.status = 'error';
      results.error = error.message;
      
      return results;
    }
  }
  
  /**
   * Validate security
   * @returns {Promise<Object>} Validation results
   * @private
   */
  async _validateSecurity() {
    const results = {
      tests: [],
      passed: 0,
      failed: 0,
      status: 'pending'
    };
    
    try {
      // Test authentication required
      try {
        try {
          await axios.get(`${this.options.baseUrl}${this.options.apiPrefix}/health/metrics/current`);
          
          results.tests.push({
            name: 'Authentication required',
            status: 'failed',
            details: 'Request without authentication token was accepted'
          });
          
          results.failed++;
        } catch (error) {
          if (error.response && error.response.status === 401) {
            results.tests.push({
              name: 'Authentication required',
              status: 'passed',
              details: 'Request without authentication token was correctly rejected'
            });
            
            results.passed++;
          } else {
            results.tests.push({
              name: 'Authentication required',
              status: 'failed',
              details: `Error: ${error.message}`
            });
            
            results.failed++;
          }
        }
      } catch (error) {
        results.tests.push({
          name: 'Authentication required',
          status: 'failed',
          details: `Error: ${error.message}`
        });
        
        results.failed++;
      }
      
      // Test authorization required
      try {
        // This assumes the test user doesn't have super_admin privileges
        try {
          await axios.post(`${this.options.baseUrl}${this.options.apiPrefix}/app-management/restart`, {}, {
            headers: {
              Authorization: `Bearer ${this.authToken}`
            }
          });
          
          // If we get here, either the test passed (user has proper permissions) or failed (no authorization check)
          // For this test, we'll assume it failed since we're testing that authorization is required
          results.tests.push({
            name: 'Authorization required',
            status: 'failed',
            details: 'Request without proper authorization was accepted'
          });
          
          results.failed++;
        } catch (error) {
          if (error.response && error.response.status === 403) {
            results.tests.push({
              name: 'Authorization required',
              status: 'passed',
              details: 'Request without proper authorization was correctly rejected'
            });
            
            results.passed++;
          } else {
            results.tests.push({
              name: 'Authorization required',
              status: 'failed',
              details: `Error: ${error.message}`
            });
            
            results.failed++;
          }
        }
      } catch (error) {
        results.tests.push({
          name: 'Authorization required',
          status: 'failed',
          details: `Error: ${error.message}`
        });
        
        results.failed++;
      }
      
      // Test CORS headers
      try {
        const response = await axios.options(`${this.options.baseUrl}${this.options.apiPrefix}/health/metrics/current`, {
          headers: {
            'Origin': this.options.baseUrl,
            'Access-Control-Request-Method': 'GET'
          }
        });
        
        const corsHeadersPresent = response.headers['access-control-allow-origin'] !== undefined &&
                                  response.headers['access-control-allow-methods'] !== undefined;
        
        results.tests.push({
          name: 'CORS headers',
          status: corsHeadersPresent ? 'passed' : 'failed',
          details: corsHeadersPresent ? 'CORS headers are properly set' : 'CORS headers are missing'
        });
        
        if (corsHeadersPresent) {
          results.passed++;
        } else {
          results.failed++;
        }
      } catch (error) {
        results.tests.push({
          name: 'CORS headers',
          status: 'failed',
          details: `Error: ${error.message}`
        });
        
        results.failed++;
      }
      
      // Calculate status
      results.status = results.failed === 0 ? 'passed' : results.passed === 0 ? 'failed' : 'partial';
      
      return results;
    } catch (error) {
      this.logger.error('Error validating security:', error);
      
      results.status = 'error';
      results.error = error.message;
      
      return results;
    }
  }
  
  /**
   * Validate UI
   * @returns {Promise<Object>} Validation results
   * @private
   */
  async _validateUI() {
    const results = {
      tests: [],
      passed: 0,
      failed: 0,
      status: 'pending'
    };
    
    try {
      // Test UI availability
      try {
        const response = await axios.get(`${this.options.baseUrl}/`);
        
        const uiAvailable = response.status === 200 && response.data.includes('<html');
        
        results.tests.push({
          name: 'UI availability',
          status: uiAvailable ? 'passed' : 'failed',
          details: uiAvailable ? 'UI is available' : 'UI is not available'
        });
        
        if (uiAvailable) {
          results.passed++;
        } else {
          results.failed++;
        }
      } catch (error) {
        results.tests.push({
          name: 'UI availability',
          status: 'failed',
          details: `Error: ${error.message}`
        });
        
        results.failed++;
      }
      
      // Test static assets
      try {
        const response = await axios.get(`${this.options.baseUrl}/static/js/main.js`);
        
        const assetsAvailable = response.status === 200;
        
        results.tests.push({
          name: 'Static assets',
          status: assetsAvailable ? 'passed' : 'failed',
          details: assetsAvailable ? 'Static assets are available' : 'Static assets are not available'
        });
        
        if (assetsAvailable) {
          results.passed++;
        } else {
          results.failed++;
        }
      } catch (error) {
        results.tests.push({
          name: 'Static assets',
          status: 'failed',
          details: `Error: ${error.message}`
        });
        
        results.failed++;
      }
      
      // Calculate status
      results.status = results.failed === 0 ? 'passed' : results.passed === 0 ? 'failed' : 'partial';
      
      return results;
    } catch (error) {
      this.logger.error('Error validating UI:', error);
      
      results.status = 'error';
      results.error = error.message;
      
      return results;
    }
  }
  
  /**
   * Calculate overall status
   * @param {Object} results - Validation results
   * @returns {Object} Overall status
   * @private
   */
  _calculateOverallStatus(results) {
    let totalPassed = 0;
    let totalFailed = 0;
    let totalTests = 0;
    
    for (const category of Object.values(results)) {
      if (category.passed !== undefined && category.failed !== undefined) {
        totalPassed += category.passed;
        totalFailed += category.failed;
        totalTests += category.passed + category.failed;
      }
    }
    
    const passRate = totalTests > 0 ? (totalPassed / totalTests) * 100 : 0;
    
    let status;
    if (passRate === 100) {
      status = 'passed';
    } else if (passRate >= 80) {
      status = 'partial';
    } else {
      status = 'failed';
    }
    
    return {
      status,
      passRate
    };
  }
}

module.exports = AdminDashboardValidation;
