/**
 * Memory Manager for Aideon AI Lite
 * 
 * Manages the memory and context preservation system for Aideon AI Lite.
 * Handles project-level memory persistence, conversation history, and artifact versioning.
 */

const EventEmitter = require('events');
const fs = require('fs').promises;
const path = require('path');
const { v4: uuidv4 } = require('uuid');

class MemoryManager extends EventEmitter {
  /**
   * Initialize the Memory Manager
   * @param {Object} config - Memory configuration
   */
  constructor(config) {
    super();
    
    this.config = config;
    this.initialized = false;
    this.memoryStore = {
      projects: new Map(),
      conversations: new Map(),
      tasks: new Map(),
      artifacts: new Map(),
      knowledge: new Map(),
      global: new Map()
    };
    
    this.persistencePath = config.persistencePath || path.join(process.cwd(), 'memory');
    this.maxHistoryLength = config.maxHistoryLength || 1000;
    this.autoSaveInterval = config.autoSaveInterval || 60000; // 1 minute
    this.autoSaveTimer = null;
  }
  
  /**
   * Initialize the memory system
   * @returns {Promise<void>}
   */
  async initialize() {
    if (this.initialized) {
      return;
    }
    
    try {
      // Ensure memory directory exists
      await fs.mkdir(this.persistencePath, { recursive: true });
      
      // Load persisted memory
      await this._loadPersistedMemory();
      
      // Start auto-save timer if enabled
      if (this.config.autoSave) {
        this._startAutoSave();
      }
      
      this.initialized = true;
    } catch (error) {
      throw new Error(`Failed to initialize memory system: ${error.message}`);
    }
  }
  
  /**
   * Create a new project
   * @param {Object} projectData - Project data
   * @returns {string} Project ID
   */
  createProject(projectData = {}) {
    const projectId = projectData.id || uuidv4();
    
    if (this.memoryStore.projects.has(projectId)) {
      throw new Error(`Project with ID ${projectId} already exists`);
    }
    
    const project = {
      id: projectId,
      name: projectData.name || 'Untitled Project',
      description: projectData.description || '',
      createdAt: projectData.createdAt || new Date(),
      updatedAt: new Date(),
      conversations: [],
      tasks: [],
      artifacts: [],
      metadata: projectData.metadata || {},
      context: projectData.context || {}
    };
    
    this.memoryStore.projects.set(projectId, project);
    this.emit('project:created', project);
    
    return projectId;
  }
  
  /**
   * Get a project by ID
   * @param {string} projectId - Project ID
   * @returns {Object} Project data
   */
  getProject(projectId) {
    const project = this.memoryStore.projects.get(projectId);
    
    if (!project) {
      throw new Error(`Project with ID ${projectId} not found`);
    }
    
    return project;
  }
  
  /**
   * Update a project
   * @param {string} projectId - Project ID
   * @param {Object} updateData - Data to update
   * @returns {Object} Updated project
   */
  updateProject(projectId, updateData) {
    const project = this.getProject(projectId);
    
    const updatedProject = {
      ...project,
      ...updateData,
      updatedAt: new Date()
    };
    
    this.memoryStore.projects.set(projectId, updatedProject);
    this.emit('project:updated', updatedProject);
    
    return updatedProject;
  }
  
  /**
   * Create a new conversation within a project
   * @param {string} projectId - Project ID
   * @param {Object} conversationData - Conversation data
   * @returns {string} Conversation ID
   */
  createConversation(projectId, conversationData = {}) {
    const project = this.getProject(projectId);
    const conversationId = conversationData.id || uuidv4();
    
    if (this.memoryStore.conversations.has(conversationId)) {
      throw new Error(`Conversation with ID ${conversationId} already exists`);
    }
    
    const conversation = {
      id: conversationId,
      projectId,
      name: conversationData.name || 'Untitled Conversation',
      createdAt: conversationData.createdAt || new Date(),
      updatedAt: new Date(),
      messages: [],
      artifacts: [],
      metadata: conversationData.metadata || {},
      context: conversationData.context || {}
    };
    
    this.memoryStore.conversations.set(conversationId, conversation);
    
    // Update project with new conversation
    project.conversations.push(conversationId);
    project.updatedAt = new Date();
    this.memoryStore.projects.set(projectId, project);
    
    this.emit('conversation:created', conversation);
    
    return conversationId;
  }
  
  /**
   * Get a conversation by ID
   * @param {string} conversationId - Conversation ID
   * @returns {Object} Conversation data
   */
  getConversation(conversationId) {
    const conversation = this.memoryStore.conversations.get(conversationId);
    
    if (!conversation) {
      throw new Error(`Conversation with ID ${conversationId} not found`);
    }
    
    return conversation;
  }
  
  /**
   * Add a message to a conversation
   * @param {string} conversationId - Conversation ID
   * @param {Object} messageData - Message data
   * @returns {string} Message ID
   */
  addMessage(conversationId, messageData) {
    const conversation = this.getConversation(conversationId);
    const messageId = messageData.id || uuidv4();
    
    const message = {
      id: messageId,
      conversationId,
      role: messageData.role || 'user',
      content: messageData.content,
      timestamp: messageData.timestamp || new Date(),
      metadata: messageData.metadata || {}
    };
    
    // Add message to conversation
    conversation.messages.push(message);
    conversation.updatedAt = new Date();
    this.memoryStore.conversations.set(conversationId, conversation);
    
    // Update project timestamp
    const project = this.getProject(conversation.projectId);
    project.updatedAt = new Date();
    this.memoryStore.projects.set(conversation.projectId, project);
    
    this.emit('message:added', message);
    
    return messageId;
  }
  
  /**
   * Create a new artifact with version control
   * @param {string} projectId - Project ID
   * @param {Object} artifactData - Artifact data
   * @returns {string} Artifact ID
   */
  createArtifact(projectId, artifactData) {
    const project = this.getProject(projectId);
    const artifactId = artifactData.id || uuidv4();
    
    const artifact = {
      id: artifactId,
      projectId,
      name: artifactData.name || 'Untitled Artifact',
      type: artifactData.type || 'generic',
      createdAt: artifactData.createdAt || new Date(),
      updatedAt: new Date(),
      versions: [],
      currentVersion: null,
      metadata: artifactData.metadata || {}
    };
    
    // Create initial version if content is provided
    if (artifactData.content) {
      const versionId = this._createArtifactVersion(artifact, {
        content: artifactData.content,
        description: 'Initial version'
      });
      artifact.currentVersion = versionId;
    }
    
    this.memoryStore.artifacts.set(artifactId, artifact);
    
    // Update project with new artifact
    project.artifacts.push(artifactId);
    project.updatedAt = new Date();
    this.memoryStore.projects.set(projectId, project);
    
    this.emit('artifact:created', artifact);
    
    return artifactId;
  }
  
  /**
   * Create a new version of an artifact
   * @param {string} artifactId - Artifact ID
   * @param {Object} versionData - Version data
   * @returns {string} Version ID
   */
  createArtifactVersion(artifactId, versionData) {
    const artifact = this.getArtifact(artifactId);
    return this._createArtifactVersion(artifact, versionData);
  }
  
  /**
   * Internal method to create artifact version
   * @param {Object} artifact - Artifact object
   * @param {Object} versionData - Version data
   * @returns {string} Version ID
   * @private
   */
  _createArtifactVersion(artifact, versionData) {
    const versionId = versionData.id || uuidv4();
    
    const version = {
      id: versionId,
      artifactId: artifact.id,
      versionNumber: artifact.versions.length + 1,
      content: versionData.content,
      description: versionData.description || '',
      createdAt: versionData.createdAt || new Date(),
      createdBy: versionData.createdBy || 'system',
      metadata: versionData.metadata || {}
    };
    
    // Add version to artifact
    artifact.versions.push(version);
    artifact.currentVersion = versionId;
    artifact.updatedAt = new Date();
    this.memoryStore.artifacts.set(artifact.id, artifact);
    
    // Update project timestamp
    const project = this.getProject(artifact.projectId);
    project.updatedAt = new Date();
    this.memoryStore.projects.set(artifact.projectId, project);
    
    this.emit('artifact:version:created', version);
    
    return versionId;
  }
  
  /**
   * Get an artifact by ID
   * @param {string} artifactId - Artifact ID
   * @returns {Object} Artifact data
   */
  getArtifact(artifactId) {
    const artifact = this.memoryStore.artifacts.get(artifactId);
    
    if (!artifact) {
      throw new Error(`Artifact with ID ${artifactId} not found`);
    }
    
    return artifact;
  }
  
  /**
   * Get a specific version of an artifact
   * @param {string} artifactId - Artifact ID
   * @param {string} versionId - Version ID
   * @returns {Object} Version data
   */
  getArtifactVersion(artifactId, versionId) {
    const artifact = this.getArtifact(artifactId);
    const version = artifact.versions.find(v => v.id === versionId);
    
    if (!version) {
      throw new Error(`Version ${versionId} of artifact ${artifactId} not found`);
    }
    
    return version;
  }
  
  /**
   * Get the current version of an artifact
   * @param {string} artifactId - Artifact ID
   * @returns {Object} Current version data
   */
  getCurrentArtifactVersion(artifactId) {
    const artifact = this.getArtifact(artifactId);
    
    if (!artifact.currentVersion) {
      throw new Error(`Artifact ${artifactId} has no versions`);
    }
    
    return this.getArtifactVersion(artifactId, artifact.currentVersion);
  }
  
  /**
   * Create a new task within a project
   * @param {string} projectId - Project ID
   * @param {Object} taskData - Task data
   * @returns {string} Task ID
   */
  createTask(projectId, taskData = {}) {
    const project = this.getProject(projectId);
    const taskId = taskData.id || uuidv4();
    
    if (this.memoryStore.tasks.has(taskId)) {
      throw new Error(`Task with ID ${taskId} already exists`);
    }
    
    const task = {
      id: taskId,
      projectId,
      name: taskData.name || 'Untitled Task',
      description: taskData.description || '',
      status: taskData.status || 'pending',
      createdAt: taskData.createdAt || new Date(),
      updatedAt: new Date(),
      completedAt: null,
      artifacts: [],
      history: [],
      metadata: taskData.metadata || {},
      context: taskData.context || {}
    };
    
    this.memoryStore.tasks.set(taskId, task);
    
    // Update project with new task
    project.tasks.push(taskId);
    project.updatedAt = new Date();
    this.memoryStore.projects.set(projectId, project);
    
    this.emit('task:created', task);
    
    return taskId;
  }
  
  /**
   * Get a task by ID
   * @param {string} taskId - Task ID
   * @returns {Object} Task data
   */
  getTask(taskId) {
    const task = this.memoryStore.tasks.get(taskId);
    
    if (!task) {
      throw new Error(`Task with ID ${taskId} not found`);
    }
    
    return task;
  }
  
  /**
   * Update a task
   * @param {string} taskId - Task ID
   * @param {Object} updateData - Data to update
   * @returns {Object} Updated task
   */
  updateTask(taskId, updateData) {
    const task = this.getTask(taskId);
    
    const updatedTask = {
      ...task,
      ...updateData,
      updatedAt: new Date()
    };
    
    // If status changed to completed, set completedAt
    if (updateData.status === 'completed' && task.status !== 'completed') {
      updatedTask.completedAt = new Date();
    }
    
    this.memoryStore.tasks.set(taskId, updatedTask);
    
    // Update project timestamp
    const project = this.getProject(task.projectId);
    project.updatedAt = new Date();
    this.memoryStore.projects.set(task.projectId, project);
    
    this.emit('task:updated', updatedTask);
    
    return updatedTask;
  }
  
  /**
   * Add an entry to task history
   * @param {string} taskId - Task ID
   * @param {Object} historyData - History entry data
   * @returns {string} History entry ID
   */
  addTaskHistory(taskId, historyData) {
    const task = this.getTask(taskId);
    const entryId = historyData.id || uuidv4();
    
    const entry = {
      id: entryId,
      taskId,
      type: historyData.type || 'event',
      content: historyData.content,
      timestamp: historyData.timestamp || new Date(),
      metadata: historyData.metadata || {}
    };
    
    // Add entry to task history
    task.history.push(entry);
    task.updatedAt = new Date();
    this.memoryStore.tasks.set(taskId, task);
    
    // Update project timestamp
    const project = this.getProject(task.projectId);
    project.updatedAt = new Date();
    this.memoryStore.projects.set(task.projectId, project);
    
    this.emit('task:history:added', entry);
    
    return entryId;
  }
  
  /**
   * Store knowledge in the global knowledge base
   * @param {string} key - Knowledge key
   * @param {any} value - Knowledge value
   * @param {Object} options - Storage options
   * @returns {boolean} Success status
   */
  storeKnowledge(key, value, options = {}) {
    const knowledgeItem = {
      key,
      value,
      createdAt: options.createdAt || new Date(),
      updatedAt: new Date(),
      expires: options.expires || null,
      metadata: options.metadata || {}
    };
    
    this.memoryStore.knowledge.set(key, knowledgeItem);
    this.emit('knowledge:stored', knowledgeItem);
    
    return true;
  }
  
  /**
   * Retrieve knowledge from the global knowledge base
   * @param {string} key - Knowledge key
   * @returns {any} Knowledge value or null if not found
   */
  retrieveKnowledge(key) {
    const knowledgeItem = this.memoryStore.knowledge.get(key);
    
    if (!knowledgeItem) {
      return null;
    }
    
    // Check if expired
    if (knowledgeItem.expires && knowledgeItem.expires < new Date()) {
      this.memoryStore.knowledge.delete(key);
      return null;
    }
    
    return knowledgeItem.value;
  }
  
  /**
   * Store context for a project
   * @param {string} projectId - Project ID
   * @param {string} key - Context key
   * @param {any} value - Context value
   * @returns {boolean} Success status
   */
  storeProjectContext(projectId, key, value) {
    const project = this.getProject(projectId);
    
    project.context[key] = value;
    project.updatedAt = new Date();
    this.memoryStore.projects.set(projectId, project);
    
    return true;
  }
  
  /**
   * Retrieve context for a project
   * @param {string} projectId - Project ID
   * @param {string} key - Context key
   * @returns {any} Context value or null if not found
   */
  retrieveProjectContext(projectId, key) {
    const project = this.getProject(projectId);
    return project.context[key] || null;
  }
  
  /**
   * Get memory statistics
   * @returns {Object} Memory statistics
   */
  getMemoryStats() {
    return {
      projects: this.memoryStore.projects.size,
      conversations: this.memoryStore.conversations.size,
      tasks: this.memoryStore.tasks.size,
      artifacts: this.memoryStore.artifacts.size,
      knowledge: this.memoryStore.knowledge.size,
      lastPersisted: this.lastPersisted
    };
  }
  
  /**
   * Persist memory to disk
   * @returns {Promise<boolean>} Success status
   */
  async persistMemory() {
    try {
      // Ensure memory directory exists
      await fs.mkdir(this.persistencePath, { recursive: true });
      
      // Convert Maps to serializable objects
      const serializedMemory = {
        projects: Object.fromEntries(this.memoryStore.projects),
        conversations: Object.fromEntries(this.memoryStore.conversations),
        tasks: Object.fromEntries(this.memoryStore.tasks),
        artifacts: Object.fromEntries(this.memoryStore.artifacts),
        knowledge: Object.fromEntries(this.memoryStore.knowledge),
        global: Object.fromEntries(this.memoryStore.global)
      };
      
      // Write to disk
      await fs.writeFile(
        path.join(this.persistencePath, 'memory.json'),
        JSON.stringify(serializedMemory, null, 2),
        'utf8'
      );
      
      this.lastPersisted = new Date();
      this.emit('memory:persisted', this.lastPersisted);
      
      return true;
    } catch (error) {
      this.emit('error', new Error(`Failed to persist memory: ${error.message}`));
      return false;
    }
  }
  
  /**
   * Load persisted memory from disk
   * @returns {Promise<boolean>} Success status
   * @private
   */
  async _loadPersistedMemory() {
    try {
      const memoryFilePath = path.join(this.persistencePath, 'memory.json');
      
      // Check if memory file exists
      try {
        await fs.access(memoryFilePath);
      } catch (error) {
        // File doesn't exist, nothing to load
        return true;
      }
      
      // Read and parse memory file
      const memoryData = JSON.parse(
        await fs.readFile(memoryFilePath, 'utf8')
      );
      
      // Convert serialized objects back to Maps
      this.memoryStore.projects = new Map(Object.entries(memoryData.projects || {}));
      this.memoryStore.conversations = new Map(Object.entries(memoryData.conversations || {}));
      this.memoryStore.tasks = new Map(Object.entries(memoryData.tasks || {}));
      this.memoryStore.artifacts = new Map(Object.entries(memoryData.artifacts || {}));
      this.memoryStore.knowledge = new Map(Object.entries(memoryData.knowledge || {}));
      this.memoryStore.global = new Map(Object.entries(memoryData.global || {}));
      
      this.emit('memory:loaded');
      
      return true;
    } catch (error) {
      this.emit('error', new Error(`Failed to load persisted memory: ${error.message}`));
      return false;
    }
  }
  
  /**
   * Start auto-save timer
   * @private
   */
  _startAutoSave() {
    if (this.autoSaveTimer) {
      clearInterval(this.autoSaveTimer);
    }
    
    this.autoSaveTimer = setInterval(
      () => this.persistMemory(),
      this.autoSaveInterval
    );
  }
  
  /**
   * Stop auto-save timer
   * @private
   */
  _stopAutoSave() {
    if (this.autoSaveTimer) {
      clearInterval(this.autoSaveTimer);
      this.autoSaveTimer = null;
    }
  }
  
  /**
   * Clean up resources
   */
  async shutdown() {
    this._stopAutoSave();
    await this.persistMemory();
  }
}

module.exports = { MemoryManager };
