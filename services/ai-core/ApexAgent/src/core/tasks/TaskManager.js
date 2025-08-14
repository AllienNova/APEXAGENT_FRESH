/**
 * Task Manager for Aideon AI Lite
 * 
 * Manages the task processing system for Aideon AI Lite.
 * Handles task creation, scheduling, execution, and monitoring.
 */

const EventEmitter = require('events');
const { v4: uuidv4 } = require('uuid');
const PriorityQueue = require('../utils/PriorityQueue');

class TaskManager extends EventEmitter {
  /**
   * Initialize the Task Manager
   * @param {Object} config - Task manager configuration
   */
  constructor(config) {
    super();
    
    this.config = config;
    this.initialized = false;
    this.taskQueue = new PriorityQueue();
    this.activeTasks = new Map();
    this.completedTasks = new Map();
    this.failedTasks = new Map();
    
    this.maxConcurrentTasks = config.maxConcurrentTasks || 5;
    this.taskTimeout = config.taskTimeout || 300000; // 5 minutes
    this.retryLimit = config.retryLimit || 3;
    
    this.processingTimer = null;
    this.stats = {
      totalSubmitted: 0,
      totalCompleted: 0,
      totalFailed: 0,
      averageProcessingTime: 0
    };
  }
  
  /**
   * Initialize the task manager
   * @returns {Promise<void>}
   */
  async initialize() {
    if (this.initialized) {
      return;
    }
    
    // Start task processing loop
    this._startProcessingLoop();
    
    this.initialized = true;
  }
  
  /**
   * Submit a new task for processing
   * @param {Object} taskData - Task data
   * @returns {Promise<Object>} Task result
   */
  async submitTask(taskData) {
    if (!this.initialized) {
      throw new Error('Task Manager is not initialized');
    }
    
    // Create task object
    const taskId = taskData.id || uuidv4();
    const task = {
      id: taskId,
      description: taskData.description,
      type: taskData.type || 'general',
      priority: taskData.priority || 5, // 1-10, 10 being highest
      status: 'pending',
      createdAt: new Date(),
      startedAt: null,
      completedAt: null,
      timeout: taskData.timeout || this.taskTimeout,
      retryCount: 0,
      retryLimit: taskData.retryLimit || this.retryLimit,
      result: null,
      error: null,
      progress: 0,
      metadata: taskData.metadata || {},
      options: taskData.options || {}
    };
    
    // Create promise for task completion
    const taskPromise = new Promise((resolve, reject) => {
      task.resolve = resolve;
      task.reject = reject;
    });
    
    // Add task to queue
    this.taskQueue.enqueue(task, task.priority);
    this.stats.totalSubmitted++;
    
    this.emit('task:submitted', task);
    
    return taskPromise;
  }
  
  /**
   * Get a task by ID
   * @param {string} taskId - Task ID
   * @returns {Object|null} Task object or null if not found
   */
  getTask(taskId) {
    // Check active tasks
    if (this.activeTasks.has(taskId)) {
      return this.activeTasks.get(taskId);
    }
    
    // Check completed tasks
    if (this.completedTasks.has(taskId)) {
      return this.completedTasks.get(taskId);
    }
    
    // Check failed tasks
    if (this.failedTasks.has(taskId)) {
      return this.failedTasks.get(taskId);
    }
    
    // Check queue
    const queuedTask = this.taskQueue.find(task => task.id === taskId);
    if (queuedTask) {
      return queuedTask;
    }
    
    return null;
  }
  
  /**
   * Get task statistics
   * @returns {Object} Task statistics
   */
  getTaskStats() {
    return {
      ...this.stats,
      queued: this.taskQueue.size(),
      active: this.activeTasks.size,
      completed: this.completedTasks.size,
      failed: this.failedTasks.size
    };
  }
  
  /**
   * Stop all tasks and clear the queue
   * @returns {Promise<void>}
   */
  async stopAllTasks() {
    // Clear the queue
    this.taskQueue.clear();
    
    // Cancel all active tasks
    for (const task of this.activeTasks.values()) {
      this._failTask(task, new Error('Task cancelled due to system shutdown'));
    }
    
    // Stop processing loop
    this._stopProcessingLoop();
  }
  
  /**
   * Start the task processing loop
   * @private
   */
  _startProcessingLoop() {
    if (this.processingTimer) {
      clearInterval(this.processingTimer);
    }
    
    // Process tasks every 100ms
    this.processingTimer = setInterval(() => {
      this._processNextTasks();
    }, 100);
  }
  
  /**
   * Stop the task processing loop
   * @private
   */
  _stopProcessingLoop() {
    if (this.processingTimer) {
      clearInterval(this.processingTimer);
      this.processingTimer = null;
    }
  }
  
  /**
   * Process next tasks in queue
   * @private
   */
  _processNextTasks() {
    // Check if we can process more tasks
    const availableSlots = this.maxConcurrentTasks - this.activeTasks.size;
    
    if (availableSlots <= 0 || this.taskQueue.isEmpty()) {
      return;
    }
    
    // Process up to availableSlots tasks
    for (let i = 0; i < availableSlots && !this.taskQueue.isEmpty(); i++) {
      const task = this.taskQueue.dequeue();
      this._processTask(task);
    }
  }
  
  /**
   * Process a single task
   * @param {Object} task - Task to process
   * @private
   */
  async _processTask(task) {
    // Mark task as active
    task.status = 'processing';
    task.startedAt = new Date();
    this.activeTasks.set(task.id, task);
    
    // Set up timeout
    const timeoutId = setTimeout(() => {
      this._handleTaskTimeout(task);
    }, task.timeout);
    
    this.emit('task:started', task);
    
    try {
      // Get core from parent (should be set during initialization)
      const core = this.parent;
      
      // Use agent manager to coordinate task
      const result = await core.agentManager.coordinateTask(task);
      
      // Clear timeout
      clearTimeout(timeoutId);
      
      // Complete task
      this._completeTask(task, result);
    } catch (error) {
      // Clear timeout
      clearTimeout(timeoutId);
      
      // Handle error
      this._handleTaskError(task, error);
    }
  }
  
  /**
   * Handle task timeout
   * @param {Object} task - Task that timed out
   * @private
   */
  _handleTaskTimeout(task) {
    const error = new Error(`Task timed out after ${task.timeout}ms`);
    this._handleTaskError(task, error);
  }
  
  /**
   * Handle task error
   * @param {Object} task - Task with error
   * @param {Error} error - Error object
   * @private
   */
  _handleTaskError(task, error) {
    // Check if we should retry
    if (task.retryCount < task.retryLimit) {
      this._retryTask(task, error);
    } else {
      this._failTask(task, error);
    }
  }
  
  /**
   * Retry a failed task
   * @param {Object} task - Task to retry
   * @param {Error} error - Error that caused the retry
   * @private
   */
  _retryTask(task, error) {
    // Remove from active tasks
    this.activeTasks.delete(task.id);
    
    // Increment retry count
    task.retryCount++;
    task.status = 'pending';
    task.startedAt = null;
    task.error = null;
    
    // Re-queue with higher priority
    const retryPriority = Math.min(10, task.priority + 1);
    this.taskQueue.enqueue(task, retryPriority);
    
    this.emit('task:retry', task, error);
  }
  
  /**
   * Mark a task as failed
   * @param {Object} task - Task to fail
   * @param {Error} error - Error that caused the failure
   * @private
   */
  _failTask(task, error) {
    // Remove from active tasks
    this.activeTasks.delete(task.id);
    
    // Update task
    task.status = 'failed';
    task.completedAt = new Date();
    task.error = {
      message: error.message,
      stack: error.stack,
      code: error.code
    };
    
    // Add to failed tasks
    this.failedTasks.set(task.id, task);
    this.stats.totalFailed++;
    
    // Reject promise
    if (task.reject) {
      task.reject(error);
    }
    
    this.emit('task:failed', task, error);
  }
  
  /**
   * Mark a task as completed
   * @param {Object} task - Task to complete
   * @param {any} result - Task result
   * @private
   */
  _completeTask(task, result) {
    // Remove from active tasks
    this.activeTasks.delete(task.id);
    
    // Calculate processing time
    const processingTime = new Date() - task.startedAt;
    
    // Update task
    task.status = 'completed';
    task.completedAt = new Date();
    task.result = result;
    task.progress = 100;
    
    // Add to completed tasks
    this.completedTasks.set(task.id, task);
    this.stats.totalCompleted++;
    
    // Update average processing time
    this.stats.averageProcessingTime = 
      (this.stats.averageProcessingTime * (this.stats.totalCompleted - 1) + processingTime) / 
      this.stats.totalCompleted;
    
    // Resolve promise
    if (task.resolve) {
      task.resolve(result);
    }
    
    this.emit('task:completed', task, result);
  }
  
  /**
   * Update task progress
   * @param {string} taskId - Task ID
   * @param {number} progress - Progress percentage (0-100)
   * @param {string} [statusMessage] - Optional status message
   * @returns {boolean} Success status
   */
  updateTaskProgress(taskId, progress, statusMessage) {
    const task = this.activeTasks.get(taskId);
    
    if (!task) {
      return false;
    }
    
    // Update progress
    task.progress = Math.max(0, Math.min(100, progress));
    
    // Update status message if provided
    if (statusMessage) {
      task.statusMessage = statusMessage;
    }
    
    this.emit('task:progress', task);
    
    return true;
  }
}

module.exports = { TaskManager };
