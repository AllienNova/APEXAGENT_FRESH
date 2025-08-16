/**
 * YOLOModel.js
 * Implementation of YOLO object detection model for Aideon AI Lite
 * Provides efficient local object detection and recognition
 */

const MLModel = require('../MLModel');
const tf = require('@tensorflow/tfjs-node');
const fs = require('fs');
const path = require('path');
const { createCanvas, loadImage } = require('canvas');

class YOLOModel extends MLModel {
  /**
   * Create a new YOLO model
   * @param {Object} provider - Provider instance
   * @param {Object} options - Model options
   */
  constructor(provider, options) {
    super(provider, options);
    
    this.modelPath = path.join(provider.modelPath, `${this.version}`);
    this.confidenceThreshold = options.requirements?.confidenceThreshold || 0.25;
    this.iouThreshold = options.requirements?.iouThreshold || 0.45;
    this.inputSize = this._getInputSize();
    
    this.model = null;
    this.labels = null;
    this.imageCache = new Map();
    this.maxCacheSize = 50;
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
      this.logger.error(`Failed to initialize YOLO model: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Execute the model
   * @param {Object} params - Model parameters
   * @param {string|Buffer} params.image - Image path or buffer
   * @param {number} params.confidenceThreshold - Confidence threshold (optional, overrides default)
   * @param {number} params.iouThreshold - IoU threshold for NMS (optional, overrides default)
   * @param {boolean} params.includeSegmentation - Whether to include segmentation masks (optional)
   * @param {boolean} params.includePose - Whether to include pose keypoints (optional)
   * @param {Object} options - Execution options
   * @returns {Promise<Object>} Model result
   * @protected
   */
  async _execute(params, options = {}) {
    try {
      const { 
        image, 
        confidenceThreshold = this.confidenceThreshold, 
        iouThreshold = this.iouThreshold,
        includeSegmentation = false,
        includePose = false
      } = params;
      
      // Preprocess image
      const { tensor, originalSize } = await this._preprocessImage(image);
      
      // Run detection
      const detections = await this._detect(tensor, confidenceThreshold, iouThreshold);
      
      // Scale detections to original image size
      const scaledDetections = this._scaleDetections(detections, originalSize);
      
      // Process segmentation if requested and available
      let segmentations = null;
      if (includeSegmentation && this.capabilities.instanceSegmentation) {
        segmentations = await this._processSegmentations(detections, originalSize);
      }
      
      // Process pose keypoints if requested and available
      let poses = null;
      if (includePose && this.capabilities.poseEstimation) {
        poses = await this._processPoses(detections, originalSize);
      }
      
      // Dispose tensor to free memory
      tensor.dispose();
      
      return {
        detections: scaledDetections,
        segmentations,
        poses,
        modelInfo: {
          id: this.id,
          name: this.name,
          version: this.version
        }
      };
    } catch (error) {
      this.logger.error(`Error executing YOLO model: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Load the YOLO model
   * @returns {Promise<void>}
   * @private
   */
  async _loadModel() {
    try {
      const modelFilePath = path.join(this.modelPath, 'model.json');
      
      // Check if model exists locally
      if (fs.existsSync(modelFilePath)) {
        this.logger.info(`Loading YOLO model from ${modelFilePath}`);
        this.model = await tf.loadGraphModel(`file://${modelFilePath}`);
      } else {
        // Download model if not available locally
        this.logger.info(`Downloading YOLO model (${this.version})`);
        
        // Determine model URL based on version
        const modelUrl = this._getModelUrl();
        
        // Load model from URL
        this.model = await tf.loadGraphModel(modelUrl);
        
        // Save model locally for future use
        await this.model.save(`file://${this.modelPath}`);
        this.logger.info(`Saved YOLO model to ${this.modelPath}`);
      }
      
      // Warm up the model
      const dummyInput = tf.zeros([1, this.inputSize, this.inputSize, 3]);
      await this.model.predict(dummyInput);
      dummyInput.dispose();
      
      this.logger.info(`YOLO model loaded successfully`);
    } catch (error) {
      this.logger.error(`Failed to load YOLO model: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Load detection labels
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
        this.logger.info(`Downloading COCO labels`);
        
        // In a real implementation, this would fetch from a URL
        // For now, we'll use a subset of COCO labels
        this.labels = [
          'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train',
          'truck', 'boat', 'traffic light', 'fire hydrant', 'stop sign', 
          'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep',
          'cow', 'elephant', 'bear', 'zebra', 'giraffe', 'backpack', 'umbrella',
          'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball',
          'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard',
          'tennis racket', 'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon',
          'bowl', 'banana', 'apple', 'sandwich', 'orange', 'broccoli', 'carrot',
          'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch', 'potted plant',
          'bed', 'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote',
          'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink',
          'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear',
          'hair drier', 'toothbrush'
        ];
        
        // Save labels locally for future use
        fs.writeFileSync(labelsFilePath, JSON.stringify(this.labels));
        this.logger.info(`Saved labels to ${labelsFilePath}`);
      }
      
      this.logger.info(`Loaded ${this.labels.length} detection labels`);
    } catch (error) {
      this.logger.error(`Failed to load labels: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Preprocess image for model input
   * @param {string|Buffer} image - Image path or buffer
   * @returns {Promise<Object>} Preprocessed image tensor and original size
   * @private
   */
  async _preprocessImage(image) {
    try {
      // Check cache first
      const cacheKey = typeof image === 'string' ? image : image.toString('base64').substring(0, 100);
      if (this.imageCache.has(cacheKey)) {
        return this.imageCache.get(cacheKey);
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
      
      // Store original size
      const originalSize = {
        width: img.width,
        height: img.height
      };
      
      // Create canvas and draw image
      const canvas = createCanvas(this.inputSize, this.inputSize);
      const ctx = canvas.getContext('2d');
      
      // Calculate resize dimensions while maintaining aspect ratio
      const scale = Math.min(this.inputSize / img.width, this.inputSize / img.height);
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
      const tensor = tf.tidy(() => {
        const imageTensor = tf.browser.fromPixels(imageData);
        // Normalize to [0,1]
        return imageTensor.toFloat().div(tf.scalar(255)).expandDims(0);
      });
      
      const result = { tensor, originalSize, scale, offsetX, offsetY };
      
      // Cache result for future use
      this._updateCache(cacheKey, result);
      
      return result;
    } catch (error) {
      this.logger.error(`Error preprocessing image: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Run detection on preprocessed image
   * @param {tf.Tensor} tensor - Preprocessed image tensor
   * @param {number} confidenceThreshold - Confidence threshold
   * @param {number} iouThreshold - IoU threshold for NMS
   * @returns {Promise<Array>} Detections
   * @private
   */
  async _detect(tensor, confidenceThreshold, iouThreshold) {
    try {
      // Run model prediction
      const output = await this.model.predict(tensor);
      
      // Process output based on model version
      let boxes, scores, classes;
      
      if (this.version.includes('v8')) {
        // YOLOv8 output format
        const predictions = output[0].arraySync()[0];
        
        // Extract boxes, scores, and classes
        const results = [];
        for (let i = 0; i < predictions.length; i++) {
          const prediction = predictions[i];
          const score = prediction[4];
          
          if (score >= confidenceThreshold) {
            // Find class with highest confidence
            let maxClassScore = 0;
            let classId = 0;
            
            for (let j = 5; j < prediction.length; j++) {
              if (prediction[j] > maxClassScore) {
                maxClassScore = prediction[j];
                classId = j - 5;
              }
            }
            
            const confidence = score * maxClassScore;
            
            if (confidence >= confidenceThreshold) {
              // Extract bounding box
              const x = prediction[0];
              const y = prediction[1];
              const w = prediction[2];
              const h = prediction[3];
              
              results.push({
                box: [x - w/2, y - h/2, w, h], // [x, y, width, height]
                confidence,
                classId
              });
            }
          }
        }
        
        // Apply non-maximum suppression
        return this._applyNMS(results, iouThreshold);
      } else {
        // Generic YOLO output format
        // This would be implemented based on the specific model version
        throw new Error(`Unsupported YOLO version: ${this.version}`);
      }
    } catch (error) {
      this.logger.error(`Error running detection: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Apply non-maximum suppression to detections
   * @param {Array} detections - Raw detections
   * @param {number} iouThreshold - IoU threshold
   * @returns {Array} Filtered detections
   * @private
   */
  _applyNMS(detections, iouThreshold) {
    // Sort by confidence
    detections.sort((a, b) => b.confidence - a.confidence);
    
    const selected = [];
    const rejected = new Set();
    
    for (let i = 0; i < detections.length; i++) {
      if (rejected.has(i)) continue;
      
      selected.push(detections[i]);
      
      // Compare with remaining boxes
      for (let j = i + 1; j < detections.length; j++) {
        if (rejected.has(j)) continue;
        
        // Calculate IoU
        const iou = this._calculateIoU(detections[i].box, detections[j].box);
        
        // If IoU exceeds threshold and classes match, reject the box
        if (iou > iouThreshold && detections[i].classId === detections[j].classId) {
          rejected.add(j);
        }
      }
    }
    
    return selected;
  }
  
  /**
   * Calculate IoU between two bounding boxes
   * @param {Array} box1 - First box [x, y, width, height]
   * @param {Array} box2 - Second box [x, y, width, height]
   * @returns {number} IoU value
   * @private
   */
  _calculateIoU(box1, box2) {
    // Convert to [x1, y1, x2, y2] format
    const box1_x1 = box1[0];
    const box1_y1 = box1[1];
    const box1_x2 = box1[0] + box1[2];
    const box1_y2 = box1[1] + box1[3];
    
    const box2_x1 = box2[0];
    const box2_y1 = box2[1];
    const box2_x2 = box2[0] + box2[2];
    const box2_y2 = box2[1] + box2[3];
    
    // Calculate intersection area
    const x1 = Math.max(box1_x1, box2_x1);
    const y1 = Math.max(box1_y1, box2_y1);
    const x2 = Math.min(box1_x2, box2_x2);
    const y2 = Math.min(box1_y2, box2_y2);
    
    const intersectionWidth = Math.max(0, x2 - x1);
    const intersectionHeight = Math.max(0, y2 - y1);
    const intersectionArea = intersectionWidth * intersectionHeight;
    
    // Calculate union area
    const box1Area = box1[2] * box1[3];
    const box2Area = box2[2] * box2[3];
    const unionArea = box1Area + box2Area - intersectionArea;
    
    return intersectionArea / unionArea;
  }
  
  /**
   * Scale detections to original image size
   * @param {Array} detections - Detections in model input size
   * @param {Object} originalSize - Original image size
   * @returns {Array} Scaled detections
   * @private
   */
  _scaleDetections(detections, originalSize) {
    return detections.map(detection => {
      // Get label
      const label = this.labels[detection.classId];
      
      // Scale box to original image size
      const [x, y, width, height] = detection.box;
      
      // Calculate scale factors
      const scaleX = originalSize.width / this.inputSize;
      const scaleY = originalSize.height / this.inputSize;
      
      // Scale box
      const scaledBox = [
        x * scaleX,
        y * scaleY,
        width * scaleX,
        height * scaleY
      ];
      
      return {
        box: scaledBox,
        label,
        confidence: detection.confidence,
        classId: detection.classId
      };
    });
  }
  
  /**
   * Process segmentation masks
   * @param {Array} detections - Detections
   * @param {Object} originalSize - Original image size
   * @returns {Promise<Array>} Segmentation masks
   * @private
   */
  async _processSegmentations(detections, originalSize) {
    // In a real implementation, this would process segmentation masks
    // For this example, we'll return placeholder data
    return detections.map(detection => ({
      classId: detection.classId,
      label: this.labels[detection.classId],
      confidence: detection.confidence,
      mask: `Simulated segmentation mask for ${this.labels[detection.classId]}`
    }));
  }
  
  /**
   * Process pose keypoints
   * @param {Array} detections - Detections
   * @param {Object} originalSize - Original image size
   * @returns {Promise<Array>} Pose keypoints
   * @private
   */
  async _processPoses(detections, originalSize) {
    // In a real implementation, this would process pose keypoints
    // For this example, we'll return placeholder data
    return detections
      .filter(detection => detection.classId === 0) // Only process 'person' class
      .map(detection => ({
        box: detection.box,
        confidence: detection.confidence,
        keypoints: [
          { x: detection.box[0] + detection.box[2] * 0.5, y: detection.box[1] + detection.box[3] * 0.1, confidence: 0.9, name: 'nose' },
          { x: detection.box[0] + detection.box[2] * 0.4, y: detection.box[1] + detection.box[3] * 0.2, confidence: 0.85, name: 'left_eye' },
          { x: detection.box[0] + detection.box[2] * 0.6, y: detection.box[1] + detection.box[3] * 0.2, confidence: 0.85, name: 'right_eye' },
          // Additional keypoints would be included in a real implementation
        ]
      }));
  }
  
  /**
   * Get model URL based on version
   * @returns {string} Model URL
   * @private
   */
  _getModelUrl() {
    // In a real implementation, this would return the actual URL
    // For now, we'll use a placeholder
    return `https://github.com/ultralytics/assets/releases/download/v0.0.0/${this.version}.onnx`;
  }
  
  /**
   * Get input size based on model version
   * @returns {number} Input size
   * @private
   */
  _getInputSize() {
    // YOLOv8 uses 640x640 input size by default
    return 640;
  }
  
  /**
   * Update image cache
   * @param {string} key - Cache key
   * @param {Object} data - Processed image data
   * @private
   */
  _updateCache(key, data) {
    // Add to cache
    this.imageCache.set(key, data);
    
    // Limit cache size
    if (this.imageCache.size > this.maxCacheSize) {
      const oldestKey = this.imageCache.keys().next().value;
      const oldestData = this.imageCache.get(oldestKey);
      
      // Dispose tensor if it exists
      if (oldestData.tensor) {
        oldestData.tensor.dispose();
      }
      
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

module.exports = YOLOModel;
