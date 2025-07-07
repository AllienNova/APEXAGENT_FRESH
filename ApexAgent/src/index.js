/**
 * index.js
 * 
 * Main entry point for Aideon AI Lite
 * Initializes the application and loads the core components
 */

const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const fs = require('fs-extra');
const { AideonCore } = require('./core/AideonCore');
const { ConfigManager } = require('./core/config/ConfigManager');
const { LogManager } = require('./core/utils/LogManager');

// Initialize logger
const logger = new LogManager({
  logLevel: 'info',
  logPath: path.join(app.getPath('userData'), 'logs')
}).getLogger('main');

// Initialize config
const configManager = new ConfigManager({
  configPath: path.join(app.getPath('userData'), 'config')
});

// Initialize core
let core;

// Keep a reference to the main window
let mainWindow;

/**
 * Create the main application window
 */
function createWindow() {
  logger.info('Creating main window');
  
  // Create the browser window
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 800,
    minHeight: 600,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      enableRemoteModule: true,
      webviewTag: true
    },
    show: false,
    backgroundColor: '#16213e',
    title: 'Aideon AI Lite'
  });
  
  // Load the index.html file
  mainWindow.loadFile(path.join(__dirname, 'ui', 'index.html'));
  
  // Show window when ready
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
    mainWindow.focus();
  });
  
  // Handle window close
  mainWindow.on('closed', () => {
    mainWindow = null;
  });
  
  // Initialize core
  initializeCore();
}

/**
 * Initialize the Aideon AI Lite core
 */
async function initializeCore() {
  try {
    logger.info('Initializing Aideon AI Lite core');
    
    // Load configuration
    const config = await configManager.loadConfig();
    
    // Initialize core
    core = new AideonCore({
      config,
      logger
    });
    
    // Initialize core components
    await core.initialize();
    
    logger.info('Aideon AI Lite core initialized successfully');
    
    // Send initialization success to renderer
    if (mainWindow) {
      mainWindow.webContents.send('core:initialized', {
        success: true
      });
    }
  } catch (error) {
    logger.error('Failed to initialize Aideon AI Lite core', error);
    
    // Send initialization error to renderer
    if (mainWindow) {
      mainWindow.webContents.send('core:initialized', {
        success: false,
        error: error.message
      });
    }
    
    // Show error dialog
    dialog.showErrorBox(
      'Initialization Error',
      `Failed to initialize Aideon AI Lite: ${error.message}`
    );
  }
}

/**
 * Handle IPC messages from renderer
 */
function setupIPC() {
  // Core API calls
  ipcMain.handle('core:call', async (event, { method, args }) => {
    try {
      if (!core) {
        throw new Error('Core not initialized');
      }
      
      if (typeof core[method] !== 'function') {
        throw new Error(`Invalid method: ${method}`);
      }
      
      return await core[method](...(args || []));
    } catch (error) {
      logger.error(`Error in core:call (${method})`, error);
      throw error;
    }
  });
}

/**
 * App lifecycle events
 */

// This method will be called when Electron has finished initialization
app.whenReady().then(() => {
  logger.info('Application ready');
  
  // Set up IPC handlers
  setupIPC();
  
  // Create main window
  createWindow();
  
  // On macOS, re-create window when dock icon is clicked
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

// Quit when all windows are closed, except on macOS
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// Handle app quit
app.on('before-quit', async () => {
  logger.info('Application quitting');
  
  // Shutdown core
  if (core) {
    try {
      await core.shutdown();
      logger.info('Core shutdown successfully');
    } catch (error) {
      logger.error('Error during core shutdown', error);
    }
  }
});

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
  logger.error('Uncaught exception', error);
  
  dialog.showErrorBox(
    'Unexpected Error',
    `An unexpected error occurred: ${error.message}\n\nThe application will now close.`
  );
  
  app.quit();
});
