/**
 * SecurityManager.js
 * 
 * Security management utility for Aideon AI Lite.
 * Provides security features including authentication, authorization,
 * encryption, threat detection, and compliance monitoring.
 * 
 * @author Aideon AI Team
 * @version 1.0.0
 */

const EventEmitter = require('events');
const crypto = require('crypto');
const jwt = require('jsonwebtoken');
const fs = require('fs').promises;
const path = require('path');

class SecurityManager extends EventEmitter {
  /**
   * Initialize the Security Manager
   * @param {Object} config - Security configuration
   */
  constructor(config = {}) {
    super();
    
    this.config = {
      encryption: {
        enabled: true,
        algorithm: 'aes-256-gcm',
        keyLength: 32,
        ivLength: 16,
        tagLength: 16
      },
      authentication: {
        enabled: true,
        method: 'jwt',
        tokenExpiration: '24h',
        refreshTokenExpiration: '7d',
        jwtSecret: process.env.JWT_SECRET || crypto.randomBytes(32).toString('hex')
      },
      permissions: {
        enabled: true,
        defaultPolicy: 'deny',
        roleDefinitionsPath: './config/roles.json'
      },
      threatDetection: {
        enabled: true,
        scanInterval: 60000, // 1 minute
        maxFailedLogins: 5,
        lockoutDuration: 300000, // 5 minutes
        ipWhitelist: [],
        ipBlacklist: []
      },
      compliance: {
        enabled: true,
        dataRetentionDays: 90,
        auditLogging: true,
        auditLogPath: './logs/audit'
      },
      ...config
    };
    
    // Initialize security components
    this.encryptionKeys = new Map();
    this.sessions = new Map();
    this.failedLogins = new Map();
    this.roles = new Map();
    this.permissions = new Map();
    this.threatDetectionTimer = null;
    
    // Load roles and permissions
    this._loadRolesAndPermissions().catch(error => {
      console.error('Failed to load roles and permissions:', error);
    });
    
    // Start threat detection if enabled
    if (this.config.threatDetection.enabled) {
      this._startThreatDetection();
    }
  }
  
  /**
   * Perform startup security checks
   * @returns {Promise<boolean>} Success status
   */
  async performStartupChecks() {
    try {
      // Check for security updates
      const securityUpdates = await this._checkSecurityUpdates();
      
      if (securityUpdates.length > 0) {
        this.emit('security:updates', securityUpdates);
      }
      
      // Check for configuration vulnerabilities
      const vulnerabilities = this._checkConfigurationVulnerabilities();
      
      if (vulnerabilities.length > 0) {
        this.emit('security:vulnerabilities', vulnerabilities);
      }
      
      // Check for file system permissions
      const fsPermissions = await this._checkFileSystemPermissions();
      
      if (!fsPermissions.success) {
        this.emit('security:filesystem', fsPermissions.issues);
      }
      
      return true;
    } catch (error) {
      this.emit('security:error', error);
      return false;
    }
  }
  
  /**
   * Authenticate a user
   * @param {Object} credentials - User credentials
   * @returns {Promise<Object>} Authentication result
   */
  async authenticate(credentials) {
    if (!this.config.authentication.enabled) {
      return { success: false, error: 'Authentication is disabled' };
    }
    
    try {
      // Check for IP lockout
      if (this._isIpLocked(credentials.ip)) {
        this.emit('security:threat', {
          type: 'login_attempt_from_locked_ip',
          ip: credentials.ip,
          timestamp: new Date()
        });
        
        return { success: false, error: 'IP address is temporarily locked' };
      }
      
      // Authenticate based on method
      let authResult;
      
      switch (this.config.authentication.method) {
        case 'jwt':
          authResult = await this._authenticateJwt(credentials);
          break;
        case 'oauth':
          authResult = await this._authenticateOAuth(credentials);
          break;
        case 'api_key':
          authResult = await this._authenticateApiKey(credentials);
          break;
        default:
          authResult = { success: false, error: 'Unsupported authentication method' };
      }
      
      // Handle failed login attempts
      if (!authResult.success) {
        this._recordFailedLogin(credentials.ip);
      } else {
        // Clear failed login attempts on success
        this._clearFailedLogins(credentials.ip);
      }
      
      return authResult;
    } catch (error) {
      this.emit('security:error', error);
      return { success: false, error: 'Authentication error' };
    }
  }
  
  /**
   * Authorize a user for a specific action
   * @param {Object} user - User object
   * @param {string} resource - Resource to access
   * @param {string} action - Action to perform
   * @returns {boolean} Authorization result
   */
  authorize(user, resource, action) {
    if (!this.config.permissions.enabled) {
      return true;
    }
    
    try {
      // Check if user has required permissions
      if (!user || !user.roles) {
        return false;
      }
      
      // Super admin has all permissions
      if (user.roles.includes('super_admin')) {
        return true;
      }
      
      // Check each role for the required permission
      for (const roleName of user.roles) {
        const role = this.roles.get(roleName);
        
        if (!role) {
          continue;
        }
        
        // Check for exact permission
        const permissionKey = `${resource}:${action}`;
        if (role.permissions.includes(permissionKey)) {
          return true;
        }
        
        // Check for wildcard permissions
        if (role.permissions.includes(`${resource}:*`)) {
          return true;
        }
        
        if (role.permissions.includes('*:*')) {
          return true;
        }
      }
      
      // Default policy
      return this.config.permissions.defaultPolicy === 'allow';
    } catch (error) {
      this.emit('security:error', error);
      return false;
    }
  }
  
  /**
   * Encrypt data
   * @param {string|Buffer} data - Data to encrypt
   * @param {string} keyId - Key identifier
   * @returns {Object} Encrypted data
   */
  encrypt(data, keyId = 'default') {
    if (!this.config.encryption.enabled) {
      return { success: false, error: 'Encryption is disabled' };
    }
    
    try {
      // Get or generate key
      let key = this.encryptionKeys.get(keyId);
      
      if (!key) {
        key = crypto.randomBytes(this.config.encryption.keyLength);
        this.encryptionKeys.set(keyId, key);
      }
      
      // Generate IV
      const iv = crypto.randomBytes(this.config.encryption.ivLength);
      
      // Create cipher
      const cipher = crypto.createCipheriv(
        this.config.encryption.algorithm,
        key,
        iv
      );
      
      // Encrypt data
      let encrypted = cipher.update(data, 'utf8', 'hex');
      encrypted += cipher.final('hex');
      
      // Get auth tag for GCM mode
      const authTag = cipher.getAuthTag().toString('hex');
      
      return {
        success: true,
        encrypted,
        iv: iv.toString('hex'),
        authTag,
        keyId
      };
    } catch (error) {
      this.emit('security:error', error);
      return { success: false, error: 'Encryption error' };
    }
  }
  
  /**
   * Decrypt data
   * @param {Object} encryptedData - Encrypted data object
   * @returns {Object} Decrypted data
   */
  decrypt(encryptedData) {
    if (!this.config.encryption.enabled) {
      return { success: false, error: 'Encryption is disabled' };
    }
    
    try {
      // Get key
      const key = this.encryptionKeys.get(encryptedData.keyId);
      
      if (!key) {
        return { success: false, error: 'Key not found' };
      }
      
      // Create decipher
      const decipher = crypto.createDecipheriv(
        this.config.encryption.algorithm,
        key,
        Buffer.from(encryptedData.iv, 'hex')
      );
      
      // Set auth tag for GCM mode
      decipher.setAuthTag(Buffer.from(encryptedData.authTag, 'hex'));
      
      // Decrypt data
      let decrypted = decipher.update(encryptedData.encrypted, 'hex', 'utf8');
      decrypted += decipher.final('utf8');
      
      return {
        success: true,
        decrypted
      };
    } catch (error) {
      this.emit('security:error', error);
      return { success: false, error: 'Decryption error' };
    }
  }
  
  /**
   * Generate a JWT token
   * @param {Object} payload - Token payload
   * @param {Object} options - Token options
   * @returns {Object} Token result
   */
  generateToken(payload, options = {}) {
    if (!this.config.authentication.enabled) {
      return { success: false, error: 'Authentication is disabled' };
    }
    
    try {
      const tokenOptions = {
        expiresIn: this.config.authentication.tokenExpiration,
        ...options
      };
      
      const token = jwt.sign(
        payload,
        this.config.authentication.jwtSecret,
        tokenOptions
      );
      
      return {
        success: true,
        token
      };
    } catch (error) {
      this.emit('security:error', error);
      return { success: false, error: 'Token generation error' };
    }
  }
  
  /**
   * Verify a JWT token
   * @param {string} token - JWT token
   * @returns {Object} Verification result
   */
  verifyToken(token) {
    if (!this.config.authentication.enabled) {
      return { success: false, error: 'Authentication is disabled' };
    }
    
    try {
      const decoded = jwt.verify(token, this.config.authentication.jwtSecret);
      
      return {
        success: true,
        decoded
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }
  
  /**
   * Create a user session
   * @param {Object} user - User object
   * @returns {Object} Session result
   */
  createSession(user) {
    if (!this.config.authentication.enabled) {
      return { success: false, error: 'Authentication is disabled' };
    }
    
    try {
      const sessionId = crypto.randomBytes(16).toString('hex');
      const session = {
        id: sessionId,
        userId: user.id,
        username: user.username,
        roles: user.roles,
        createdAt: new Date(),
        expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000), // 24 hours
        lastActivity: new Date()
      };
      
      this.sessions.set(sessionId, session);
      
      return {
        success: true,
        session
      };
    } catch (error) {
      this.emit('security:error', error);
      return { success: false, error: 'Session creation error' };
    }
  }
  
  /**
   * Get a user session
   * @param {string} sessionId - Session ID
   * @returns {Object} Session result
   */
  getSession(sessionId) {
    if (!this.config.authentication.enabled) {
      return { success: false, error: 'Authentication is disabled' };
    }
    
    try {
      const session = this.sessions.get(sessionId);
      
      if (!session) {
        return { success: false, error: 'Session not found' };
      }
      
      // Check if session is expired
      if (session.expiresAt < new Date()) {
        this.sessions.delete(sessionId);
        return { success: false, error: 'Session expired' };
      }
      
      // Update last activity
      session.lastActivity = new Date();
      
      return {
        success: true,
        session
      };
    } catch (error) {
      this.emit('security:error', error);
      return { success: false, error: 'Session retrieval error' };
    }
  }
  
  /**
   * Destroy a user session
   * @param {string} sessionId - Session ID
   * @returns {Object} Result
   */
  destroySession(sessionId) {
    if (!this.config.authentication.enabled) {
      return { success: false, error: 'Authentication is disabled' };
    }
    
    try {
      const session = this.sessions.get(sessionId);
      
      if (!session) {
        return { success: false, error: 'Session not found' };
      }
      
      this.sessions.delete(sessionId);
      
      return {
        success: true
      };
    } catch (error) {
      this.emit('security:error', error);
      return { success: false, error: 'Session destruction error' };
    }
  }
  
  /**
   * Log a security audit event
   * @param {string} action - Action performed
   * @param {Object} details - Event details
   * @returns {Promise<boolean>} Success status
   */
  async logAuditEvent(action, details) {
    if (!this.config.compliance.enabled || !this.config.compliance.auditLogging) {
      return true;
    }
    
    try {
      const event = {
        action,
        timestamp: new Date(),
        ...details
      };
      
      // Ensure audit log directory exists
      await fs.mkdir(this.config.compliance.auditLogPath, { recursive: true });
      
      // Write to audit log
      const logFile = path.join(
        this.config.compliance.auditLogPath,
        `audit-${new Date().toISOString().split('T')[0]}.log`
      );
      
      await fs.appendFile(
        logFile,
        JSON.stringify(event) + '\n',
        'utf8'
      );
      
      return true;
    } catch (error) {
      this.emit('security:error', error);
      return false;
    }
  }
  
  /**
   * Get security status
   * @returns {Object} Security status
   */
  getStatus() {
    return {
      encryption: {
        enabled: this.config.encryption.enabled,
        algorithm: this.config.encryption.algorithm,
        keysCount: this.encryptionKeys.size
      },
      authentication: {
        enabled: this.config.authentication.enabled,
        method: this.config.authentication.method
      },
      permissions: {
        enabled: this.config.permissions.enabled,
        rolesCount: this.roles.size,
        permissionsCount: this.permissions.size
      },
      sessions: {
        count: this.sessions.size
      },
      threatDetection: {
        enabled: this.config.threatDetection.enabled,
        lockedIPs: Array.from(this.failedLogins.entries())
          .filter(([_, attempts]) => attempts >= this.config.threatDetection.maxFailedLogins)
          .map(([ip]) => ip)
      },
      compliance: {
        enabled: this.config.compliance.enabled,
        auditLogging: this.config.compliance.auditLogging
      }
    };
  }
  
  /**
   * Load roles and permissions
   * @returns {Promise<void>}
   * @private
   */
  async _loadRolesAndPermissions() {
    try {
      // Check if roles file exists
      const rolesPath = this.config.permissions.roleDefinitionsPath;
      
      let rolesData;
      try {
        const data = await fs.readFile(rolesPath, 'utf8');
        rolesData = JSON.parse(data);
      } catch (error) {
        // Use default roles if file doesn't exist
        rolesData = this._getDefaultRoles();
      }
      
      // Process roles
      for (const [roleName, roleData] of Object.entries(rolesData)) {
        this.roles.set(roleName, {
          name: roleName,
          description: roleData.description || '',
          permissions: roleData.permissions || []
        });
        
        // Process permissions
        for (const permission of roleData.permissions || []) {
          if (!this.permissions.has(permission)) {
            this.permissions.set(permission, new Set());
          }
          
          this.permissions.get(permission).add(roleName);
        }
      }
    } catch (error) {
      throw new Error(`Failed to load roles and permissions: ${error.message}`);
    }
  }
  
  /**
   * Get default roles
   * @returns {Object} Default roles
   * @private
   */
  _getDefaultRoles() {
    return {
      super_admin: {
        description: 'Super administrator with all permissions',
        permissions: ['*:*']
      },
      admin: {
        description: 'Administrator with most permissions',
        permissions: [
          'users:*',
          'tasks:*',
          'tools:*',
          'config:read',
          'config:update',
          'logs:*',
          'system:status',
          'system:restart'
        ]
      },
      user: {
        description: 'Regular user',
        permissions: [
          'tasks:create',
          'tasks:read',
          'tasks:update',
          'tasks:delete',
          'tools:use',
          'system:status'
        ]
      },
      guest: {
        description: 'Guest user with limited permissions',
        permissions: [
          'tasks:read',
          'system:status'
        ]
      }
    };
  }
  
  /**
   * Start threat detection
   * @private
   */
  _startThreatDetection() {
    this.threatDetectionTimer = setInterval(() => {
      this._runThreatDetection();
    }, this.config.threatDetection.scanInterval);
  }
  
  /**
   * Run threat detection
   * @private
   */
  _runThreatDetection() {
    try {
      // Check for expired lockouts
      const now = Date.now();
      const lockoutDuration = this.config.threatDetection.lockoutDuration;
      
      for (const [ip, data] of this.failedLogins.entries()) {
        if (data.timestamp + lockoutDuration < now) {
          this.failedLogins.delete(ip);
        }
      }
      
      // Additional threat detection logic would go here
    } catch (error) {
      this.emit('security:error', error);
    }
  }
  
  /**
   * Record a failed login attempt
   * @param {string} ip - IP address
   * @private
   */
  _recordFailedLogin(ip) {
    if (!ip) return;
    
    const data = this.failedLogins.get(ip) || {
      count: 0,
      timestamp: Date.now()
    };
    
    data.count++;
    data.timestamp = Date.now();
    
    this.failedLogins.set(ip, data);
    
    // Check if IP should be locked
    if (data.count >= this.config.threatDetection.maxFailedLogins) {
      this.emit('security:threat', {
        type: 'max_failed_logins',
        ip,
        count: data.count,
        timestamp: new Date()
      });
    }
  }
  
  /**
   * Clear failed login attempts
   * @param {string} ip - IP address
   * @private
   */
  _clearFailedLogins(ip) {
    if (!ip) return;
    this.failedLogins.delete(ip);
  }
  
  /**
   * Check if an IP is locked
   * @param {string} ip - IP address
   * @returns {boolean} Whether the IP is locked
   * @private
   */
  _isIpLocked(ip) {
    if (!ip) return false;
    
    // Check whitelist
    if (this.config.threatDetection.ipWhitelist.includes(ip)) {
      return false;
    }
    
    // Check blacklist
    if (this.config.threatDetection.ipBlacklist.includes(ip)) {
      return true;
    }
    
    // Check failed login attempts
    const data = this.failedLogins.get(ip);
    
    if (!data) {
      return false;
    }
    
    return (
      data.count >= this.config.threatDetection.maxFailedLogins &&
      data.timestamp + this.config.threatDetection.lockoutDuration > Date.now()
    );
  }
  
  /**
   * Authenticate using JWT
   * @param {Object} credentials - User credentials
   * @returns {Promise<Object>} Authentication result
   * @private
   */
  async _authenticateJwt(credentials) {
    // In a real implementation, this would validate against a user database
    // For now, we'll use a placeholder implementation
    if (credentials.username === 'admin' && credentials.password === 'admin') {
      const user = {
        id: '1',
        username: 'admin',
        roles: ['admin']
      };
      
      const tokenResult = this.generateToken(user);
      
      if (!tokenResult.success) {
        return tokenResult;
      }
      
      return {
        success: true,
        user,
        token: tokenResult.token
      };
    }
    
    return {
      success: false,
      error: 'Invalid credentials'
    };
  }
  
  /**
   * Authenticate using OAuth
   * @param {Object} credentials - OAuth credentials
   * @returns {Promise<Object>} Authentication result
   * @private
   */
  async _authenticateOAuth(credentials) {
    // Placeholder for OAuth authentication
    return {
      success: false,
      error: 'OAuth authentication not implemented'
    };
  }
  
  /**
   * Authenticate using API key
   * @param {Object} credentials - API key credentials
   * @returns {Promise<Object>} Authentication result
   * @private
   */
  async _authenticateApiKey(credentials) {
    // Placeholder for API key authentication
    return {
      success: false,
      error: 'API key authentication not implemented'
    };
  }
  
  /**
   * Check for security updates
   * @returns {Promise<Array>} Security updates
   * @private
   */
  async _checkSecurityUpdates() {
    // In a real implementation, this would check for security updates
    // For now, we'll return an empty array
    return [];
  }
  
  /**
   * Check for configuration vulnerabilities
   * @returns {Array} Vulnerabilities
   * @private
   */
  _checkConfigurationVulnerabilities() {
    const vulnerabilities = [];
    
    // Check for default JWT secret
    if (
      this.config.authentication.enabled &&
      this.config.authentication.method === 'jwt' &&
      !process.env.JWT_SECRET
    ) {
      vulnerabilities.push({
        type: 'default_jwt_secret',
        severity: 'high',
        message: 'Using auto-generated JWT secret. Set JWT_SECRET environment variable for production.'
      });
    }
    
    // Additional vulnerability checks would go here
    
    return vulnerabilities;
  }
  
  /**
   * Check file system permissions
   * @returns {Promise<Object>} File system permissions check result
   * @private
   */
  async _checkFileSystemPermissions() {
    // In a real implementation, this would check file system permissions
    // For now, we'll return a success result
    return {
      success: true,
      issues: []
    };
  }
}

module.exports = { SecurityManager };
