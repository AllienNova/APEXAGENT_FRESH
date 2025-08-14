/**
 * LocalProcessingManager.js
 * 
 * Manages local processing capabilities for Aideon AI Lite.
 * Handles resource allocation, process scheduling, and optimization
 * for tasks that can be executed locally on the user's device.
 * 
 * @author Aideon AI Team
 * @version 1.0.0
 */

const EventEmitter = require('events');
const os = require('os');
const { Worker } = require('worker_threads');
const path = require('path');
const { v4: uuidv4 } = require('uuid');

/**
 * LocalProcessingManager class for managing local processing capabilities
 */
class LocalProcessingManager extends EventEmitter {
  /**
   * Create a new LocalProcessingManager instance
   * @param {Object} config - Configuration options
   */
  constructor(config = {}) {
    super();
    
    this.config = {
      enabled: config.enabled !== undefined ? config.enabled : true,
      maxConcurrency: config.maxConcurrency || Math.max(1, os.cpus().length - 1),
      workerTimeout: config.workerTimeout || 60000, // 1 minute
      workerPath: config.workerPath || path.join(__dirname, 'workers'),
      priorityLevels: config.priorityLevels || {
        low: 0,
        normal: 1,
        high: 2,
        critical: 3
      },
      ...config
    };
    
    // Initialize worker pool
    this.workers = new Map();
    this.availableWorkers = [];
    
    // Initialize task queue
    this.taskQueue = [];
    this.activeTasks = new Map();
    
    // Initialize resource monitoring
    this.resources = {
      cpu: {
        usage: 0,
        limit: config.cpuLimit || 0.8 // 80% max usage
      },
      memory: {
        usage: 0,
        limit: config.memoryLimit || 0.8 // 80% max usage
      }
    };
    
    // Initialize metrics
    this.metrics = {
      tasksProcessed: 0,
      tasksSucceeded: 0,
      tasksFailed: 0,
      averageProcessingTime: 0,
      peakConcurrency: 0
    };
    
    // Resource monitoring interval
    this.monitoringInterval = null;
    
    console.log('LocalProcessingManager initialized');
  }
  
  /**
   * Initialize the LocalProcessingManager
   * @returns {Promise<boolean>} Success status
   */
  async initialize() {
    if (!this.config.enabled) {
      console.log('Local processing is disabled');
      return false;
    }
    
    try {
      console.log('Initializing LocalProcessingManager');
      
      // Initialize worker pool
      await this._initializeWorkerPool();
      
      // Start resource monitoring
      this._startResourceMonitoring();
      
      console.log(`LocalProcessingManager initialized with ${this.config.maxConcurrency} workers`);
      
      return true;
    } catch (error) {
      console.error('Error initializing LocalProcessingManager:', error);
      throw error;
    }
  }
  
  /**
   * Initialize the worker pool
   * @private
   * @returns {Promise<void>}
   */
  async _initializeWorkerPool() {
    try {
      console.log(`Initializing worker pool with ${this.config.maxConcurrency} workers`);
      
      for (let i = 0; i < this.config.maxConcurrency; i++) {
        const workerId = `worker-${i}`;
        
        // Create worker
        const worker = new Worker(path.join(this.config.workerPath, 'processor.js'), {
          workerData: {
            id: workerId,
            config: this.config
          }
        });
        
        // Set up worker event handlers
        worker.on('message', (message) => this._handleWorkerMessage(workerId, message));
        worker.on('error', (error) => this._handleWorkerError(workerId, error));
        worker.on('exit', (code) => this._handleWorkerExit(workerId, code));
        
        // Add worker to pool
        this.workers.set(workerId, {
          id: workerId,
          worker,
          status: 'idle',
          currentTask: null,
          startTime: Date.now(),
          tasksProcessed: 0,
          lastActive: Date.now()
        });
        
        this.availableWorkers.push(workerId);
        
        console.log(`Worker ${workerId} initialized`);
      }
    } catch (error) {
      console.error('Error initializing worker pool:', error);
      throw error;
    }
  }
  
  /**
   * Start resource monitoring
   * @private
   */
  _startResourceMonitoring() {
    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval);
    }
    
    this.monitoringInterval = setInterval(() => {
      this._monitorResources();
    }, 5000); // Check every 5 seconds
  }
  
  /**
   * Monitor system resources
   * @private
   */
  _monitorResources() {
    try {
      // Get CPU usage
      const cpus = os.cpus();
      let totalIdle = 0;
      let totalTick = 0;
      
      for (const cpu of cpus) {
        for (const type in cpu.times) {
          totalTick += cpu.times[type];
        }
        totalIdle += cpu.times.idle;
      }
      
      const idle = totalIdle / cpus.length;
      const total = totalTick / cpus.length;
      const usage = 1 - idle / total;
      
      this.resources.cpu.usage = usage;
      
      // Get memory usage
      const totalMemory = os.totalmem();
      const freeMemory = os.freemem();
      const usedMemory = totalMemory - freeMemory;
      const memoryUsage = usedMemory / totalMemory;
      
      this.resources.memory.usage = memoryUsage;
      
      // Check if we're over resource limits
      if (usage > this.resources.cpu.limit) {
        console.warn(`CPU usage (${Math.round(usage * 100)}%) exceeds limit (${Math.round(this.resources.cpu.limit * 100)}%)`);
        this._throttleProcessing();
      }
      
      if (memoryUsage > this.resources.memory.limit) {
        console.warn(`Memory usage (${Math.round(memoryUsage * 100)}%) exceeds limit (${Math.round(this.resources.memory.limit * 100)}%)`);
        this._throttleProcessing();
      }
    } catch (error) {
      console.error('Error monitoring resources:', error);
    }
  }
  
  /**
   * Throttle processing when resource limits are exceeded
   * @private
   */
  _throttleProcessing() {
    // Pause processing of new tasks
    const pauseDuration = 5000; // 5 seconds
    
    console.log(`Throttling processing for ${pauseDuration}ms due to resource constraints`);
    
    // Emit throttling event
    this.emit('processing:throttled', {
      duration: pauseDuration,
      cpuUsage: this.resources.cpu.usage,
      memoryUsage: this.resources.memory.usage
    });
    
    // Resume processing after pause
    setTimeout(() => {
      console.log('Resuming processing after throttling');
      this._processNextTask();
    }, pauseDuration);
  }
  
  /**
   * Handle worker message
   * @param {string} workerId - Worker ID
   * @param {Object} message - Message from worker
   * @private
   */
  _handleWorkerMessage(workerId, message) {
    const workerInfo = this.workers.get(workerId);
    
    if (!workerInfo) {
      console.warn(`Received message from unknown worker: ${workerId}`);
      return;
    }
    
    switch (message.type) {
      case 'task:result':
        this._handleTaskResult(workerId, message.taskId, message.result);
        break;
      case 'task:progress':
        this._handleTaskProgress(workerId, message.taskId, message.progress);
        break;
      case 'worker:status':
        this._updateWorkerStatus(workerId, message.status);
        break;
      default:
        console.warn(`Unknown message type from worker ${workerId}:`, message.type);
    }
  }
  
  /**
   * Handle worker error
   * @param {string} workerId - Worker ID
   * @param {Error} error - Error from worker
   * @private
   */
  _handleWorkerError(workerId, error) {
    console.error(`Error in worker ${workerId}:`, error);
    
    const workerInfo = this.workers.get(workerId);
    
    if (!workerInfo) {
      return;
    }
    
    // If worker was processing a task, mark it as failed
    if (workerInfo.currentTask) {
      const taskId = workerInfo.currentTask;
      const taskInfo = this.activeTasks.get(taskId);
      
      if (taskInfo) {
        this._handleTaskFailure(workerId, taskId, error);
      }
    }
    
    // Restart the worker
    this._restartWorker(workerId);
  }
  
  /**
   * Handle worker exit
   * @param {string} workerId - Worker ID
   * @param {number} code - Exit code
   * @private
   */
  _handleWorkerExit(workerId, code) {
    console.log(`Worker ${workerId} exited with code ${code}`);
    
    const workerInfo = this.workers.get(workerId);
    
    if (!workerInfo) {
      return;
    }
    
    // If worker was processing a task, mark it as failed
    if (workerInfo.currentTask) {
      const taskId = workerInfo.currentTask;
      const taskInfo = this.activeTasks.get(taskId);
      
      if (taskInfo) {
        this._handleTaskFailure(workerId, taskId, new Error(`Worker exited with code ${code}`));
      }
    }
    
    // Remove worker from pool
    this.workers.delete(workerId);
    
    // Remove from available workers if present
    const availableIndex = this.availableWorkers.indexOf(workerId);
    if (availableIndex !== -1) {
      this.availableWorkers.splice(availableIndex, 1);
    }
    
    // Restart the worker if exit was unexpected
    if (code !== 0) {
      this._restartWorker(workerId);
    }
  }
  
  /**
   * Restart a worker
   * @param {string} workerId - Worker ID
   * @private
   */
  async _restartWorker(workerId) {
    try {
      console.log(`Restarting worker ${workerId}`);
      
      // Create new worker
      const worker = new Worker(path.join(this.config.workerPath, 'processor.js'), {
        workerData: {
          id: workerId,
          config: this.config
        }
      });
      
      // Set up worker event handlers
      worker.on('message', (message) => this._handleWorkerMessage(workerId, message));
      worker.on('error', (error) => this._handleWorkerError(workerId, error));
      worker.on('exit', (code) => this._handleWorkerExit(workerId, code));
      
      // Add worker to pool
      this.workers.set(workerId, {
        id: workerId,
        worker,
        status: 'idle',
        currentTask: null,
        startTime: Date.now(),
        tasksProcessed: 0,
        lastActive: Date.now()
      });
      
      this.availableWorkers.push(workerId);
      
      console.log(`Worker ${workerId} restarted`);
    } catch (error) {
      console.error(`Error restarting worker ${workerId}:`, error);
    }
  }
  
  /**
   * Update worker status
   * @param {string} workerId - Worker ID
   * @param {string} status - New status
   * @private
   */
  _updateWorkerStatus(workerId, status) {
    const workerInfo = this.workers.get(workerId);
    
    if (!workerInfo) {
      return;
    }
    
    workerInfo.status = status;
    workerInfo.lastActive = Date.now();
    
    // If worker is now idle, add to available workers
    if (status === 'idle' && !this.availableWorkers.includes(workerId)) {
      this.availableWorkers.push(workerId);
      this._processNextTask();
    }
  }
  
  /**
   * Handle task result
   * @param {string} workerId - Worker ID
   * @param {string} taskId - Task ID
   * @param {Object} result - Task result
   * @private
   */
  _handleTaskResult(workerId, taskId, result) {
    const taskInfo = this.activeTasks.get(taskId);
    
    if (!taskInfo) {
      console.warn(`Received result for unknown task: ${taskId}`);
      return;
    }
    
    const workerInfo = this.workers.get(workerId);
    
    if (!workerInfo) {
      console.warn(`Received result from unknown worker: ${workerId}`);
      return;
    }
    
    // Update task info
    taskInfo.status = 'completed';
    taskInfo.result = result;
    taskInfo.endTime = Date.now();
    taskInfo.processingTime = taskInfo.endTime - taskInfo.startTime;
    
    // Update worker info
    workerInfo.status = 'idle';
    workerInfo.currentTask = null;
    workerInfo.tasksProcessed++;
    workerInfo.lastActive = Date.now();
    
    // Add worker back to available pool
    if (!this.availableWorkers.includes(workerId)) {
      this.availableWorkers.push(workerId);
    }
    
    // Update metrics
    this.metrics.tasksProcessed++;
    this.metrics.tasksSucceeded++;
    this.metrics.averageProcessingTime = (
      (this.metrics.averageProcessingTime * (this.metrics.tasksProcessed - 1)) +
      taskInfo.processingTime
    ) / this.metrics.tasksProcessed;
    
    // Resolve task promise
    taskInfo.resolve(result);
    
    // Remove from active tasks
    this.activeTasks.delete(taskId);
    
    // Emit task completed event
    this.emit('task:completed', {
      taskId,
      workerId,
      processingTime: taskInfo.processingTime,
      result
    });
    
    // Process next task
    this._processNextTask();
  }
  
  /**
   * Handle task progress
   * @param {string} workerId - Worker ID
   * @param {string} taskId - Task ID
   * @param {Object} progress - Progress information
   * @private
   */
  _handleTaskProgress(workerId, taskId, progress) {
    const taskInfo = this.activeTasks.get(taskId);
    
    if (!taskInfo) {
      return;
    }
    
    // Update task progress
    taskInfo.progress = progress;
    
    // Emit task progress event
    this.emit('task:progress', {
      taskId,
      workerId,
      progress
    });
  }
  
  /**
   * Handle task failure
   * @param {string} workerId - Worker ID
   * @param {string} taskId - Task ID
   * @param {Error} error - Error that caused the failure
   * @private
   */
  _handleTaskFailure(workerId, taskId, error) {
    const taskInfo = this.activeTasks.get(taskId);
    
    if (!taskInfo) {
      console.warn(`Received failure for unknown task: ${taskId}`);
      return;
    }
    
    const workerInfo = this.workers.get(workerId);
    
    if (!workerInfo) {
      console.warn(`Received failure from unknown worker: ${workerId}`);
      return;
    }
    
    // Update task info
    taskInfo.status = 'failed';
    taskInfo.error = error.message;
    taskInfo.endTime = Date.now();
    taskInfo.processingTime = taskInfo.endTime - taskInfo.startTime;
    
    // Update worker info
    workerInfo.status = 'idle';
    workerInfo.currentTask = null;
    workerInfo.lastActive = Date.now();
    
    // Add worker back to available pool
    if (!this.availableWorkers.includes(workerId)) {
      this.availableWorkers.push(workerId);
    }
    
    // Update metrics
    this.metrics.tasksProcessed++;
    this.metrics.tasksFailed++;
    
    // Reject task promise
    taskInfo.reject(error);
    
    // Remove from active tasks
    this.activeTasks.delete(taskId);
    
    // Emit task failed event
    this.emit('task:failed', {
      taskId,
      workerId,
      error: error.message
    });
    
    // Process next task
    this._processNextTask();
  }
  
  /**
   * Process a task locally
   * @param {Object} task - Task to process
   * @param {Object} options - Processing options
   * @returns {Promise<Object>} Task result
   */
  async processTask(task, options = {}) {
    if (!this.config.enabled) {
      throw new Error('Local processing is disabled');
    }
    
    // Generate task ID if not provided
    const taskId = task.id || uuidv4();
    
    // Set default priority if not provided
    const priority = options.priority || 'normal';
    const priorityLevel = this.config.priorityLevels[priority] || this.config.priorityLevels.normal;
    
    // Create task promise
    const taskPromise = new Promise((resolve, reject) => {
      // Create task info
      const taskInfo = {
        id: taskId,
        task,
        options,
        priority,
        priorityLevel,
        status: 'queued',
        progress: 0,
        startTime: Date.now(),
        endTime: null,
        processingTime: null,
        result: null,
        error: null,
        resolve,
        reject
      };
      
      // Add to task queue
      this._addToTaskQueue(taskInfo);
      
      // Emit task queued event
      this.emit('task:queued', {
        taskId,
        priority,
        queueLength: this.taskQueue.length
      });
      
      // Process next task if workers are available
      this._processNextTask();
    });
    
    return taskPromise;
  }
  
  /**
   * Add a task to the queue
   * @param {Object} taskInfo - Task information
   * @private
   */
  _addToTaskQueue(taskInfo) {
    // Find position in queue based on priority
    let insertIndex = this.taskQueue.length;
    
    for (let i = 0; i < this.taskQueue.length; i++) {
      if (taskInfo.priorityLevel > this.taskQueue[i].priorityLevel) {
        insertIndex = i;
        break;
      }
    }
    
    // Insert task at the appropriate position
    this.taskQueue.splice(insertIndex, 0, taskInfo);
  }
  
  /**
   * Process the next task in the queue
   * @private
   */
  _processNextTask() {
    // Check if there are available workers
    if (this.availableWorkers.length === 0) {
      return;
    }
    
    // Check if there are tasks in the queue
    if (this.taskQueue.length === 0) {
      return;
    }
    
    // Get next task
    const taskInfo = this.taskQueue.shift();
    
    // Get available worker
    const workerId = this.availableWorkers.shift();
    const workerInfo = this.workers.get(workerId);
    
    if (!workerInfo) {
      // Worker no longer exists, put task back in queue
      this.taskQueue.unshift(taskInfo);
      return;
    }
    
    // Update task info
    taskInfo.status = 'processing';
    taskInfo.startTime = Date.now();
    
    // Update worker info
    workerInfo.status = 'busy';
    workerInfo.currentTask = taskInfo.id;
    workerInfo.lastActive = Date.now();
    
    // Add to active tasks
    this.activeTasks.set(taskInfo.id, taskInfo);
    
    // Update metrics
    const currentConcurrency = this.activeTasks.size;
    if (currentConcurrency > this.metrics.peakConcurrency) {
      this.metrics.peakConcurrency = currentConcurrency;
    }
    
    // Send task to worker
    workerInfo.worker.postMessage({
      type: 'task:process',
      taskId: taskInfo.id,
      task: taskInfo.task,
      options: taskInfo.options
    });
    
    // Emit task started event
    this.emit('task:started', {
      taskId: taskInfo.id,
      workerId,
      concurrency: this.activeTasks.size
    });
  }
  
  /**
   * Cancel a task
   * @param {string} taskId - ID of the task to cancel
   * @returns {boolean} Whether the task was cancelled
   */
  cancelTask(taskId) {
    // Check if task is in queue
    const queueIndex = this.taskQueue.findIndex(task => task.id === taskId);
    
    if (queueIndex !== -1) {
      // Remove from queue
      const taskInfo = this.taskQueue.splice(queueIndex, 1)[0];
      
      // Reject task promise
      taskInfo.reject(new Error('Task cancelled'));
      
      // Emit task cancelled event
      this.emit('task:cancelled', {
        taskId,
        status: 'queued'
      });
      
      return true;
    }
    
    // Check if task is active
    const taskInfo = this.activeTasks.get(taskId);
    
    if (taskInfo) {
      // Find worker processing this task
      let workerId = null;
      
      for (const [id, info] of this.workers.entries()) {
        if (info.currentTask === taskId) {
          workerId = id;
          break;
        }
      }
      
      if (workerId) {
        const workerInfo = this.workers.get(workerId);
        
        // Send cancel message to worker
        workerInfo.worker.postMessage({
          type: 'task:cancel',
          taskId
        });
        
        // Update worker info
        workerInfo.status = 'idle';
        workerInfo.currentTask = null;
        workerInfo.lastActive = Date.now();
        
        // Add worker back to available pool
        if (!this.availableWorkers.includes(workerId)) {
          this.availableWorkers.push(workerId);
        }
      }
      
      // Update task info
      taskInfo.status = 'cancelled';
      taskInfo.endTime = Date.now();
      taskInfo.processingTime = taskInfo.endTime - taskInfo.startTime;
      
      // Reject task promise
      taskInfo.reject(new Error('Task cancelled'));
      
      // Remove from active tasks
      this.activeTasks.delete(taskId);
      
      // Emit task cancelled event
      this.emit('task:cancelled', {
        taskId,
        status: 'processing',
        workerId
      });
      
      // Process next task
      this._processNextTask();
      
      return true;
    }
    
    return false;
  }
  
  /**
   * Get task status
   * @param {string} taskId - ID of the task
   * @returns {Object|null} Task status or null if not found
   */
  getTaskStatus(taskId) {
    // Check active tasks
    const activeTask = this.activeTasks.get(taskId);
    
    if (activeTask) {
      return {
        id: activeTask.id,
        status: activeTask.status,
        progress: activeTask.progress,
        startTime: activeTask.startTime,
        processingTime: Date.now() - activeTask.startTime
      };
    }
    
    // Check queued tasks
    const queuedTask = this.taskQueue.find(task => task.id === taskId);
    
    if (queuedTask) {
      return {
        id: queuedTask.id,
        status: 'queued',
        priority: queuedTask.priority,
        queuePosition: this.taskQueue.indexOf(queuedTask) + 1,
        queuedTime: Date.now() - queuedTask.startTime
      };
    }
    
    return null;
  }
  
  /**
   * Get status of all tasks
   * @returns {Object} Status of all tasks
   */
  getAllTaskStatus() {
    return {
      queued: this.taskQueue.length,
      active: this.activeTasks.size,
      queuedTasks: this.taskQueue.map((task, index) => ({
        id: task.id,
        status: 'queued',
        priority: task.priority,
        queuePosition: index + 1,
        queuedTime: Date.now() - task.startTime
      })),
      activeTasks: Array.from(this.activeTasks.values()).map(task => ({
        id: task.id,
        status: task.status,
        progress: task.progress,
        startTime: task.startTime,
        processingTime: Date.now() - task.startTime
      }))
    };
  }
  
  /**
   * Get worker status
   * @param {string} workerId - ID of the worker
   * @returns {Object|null} Worker status or null if not found
   */
  getWorkerStatus(workerId) {
    const workerInfo = this.workers.get(workerId);
    
    if (!workerInfo) {
      return null;
    }
    
    return {
      id: workerInfo.id,
      status: workerInfo.status,
      currentTask: workerInfo.currentTask,
      uptime: Date.now() - workerInfo.startTime,
      tasksProcessed: workerInfo.tasksProcessed,
      lastActive: workerInfo.lastActive
    };
  }
  
  /**
   * Get status of all workers
   * @returns {Object} Status of all workers
   */
  getAllWorkerStatus() {
    return {
      total: this.workers.size,
      available: this.availableWorkers.length,
      busy: this.workers.size - this.availableWorkers.length,
      workers: Array.from(this.workers.values()).map(worker => ({
        id: worker.id,
        status: worker.status,
        currentTask: worker.currentTask,
        uptime: Date.now() - worker.startTime,
        tasksProcessed: worker.tasksProcessed,
        lastActive: worker.lastActive
      }))
    };
  }
  
  /**
   * Get resource usage
   * @returns {Object} Resource usage
   */
  getResourceUsage() {
    return {
      cpu: {
        usage: this.resources.cpu.usage,
        limit: this.resources.cpu.limit
      },
      memory: {
        usage: this.resources.memory.usage,
        limit: this.resources.memory.limit,
        total: os.totalmem(),
        free: os.freemem()
      }
    };
  }
  
  /**
   * Get processing metrics
   * @returns {Object} Processing metrics
   */
  getMetrics() {
    return this.metrics;
  }
  
  /**
   * Get overall status
   * @returns {Object} Overall status
   */
  getStatus() {
    return {
      enabled: this.config.enabled,
      workers: {
        total: this.workers.size,
        available: this.availableWorkers.length,
        busy: this.workers.size - this.availableWorkers.length
      },
      tasks: {
        queued: this.taskQueue.length,
        active: this.activeTasks.size,
        processed: this.metrics.tasksProcessed,
        succeeded: this.metrics.tasksSucceeded,
        failed: this.metrics.tasksFailed
      },
      resources: this.getResourceUsage(),
      metrics: this.metrics
    };
  }
  
  /**
   * Shutdown the LocalProcessingManager
   * @returns {Promise<void>}
   */
  async shutdown() {
    try {
      console.log('Shutting down LocalProcessingManager');
      
      // Stop resource monitoring
      if (this.monitoringInterval) {
        clearInterval(this.monitoringInterval);
        this.monitoringInterval = null;
      }
      
      // Cancel all queued tasks
      while (this.taskQueue.length > 0) {
        const taskInfo = this.taskQueue.shift();
        taskInfo.reject(new Error('LocalProcessingManager shutting down'));
      }
      
      // Cancel all active tasks
      for (const [taskId, taskInfo] of this.activeTasks.entries()) {
        taskInfo.reject(new Error('LocalProcessingManager shutting down'));
      }
      
      this.activeTasks.clear();
      
      // Terminate all workers
      const terminationPromises = [];
      
      for (const [workerId, workerInfo] of this.workers.entries()) {
        terminationPromises.push(
          new Promise((resolve) => {
            workerInfo.worker.once('exit', () => {
              resolve();
            });
            
            workerInfo.worker.terminate();
          })
        );
      }
      
      await Promise.all(terminationPromises);
      
      this.workers.clear();
      this.availableWorkers = [];
      
      console.log('LocalProcessingManager shutdown complete');
    } catch (error) {
      console.error('Error shutting down LocalProcessingManager:', error);
      throw error;
    }
  }
}

module.exports = { LocalProcessingManager };
