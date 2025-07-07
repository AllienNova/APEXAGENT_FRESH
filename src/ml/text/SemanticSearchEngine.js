/**
 * SemanticSearchEngine.js
 * High-level semantic search capabilities for Aideon AI Lite
 * Provides text-based semantic search using Sentence-BERT embeddings
 */

class SemanticSearchEngine {
  /**
   * Create a new semantic search engine
   * @param {Object} provider - SentenceBERTProvider instance
   */
  constructor(provider) {
    this.provider = provider;
    this.embeddingStore = provider.embeddingStore;
    this.logger = provider.logger;
    this.defaultModel = null;
    
    // Initialize default model
    this._initializeDefaultModel();
  }
  
  /**
   * Search for similar content using semantic search
   * @param {string} query - Search query
   * @param {Object} options - Search options
   * @param {string} options.modelId - Model ID to use for embedding generation
   * @param {number} options.limit - Maximum number of results (default: 10)
   * @param {number} options.threshold - Similarity threshold (default: 0.0)
   * @param {string} options.metric - Similarity metric ('cosine', 'euclidean', 'dot')
   * @param {Array<string>} options.excludeIds - IDs to exclude from results
   * @param {Object} options.filter - Filter criteria for metadata
   * @returns {Promise<Array>} Search results
   */
  async search(query, options = {}) {
    try {
      const startTime = Date.now();
      this.logger.debug(`Semantic search for query: "${query}"`);
      
      // Set default options
      const searchOptions = {
        modelId: options.modelId || this.defaultModel?.id,
        limit: options.limit || 10,
        threshold: options.threshold ?? 0.0, // Changed default threshold to 0.0
        metric: options.metric || 'cosine',
        excludeIds: options.excludeIds || [],
        filter: options.filter || {}
      };
      
      // Generate embedding for query
      const { embedding } = await this.provider.generateEmbeddings(query, {
        modelId: searchOptions.modelId
      });
      
      // Find similar embeddings
      let results = await this.embeddingStore.findSimilar(embedding, {
        limit: searchOptions.limit * 2, // Get more results for filtering
        threshold: searchOptions.threshold,
        metric: searchOptions.metric,
        excludeIds: searchOptions.excludeIds
      });
      
      // Apply metadata filters if specified
      if (Object.keys(searchOptions.filter).length > 0) {
        results = this._applyMetadataFilters(results, searchOptions.filter);
      }
      
      // Limit results
      results = results.slice(0, searchOptions.limit);
      
      // Enrich results with additional information
      const enrichedResults = this._enrichResults(results, query);
      
      const duration = Date.now() - startTime;
      this.logger.info(`Semantic search completed in ${duration}ms, found ${results.length} results`);
      
      return enrichedResults;
    } catch (error) {
      this.logger.error('Semantic search failed:', error);
      throw error;
    }
  }
  
  /**
   * Index a document for semantic search
   * @param {Object} document - Document to index
   * @param {string} document.id - Document ID
   * @param {string} document.text - Document text
   * @param {Object} document.metadata - Document metadata
   * @param {Object} options - Indexing options
   * @param {string} options.modelId - Model ID to use for embedding generation
   * @param {boolean} options.splitSections - Whether to split document into sections
   * @param {number} options.sectionLength - Maximum section length in characters
   * @param {number} options.sectionOverlap - Section overlap in characters
   * @returns {Promise<Object>} Indexing result
   */
  async indexDocument(document, options = {}) {
    try {
      const startTime = Date.now();
      this.logger.debug(`Indexing document: ${document.id}`);
      
      // Set default options
      const indexOptions = {
        modelId: options.modelId || this.defaultModel?.id,
        splitSections: options.splitSections || false,
        sectionLength: options.sectionLength || 1000,
        sectionOverlap: options.sectionOverlap || 200
      };
      
      // Validate document
      if (!document.id || !document.text) {
        throw new Error('Document must have id and text properties');
      }
      
      let sections = [];
      let embeddingIds = [];
      
      // Split document into sections if requested
      if (indexOptions.splitSections && document.text.length > indexOptions.sectionLength) {
        sections = this._splitTextIntoSections(
          document.text,
          indexOptions.sectionLength,
          indexOptions.sectionOverlap
        );
        
        // Generate IDs for sections
        embeddingIds = sections.map((_, index) => 
          `${document.id}_section_${index}`
        );
      } else {
        sections = [document.text];
        embeddingIds = [document.id];
      }
      
      // Generate embeddings for all sections
      const { embeddings } = await this.provider.generateEmbeddings(sections, {
        modelId: indexOptions.modelId,
        storeEmbeddings: true,
        ids: embeddingIds,
        metadata: sections.map((section, index) => ({
          documentId: document.id,
          sectionIndex: index,
          sectionCount: sections.length,
          ...document.metadata
        }))
      });
      
      const duration = Date.now() - startTime;
      this.logger.info(`Document indexed in ${duration}ms, created ${sections.length} embeddings`);
      
      return {
        documentId: document.id,
        sectionCount: sections.length,
        embeddingIds
      };
    } catch (error) {
      this.logger.error(`Failed to index document ${document.id}:`, error);
      throw error;
    }
  }
  
  /**
   * Delete a document from the index
   * @param {string} documentId - Document ID
   * @param {boolean} includeAllSections - Whether to delete all sections
   * @returns {Promise<Object>} Deletion result
   */
  async deleteDocument(documentId, includeAllSections = true) {
    try {
      this.logger.debug(`Deleting document: ${documentId}`);
      
      // Delete main document embedding
      await this.embeddingStore.deleteEmbedding(documentId);
      
      let sectionCount = 0;
      
      // Delete section embeddings if requested
      if (includeAllSections) {
        // Find all section embeddings
        const sectionPrefix = `${documentId}_section_`;
        
        // This is a simplified approach; in production, use a more efficient method
        const allMetadata = Array.from(this.embeddingStore.metadata.entries());
        const sectionIds = allMetadata
          .filter(([id]) => id.startsWith(sectionPrefix))
          .map(([id]) => id);
        
        // Delete each section
        for (const sectionId of sectionIds) {
          await this.embeddingStore.deleteEmbedding(sectionId);
          sectionCount++;
        }
      }
      
      this.logger.info(`Document deleted: ${documentId}, removed ${sectionCount} sections`);
      
      return {
        documentId,
        sectionCount,
        success: true
      };
    } catch (error) {
      this.logger.error(`Failed to delete document ${documentId}:`, error);
      throw error;
    }
  }
  
  /**
   * Initialize default model
   * @private
   */
  _initializeDefaultModel() {
    // Get first available embedding model
    const embeddingModels = this.provider.getModelsByType('embedding');
    
    if (embeddingModels.length > 0) {
      this.defaultModel = embeddingModels[0];
      this.logger.debug(`Default model set to: ${this.defaultModel.name} (${this.defaultModel.id})`);
    } else {
      this.logger.warn('No embedding models available for semantic search');
    }
  }
  
  /**
   * Split text into overlapping sections
   * @param {string} text - Text to split
   * @param {number} sectionLength - Maximum section length
   * @param {number} overlap - Overlap between sections
   * @returns {Array<string>} Text sections
   * @private
   */
  _splitTextIntoSections(text, sectionLength, overlap) {
    const sections = [];
    const sentences = text.split(/(?<=[.!?])\s+/);
    let currentSection = '';
    
    for (const sentence of sentences) {
      // If adding this sentence would exceed section length, start a new section
      if (currentSection.length + sentence.length > sectionLength && currentSection.length > 0) {
        sections.push(currentSection);
        
        // Start new section with overlap from previous section
        const words = currentSection.split(/\s+/);
        const overlapWords = words.slice(-Math.ceil(overlap / 5)); // Approximate words in overlap
        currentSection = overlapWords.join(' ') + ' ' + sentence;
      } else {
        // Add sentence to current section
        if (currentSection.length > 0) {
          currentSection += ' ';
        }
        currentSection += sentence;
      }
    }
    
    // Add final section if not empty
    if (currentSection.length > 0) {
      sections.push(currentSection);
    }
    
    return sections;
  }
  
  /**
   * Apply metadata filters to search results
   * @param {Array} results - Search results
   * @param {Object} filters - Metadata filters
   * @returns {Array} Filtered results
   * @private
   */
  _applyMetadataFilters(results, filters) {
    return results.filter(result => {
      // Skip if no metadata
      if (!result.metadata) return false;
      
      // Check each filter
      for (const [key, value] of Object.entries(filters)) {
        // Handle array values (OR condition)
        if (Array.isArray(value)) {
          if (!value.includes(result.metadata[key])) {
            return false;
          }
        }
        // Handle object with comparison operators
        else if (typeof value === 'object') {
          for (const [op, opValue] of Object.entries(value)) {
            const fieldValue = result.metadata[key];
            
            switch (op) {
              case '$eq':
                if (fieldValue !== opValue) return false;
                break;
              case '$ne':
                if (fieldValue === opValue) return false;
                break;
              case '$gt':
                if (!(fieldValue > opValue)) return false;
                break;
              case '$gte':
                if (!(fieldValue >= opValue)) return false;
                break;
              case '$lt':
                if (!(fieldValue < opValue)) return false;
                break;
              case '$lte':
                if (!(fieldValue <= opValue)) return false;
                break;
              case '$in':
                if (!Array.isArray(opValue) || !opValue.includes(fieldValue)) return false;
                break;
              case '$nin':
                if (!Array.isArray(opValue) || opValue.includes(fieldValue)) return false;
                break;
            }
          }
        }
        // Handle simple equality
        else if (result.metadata[key] !== value) {
          return false;
        }
      }
      
      return true;
    });
  }
  
  /**
   * Enrich search results with additional information
   * @param {Array} results - Search results
   * @param {string} query - Original query
   * @returns {Array} Enriched results
   * @private
   */
  _enrichResults(results, query) {
    return results.map(result => {
      // Extract relevant text snippet if available
      let snippet = result.text;
      
      if (snippet && snippet.length > 200) {
        // Find best snippet containing query terms
        const queryTerms = query.toLowerCase().split(/\s+/).filter(term => term.length > 2);
        const sentences = snippet.split(/(?<=[.!?])\s+/);
        
        // Score sentences by query term matches
        const scoredSentences = sentences.map(sentence => {
          const lowerSentence = sentence.toLowerCase();
          let score = 0;
          
          for (const term of queryTerms) {
            if (lowerSentence.includes(term)) {
              score += 1;
            }
          }
          
          return { sentence, score };
        });
        
        // Sort by score and take top sentences
        scoredSentences.sort((a, b) => b.score - a.score);
        const topSentences = scoredSentences.slice(0, 3).map(s => s.sentence);
        
        // Create snippet from top sentences
        snippet = topSentences.join(' ');
        
        // Truncate if still too long
        if (snippet.length > 200) {
          snippet = snippet.substring(0, 197) + '...';
        }
      }
      
      return {
        ...result,
        snippet,
        queryScore: result.score,
        relevance: Math.round(result.score * 100) / 100
      };
    });
  }
}

module.exports = SemanticSearchEngine;
