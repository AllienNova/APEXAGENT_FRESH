/**
 * WhisperProvider.js
 * Provider for Whisper speech recognition models in Aideon AI Lite
 * Enables efficient local speech-to-text capabilities
 */

const MLModelProvider = require('../MLModelProvider');
const WhisperModel = require('./WhisperModel');
const fs = require('fs');
const path = require('path');

class WhisperProvider extends MLModelProvider {
  /**
   * Create a new Whisper provider
   * @param {Object} core - Core system reference
   */
  constructor(core) {
    super(core);
    
    this.modelPath = this.config.modelPath || path.join(core.paths.models, 'audio', 'whisper');
    this.modelVersion = this.config.modelVersion || 'small';
    this.language = this.config.language || 'en';
    this.multilingual = this.config.multilingual !== false;
  }
  
  /**
   * Get provider ID
   * @returns {string} Provider ID
   */
  get id() {
    return 'whisper';
  }
  
  /**
   * Get provider name
   * @returns {string} Provider name
   */
  get name() {
    return 'Whisper Speech Recognition';
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
      
      // Register Whisper model
      const model = new WhisperModel(this, {
        id: `whisper-${this.modelVersion}`,
        name: `Whisper ${this.modelVersion.charAt(0).toUpperCase() + this.modelVersion.slice(1)}`,
        type: 'audio',
        version: this.modelVersion,
        isLocal: true,
        capabilities: {
          speechRecognition: true,
          languageDetection: this.multilingual,
          timestampGeneration: true,
          batchProcessing: true,
          streamingProcessing: this.modelVersion === 'tiny' || this.modelVersion === 'base'
        },
        requirements: {
          language: this.language,
          multilingual: this.multilingual
        }
      });
      
      this.models.push(model);
      this.audioModels.push(model);
      
      this.logger.info(`Registered Whisper model: ${model.name} (${model.id})`);
    } catch (error) {
      this.logger.error('Failed to register Whisper models:', error);
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
    const validVersions = ['tiny', 'base', 'small', 'medium', 'large'];
    if (!validVersions.includes(this.modelVersion)) {
      this.logger.error(`Invalid Whisper version: ${this.modelVersion}. Valid versions: ${validVersions.join(', ')}`);
      return false;
    }
    
    return true;
  }
}

module.exports = WhisperProvider;
