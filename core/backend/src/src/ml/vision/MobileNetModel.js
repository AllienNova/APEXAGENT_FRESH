/**
 * MobileNetModel.js
 * Implementation of MobileNet vision model for Aideon AI Lite
 * Provides efficient local image recognition and classification
 */

const MLModel = require('../MLModel');
const tf = require('@tensorflow/tfjs-node');
const fs = require('fs');
const path = require('path');
const { createCanvas, loadImage } = require('canvas');

class MobileNetModel extends MLModel {
  /**
   * Create a new MobileNet model
   * @param {Object} provider - Provider instance
   * @param {Object} options - Model options
   */
  constructor(provider, options) {
    super(provider, options);
    
    this.modelPath = path.join(provider.modelPath, `${this.version}`);
    this.inputSize = options.requirements?.inputSize || 224;
    this.quantized = options.requirements?.quantized !== false;
    this.alpha = options.requirements?.alpha || 1.0;
    
    this.model = null;
    this.labels = null;
    this.imageCache = new Map();
    this.maxCacheSize = 100;
  }
  
  /**
   * Initialize the model
   * @returns {Promise<boolean>} Success status
   * @protected
   */
  async _initialize() {
    try {
      // Ensure model directory exists
      if (!fs.existsSync(this.modelPath)) {
        fs.mkdirSync(this.modelPath, { recursive: true });
      }
      
      // Load model
      await this._loadModel();
      
      // Load labels
      await this._loadLabels();
      
      return true;
    } catch (error) {
      this.logger.error(`Failed to initialize MobileNet model: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Execute the model
   * @param {Object} params - Model parameters
   * @param {string|Buffer} params.image - Image path or buffer
   * @param {number} params.topK - Number of top predictions to return
   * @param {number} params.threshold - Confidence threshold
   * @param {boolean} params.includeFeatures - Whether to include feature vectors
   * @param {Object} options - Execution options
   * @returns {Promise<Object>} Model result
   * @protected
   */
  async _execute(params, options = {}) {
    try {
      const { 
        image, 
        topK = 5, 
        threshold = 0.1, 
        includeFeatures = false 
      } = params;
      
      // Preprocess image
      const tensor = await this._preprocessImage(image);
      
      // Get predictions
      const predictions = await this._predict(tensor, topK, threshold);
      
      // Get feature vector if requested
      let features = null;
      if (includeFeatures) {
        features = await this._extractFeatures(tensor);
      }
      
      // Dispose tensor to free memory
      tensor.dispose();
      
      return {
        predictions,
        features: features ? Array.from(features.dataSync()) : null,
        modelInfo: {
          id: this.id,
          name: this.name,
          version: this.version
        }
      };
    } catch (error) {
      this.logger.error(`Error executing MobileNet model: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Load the MobileNet model
   * @returns {Promise<void>}
   * @private
   */
  async _loadModel() {
    try {
      const modelFilePath = path.join(this.modelPath, 'model.json');
      
      // Check if model exists locally
      if (fs.existsSync(modelFilePath)) {
        this.logger.info(`Loading MobileNet model from ${modelFilePath}`);
        this.model = await tf.loadLayersModel(`file://${modelFilePath}`);
      } else {
        // Download model if not available locally
        this.logger.info(`Downloading MobileNet model (${this.version})`);
        
        // Determine model URL based on version and parameters
        const modelUrl = this._getModelUrl();
        
        // Load model from URL
        this.model = await tf.loadLayersModel(modelUrl);
        
        // Save model locally for future use
        await this.model.save(`file://${this.modelPath}`);
        this.logger.info(`Saved MobileNet model to ${this.modelPath}`);
      }
      
      // Warm up the model
      const dummyInput = tf.zeros([1, this.inputSize, this.inputSize, 3]);
      await this.model.predict(dummyInput);
      dummyInput.dispose();
      
      this.logger.info(`MobileNet model loaded successfully`);
    } catch (error) {
      this.logger.error(`Failed to load MobileNet model: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Load classification labels
   * @returns {Promise<void>}
   * @private
   */
  async _loadLabels() {
    try {
      const labelsFilePath = path.join(this.modelPath, 'labels.json');
      
      // Check if labels exist locally
      if (fs.existsSync(labelsFilePath)) {
        this.logger.info(`Loading labels from ${labelsFilePath}`);
        this.labels = JSON.parse(fs.readFileSync(labelsFilePath, 'utf8'));
      } else {
        // Download labels if not available locally
        this.logger.info(`Downloading ImageNet labels`);
        
        // In a real implementation, this would fetch from a URL
        // For now, we'll use a subset of ImageNet labels
        this.labels = [
          'background', 'tench', 'goldfish', 'great white shark', 'tiger shark',
          'hammerhead', 'electric ray', 'stingray', 'cock', 'hen',
          // ... more labels would be included in a real implementation
        ];
        
        // Save labels locally for future use
        fs.writeFileSync(labelsFilePath, JSON.stringify(this.labels));
        this.logger.info(`Saved labels to ${labelsFilePath}`);
      }
      
      this.logger.info(`Loaded ${this.labels.length} classification labels`);
    } catch (error) {
      this.logger.error(`Failed to load labels: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Preprocess image for model input
   * @param {string|Buffer} image - Image path or buffer
   * @returns {Promise<tf.Tensor>} Preprocessed image tensor
   * @private
   */
  async _preprocessImage(image) {
    try {
      // Check cache first
      const cacheKey = typeof image === 'string' ? image : image.toString('base64').substring(0, 100);
      if (this.imageCache.has(cacheKey)) {
        return this.imageCache.get(cacheKey).clone();
      }
      
      // Load image
      let img;
      if (typeof image === 'string') {
        // Load from file path
        img = await loadImage(image);
      } else {
        // Load from buffer
        img = await loadImage(image);
      }
      
      // Create canvas and draw image
      const canvas = createCanvas(this.inputSize, this.inputSize);
      const ctx = canvas.getContext('2d');
      
      // Calculate resize dimensions while maintaining aspect ratio
      const scale = Math.max(this.inputSize / img.width, this.inputSize / img.height);
      const width = Math.round(img.width * scale);
      const height = Math.round(img.height * scale);
      
      // Center image on canvas
      const offsetX = (this.inputSize - width) / 2;
      const offsetY = (this.inputSize - height) / 2;
      
      // Draw image on canvas
      ctx.fillStyle = '#000000';
      ctx.fillRect(0, 0, this.inputSize, this.inputSize);
      ctx.drawImage(img, offsetX, offsetY, width, height);
      
      // Get image data
      const imageData = ctx.getImageData(0, 0, this.inputSize, this.inputSize);
      
      // Convert to tensor
      const tensor = tf.browser.fromPixels(imageData, 3)
        .toFloat()
        .div(tf.scalar(127.5))
        .sub(tf.scalar(1))
        .expandDims(0);
      
      // Cache tensor for future use
      this._updateCache(cacheKey, tensor.clone());
      
      return tensor;
    } catch (error) {
      this.logger.error(`Error preprocessing image: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Run prediction on preprocessed image
   * @param {tf.Tensor} tensor - Preprocessed image tensor
   * @param {number} topK - Number of top predictions to return
   * @param {number} threshold - Confidence threshold
   * @returns {Promise<Array>} Predictions
   * @private
   */
  async _predict(tensor, topK, threshold) {
    try {
      // Run prediction
      const predictions = await this.model.predict(tensor);
      const data = predictions.dataSync();
      
      // Get top K predictions
      const indices = [];
      for (let i = 0; i < data.length; i++) {
        indices.push({ index: i, value: data[i] });
      }
      
      // Sort by confidence
      indices.sort((a, b) => b.value - a.value);
      
      // Filter by threshold and limit to topK
      const result = indices
        .filter(item => item.value >= threshold)
        .slice(0, topK)
        .map(item => ({
          label: this.labels[item.index],
          confidence: item.value,
          index: item.index
        }));
      
      // Dispose predictions tensor
      predictions.dispose();
      
      return result;
    } catch (error) {
      this.logger.error(`Error running prediction: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Extract feature vector from preprocessed image
   * @param {tf.Tensor} tensor - Preprocessed image tensor
   * @returns {Promise<tf.Tensor>} Feature vector
   * @private
   */
  async _extractFeatures(tensor) {
    try {
      // Get the second-to-last layer for feature extraction
      const featureModel = tf.model({
        inputs: this.model.inputs,
        outputs: this.model.layers[this.model.layers.length - 2].output
      });
      
      // Extract features
      const features = featureModel.predict(tensor);
      
      return features;
    } catch (error) {
      this.logger.error(`Error extracting features: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Get model URL based on version and parameters
   * @returns {string} Model URL
   * @private
   */
  _getModelUrl() {
    // In a real implementation, this would return the actual URL
    // For now, we'll use a placeholder
    return `https://storage.googleapis.com/tfjs-models/tfjs/mobilenet_v${this.version.replace('v', '')}_${this.alpha * 100}_${this.inputSize}/${this.quantized ? 'quant' : 'float'}/model.json`;
  }
  
  /**
   * Update image cache
   * @param {string} key - Cache key
   * @param {tf.Tensor} tensor - Image tensor
   * @private
   */
  _updateCache(key, tensor) {
    // Add to cache
    this.imageCache.set(key, tensor);
    
    // Limit cache size
    if (this.imageCache.size > this.maxCacheSize) {
      const oldestKey = this.imageCache.keys().next().value;
      const oldestTensor = this.imageCache.get(oldestKey);
      oldestTensor.dispose();
      this.imageCache.delete(oldestKey);
    }
  }
  
  /**
   * Validate model parameters
   * @param {Object} params - Model parameters
   * @protected
   */
  _validateParams(params) {
    if (!params) {
      throw new Error('Model parameters are required');
    }
    
    if (!params.image) {
      throw new Error('Image parameter is required');
    }
  }
}

module.exports = MobileNetModel;
