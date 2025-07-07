/**
 * SentenceBERTProvider.js
 * Provider for Sentence-BERT text embedding models in Aideon AI Lite
 * Enables semantic text embeddings, similarity search, and enhanced NLP capabilities
 */

const MLModelProvider = require('../MLModelProvider');
const SentenceBERTModel = require('./SentenceBERTModel');
const EmbeddingStore = require('./EmbeddingStore');
const SemanticSearchEngine = require('./SemanticSearchEngine');
const fs = require('fs');
const path = require('path');

class SentenceBERTProvider extends MLModelProvider {
  /**
   * Create a new Sentence-BERT provider
   * @param {Object} core - Core system reference
   */
  constructor(core) {
    super(core);
    
    this.modelPath = this.config.modelPath || path.join(core.paths.models, 'text', 'sentence-bert');
    this.embeddingStore = new EmbeddingStore(core, this.config.embeddingStore || {});
    this.semanticSearchEngine = null;
    
    // Add reference tracking for debugging
    this.embeddingStore._providerRef = this;
    this.embeddingStore._instanceId = Date.now();
    this.logger.debug(`Created EmbeddingStore instance ID: ${this.embeddingStore._instanceId}`);
    
    // Ensure model directory exists
    this._ensureModelDirectory();
  }
  
  /**
   * Get provider ID
   * @returns {string} Provider ID
   */
  get id() {
    return 'sentence-bert';
  }
  
  /**
   * Get provider name
   * @returns {string} Provider name
   */
  get name() {
    return 'Sentence-BERT';
  }
  
  /**
   * Initialize the provider
   * @returns {Promise<boolean>} Success status
   */
  async initialize() {
    try {
      this.logger.debug(`Initializing EmbeddingStore instance ID: ${this.embeddingStore._instanceId}`);
      
      // Initialize embedding store
      await this.embeddingStore.initialize();
      
      // Initialize base provider
      const result = await super.initialize();
      
      if (result) {
        // Initialize semantic search engine
        this.semanticSearchEngine = new SemanticSearchEngine(this);
        
        // Verify reference integrity
        this.logger.debug(`SemanticSearchEngine using EmbeddingStore instance ID: ${this.semanticSearchEngine.embeddingStore._instanceId}`);
        this.logger.debug(`Reference equality check: ${this.embeddingStore === this.semanticSearchEngine.embeddingStore}`);
        
        this.logger.info('Sentence-BERT provider fully initialized');
      }
      
      return result;
    } catch (error) {
      this.logger.error('Failed to initialize Sentence-BERT provider:', error);
      return false;
    }
  }
  
  /**
   * Get semantic search engine
   * @returns {SemanticSearchEngine} Semantic search engine instance
   */
  getSemanticSearchEngine() {
    if (!this.semanticSearchEngine) {
      throw new Error('Semantic search engine not initialized');
    }
    
    // Verify reference integrity
    this.logger.debug(`Returning SemanticSearchEngine with EmbeddingStore instance ID: ${this.semanticSearchEngine.embeddingStore._instanceId}`);
    this.logger.debug(`Reference equality check: ${this.embeddingStore === this.semanticSearchEngine.embeddingStore}`);
    
    return this.semanticSearchEngine;
  }
  
  /**
   * Generate embeddings for text
   * @param {string|Array<string>} text - Text or array of texts to embed
   * @param {Object} options - Embedding options
   * @param {string} options.modelId - Model ID to use (default: first available)
   * @param {boolean} options.storeEmbeddings - Whether to store embeddings
   * @param {string|Array<string>} options.ids - IDs for storing embeddings
   * @param {Object|Array<Object>} options.metadata - Metadata for embeddings
   * @returns {Promise<Object>} Embedding result
   */
  async generateEmbeddings(text, options = {}) {
    const modelId = options.modelId || this.getModelsByType('embedding')[0]?.id;
    
    if (!modelId) {
      throw new Error('No embedding models available');
    }
    
    const params = {
      ...(Array.isArray(text) ? { texts: text } : { text }),
      storeEmbeddings: options.storeEmbeddings || false,
      ids: options.ids,
      metadata: options.metadata
    };
    
    // Verify embedding store reference before execution
    this.logger.debug(`Using EmbeddingStore instance ID: ${this.embeddingStore._instanceId} for embedding generation`);
    
    return this.executeModel(modelId, params, options);
  }
  
  /**
   * Perform semantic search
   * @param {string} query - Search query
   * @param {Object} options - Search options
   * @returns {Promise<Array>} Search results
   */
  async semanticSearch(query, options = {}) {
    return this.getSemanticSearchEngine().search(query, options);
  }
  
  /**
   * Index a document for semantic search
   * @param {Object} document - Document to index
   * @param {string} document.id - Document ID
   * @param {string} document.text - Document text
   * @param {Object} document.metadata - Document metadata
   * @param {Object} options - Indexing options
   * @returns {Promise<Object>} Indexing result
   */
  async indexDocument(document, options = {}) {
    return this.getSemanticSearchEngine().indexDocument(document, options);
  }
  
  /**
   * Validate provider configuration
   * @returns {boolean} Validation result
   * @protected
   */
  _validateConfig() {
    // Validate base configuration
    if (!super._validateConfig()) {
      return false;
    }
    
    // Validate Sentence-BERT specific configuration
    if (this.config.models && !Array.isArray(this.config.models)) {
      this.logger.error('Invalid models configuration: must be an array');
      return false;
    }
    
    return true;
  }
  
  /**
   * Ensure model directory exists
   * @private
   */
  _ensureModelDirectory() {
    try {
      if (!fs.existsSync(this.modelPath)) {
        fs.mkdirSync(this.modelPath, { recursive: true });
      }
    } catch (error) {
      this.logger.error('Failed to create model directory:', error);
    }
  }
  
  /**
   * Register available models
   * @protected
   */
  async _registerModels() {
    // Register default models
    const defaultModels = [
      {
        id: 'all-MiniLM-L6-v2',
        name: 'MiniLM-L6-v2',
        type: 'embedding',
        isLocal: true,
        capabilities: {
          textEmbedding: true,
          semanticSearch: true,
          multilingual: false,
          maxSequenceLength: 256
        },
        requirements: {
          memory: 'low',
          speed: 'fast',
          dimensions: 384
        }
      },
      {
        id: 'all-mpnet-base-v2',
        name: 'MPNet-Base-v2',
        type: 'embedding',
        isLocal: true,
        capabilities: {
          textEmbedding: true,
          semanticSearch: true,
          multilingual: false,
          maxSequenceLength: 384
        },
        requirements: {
          memory: 'medium',
          speed: 'medium',
          dimensions: 768
        }
      },
      {
        id: 'multi-qa-mpnet-base-dot-v1',
        name: 'Multi-QA MPNet Base',
        type: 'embedding',
        isLocal: true,
        capabilities: {
          textEmbedding: true,
          semanticSearch: true,
          multilingual: true,
          maxSequenceLength: 384
        },
        requirements: {
          memory: 'medium',
          speed: 'medium',
          dimensions: 768
        }
      }
    ];
    
    // Register each model
    for (const modelConfig of defaultModels) {
      const model = new SentenceBERTModel(this, modelConfig);
      await model.initialize();
      this.registerModel(model);
    }
    
    // Register custom models if specified
    if (this.config.models && Array.isArray(this.config.models)) {
      for (const modelConfig of this.config.models) {
        const model = new SentenceBERTModel(this, modelConfig);
        await model.initialize();
        this.registerModel(model);
      }
    }
  }
  
  /**
   * Execute model with parameters
   * @param {string} modelId - Model ID
   * @param {Object} params - Model parameters
   * @param {Object} options - Execution options
   * @returns {Promise<Object>} Model result
   * @protected
   */
  async executeModel(modelId, params, options = {}) {
    const result = await super.executeModel(modelId, params, options);
    
    // Handle embedding storage if requested
    if (params.storeEmbeddings && (result.embedding || result.embeddings)) {
      await this._storeEmbeddings(result, params, options);
    }
    
    return result;
  }
  
  /**
   * Store embeddings in embedding store
   * @param {Object} result - Model result
   * @param {Object} params - Model parameters
   * @param {Object} options - Execution options
   * @returns {Promise<void>}
   * @private
   */
  async _storeEmbeddings(result, params, options) {
    try {
      // Verify embedding store reference before storage
      this.logger.debug(`Storing embeddings using EmbeddingStore instance ID: ${this.embeddingStore._instanceId}`);
      
      // Handle single embedding
      if (result.embedding) {
        const id = params.ids || `embedding_${Date.now()}`;
        const metadata = {
          text: params.text || '',
          metadata: params.metadata || {}
        };
        
        await this.embeddingStore.storeEmbedding(id, result.embedding, metadata);
      }
      // Handle multiple embeddings
      else if (result.embeddings) {
        const ids = params.ids || result.embeddings.map((_, i) => `embedding_${Date.now()}_${i}`);
        const texts = params.texts || [];
        const metadataArray = params.metadata || [];
        
        for (let i = 0; i < result.embeddings.length; i++) {
          const id = Array.isArray(ids) ? ids[i] : `${ids}_${i}`;
          const text = texts[i] || '';
          const metadata = Array.isArray(metadataArray) ? metadataArray[i] || {} : metadataArray;
          
          await this.embeddingStore.storeEmbedding(id, result.embeddings[i], {
            text,
            metadata
          });
        }
      }
    } catch (error) {
      this.logger.error('Failed to store embeddings:', error);
    }
  }
}

module.exports = SentenceBERTProvider;
