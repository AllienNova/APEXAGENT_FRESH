/**
 * EmbeddingStore.js
 * Storage and retrieval system for text embeddings in Aideon AI Lite
 * Supports multiple storage backends and efficient similarity search
 */

const fs = require('fs').promises;
const { existsSync } = require('fs');
const path = require('path');
const VectorSimilarity = require('../utils/VectorSimilarity');

class EmbeddingStore {
  /**
   * Create a new embedding store
   * @param {Object} core - Core system reference
   * @param {Object} options - Store options
   * @param {string} options.storageType - Storage type ('memory', 'file', 'hybrid')
   * @param {string} options.storagePath - Path for file storage
   * @param {number} options.maxMemoryItems - Maximum items to keep in memory
   * @param {boolean} options.enableIndexing - Whether to enable vector indexing
   * @param {string} options.indexType - Index type ('flat', 'ivf', 'hnsw')
   */
  constructor(core, options = {}) {
    this.core = core;
    this.logger = core.logger || console;
    
    // Configuration
    this.storageType = options.storageType || 'hybrid';
    this.storagePath = options.storagePath || path.join(core.paths?.data || '/tmp', 'embeddings');
    this.maxMemoryItems = options.maxMemoryItems || 10000;
    this.enableIndexing = options.enableIndexing !== false;
    this.indexType = options.indexType || 'flat';
    
    // Storage backends
    this.memoryStore = new Map();
    this.fileStore = null;
    this.vectorIndex = null;
    
    // Metadata storage
    this.metadata = new Map();
    
    // Performance tracking
    this.stats = {
      totalEmbeddings: 0,
      memoryHits: 0,
      fileHits: 0,
      searchQueries: 0,
      averageSearchTime: 0
    };
    
    this.initialized = false;
  }
  
  /**
   * Initialize the embedding store
   * @returns {Promise<boolean>} Success status
   */
  async initialize() {
    try {
      this.logger.info('Initializing embedding store');
      
      // Ensure storage directory exists
      await this._ensureStorageDirectory();
      
      // Initialize file store if needed
      if (this.storageType === 'file' || this.storageType === 'hybrid') {
        await this._initializeFileStore();
      }
      
      // Initialize vector index if enabled
      if (this.enableIndexing) {
        await this._initializeVectorIndex();
      }
      
      // Load existing embeddings
      await this._loadExistingEmbeddings();
      
      this.initialized = true;
      this.logger.info(`Embedding store initialized with ${this.stats.totalEmbeddings} embeddings`);
      return true;
    } catch (error) {
      this.logger.error('Failed to initialize embedding store:', error);
      return false;
    }
  }
  
  /**
   * Store an embedding with metadata
   * @param {string} id - Unique identifier for the embedding
   * @param {Array<number>} embedding - The embedding vector
   * @param {Object} metadata - Associated metadata
   * @param {string} metadata.text - Original text
   * @param {Object} metadata.metadata - Additional metadata
   * @returns {Promise<boolean>} Success status
   */
  async storeEmbedding(id, embedding, metadata = {}) {
    try {
      if (!this.initialized) {
        throw new Error('Embedding store not initialized');
      }
      
      // Validate inputs
      this._validateEmbedding(id, embedding);
      
      // Create embedding record
      const record = {
        id,
        embedding,
        text: metadata.text || '',
        metadata: metadata.metadata || {},
        timestamp: Date.now(),
        dimension: embedding.length
      };
      
      // Store in memory if using memory or hybrid storage
      if (this.storageType === 'memory' || this.storageType === 'hybrid') {
        this.memoryStore.set(id, record);
        
        // Manage memory limits for hybrid storage
        if (this.storageType === 'hybrid' && this.memoryStore.size > this.maxMemoryItems) {
          await this._evictOldestFromMemory();
        }
      }
      
      // Store in file if using file or hybrid storage
      if (this.storageType === 'file' || this.storageType === 'hybrid') {
        await this._storeToFile(record);
      }
      
      // Update vector index - FIXED: Added debug logging and verification
      if (this.vectorIndex) {
        this.logger.debug(`Adding vector to index: ${id}, dimension: ${embedding.length}`);
        await this.vectorIndex.addVector(id, embedding);
        this.logger.debug(`Vector index size after addition: ${this.vectorIndex.vectors.size}`);
      } else {
        this.logger.warn('Vector index not available for storing embedding');
      }
      
      // Store metadata separately
      this.metadata.set(id, {
        text: metadata.text || '',
        metadata: metadata.metadata || {},
        timestamp: record.timestamp
      });
      
      this.stats.totalEmbeddings++;
      this.logger.debug(`Stored embedding: ${id}`);
      return true;
    } catch (error) {
      this.logger.error(`Failed to store embedding ${id}:`, error);
      return false;
    }
  }
  
  /**
   * Retrieve an embedding by ID
   * @param {string} id - Embedding ID
   * @returns {Promise<Object|null>} Embedding record or null if not found
   */
  async getEmbedding(id) {
    try {
      if (!this.initialized) {
        throw new Error('Embedding store not initialized');
      }
      
      // Check memory store first
      if (this.memoryStore.has(id)) {
        this.stats.memoryHits++;
        return this.memoryStore.get(id);
      }
      
      // Check file store if using file or hybrid storage
      if (this.storageType === 'file' || this.storageType === 'hybrid') {
        const record = await this._loadFromFile(id);
        if (record) {
          this.stats.fileHits++;
          
          // Cache in memory for hybrid storage
          if (this.storageType === 'hybrid') {
            this.memoryStore.set(id, record);
          }
          
          return record;
        }
      }
      
      return null;
    } catch (error) {
      this.logger.error(`Failed to get embedding ${id}:`, error);
      return null;
    }
  }
  
  /**
   * Find similar embeddings using vector similarity search
   * @param {Array<number>} queryEmbedding - Query embedding vector
   * @param {Object} options - Search options
   * @param {number} options.limit - Maximum number of results (default: 10)
   * @param {number} options.threshold - Similarity threshold (default: 0.0)
   * @param {string} options.metric - Similarity metric ('cosine', 'euclidean', 'dot')
   * @param {Array<string>} options.excludeIds - IDs to exclude from results
   * @returns {Promise<Array>} Array of similar embeddings with scores
   */
  async findSimilar(queryEmbedding, options = {}) {
    const startTime = Date.now();
    
    try {
      if (!this.initialized) {
        throw new Error('Embedding store not initialized');
      }
      
      const {
        limit = 10,
        threshold = -1.0, // FIXED: Changed default threshold to include negative similarities
        metric = 'cosine',
        excludeIds = []
      } = options;
      
      let results = [];
      
      // Use vector index if available
      if (this.vectorIndex) {
        this.logger.debug(`Using vector index for search, index size: ${this.vectorIndex.vectors.size}`);
        results = await this.vectorIndex.search(queryEmbedding, {
          limit: limit * 2, // Get more results to filter
          metric,
          excludeIds
        });
      } else {
        // Fallback to brute force search
        this.logger.debug('Vector index not available, using brute force search');
        results = await this._bruteForceSearch(queryEmbedding, options);
      }
      
      // Debug logging for search results
      this.logger.debug(`Raw search results: ${JSON.stringify(results)}`);
      
      // Filter by threshold and limit
      results = results
        .filter(result => result.score >= threshold)
        .slice(0, limit);
      
      // Enrich results with metadata
      const enrichedResults = await Promise.all(
        results.map(async (result) => {
          const metadata = this.metadata.get(result.id);
          return {
            id: result.id,
            score: result.score,
            text: metadata?.text || '',
            metadata: metadata?.metadata || {},
            timestamp: metadata?.timestamp
          };
        })
      );
      
      // Update statistics
      const searchTime = Date.now() - startTime;
      this.stats.searchQueries++;
      this.stats.averageSearchTime = 
        (this.stats.averageSearchTime * (this.stats.searchQueries - 1) + searchTime) / this.stats.searchQueries;
      
      this.logger.debug(`Found ${enrichedResults.length} similar embeddings in ${searchTime}ms`);
      return enrichedResults;
    } catch (error) {
      this.logger.error('Failed to find similar embeddings:', error);
      return [];
    }
  }
  
  /**
   * Delete an embedding by ID
   * @param {string} id - Embedding ID
   * @returns {Promise<boolean>} Success status
   */
  async deleteEmbedding(id) {
    try {
      if (!this.initialized) {
        throw new Error('Embedding store not initialized');
      }
      
      let deleted = false;
      
      // Remove from memory store
      if (this.memoryStore.has(id)) {
        this.memoryStore.delete(id);
        deleted = true;
      }
      
      // Remove from file store
      if (this.storageType === 'file' || this.storageType === 'hybrid') {
        const fileDeleted = await this._deleteFromFile(id);
        deleted = deleted || fileDeleted;
      }
      
      // Remove from vector index
      if (this.vectorIndex) {
        await this.vectorIndex.removeVector(id);
      }
      
      // Remove metadata
      this.metadata.delete(id);
      
      if (deleted) {
        this.stats.totalEmbeddings--;
        this.logger.debug(`Deleted embedding: ${id}`);
      }
      
      return deleted;
    } catch (error) {
      this.logger.error(`Failed to delete embedding ${id}:`, error);
      return false;
    }
  }
  
  /**
   * Get store statistics
   * @returns {Object} Store statistics
   */
  getStats() {
    return {
      ...this.stats,
      memorySize: this.memoryStore.size,
      storageType: this.storageType,
      indexType: this.indexType,
      initialized: this.initialized
    };
  }
  
  /**
   * Clear all embeddings
   * @returns {Promise<boolean>} Success status
   */
  async clear() {
    try {
      // Clear memory store
      this.memoryStore.clear();
      
      // Clear file store
      if (this.storageType === 'file' || this.storageType === 'hybrid') {
        await this._clearFileStore();
      }
      
      // Clear vector index
      if (this.vectorIndex) {
        await this.vectorIndex.clear();
      }
      
      // Clear metadata
      this.metadata.clear();
      
      // Reset statistics
      this.stats.totalEmbeddings = 0;
      
      this.logger.info('Embedding store cleared');
      return true;
    } catch (error) {
      this.logger.error('Failed to clear embedding store:', error);
      return false;
    }
  }
  
  /**
   * Validate embedding input
   * @param {string} id - Embedding ID
   * @param {Array<number>} embedding - Embedding vector
   * @private
   */
  _validateEmbedding(id, embedding) {
    if (!id || typeof id !== 'string') {
      throw new Error('Embedding ID must be a non-empty string');
    }
    
    if (!Array.isArray(embedding) || embedding.length === 0) {
      throw new Error('Embedding must be a non-empty array');
    }
    
    if (!embedding.every(val => typeof val === 'number' && !isNaN(val))) {
      throw new Error('Embedding must contain only valid numbers');
    }
  }
  
  /**
   * Ensure storage directory exists
   * @returns {Promise<void>}
   * @private
   */
  async _ensureStorageDirectory() {
    try {
      await fs.mkdir(this.storagePath, { recursive: true });
      this.logger.debug(`Ensured storage directory exists: ${this.storagePath}`);
    } catch (error) {
      this.logger.error(`Failed to create storage directory: ${this.storagePath}`, error);
      throw error;
    }
  }
  
  /**
   * Initialize file store
   * @returns {Promise<void>}
   * @private
   */
  async _initializeFileStore() {
    this.fileStore = {
      embeddingsPath: path.join(this.storagePath, 'embeddings.jsonl'),
      indexPath: path.join(this.storagePath, 'index.json')
    };
    
    this.logger.debug('File store initialized');
  }
  
  /**
   * Initialize vector index
   * @returns {Promise<void>}
   * @private
   */
  async _initializeVectorIndex() {
    // For now, use a simple flat index
    // In production, implement more sophisticated indexing
    this.vectorIndex = {
      vectors: new Map(),
      
      async addVector(id, vector) {
        this.vectors.set(id, vector);
        console.log(`Vector added to index: ${id}, total vectors: ${this.vectors.size}`);
      },
      
      async removeVector(id) {
        this.vectors.delete(id);
      },
      
      async search(queryVector, options = {}) {
        const { limit = 10, metric = 'cosine', excludeIds = [] } = options;
        const results = [];
        
        console.log(`Searching ${this.vectors.size} vectors in index`);
        
        for (const [id, vector] of this.vectors) {
          if (excludeIds.includes(id)) continue;
          
          const score = VectorSimilarity.calculateSimilarity(queryVector, vector, metric);
          results.push({ id, score });
        }
        
        return results
          .sort((a, b) => b.score - a.score)
          .slice(0, limit);
      },
      
      async clear() {
        this.vectors.clear();
      }
    };
    
    this.logger.debug('Vector index initialized');
  }
  
  /**
   * Load existing embeddings from storage
   * @returns {Promise<void>}
   * @private
   */
  async _loadExistingEmbeddings() {
    if (this.storageType === 'file' || this.storageType === 'hybrid') {
      await this._loadFromFileStore();
    }
  }
  
  /**
   * Load embeddings from file store
   * @returns {Promise<void>}
   * @private
   */
  async _loadFromFileStore() {
    try {
      if (!existsSync(this.fileStore.embeddingsPath)) {
        return;
      }
      
      const data = await fs.readFile(this.fileStore.embeddingsPath, 'utf8');
      const lines = data.trim().split('\n');
      
      for (const line of lines) {
        if (line.trim()) {
          const record = JSON.parse(line);
          
          // Load into memory if using hybrid storage
          if (this.storageType === 'hybrid' && this.memoryStore.size < this.maxMemoryItems) {
            this.memoryStore.set(record.id, record);
          }
          
          // Load into vector index
          if (this.vectorIndex) {
            await this.vectorIndex.addVector(record.id, record.embedding);
          }
          
          // Load metadata
          this.metadata.set(record.id, {
            text: record.text,
            metadata: record.metadata,
            timestamp: record.timestamp
          });
          
          this.stats.totalEmbeddings++;
        }
      }
      
      this.logger.debug(`Loaded ${this.stats.totalEmbeddings} embeddings from file store`);
    } catch (error) {
      this.logger.error('Failed to load from file store:', error);
    }
  }
  
  /**
   * Store embedding to file
   * @param {Object} record - Embedding record
   * @returns {Promise<void>}
   * @private
   */
  async _storeToFile(record) {
    try {
      const line = JSON.stringify(record) + '\n';
      await fs.appendFile(this.fileStore.embeddingsPath, line);
    } catch (error) {
      this.logger.error('Failed to store to file:', error);
      throw error;
    }
  }
  
  /**
   * Load embedding from file
   * @param {string} id - Embedding ID
   * @returns {Promise<Object|null>} Embedding record or null
   * @private
   */
  async _loadFromFile(id) {
    // This is a simplified implementation
    // In production, use a more efficient file format or database
    try {
      if (!existsSync(this.fileStore.embeddingsPath)) {
        return null;
      }
      
      const data = await fs.readFile(this.fileStore.embeddingsPath, 'utf8');
      const lines = data.trim().split('\n');
      
      for (const line of lines) {
        if (line.trim()) {
          const record = JSON.parse(line);
          if (record.id === id) {
            return record;
          }
        }
      }
      
      return null;
    } catch (error) {
      this.logger.error(`Failed to load from file: ${id}`, error);
      return null;
    }
  }
  
  /**
   * Delete embedding from file
   * @param {string} id - Embedding ID
   * @returns {Promise<boolean>} Success status
   * @private
   */
  async _deleteFromFile(id) {
    // This is a simplified implementation
    // In production, use a more efficient approach
    try {
      if (!existsSync(this.fileStore.embeddingsPath)) {
        return false;
      }
      
      const data = await fs.readFile(this.fileStore.embeddingsPath, 'utf8');
      const lines = data.trim().split('\n');
      const filteredLines = lines.filter(line => {
        if (!line.trim()) return false;
        const record = JSON.parse(line);
        return record.id !== id;
      });
      
      await fs.writeFile(this.fileStore.embeddingsPath, filteredLines.join('\n') + '\n');
      return lines.length !== filteredLines.length;
    } catch (error) {
      this.logger.error(`Failed to delete from file: ${id}`, error);
      return false;
    }
  }
  
  /**
   * Clear file store
   * @returns {Promise<void>}
   * @private
   */
  async _clearFileStore() {
    try {
      if (existsSync(this.fileStore.embeddingsPath)) {
        await fs.unlink(this.fileStore.embeddingsPath);
      }
      if (existsSync(this.fileStore.indexPath)) {
        await fs.unlink(this.fileStore.indexPath);
      }
    } catch (error) {
      this.logger.error('Failed to clear file store:', error);
      throw error;
    }
  }
  
  /**
   * Evict oldest item from memory
   * @returns {Promise<void>}
   * @private
   */
  async _evictOldestFromMemory() {
    let oldestId = null;
    let oldestTimestamp = Infinity;
    
    for (const [id, record] of this.memoryStore) {
      if (record.timestamp < oldestTimestamp) {
        oldestTimestamp = record.timestamp;
        oldestId = id;
      }
    }
    
    if (oldestId) {
      this.memoryStore.delete(oldestId);
      this.logger.debug(`Evicted oldest embedding from memory: ${oldestId}`);
    }
  }
  
  /**
   * Perform brute force similarity search
   * @param {Array<number>} queryEmbedding - Query embedding
   * @param {Object} options - Search options
   * @returns {Promise<Array>} Search results
   * @private
   */
  async _bruteForceSearch(queryEmbedding, options = {}) {
    const { limit = 10, metric = 'cosine', excludeIds = [] } = options;
    const results = [];
    
    // Debug logging for brute force search
    this.logger.debug(`Performing brute force search with ${this.memoryStore.size} embeddings in memory`);
    
    // Search memory store
    for (const [id, record] of this.memoryStore) {
      if (excludeIds.includes(id)) continue;
      
      const score = VectorSimilarity.calculateSimilarity(queryEmbedding, record.embedding, metric);
      results.push({ id, score });
      
      // Debug logging for individual similarity scores
      this.logger.debug(`Similarity score for ${id}: ${score}`);
    }
    
    return results
      .sort((a, b) => b.score - a.score)
      .slice(0, limit);
  }
}

module.exports = EmbeddingStore;
