/**
 * MobileNetProvider.js
 * Provider for MobileNet vision models in Aideon AI Lite
 * Enables efficient local image recognition and classification
 */

const MLModelProvider = require('../MLModelProvider');
const MobileNetModel = require('./MobileNetModel');
const fs = require('fs');
const path = require('path');

class MobileNetProvider extends MLModelProvider {
  /**
   * Create a new MobileNet provider
   * @param {Object} core - Core system reference
   */
  constructor(core) {
    super(core);
    
    this.modelPath = this.config.modelPath || path.join(core.paths.models, 'vision', 'mobilenet');
    this.modelVersion = this.config.modelVersion || 'v2';
    this.modelVariant = this.config.modelVariant || '1.0';
    this.inputSize = this.config.inputSize || 224;
    this.quantized = this.config.quantized !== false;
    this.alpha = this.config.alpha || 1.0;
  }
  
  /**
   * Get provider ID
   * @returns {string} Provider ID
   */
  get id() {
    return 'mobilenet';
  }
  
  /**
   * Get provider name
   * @returns {string} Provider name
   */
  get name() {
    return 'MobileNet Vision';
  }
  
  /**
   * Register models provided by this provider
   * @returns {Promise<void>}
   * @protected
   */
  async _registerModels() {
    try {
      // Ensure model directory exists
      if (!fs.existsSync(this.modelPath)) {
        fs.mkdirSync(this.modelPath, { recursive: true });
      }
      
      // Register MobileNet model
      const model = new MobileNetModel(this, {
        id: `mobilenet-${this.modelVersion}-${this.modelVariant}`,
        name: `MobileNet ${this.modelVersion.toUpperCase()} (${this.modelVariant})`,
        type: 'vision',
        version: `${this.modelVersion}-${this.modelVariant}`,
        isLocal: true,
        capabilities: {
          imageClassification: true,
          featureExtraction: true,
          batchProcessing: true,
          realTimeProcessing: true
        },
        requirements: {
          inputSize: this.inputSize,
          quantized: this.quantized,
          alpha: this.alpha
        }
      });
      
      this.models.push(model);
      this.visionModels.push(model);
      
      this.logger.info(`Registered MobileNet model: ${model.name} (${model.id})`);
    } catch (error) {
      this.logger.error('Failed to register MobileNet models:', error);
      throw error;
    }
  }
  
  /**
   * Validate provider configuration
   * @returns {boolean} Validation result
   * @protected
   */
  _validateConfig() {
    // Validate model version
    const validVersions = ['v1', 'v2', 'v3'];
    if (!validVersions.includes(this.modelVersion)) {
      this.logger.error(`Invalid MobileNet version: ${this.modelVersion}. Valid versions: ${validVersions.join(', ')}`);
      return false;
    }
    
    // Validate model variant
    const validVariants = ['1.0', '0.75', '0.5', '0.25'];
    if (!validVariants.includes(this.modelVariant)) {
      this.logger.error(`Invalid MobileNet variant: ${this.modelVariant}. Valid variants: ${validVariants.join(', ')}`);
      return false;
    }
    
    return true;
  }
}

module.exports = MobileNetProvider;
