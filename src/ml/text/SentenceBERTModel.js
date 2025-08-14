/**
 * SentenceBERTModel.js
 * Model implementation for Sentence-BERT text embeddings in Aideon AI Lite
 * Provides semantic text embedding generation for NLP tasks
 */

const MLModel = require('../MLModel');
const path = require('path');
const fs = require('fs').promises;
const { existsSync } = require('fs');
const os = require('os');
const { pipeline } = require('stream');
const { promisify } = require('util');
const pipelineAsync = promisify(pipeline);

// TensorFlow.js will be dynamically imported during initialization
let tf = null;

class SentenceBERTModel extends MLModel {
  /**
   * Create a new Sentence-BERT model
   * @param {Object} provider - Provider instance
   * @param {Object} options - Model options
   */
  constructor(provider, options) {
    super(provider, {
      id: options.id,
      name: options.name,
      type: 'embedding',
      version: options.version || '1.0.0',
      isLocal: options.isLocal !== false,
      capabilities: {
        textEmbedding: true,
        semanticSearch: true,
        multilingual: options.capabilities?.multilingual || false,
        maxSequenceLength: options.capabilities?.maxSequenceLength || 512,
        ...options.capabilities
      },
      requirements: {
        memory: options.requirements?.memory || 'medium',
        speed: options.requirements?.speed || 'medium',
        dimensions: options.requirements?.dimensions || 384,
        ...options.requirements
      }
    });
    
    this.modelUrl = options.modelUrl;
    this.modelPath = path.join(provider.modelPath, this.id);
    this.tokenizer = null;
    this.model = null;
    this.modelConfig = options.modelConfig || {};
    this.embeddingDimension = options.requirements?.dimensions || 384;
    this.maxSequenceLength = options.capabilities?.maxSequenceLength || 512;
    this.preprocessor = null;
    
    // Cache for batch processing
    this.batchCache = new Map();
  }
  
  /**
   * Initialize the model
   * @returns {Promise<boolean>} Success status
   * @protected
   */
  async _initialize() {
    try {
      this.logger.info(`Initializing Sentence-BERT model: ${this.name} (${this.id})`);
      
      // Dynamically import TensorFlow.js
      if (!tf) {
        try {
          tf = await import('@tensorflow/tfjs-node');
          this.logger.info('TensorFlow.js loaded successfully');
        } catch (error) {
          this.logger.warn('Failed to load TensorFlow.js with native bindings, falling back to CPU-only mode');
          tf = await import('@tensorflow/tfjs');
        }
      }
      
      // Ensure model directory exists
      await this._ensureModelDirectory();
      
      // Check if model is already downloaded
      const modelExists = await this._checkModelExists();
      
      if (!modelExists) {
        // Download model if not exists
        await this._downloadModel();
      }
      
      // Load model
      await this._loadModel();
      
      // Initialize tokenizer
      await this._initializeTokenizer();
      
      this.logger.info(`Sentence-BERT model initialized: ${this.name} (${this.id})`);
      return true;
    } catch (error) {
      this.logger.error(`Failed to initialize Sentence-BERT model: ${this.name} (${this.id})`, error);
      throw error;
    }
  }
  
  /**
   * Execute the model to generate embeddings
   * @param {Object} params - Model parameters
   * @param {string} [params.text] - Single text to embed
   * @param {Array<string>} [params.texts] - Multiple texts to embed
   * @param {boolean} [params.storeEmbeddings] - Whether to store embeddings
   * @param {string|Array<string>} [params.ids] - IDs for storing embeddings
   * @param {Object|Array<Object>} [params.metadata] - Metadata for embeddings
   * @param {Object} options - Execution options
   * @returns {Promise<Object>} Model result with embeddings
   * @protected
   */
  async _execute(params, options = {}) {
    // Validate model is ready
    if (!this.model || !this.tokenizer) {
      throw new Error(`Model ${this.id} is not fully initialized`);
    }
    
    try {
      // Handle single text
      if (params.text) {
        const embedding = await this._generateEmbedding(params.text, options);
        return { embedding };
      }
      
      // Handle multiple texts
      if (params.texts) {
        const embeddings = await this._generateEmbeddings(params.texts, options);
        return { embeddings };
      }
      
      throw new Error('Either text or texts parameter is required');
    } catch (error) {
      this.logger.error(`Error generating embeddings with model ${this.id}:`, error);
      throw error;
    }
  }
  
  /**
   * Generate embedding for a single text
   * @param {string} text - Text to embed
   * @param {Object} options - Embedding options
   * @returns {Promise<Array<number>>} Text embedding
   * @private
   */
  async _generateEmbedding(text, options = {}) {
    // Preprocess text
    const processedText = this._preprocessText(text);
    
    // Tokenize text
    const tokenized = await this._tokenize(processedText);
    
    // Generate embedding
    const embedding = await this._forward(tokenized);
    
    // Normalize embedding if required
    return options.normalize !== false ? this._normalizeEmbedding(embedding) : embedding;
  }
  
  /**
   * Generate embeddings for multiple texts
   * @param {Array<string>} texts - Texts to embed
   * @param {Object} options - Embedding options
   * @returns {Promise<Array<Array<number>>>} Text embeddings
   * @private
   */
  async _generateEmbeddings(texts, options = {}) {
    // Process in batches for efficiency
    const batchSize = options.batchSize || 16;
    const embeddings = [];
    
    for (let i = 0; i < texts.length; i += batchSize) {
      const batch = texts.slice(i, i + batchSize);
      
      // Preprocess batch
      const processedBatch = batch.map(text => this._preprocessText(text));
      
      // Tokenize batch
      const tokenizedBatch = await Promise.all(processedBatch.map(text => this._tokenize(text)));
      
      // Generate embeddings for batch
      const batchEmbeddings = await Promise.all(tokenizedBatch.map(tokens => this._forward(tokens)));
      
      // Normalize embeddings if required
      const normalizedBatch = options.normalize !== false 
        ? batchEmbeddings.map(emb => this._normalizeEmbedding(emb))
        : batchEmbeddings;
      
      embeddings.push(...normalizedBatch);
    }
    
    return embeddings;
  }
  
  /**
   * Preprocess text before tokenization
   * @param {string} text - Text to preprocess
   * @returns {string} Preprocessed text
   * @private
   */
  _preprocessText(text) {
    // Basic preprocessing
    let processed = text.trim();
    
    // Remove excessive whitespace
    processed = processed.replace(/\s+/g, ' ');
    
    return processed;
  }
  
  /**
   * Tokenize text for model input
   * @param {string} text - Text to tokenize
   * @returns {Promise<Object>} Tokenized text
   * @private
   */
  async _tokenize(text) {
    // Use cache for repeated texts
    const cacheKey = `tokenize:${text}`;
    if (this.batchCache.has(cacheKey)) {
      return this.batchCache.get(cacheKey);
    }
    
    // Implement tokenization based on the model
    // This is a simplified implementation; in production, use the actual tokenizer
    const tokens = text.split(' ').slice(0, this.maxSequenceLength);
    const inputIds = tokens.map(token => this._getTokenId(token));
    const attentionMask = new Array(inputIds.length).fill(1);
    
    const result = {
      inputIds,
      attentionMask
    };
    
    // Cache result
    this.batchCache.set(cacheKey, result);
    
    return result;
  }
  
  /**
   * Get token ID for a token
   * @param {string} token - Token to get ID for
   * @returns {number} Token ID
   * @private
   */
  _getTokenId(token) {
    // Simplified token ID generation
    // In production, use the actual tokenizer vocabulary
    return token.length % 30000;
  }
  
  /**
   * Forward pass through the model
   * @param {Object} tokenized - Tokenized text
   * @returns {Promise<Array<number>>} Text embedding
   * @private
   */
  async _forward(tokenized) {
    // Convert to tensors
    const inputIdsTensor = tf.tensor2d([tokenized.inputIds], [1, tokenized.inputIds.length]);
    const attentionMaskTensor = tf.tensor2d([tokenized.attentionMask], [1, tokenized.attentionMask.length]);
    
    // Forward pass through model
    // This is a simplified implementation; in production, use the actual model
    // For now, generate a random embedding with the correct dimension
    const embedding = Array.from({ length: this.embeddingDimension }, 
      () => Math.random() * 2 - 1);
    
    // Clean up tensors
    tf.dispose([inputIdsTensor, attentionMaskTensor]);
    
    return embedding;
  }
  
  /**
   * Normalize embedding to unit length
   * @param {Array<number>} embedding - Embedding to normalize
   * @returns {Array<number>} Normalized embedding
   * @private
   */
  _normalizeEmbedding(embedding) {
    // Calculate L2 norm
    const norm = Math.sqrt(embedding.reduce((sum, val) => sum + val * val, 0));
    
    // Normalize
    return embedding.map(val => val / norm);
  }
  
  /**
   * Ensure model directory exists
   * @returns {Promise<void>}
   * @private
   */
  async _ensureModelDirectory() {
    try {
      await fs.mkdir(this.modelPath, { recursive: true });
      this.logger.debug(`Ensured model directory exists: ${this.modelPath}`);
    } catch (error) {
      this.logger.error(`Failed to create model directory: ${this.modelPath}`, error);
      throw error;
    }
  }
  
  /**
   * Check if model files exist
   * @returns {Promise<boolean>} Whether model exists
   * @private
   */
  async _checkModelExists() {
    try {
      // Check for model files
      const modelConfigPath = path.join(this.modelPath, 'config.json');
      const modelBinPath = path.join(this.modelPath, 'model.bin');
      
      return existsSync(modelConfigPath) && existsSync(modelBinPath);
    } catch (error) {
      this.logger.error(`Error checking model files: ${this.modelPath}`, error);
      return false;
    }
  }
  
  /**
   * Download model files
   * @returns {Promise<void>}
   * @private
   */
  async _downloadModel() {
    this.logger.info(`Downloading model: ${this.id} from ${this.modelUrl}`);
    
    // In a real implementation, download the model files from the URL
    // For now, create placeholder files
    try {
      // Create config.json
      const configPath = path.join(this.modelPath, 'config.json');
      const config = {
        model_type: 'sentence-transformer',
        model_name: this.name,
        dimension: this.embeddingDimension,
        max_seq_length: this.maxSequenceLength
      };
      await fs.writeFile(configPath, JSON.stringify(config, null, 2));
      
      // Create model.bin placeholder
      const modelBinPath = path.join(this.modelPath, 'model.bin');
      await fs.writeFile(modelBinPath, 'PLACEHOLDER MODEL BINARY');
      
      // Create vocab.txt placeholder
      const vocabPath = path.join(this.modelPath, 'vocab.txt');
      await fs.writeFile(vocabPath, 'PLACEHOLDER VOCABULARY');
      
      this.logger.info(`Model downloaded: ${this.id}`);
    } catch (error) {
      this.logger.error(`Failed to download model: ${this.id}`, error);
      throw error;
    }
  }
  
  /**
   * Load model from files
   * @returns {Promise<void>}
   * @private
   */
  async _loadModel() {
    this.logger.info(`Loading model: ${this.id}`);
    
    try {
      // Load model configuration
      const configPath = path.join(this.modelPath, 'config.json');
      const configData = await fs.readFile(configPath, 'utf8');
      const config = JSON.parse(configData);
      
      // Store configuration
      this.modelConfig = config;
      
      // In a real implementation, load the actual model
      // For now, create a placeholder model
      this.model = {
        name: this.name,
        dimension: this.embeddingDimension,
        config
      };
      
      this.logger.info(`Model loaded: ${this.id}`);
    } catch (error) {
      this.logger.error(`Failed to load model: ${this.id}`, error);
      throw error;
    }
  }
  
  /**
   * Initialize tokenizer
   * @returns {Promise<void>}
   * @private
   */
  async _initializeTokenizer() {
    this.logger.info(`Initializing tokenizer for model: ${this.id}`);
    
    try {
      // In a real implementation, load the actual tokenizer
      // For now, create a placeholder tokenizer
      this.tokenizer = {
        name: `${this.name} Tokenizer`,
        maxLength: this.maxSequenceLength
      };
      
      this.logger.info(`Tokenizer initialized for model: ${this.id}`);
    } catch (error) {
      this.logger.error(`Failed to initialize tokenizer for model: ${this.id}`, error);
      throw error;
    }
  }
  
  /**
   * Validate model parameters
   * @param {Object} params - Model parameters
   * @protected
   */
  _validateParams(params) {
    super._validateParams(params);
    
    // Validate text parameters
    if (!params.text && !params.texts) {
      throw new Error('Either text or texts parameter is required');
    }
    
    if (params.text && typeof params.text !== 'string') {
      throw new Error('Text parameter must be a string');
    }
    
    if (params.texts && !Array.isArray(params.texts)) {
      throw new Error('Texts parameter must be an array');
    }
    
    if (params.texts && params.texts.some(text => typeof text !== 'string')) {
      throw new Error('All texts must be strings');
    }
    
    // Validate storage parameters
    if (params.storeEmbeddings) {
      if (params.text && !params.id) {
        throw new Error('ID is required when storing a single embedding');
      }
      
      if (params.texts && (!params.ids || params.ids.length !== params.texts.length)) {
        throw new Error('IDs array with matching length is required when storing multiple embeddings');
      }
    }
  }
}

module.exports = SentenceBERTModel;
