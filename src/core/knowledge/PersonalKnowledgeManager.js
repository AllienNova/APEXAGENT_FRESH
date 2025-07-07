/**
 * PersonalKnowledgeManager.js
 * 
 * Provides integrated knowledge management capabilities for Aideon AI Lite.
 * Helps users organize, retrieve, and leverage their personal and professional knowledge
 * across all tools and workflows.
 * 
 * @author Aideon AI Team
 * @version 1.0.0
 */

const EventEmitter = require("events");
const { v4: uuidv4 } = require("uuid");
const path = require("path");
const fs = require("fs").promises;

// Placeholder for vector database/embedding service
class KnowledgeVectorStore {
  constructor(options) {
    this.options = options;
    this.vectors = new Map(); // In a real implementation, this would be a proper vector DB
    this.dimensions = options.dimensions || 384; // Default embedding dimensions
  }
  
  async addItem(id, content, metadata = {}) {
    console.log(`[KnowledgeVectorStore] Adding item: ${id}`);
    // In a real implementation, this would generate embeddings using a model
    const embedding = this._generateMockEmbedding(content);
    this.vectors.set(id, { embedding, metadata, content });
    return id;
  }
  
  async updateItem(id, content, metadata = {}) {
    if (!this.vectors.has(id)) {
      throw new Error(`Item with ID ${id} not found`);
    }
    console.log(`[KnowledgeVectorStore] Updating item: ${id}`);
    const embedding = this._generateMockEmbedding(content);
    const existingMetadata = this.vectors.get(id).metadata;
    this.vectors.set(id, { 
      embedding, 
      metadata: { ...existingMetadata, ...metadata },
      content 
    });
    return id;
  }
  
  async deleteItem(id) {
    console.log(`[KnowledgeVectorStore] Deleting item: ${id}`);
    return this.vectors.delete(id);
  }
  
  async search(query, limit = 10, filters = {}) {
    console.log(`[KnowledgeVectorStore] Searching for: "${query}" with filters: ${JSON.stringify(filters)}`);
    // In a real implementation, this would generate a query embedding and perform similarity search
    const queryEmbedding = this._generateMockEmbedding(query);
    
    // Filter items based on metadata filters
    let items = Array.from(this.vectors.entries())
      .filter(([_, item]) => {
        // Apply metadata filters
        for (const [key, value] of Object.entries(filters)) {
          if (item.metadata[key] !== value) {
            return false;
          }
        }
        return true;
      });
    
    // Calculate similarity scores (cosine similarity)
    items = items.map(([id, item]) => {
      const similarity = this._calculateCosineSimilarity(queryEmbedding, item.embedding);
      return { id, item, similarity };
    });
    
    // Sort by similarity (descending) and take top results
    items.sort((a, b) => b.similarity - a.similarity);
    const results = items.slice(0, limit).map(({ id, item, similarity }) => ({
      id,
      content: item.content,
      metadata: item.metadata,
      similarity
    }));
    
    console.log(`[KnowledgeVectorStore] Found ${results.length} results`);
    return results;
  }
  
  // Mock methods for demonstration purposes
  _generateMockEmbedding(text) {
    // In a real implementation, this would use a proper embedding model
    const seed = text.length;
    const embedding = new Array(this.dimensions).fill(0).map((_, i) => {
      // Generate a deterministic but seemingly random value based on text and position
      return Math.sin(seed * (i + 1) * 0.1) * 0.5 + 0.5;
    });
    return embedding;
  }
  
  _calculateCosineSimilarity(vec1, vec2) {
    // Calculate cosine similarity between two vectors
    let dotProduct = 0;
    let mag1 = 0;
    let mag2 = 0;
    
    for (let i = 0; i < vec1.length; i++) {
      dotProduct += vec1[i] * vec2[i];
      mag1 += vec1[i] * vec1[i];
      mag2 += vec2[i] * vec2[i];
    }
    
    mag1 = Math.sqrt(mag1);
    mag2 = Math.sqrt(mag2);
    
    if (mag1 === 0 || mag2 === 0) return 0;
    return dotProduct / (mag1 * mag2);
  }
}

class PersonalKnowledgeManager extends EventEmitter {
  /**
   * Creates a new PersonalKnowledgeManager instance
   * 
   * @param {Object} core - The Aideon core instance
   */
  constructor(core) {
    super();
    this.core = core;
    this.logger = core.logManager.getLogger("knowledge");
    this.configManager = core.configManager;
    this.toolManager = core.toolManager;
    
    this.isEnabled = false;
    this.knowledgeBase = null;
    this.knowledgeGraph = null;
    this.vectorStore = null;
    
    this.knowledgeSources = new Map();
    this.knowledgeProcessors = new Map();
    this.knowledgeConnectors = new Map();
    
    this.knowledgeBasePath = null;
    this.knowledgeIndexPath = null;
  }
  
  /**
   * Initializes the PersonalKnowledgeManager
   * 
   * @returns {Promise<boolean>} True if initialization was successful
   */
  async initialize() {
    try {
      this.logger.info("Initializing PersonalKnowledgeManager");
      
      const config = this.configManager.getConfig().knowledge || {};
      this.isEnabled = config.enabled !== false;
      
      if (!this.isEnabled) {
        this.logger.info("PersonalKnowledgeManager is disabled in configuration");
        return true;
      }
      
      // Set up file paths
      const dataDir = this.configManager.getDataDir();
      this.knowledgeBasePath = path.join(dataDir, "knowledge_base");
      this.knowledgeIndexPath = path.join(dataDir, "knowledge_index");
      
      // Ensure directories exist
      await this._ensureDirectories();
      
      // Initialize vector store
      this.vectorStore = new KnowledgeVectorStore(config.vectorStore || {});
      
      // Initialize knowledge sources
      this._initializeKnowledgeSources(config.sources || {});
      
      // Initialize knowledge processors
      this._initializeKnowledgeProcessors(config.processors || {});
      
      // Initialize knowledge connectors
      this._initializeKnowledgeConnectors(config.connectors || {});
      
      // Load existing knowledge index
      await this._loadKnowledgeIndex();
      
      // Register event listeners
      this._registerEventListeners();
      
      this.logger.info("PersonalKnowledgeManager initialized successfully");
      return true;
    } catch (error) {
      this.logger.error(`Failed to initialize PersonalKnowledgeManager: ${error.message}`, error);
      return false;
    }
  }
  
  /**
   * Adds a knowledge item to the knowledge base
   * 
   * @param {Object} item - The knowledge item to add
   * @param {string} item.content - The content of the knowledge item
   * @param {string} item.title - The title of the knowledge item
   * @param {string} item.type - The type of knowledge (e.g., note, document, code, etc.)
   * @param {Object} item.metadata - Additional metadata for the knowledge item
   * @param {string[]} item.tags - Tags for the knowledge item
   * @returns {Promise<string>} The ID of the added knowledge item
   */
  async addKnowledgeItem(item) {
    if (!this.isEnabled) {
      throw new Error("PersonalKnowledgeManager is disabled");
    }
    
    this.logger.debug(`Adding knowledge item: ${item.title}`);
    
    try {
      // Validate the item
      this._validateKnowledgeItem(item);
      
      // Generate an ID if not provided
      const id = item.id || uuidv4();
      
      // Process the content if a processor exists for the item type
      let processedContent = item.content;
      if (this.knowledgeProcessors.has(item.type)) {
        const processor = this.knowledgeProcessors.get(item.type);
        processedContent = await processor.process(item.content);
      }
      
      // Prepare metadata
      const metadata = {
        ...item.metadata,
        title: item.title,
        type: item.type,
        tags: item.tags || [],
        created: Date.now(),
        updated: Date.now()
      };
      
      // Add to vector store for semantic search
      await this.vectorStore.addItem(id, processedContent, metadata);
      
      // Save the item to the knowledge base
      await this._saveKnowledgeItem(id, {
        ...item,
        id,
        content: processedContent,
        metadata
      });
      
      this.logger.info(`Added knowledge item: ${id} - ${item.title}`);
      this.emit("knowledgeItemAdded", { id, title: item.title, type: item.type });
      
      return id;
    } catch (error) {
      this.logger.error(`Failed to add knowledge item: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Updates an existing knowledge item
   * 
   * @param {string} id - The ID of the knowledge item to update
   * @param {Object} updates - The updates to apply
   * @returns {Promise<boolean>} True if the update was successful
   */
  async updateKnowledgeItem(id, updates) {
    if (!this.isEnabled) {
      throw new Error("PersonalKnowledgeManager is disabled");
    }
    
    this.logger.debug(`Updating knowledge item: ${id}`);
    
    try {
      // Get the existing item
      const existingItem = await this._loadKnowledgeItem(id);
      if (!existingItem) {
        throw new Error(`Knowledge item not found: ${id}`);
      }
      
      // Apply updates
      const updatedItem = {
        ...existingItem,
        ...updates,
        metadata: {
          ...existingItem.metadata,
          ...(updates.metadata || {}),
          updated: Date.now()
        }
      };
      
      // Process the content if it was updated and a processor exists
      let processedContent = updatedItem.content;
      if (updates.content && this.knowledgeProcessors.has(updatedItem.type)) {
        const processor = this.knowledgeProcessors.get(updatedItem.type);
        processedContent = await processor.process(updatedItem.content);
        updatedItem.content = processedContent;
      }
      
      // Update in vector store
      await this.vectorStore.updateItem(id, processedContent, updatedItem.metadata);
      
      // Save the updated item
      await this._saveKnowledgeItem(id, updatedItem);
      
      this.logger.info(`Updated knowledge item: ${id}`);
      this.emit("knowledgeItemUpdated", { id, title: updatedItem.title, type: updatedItem.type });
      
      return true;
    } catch (error) {
      this.logger.error(`Failed to update knowledge item: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Deletes a knowledge item
   * 
   * @param {string} id - The ID of the knowledge item to delete
   * @returns {Promise<boolean>} True if the deletion was successful
   */
  async deleteKnowledgeItem(id) {
    if (!this.isEnabled) {
      throw new Error("PersonalKnowledgeManager is disabled");
    }
    
    this.logger.debug(`Deleting knowledge item: ${id}`);
    
    try {
      // Get the existing item
      const existingItem = await this._loadKnowledgeItem(id);
      if (!existingItem) {
        throw new Error(`Knowledge item not found: ${id}`);
      }
      
      // Remove from vector store
      await this.vectorStore.deleteItem(id);
      
      // Delete the item file
      const itemPath = path.join(this.knowledgeBasePath, `${id}.json`);
      await fs.unlink(itemPath);
      
      this.logger.info(`Deleted knowledge item: ${id}`);
      this.emit("knowledgeItemDeleted", { id, title: existingItem.title, type: existingItem.type });
      
      return true;
    } catch (error) {
      this.logger.error(`Failed to delete knowledge item: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Gets a knowledge item by ID
   * 
   * @param {string} id - The ID of the knowledge item to get
   * @returns {Promise<Object>} The knowledge item
   */
  async getKnowledgeItem(id) {
    if (!this.isEnabled) {
      throw new Error("PersonalKnowledgeManager is disabled");
    }
    
    this.logger.debug(`Getting knowledge item: ${id}`);
    
    try {
      const item = await this._loadKnowledgeItem(id);
      if (!item) {
        throw new Error(`Knowledge item not found: ${id}`);
      }
      
      this.emit("knowledgeItemAccessed", { id, title: item.title, type: item.type });
      return item;
    } catch (error) {
      this.logger.error(`Failed to get knowledge item: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Searches the knowledge base
   * 
   * @param {Object} options - Search options
   * @param {string} options.query - The search query
   * @param {Object} options.filters - Metadata filters to apply
   * @param {number} options.limit - Maximum number of results to return
   * @returns {Promise<Array>} The search results
   */
  async searchKnowledge(options) {
    if (!this.isEnabled) {
      throw new Error("PersonalKnowledgeManager is disabled");
    }
    
    const { query, filters = {}, limit = 10 } = options;
    this.logger.debug(`Searching knowledge: "${query}" with filters: ${JSON.stringify(filters)}`);
    
    try {
      // Perform semantic search using vector store
      const results = await this.vectorStore.search(query, limit, filters);
      
      // Enhance results with full knowledge items
      const enhancedResults = await Promise.all(results.map(async (result) => {
        const item = await this._loadKnowledgeItem(result.id);
        return {
          ...result,
          item
        };
      }));
      
      this.logger.info(`Search completed: ${enhancedResults.length} results for "${query}"`);
      this.emit("knowledgeSearched", { query, filters, resultCount: enhancedResults.length });
      
      return enhancedResults;
    } catch (error) {
      this.logger.error(`Failed to search knowledge: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Imports knowledge from an external source
   * 
   * @param {string} sourceId - The ID of the knowledge source
   * @param {Object} options - Import options specific to the source
   * @returns {Promise<Object>} Import results
   */
  async importKnowledge(sourceId, options = {}) {
    if (!this.isEnabled) {
      throw new Error("PersonalKnowledgeManager is disabled");
    }
    
    if (!this.knowledgeSources.has(sourceId)) {
      throw new Error(`Knowledge source not found: ${sourceId}`);
    }
    
    this.logger.info(`Importing knowledge from source: ${sourceId}`);
    this.emit("knowledgeImportStarted", { sourceId, options });
    
    try {
      const source = this.knowledgeSources.get(sourceId);
      const importedItems = await source.import(options);
      
      // Process and add each imported item
      const results = {
        total: importedItems.length,
        successful: 0,
        failed: 0,
        items: []
      };
      
      for (const item of importedItems) {
        try {
          const id = await this.addKnowledgeItem(item);
          results.successful++;
          results.items.push({ id, title: item.title, success: true });
        } catch (error) {
          results.failed++;
          results.items.push({ title: item.title, success: false, error: error.message });
          this.logger.warn(`Failed to import item "${item.title}": ${error.message}`);
        }
      }
      
      this.logger.info(`Import completed: ${results.successful}/${results.total} items imported successfully`);
      this.emit("knowledgeImportCompleted", results);
      
      return results;
    } catch (error) {
      this.logger.error(`Failed to import knowledge: ${error.message}`, error);
      this.emit("knowledgeImportFailed", { sourceId, error: error.message });
      throw error;
    }
  }
  
  /**
   * Exports knowledge to an external destination
   * 
   * @param {string} connectorId - The ID of the knowledge connector
   * @param {Object} options - Export options specific to the connector
   * @returns {Promise<Object>} Export results
   */
  async exportKnowledge(connectorId, options = {}) {
    if (!this.isEnabled) {
      throw new Error("PersonalKnowledgeManager is disabled");
    }
    
    if (!this.knowledgeConnectors.has(connectorId)) {
      throw new Error(`Knowledge connector not found: ${connectorId}`);
    }
    
    this.logger.info(`Exporting knowledge to connector: ${connectorId}`);
    this.emit("knowledgeExportStarted", { connectorId, options });
    
    try {
      // Get items to export based on options
      const filters = options.filters || {};
      const items = await this._getKnowledgeItems(filters);
      
      // Export using the connector
      const connector = this.knowledgeConnectors.get(connectorId);
      const exportResults = await connector.export(items, options);
      
      this.logger.info(`Export completed: ${exportResults.successful}/${exportResults.total} items exported successfully`);
      this.emit("knowledgeExportCompleted", exportResults);
      
      return exportResults;
    } catch (error) {
      this.logger.error(`Failed to export knowledge: ${error.message}`, error);
      this.emit("knowledgeExportFailed", { connectorId, error: error.message });
      throw error;
    }
  }
  
  /**
   * Gets all available knowledge sources
   * 
   * @returns {Array} List of knowledge sources
   */
  getKnowledgeSources() {
    return Array.from(this.knowledgeSources.entries()).map(([id, source]) => ({
      id,
      name: source.name,
      description: source.description,
      capabilities: source.capabilities
    }));
  }
  
  /**
   * Gets all available knowledge connectors
   * 
   * @returns {Array} List of knowledge connectors
   */
  getKnowledgeConnectors() {
    return Array.from(this.knowledgeConnectors.entries()).map(([id, connector]) => ({
      id,
      name: connector.name,
      description: connector.description,
      capabilities: connector.capabilities
    }));
  }
  
  /**
   * Analyzes knowledge to extract insights
   * 
   * @param {Object} options - Analysis options
   * @returns {Promise<Object>} Analysis results
   */
  async analyzeKnowledge(options = {}) {
    if (!this.isEnabled) {
      throw new Error("PersonalKnowledgeManager is disabled");
    }
    
    this.logger.info("Analyzing knowledge base");
    
    try {
      // Get items to analyze based on options
      const filters = options.filters || {};
      const items = await this._getKnowledgeItems(filters);
      
      // Perform basic analysis
      const analysis = {
        totalItems: items.length,
        byType: {},
        byTag: {},
        byDate: {
          last7Days: 0,
          last30Days: 0,
          last90Days: 0,
          older: 0
        },
        mostAccessed: [],
        recentlyUpdated: []
      };
      
      const now = Date.now();
      const day = 24 * 60 * 60 * 1000;
      
      items.forEach(item => {
        // Count by type
        analysis.byType[item.type] = (analysis.byType[item.type] || 0) + 1;
        
        // Count by tag
        (item.metadata.tags || []).forEach(tag => {
          analysis.byTag[tag] = (analysis.byTag[tag] || 0) + 1;
        });
        
        // Count by date
        const age = now - item.metadata.created;
        if (age <= 7 * day) {
          analysis.byDate.last7Days++;
        } else if (age <= 30 * day) {
          analysis.byDate.last30Days++;
        } else if (age <= 90 * day) {
          analysis.byDate.last90Days++;
        } else {
          analysis.byDate.older++;
        }
      });
      
      // Sort items by access count and update date
      analysis.mostAccessed = items
        .filter(item => item.metadata.accessCount)
        .sort((a, b) => (b.metadata.accessCount || 0) - (a.metadata.accessCount || 0))
        .slice(0, 10)
        .map(item => ({
          id: item.id,
          title: item.title,
          type: item.type,
          accessCount: item.metadata.accessCount || 0
        }));
      
      analysis.recentlyUpdated = items
        .sort((a, b) => b.metadata.updated - a.metadata.updated)
        .slice(0, 10)
        .map(item => ({
          id: item.id,
          title: item.title,
          type: item.type,
          updated: item.metadata.updated
        }));
      
      this.logger.info("Knowledge analysis completed");
      this.emit("knowledgeAnalyzed", analysis);
      
      return analysis;
    } catch (error) {
      this.logger.error(`Failed to analyze knowledge: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Initializes knowledge sources
   * 
   * @private
   * @param {Object} config - Knowledge sources configuration
   */
  _initializeKnowledgeSources(config) {
    this.logger.debug("Initializing knowledge sources...");
    
    // Example: File system source
    this.knowledgeSources.set("filesystem", {
      name: "File System",
      description: "Import knowledge from local files and directories",
      capabilities: ["import"],
      import: async (options) => {
        console.log("[FileSystemSource] Importing from path:", options.path);
        // In a real implementation, this would scan files and convert them to knowledge items
        return [
          {
            title: "Example File",
            content: "This is content from a file import",
            type: "document",
            tags: ["imported", "file"]
          }
        ];
      }
    });
    
    // Example: Web page source
    this.knowledgeSources.set("webpage", {
      name: "Web Page",
      description: "Import knowledge from web pages",
      capabilities: ["import"],
      import: async (options) => {
        console.log("[WebPageSource] Importing from URL:", options.url);
        // In a real implementation, this would fetch and parse web pages
        return [
          {
            title: options.url ? `Page from ${options.url}` : "Example Web Page",
            content: "This is content from a web page import",
            type: "webpage",
            tags: ["imported", "web"],
            metadata: { url: options.url }
          }
        ];
      }
    });
    
    this.logger.info(`Initialized ${this.knowledgeSources.size} knowledge sources`);
  }
  
  /**
   * Initializes knowledge processors
   * 
   * @private
   * @param {Object} config - Knowledge processors configuration
   */
  _initializeKnowledgeProcessors(config) {
    this.logger.debug("Initializing knowledge processors...");
    
    // Example: Text processor
    this.knowledgeProcessors.set("text", {
      process: async (content) => {
        // In a real implementation, this might extract key phrases, entities, etc.
        return content;
      }
    });
    
    // Example: Document processor
    this.knowledgeProcessors.set("document", {
      process: async (content) => {
        // In a real implementation, this might extract structured data from documents
        return content;
      }
    });
    
    // Example: Code processor
    this.knowledgeProcessors.set("code", {
      process: async (content) => {
        // In a real implementation, this might extract functions, classes, etc.
        return content;
      }
    });
    
    this.logger.info(`Initialized ${this.knowledgeProcessors.size} knowledge processors`);
  }
  
  /**
   * Initializes knowledge connectors
   * 
   * @private
   * @param {Object} config - Knowledge connectors configuration
   */
  _initializeKnowledgeConnectors(config) {
    this.logger.debug("Initializing knowledge connectors...");
    
    // Example: Markdown connector
    this.knowledgeConnectors.set("markdown", {
      name: "Markdown",
      description: "Export knowledge as Markdown files",
      capabilities: ["export"],
      export: async (items, options) => {
        console.log("[MarkdownConnector] Exporting items:", items.length);
        // In a real implementation, this would convert items to Markdown and save them
        return {
          total: items.length,
          successful: items.length,
          failed: 0
        };
      }
    });
    
    // Example: JSON connector
    this.knowledgeConnectors.set("json", {
      name: "JSON",
      description: "Export knowledge as JSON files",
      capabilities: ["export"],
      export: async (items, options) => {
        console.log("[JSONConnector] Exporting items:", items.length);
        // In a real implementation, this would convert items to JSON and save them
        return {
          total: items.length,
          successful: items.length,
          failed: 0
        };
      }
    });
    
    this.logger.info(`Initialized ${this.knowledgeConnectors.size} knowledge connectors`);
  }
  
  /**
   * Ensures required directories exist
   * 
   * @private
   */
  async _ensureDirectories() {
    try {
      await fs.mkdir(this.knowledgeBasePath, { recursive: true });
      await fs.mkdir(this.knowledgeIndexPath, { recursive: true });
    } catch (error) {
      this.logger.error(`Failed to create directories: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Loads the knowledge index
   * 
   * @private
   */
  async _loadKnowledgeIndex() {
    try {
      const indexPath = path.join(this.knowledgeIndexPath, "index.json");
      
      try {
        const data = await fs.readFile(indexPath, "utf8");
        const index = JSON.parse(data);
        this.logger.info(`Loaded knowledge index with ${Object.keys(index).length} items`);
        
        // Rebuild vector store from index
        for (const [id, metadata] of Object.entries(index)) {
          try {
            const item = await this._loadKnowledgeItem(id);
            if (item) {
              await this.vectorStore.addItem(id, item.content, item.metadata);
            }
          } catch (error) {
            this.logger.warn(`Failed to load knowledge item ${id}: ${error.message}`);
          }
        }
      } catch (error) {
        if (error.code === "ENOENT") {
          this.logger.info("No knowledge index found, creating new index");
          await this._saveKnowledgeIndex({});
        } else {
          throw error;
        }
      }
    } catch (error) {
      this.logger.error(`Failed to load knowledge index: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Saves the knowledge index
   * 
   * @private
   * @param {Object} index - The index to save
   */
  async _saveKnowledgeIndex(index) {
    try {
      const indexPath = path.join(this.knowledgeIndexPath, "index.json");
      await fs.writeFile(indexPath, JSON.stringify(index, null, 2), "utf8");
      this.logger.debug("Saved knowledge index");
    } catch (error) {
      this.logger.error(`Failed to save knowledge index: ${error.message}`, error);
      throw error;
    }
  }
  
  /**
   * Loads a knowledge item from the knowledge base
   * 
   * @private
   * @param {string} id - The ID of the knowledge item to load
   * @returns {Promise<Object>} The knowledge item
   */
  async _loadKnowledgeItem(id) {
    try {
      const itemPath = path.join(this.knowledgeBasePath, `${id}.json`);
      const data = await fs.readFile(itemPath, "utf8");
      const item = JSON.parse(data);
      
      // Update access count
      if (item.metadata) {
        item.metadata.accessCount = (item.metadata.accessCount || 0) + 1;
        await fs.writeFile(itemPath, JSON.stringify(item, null, 2), "utf8");
      }
      
      return item;
    } catch (error) {
      if (error.code === "ENOENT") {
        return null;
      }
      throw error;
    }
  }
  
  /**
   * Saves a knowledge item to the knowledge base
   * 
   * @private
   * @param {string} id - The ID of the knowledge item
   * @param {Object} item - The knowledge item to save
   */
  async _saveKnowledgeItem(id, item) {
    try {
      const itemPath = path.join(this.knowledgeBasePath, `${id}.json`);
      await fs.writeFile(itemPath, JSON.stringify(item, null, 2), "utf8");
      
      // Update index
      const indexPath = path.join(this.knowledgeIndexPath, "index.json");
      let index = {};
      
      try {
        const data = await fs.readFile(indexPath, "utf8");
        index = JSON.parse(data);
      } catch (error) {
        if (error.code !== "ENOENT") {
          throw error;
        }
      }
      
      index[id] = {
        title: item.title,
        type: item.type,
        created: item.metadata.created,
        updated: item.metadata.updated
      };
      
      await this._saveKnowledgeIndex(index);
    } catch (error) {
      throw error;
    }
  }
  
  /**
   * Gets knowledge items based on filters
   * 
   * @private
   * @param {Object} filters - Metadata filters to apply
   * @returns {Promise<Array>} The filtered knowledge items
   */
  async _getKnowledgeItems(filters = {}) {
    try {
      const indexPath = path.join(this.knowledgeIndexPath, "index.json");
      const data = await fs.readFile(indexPath, "utf8");
      const index = JSON.parse(data);
      
      const items = [];
      for (const [id, metadata] of Object.entries(index)) {
        // Apply filters
        let match = true;
        for (const [key, value] of Object.entries(filters)) {
          if (metadata[key] !== value) {
            match = false;
            break;
          }
        }
        
        if (match) {
          try {
            const item = await this._loadKnowledgeItem(id);
            if (item) {
              items.push(item);
            }
          } catch (error) {
            this.logger.warn(`Failed to load knowledge item ${id}: ${error.message}`);
          }
        }
      }
      
      return items;
    } catch (error) {
      if (error.code === "ENOENT") {
        return [];
      }
      throw error;
    }
  }
  
  /**
   * Validates a knowledge item
   * 
   * @private
   * @param {Object} item - The knowledge item to validate
   * @throws {Error} If the item is invalid
   */
  _validateKnowledgeItem(item) {
    if (!item.content) {
      throw new Error("Knowledge item must have content");
    }
    
    if (!item.title) {
      throw new Error("Knowledge item must have a title");
    }
    
    if (!item.type) {
      throw new Error("Knowledge item must have a type");
    }
    
    // Additional validation could be performed here
  }
  
  /**
   * Registers event listeners
   * 
   * @private
   */
  _registerEventListeners() {
    // Listen for relevant events from other components
    // For example, listen for document creation/editing events to automatically capture knowledge
    
    // Example: Listen for document creation
    this.core.on("documentCreated", async (document) => {
      if (!this.isEnabled) return;
      
      try {
        // Automatically add document as knowledge item
        await this.addKnowledgeItem({
          title: document.title,
          content: document.content,
          type: "document",
          tags: ["auto-captured"],
          metadata: {
            source: "document_system",
            documentId: document.id
          }
        });
      } catch (error) {
        this.logger.warn(`Failed to auto-capture document: ${error.message}`);
      }
    });
  }
}

module.exports = { PersonalKnowledgeManager };
