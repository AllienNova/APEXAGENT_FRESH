/**
 * YOLOProvider.js
 * Provider for YOLO object detection models in Aideon AI Lite
 * Enables efficient local object detection and recognition
 */

const MLModelProvider = require('../MLModelProvider');
const YOLOModel = require('./YOLOModel');
const fs = require('fs');
const path = require('path');

class YOLOProvider extends MLModelProvider {
  /**
   * Create a new YOLO provider
   * @param {Object} core - Core system reference
   */
  constructor(core) {
    super(core);
    
    this.modelPath = this.config.modelPath || path.join(core.paths.models, 'vision', 'yolo');
    this.modelVersion = this.config.modelVersion || 'yolov8n';
    this.confidenceThreshold = this.config.confidenceThreshold || 0.25;
    this.iouThreshold = this.config.iouThreshold || 0.45;
  }
  
  /**
   * Get provider ID
   * @returns {string} Provider ID
   */
  get id() {
    return 'yolo';
  }
  
  /**
   * Get provider name
   * @returns {string} Provider name
   */
  get name() {
    return 'YOLO Object Detection';
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
      
      // Register YOLO model
      const model = new YOLOModel(this, {
        id: `yolo-${this.modelVersion}`,
        name: `YOLO ${this.modelVersion.toUpperCase()}`,
        type: 'vision',
        version: this.modelVersion,
        isLocal: true,
        capabilities: {
          objectDetection: true,
          instanceSegmentation: this.modelVersion.includes('seg'),
          poseEstimation: this.modelVersion.includes('pose'),
          batchProcessing: true
        },
        requirements: {
          confidenceThreshold: this.confidenceThreshold,
          iouThreshold: this.iouThreshold
        }
      });
      
      this.models.push(model);
      this.visionModels.push(model);
      
      this.logger.info(`Registered YOLO model: ${model.name} (${model.id})`);
    } catch (error) {
      this.logger.error('Failed to register YOLO models:', error);
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
    const validVersions = ['yolov8n', 'yolov8s', 'yolov8m', 'yolov8l', 'yolov8x', 
                          'yolov8n-seg', 'yolov8s-seg', 'yolov8m-seg', 'yolov8l-seg', 'yolov8x-seg',
                          'yolov8n-pose', 'yolov8s-pose', 'yolov8m-pose', 'yolov8l-pose', 'yolov8x-pose'];
    if (!validVersions.includes(this.modelVersion)) {
      this.logger.error(`Invalid YOLO version: ${this.modelVersion}. Valid versions: ${validVersions.join(', ')}`);
      return false;
    }
    
    // Validate confidence threshold
    if (this.confidenceThreshold < 0 || this.confidenceThreshold > 1) {
      this.logger.error(`Invalid confidence threshold: ${this.confidenceThreshold}. Must be between 0 and 1.`);
      return false;
    }
    
    // Validate IoU threshold
    if (this.iouThreshold < 0 || this.iouThreshold > 1) {
      this.logger.error(`Invalid IoU threshold: ${this.iouThreshold}. Must be between 0 and 1.`);
      return false;
    }
    
    return true;
  }
}

module.exports = YOLOProvider;
