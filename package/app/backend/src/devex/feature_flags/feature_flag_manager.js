// Feature Flag System for ApexAgent
// This module provides a centralized system for managing feature flags

/**
 * Feature Flag Manager
 * Provides methods for checking, enabling, and disabling feature flags
 */
class FeatureFlagManager {
  /**
   * Constructor
   * @param {Object} options - Configuration options
   * @param {string} options.configPath - Path to feature flags configuration file
   * @param {Object} options.defaultFlags - Default feature flag values
   * @param {Function} options.onChange - Callback when flags change
   */
  constructor(options = {}) {
    this.configPath = options.configPath || '/app/config/feature_flags.json';
    this.defaultFlags = options.defaultFlags || {};
    this.onChange = options.onChange || (() => {});
    this.flags = { ...this.defaultFlags };
    this.userOverrides = new Map();
    this.percentageRollouts = new Map();
    
    // Load flags from configuration
    this.loadFlags();
  }

  /**
   * Load feature flags from configuration
   * @private
   */
  loadFlags() {
    try {
      // In a browser environment, fetch the configuration
      if (typeof window !== 'undefined') {
        fetch(this.configPath)
          .then(response => response.json())
          .then(data => {
            this.flags = { ...this.defaultFlags, ...data };
            this.onChange(this.flags);
          })
          .catch(error => {
            console.error('Error loading feature flags:', error);
          });
      } 
      // In a Node.js environment, require the configuration
      else if (typeof require !== 'undefined') {
        try {
          const fs = require('fs');
          const data = JSON.parse(fs.readFileSync(this.configPath, 'utf8'));
          this.flags = { ...this.defaultFlags, ...data };
          this.onChange(this.flags);
        } catch (error) {
          console.error('Error loading feature flags:', error);
        }
      }
    } catch (error) {
      console.error('Error loading feature flags:', error);
    }
  }

  /**
   * Check if a feature flag is enabled
   * @param {string} flagName - Name of the feature flag
   * @param {Object} context - Context for the flag check (e.g., user information)
   * @returns {boolean} Whether the flag is enabled
   */
  isEnabled(flagName, context = {}) {
    // Check for user override
    if (context.userId && this.userOverrides.has(flagName)) {
      const userIds = this.userOverrides.get(flagName);
      if (userIds.includes(context.userId)) {
        return true;
      }
    }
    
    // Check for percentage rollout
    if (this.percentageRollouts.has(flagName) && context.userId) {
      const percentage = this.percentageRollouts.get(flagName);
      const hash = this.hashString(`${flagName}:${context.userId}`);
      const normalizedHash = hash % 100;
      if (normalizedHash < percentage) {
        return true;
      }
    }
    
    // Check for environment override
    if (context.environment && this.flags[`${flagName}_${context.environment}`] !== undefined) {
      return !!this.flags[`${flagName}_${context.environment}`];
    }
    
    // Default flag value
    return !!this.flags[flagName];
  }

  /**
   * Enable a feature flag
   * @param {string} flagName - Name of the feature flag
   * @param {Object} options - Options for enabling the flag
   * @param {string} options.environment - Environment to enable the flag in (optional)
   * @returns {void}
   */
  enable(flagName, options = {}) {
    if (options.environment) {
      this.flags[`${flagName}_${options.environment}`] = true;
    } else {
      this.flags[flagName] = true;
    }
    this.onChange(this.flags);
  }

  /**
   * Disable a feature flag
   * @param {string} flagName - Name of the feature flag
   * @param {Object} options - Options for disabling the flag
   * @param {string} options.environment - Environment to disable the flag in (optional)
   * @returns {void}
   */
  disable(flagName, options = {}) {
    if (options.environment) {
      this.flags[`${flagName}_${options.environment}`] = false;
    } else {
      this.flags[flagName] = false;
    }
    this.onChange(this.flags);
  }

  /**
   * Enable a feature flag for specific users
   * @param {string} flagName - Name of the feature flag
   * @param {string[]} userIds - Array of user IDs
   * @returns {void}
   */
  enableForUsers(flagName, userIds) {
    this.userOverrides.set(flagName, userIds);
    this.onChange(this.flags);
  }

  /**
   * Set percentage rollout for a feature flag
   * @param {string} flagName - Name of the feature flag
   * @param {number} percentage - Percentage of users to enable the flag for (0-100)
   * @returns {void}
   */
  setPercentageRollout(flagName, percentage) {
    if (percentage < 0 || percentage > 100) {
      throw new Error('Percentage must be between 0 and 100');
    }
    this.percentageRollouts.set(flagName, percentage);
    this.onChange(this.flags);
  }

  /**
   * Get all feature flags
   * @returns {Object} All feature flags
   */
  getAllFlags() {
    return { ...this.flags };
  }

  /**
   * Save feature flags to configuration
   * @returns {Promise<void>}
   */
  async saveFlags() {
    try {
      // In a Node.js environment, write to the configuration file
      if (typeof require !== 'undefined') {
        const fs = require('fs');
        fs.writeFileSync(this.configPath, JSON.stringify(this.flags, null, 2), 'utf8');
      } 
      // In a browser environment, send to an API endpoint
      else if (typeof window !== 'undefined') {
        await fetch('/api/feature-flags', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(this.flags),
        });
      }
    } catch (error) {
      console.error('Error saving feature flags:', error);
      throw error;
    }
  }

  /**
   * Simple string hash function
   * @private
   * @param {string} str - String to hash
   * @returns {number} Hash value
   */
  hashString(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32bit integer
    }
    return Math.abs(hash);
  }
}

// Export singleton instance
const featureFlags = new FeatureFlagManager({
  defaultFlags: {
    enableNewUI: false,
    enablePluginSystem: false,
    enablePerformanceMetrics: false,
    enableDebugMode: false,
  },
  onChange: (flags) => {
    console.log('Feature flags updated:', flags);
  },
});

export default featureFlags;

// React hook for using feature flags
export const useFeatureFlag = (flagName, context = {}) => {
  const [isEnabled, setIsEnabled] = React.useState(featureFlags.isEnabled(flagName, context));

  React.useEffect(() => {
    const handleChange = () => {
      setIsEnabled(featureFlags.isEnabled(flagName, context));
    };

    // Subscribe to changes
    const originalOnChange = featureFlags.onChange;
    featureFlags.onChange = (flags) => {
      originalOnChange(flags);
      handleChange();
    };

    // Cleanup
    return () => {
      featureFlags.onChange = originalOnChange;
    };
  }, [flagName, context]);

  return isEnabled;
};
