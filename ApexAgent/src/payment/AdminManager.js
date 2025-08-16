/**
 * AdminManager.js
 * Manages admin recognition and payment exemption for system administrators
 */

class AdminManager {
  constructor() {
    // Admin identification methods
    this.identificationMethods = {
      INSTALL_KEY: 'install_key',
      GCP_DEPLOYMENT: 'gcp_deployment',
      EMAIL_DOMAIN: 'email_domain',
      LICENSE_KEY: 'license_key'
    };
    
    // Admin privileges
    this.adminPrivileges = {
      PAYMENT_EXEMPT: 'payment_exempt',
      USER_MANAGEMENT: 'user_management',
      SUBSCRIPTION_MANAGEMENT: 'subscription_management',
      SYSTEM_CONFIGURATION: 'system_configuration',
      ANALYTICS_ACCESS: 'analytics_access'
    };
    
    // Default admin configuration
    this.adminConfig = {
      installKeys: ['aideon-admin-install-2025'],
      gcpProjectIds: ['aideon-ai-lite-prod', 'aideon-ai-lite-staging'],
      adminEmailDomains: ['aideon.ai', 'alliennova.com'],
      adminLicenseKeys: ['ADMIN-AIDEON-2025-MASTER']
    };
  }
  
  /**
   * Initialize the admin manager with configuration
   * @param {Object} config - Admin configuration
   */
  initialize(config) {
    if (config) {
      // Merge provided config with defaults
      this.adminConfig = {
        ...this.adminConfig,
        ...config
      };
    }
    
    console.log('Admin manager initialized');
    return true;
  }
  
  /**
   * Check if a user is an admin based on various identification methods
   * @param {Object} userData - User data including email, installInfo, etc.
   * @returns {boolean} Whether the user is an admin
   */
  isAdmin(userData) {
    if (!userData) {
      return false;
    }
    
    // Check install key
    if (userData.installKey && 
        this.adminConfig.installKeys.includes(userData.installKey)) {
      return true;
    }
    
    // Check GCP project ID
    if (userData.gcpProjectId && 
        this.adminConfig.gcpProjectIds.includes(userData.gcpProjectId)) {
      return true;
    }
    
    // Check email domain
    if (userData.email) {
      const domain = userData.email.split('@')[1];
      if (domain && this.adminConfig.adminEmailDomains.includes(domain)) {
        return true;
      }
    }
    
    // Check license key
    if (userData.licenseKey && 
        this.adminConfig.adminLicenseKeys.includes(userData.licenseKey)) {
      return true;
    }
    
    return false;
  }
  
  /**
   * Grant admin privileges to a user
   * @param {string} userId - User ID
   * @param {Array} privileges - List of privileges to grant
   * @returns {Object} Updated admin privileges
   */
  grantAdminPrivileges(userId, privileges = []) {
    if (!userId) {
      throw new Error('User ID is required');
    }
    
    // Default to all privileges if none specified
    if (!privileges || privileges.length === 0) {
      privileges = Object.values(this.adminPrivileges);
    }
    
    // In production, this would update a database
    console.log(`Granting admin privileges to user ${userId}: ${privileges.join(', ')}`);
    
    return {
      userId,
      privileges,
      grantedAt: new Date()
    };
  }
  
  /**
   * Check if a user has a specific admin privilege
   * @param {string} userId - User ID
   * @param {string} privilege - Privilege to check
   * @returns {boolean} Whether the user has the privilege
   */
  hasAdminPrivilege(userId, privilege) {
    if (!userId || !privilege) {
      return false;
    }
    
    // In production, this would check the database
    // For now, simulate that the user has the privilege if they're an admin
    const isUserAdmin = this.isAdmin({ userId, email: `${userId}@aideon.ai` });
    
    return isUserAdmin;
  }
  
  /**
   * Apply payment exemption to an admin user
   * @param {string} userId - User ID
   * @returns {Object} Exemption result
   */
  applyPaymentExemption(userId) {
    if (!userId) {
      throw new Error('User ID is required');
    }
    
    // Check if user is an admin
    const isUserAdmin = this.isAdmin({ userId, email: `${userId}@aideon.ai` });
    
    if (!isUserAdmin) {
      throw new Error('User is not an admin');
    }
    
    // In production, this would update the user's subscription in the database
    console.log(`Applying payment exemption to admin user ${userId}`);
    
    return {
      userId,
      paymentExempt: true,
      appliedAt: new Date(),
      expiresAt: null // Never expires for admin
    };
  }
  
  /**
   * Detect admin during installation or deployment
   * @param {Object} installationData - Installation or deployment data
   * @returns {Object} Detection result with admin status
   */
  detectAdminDuringSetup(installationData) {
    if (!installationData) {
      return { isAdmin: false };
    }
    
    const isAdminInstall = this.isAdmin(installationData);
    
    if (isAdminInstall) {
      // Auto-register admin privileges if detected during installation
      const userId = installationData.userId || `admin_${Date.now()}`;
      this.grantAdminPrivileges(userId);
      this.applyPaymentExemption(userId);
      
      return {
        isAdmin: true,
        userId,
        detectionMethod: this._determineDetectionMethod(installationData)
      };
    }
    
    return { isAdmin: false };
  }
  
  /**
   * Determine which method was used to detect the admin
   * @param {Object} installationData - Installation data
   * @returns {string} Detection method
   * @private
   */
  _determineDetectionMethod(installationData) {
    if (installationData.installKey) {
      return this.identificationMethods.INSTALL_KEY;
    }
    
    if (installationData.gcpProjectId) {
      return this.identificationMethods.GCP_DEPLOYMENT;
    }
    
    if (installationData.email) {
      return this.identificationMethods.EMAIL_DOMAIN;
    }
    
    if (installationData.licenseKey) {
      return this.identificationMethods.LICENSE_KEY;
    }
    
    return 'unknown';
  }
  
  /**
   * Get admin dashboard data
   * @param {string} userId - Admin user ID
   * @returns {Object} Admin dashboard data
   */
  getAdminDashboardData(userId) {
    if (!userId || !this.hasAdminPrivilege(userId, this.adminPrivileges.ANALYTICS_ACCESS)) {
      throw new Error('Unauthorized access to admin dashboard');
    }
    
    // In production, this would fetch real data
    return {
      activeUsers: 1250,
      subscriptionTiers: {
        basic: 850,
        pro: 320,
        expert: 75,
        enterprise: 5
      },
      totalRevenue: 78500,
      creditUsage: 1250000,
      apiKeyStats: {
        userProvided: 420,
        systemProvided: 830
      }
    };
  }
}

module.exports = AdminManager;
