/**
 * LogManager.js
 * 
 * Logging utility for Aideon AI Lite.
 * Provides centralized logging capabilities with different log levels and outputs.
 * 
 * @author Aideon AI Team
 * @version 1.0.0
 */

const winston = require('winston');
const path = require('path');
const fs = require('fs');

class LogManager {
  constructor(config = {}) {
    this.config = {
      logLevel: 'info',
      logDir: path.join(process.cwd(), 'logs'),
      maxLogFiles: 10,
      maxLogSize: 10 * 1024 * 1024, // 10 MB
      consoleOutput: true,
      fileOutput: true,
      format: 'json',
      ...config
    };
    
    // Create log directory if it doesn't exist
    if (this.config.fileOutput && !fs.existsSync(this.config.logDir)) {
      fs.mkdirSync(this.config.logDir, { recursive: true });
    }
    
    // Initialize Winston logger
    this.initializeLogger();
    
    // Store loggers by category
    this.loggers = new Map();
  }

  /**
   * Initialize the Winston logger
   * @private
   */
  initializeLogger() {
    // Define log format
    const logFormat = winston.format.combine(
      winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
      winston.format.errors({ stack: true }),
      this.config.format === 'json' ? 
        winston.format.json() : 
        winston.format.printf(({ timestamp, level, message, category, ...meta }) => {
          return `${timestamp} [${level.toUpperCase()}] ${category ? `[${category}] ` : ''}${message} ${
            Object.keys(meta).length ? JSON.stringify(meta) : ''
          }`;
        })
    );
    
    // Define transports
    const transports = [];
    
    // Add console transport if enabled
    if (this.config.consoleOutput) {
      transports.push(new winston.transports.Console({
        format: winston.format.combine(
          winston.format.colorize(),
          logFormat
        )
      }));
    }
    
    // Add file transport if enabled
    if (this.config.fileOutput) {
      transports.push(new winston.transports.File({
        filename: path.join(this.config.logDir, 'aideon.log'),
        maxsize: this.config.maxLogSize,
        maxFiles: this.config.maxLogFiles,
        tailable: true
      }));
      
      // Add error file transport
      transports.push(new winston.transports.File({
        filename: path.join(this.config.logDir, 'error.log'),
        level: 'error',
        maxsize: this.config.maxLogSize,
        maxFiles: this.config.maxLogFiles,
        tailable: true
      }));
    }
    
    // Create logger
    this.logger = winston.createLogger({
      level: this.config.logLevel,
      format: logFormat,
      defaultMeta: { service: 'aideon-ai' },
      transports
    });
    
    // Log initialization
    this.logger.info('LogManager initialized');
  }

  /**
   * Get a logger for a specific category
   * @param {string} category - Logger category
   * @returns {Object} Category logger
   */
  getLogger(category) {
    if (!this.loggers.has(category)) {
      // Create a new logger for this category
      const categoryLogger = {
        debug: (message, meta = {}) => this.log('debug', message, { category, ...meta }),
        info: (message, meta = {}) => this.log('info', message, { category, ...meta }),
        warn: (message, meta = {}) => this.log('warn', message, { category, ...meta }),
        error: (message, meta = {}) => this.log('error', message, { category, ...meta }),
        critical: (message, meta = {}) => this.log('error', `CRITICAL: ${message}`, { category, ...meta, critical: true })
      };
      
      this.loggers.set(category, categoryLogger);
    }
    
    return this.loggers.get(category);
  }

  /**
   * Log a message
   * @param {string} level - Log level
   * @param {string} message - Log message
   * @param {Object} meta - Additional metadata
   */
  log(level, message, meta = {}) {
    if (typeof message !== 'string') {
      if (message instanceof Error) {
        meta.error = message;
        message = message.message;
      } else {
        try {
          message = JSON.stringify(message);
        } catch (error) {
          message = String(message);
        }
      }
    }
    
    this.logger.log(level, message, meta);
  }

  /**
   * Set the log level
   * @param {string} level - New log level
   */
  setLogLevel(level) {
    this.config.logLevel = level;
    this.logger.level = level;
    this.logger.info(`Log level set to ${level}`);
  }

  /**
   * Get all logs
   * @param {Object} options - Query options
   * @returns {Promise<Array>} Logs
   */
  async getLogs(options = {}) {
    const { level, category, startTime, endTime, limit = 100, offset = 0 } = options;
    
    // In a real implementation, this would query logs from storage
    // For now, we'll return a placeholder
    return [];
  }

  /**
   * Clear logs
   * @param {Object} options - Clear options
   * @returns {Promise<boolean>} Success status
   */
  async clearLogs(options = {}) {
    const { level, category, olderThan } = options;
    
    // In a real implementation, this would clear logs from storage
    // For now, we'll return a placeholder
    return true;
  }

  /**
   * Create a child logger with additional default metadata
   * @param {Object} defaultMeta - Default metadata
   * @returns {Object} Child logger
   */
  child(defaultMeta) {
    const childLogger = this.logger.child(defaultMeta);
    
    return {
      debug: (message, meta = {}) => childLogger.debug(message, meta),
      info: (message, meta = {}) => childLogger.info(message, meta),
      warn: (message, meta = {}) => childLogger.warn(message, meta),
      error: (message, meta = {}) => childLogger.error(message, meta),
      critical: (message, meta = {}) => childLogger.error(`CRITICAL: ${message}`, { ...meta, critical: true })
    };
  }
}

module.exports = { LogManager };
