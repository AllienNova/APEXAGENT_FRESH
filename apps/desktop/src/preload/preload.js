const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  // Store operations
  store: {
    get: (key, defaultValue) => ipcRenderer.invoke('store-get', key, defaultValue),
    set: (key, value) => ipcRenderer.invoke('store-set', key, value)
  },

  // File operations
  dialog: {
    showOpenDialog: (options) => ipcRenderer.invoke('show-open-dialog', options),
    showSaveDialog: (options) => ipcRenderer.invoke('show-save-dialog', options)
  },

  // System information
  system: {
    getInfo: () => ipcRenderer.invoke('get-system-info')
  },

  // App control
  app: {
    quit: () => ipcRenderer.invoke('app-quit'),
    minimize: () => ipcRenderer.invoke('app-minimize'),
    maximize: () => ipcRenderer.invoke('app-maximize')
  },

  // Event listeners
  on: (channel, callback) => {
    const validChannels = [
      'menu-new-project',
      'menu-open-project', 
      'menu-save-project',
      'menu-import-data',
      'menu-export-data',
      'menu-preferences',
      'menu-shortcuts',
      'menu-model-manager',
      'menu-agent-monitor',
      'local-processing-changed',
      'offline-mode-changed',
      'theme-changed',
      'update-available',
      'update-downloaded',
      'system-info'
    ];
    
    if (validChannels.includes(channel)) {
      ipcRenderer.on(channel, callback);
    }
  },

  // Remove event listeners
  removeAllListeners: (channel) => {
    ipcRenderer.removeAllListeners(channel);
  }
});

// Expose desktop-specific APIs
contextBridge.exposeInMainWorld('desktopAPI', {
  // Platform information
  platform: process.platform,
  isDesktop: true,
  
  // Desktop-specific features
  features: {
    localProcessing: true,
    offlineMode: true,
    fileSystemAccess: true,
    systemIntegration: true,
    autoUpdates: true,
    nativeNotifications: true
  },

  // Version information
  versions: {
    app: process.env.npm_package_version || '1.0.0',
    electron: process.versions.electron,
    node: process.versions.node,
    chrome: process.versions.chrome
  }
});

// Expose hybrid system APIs
contextBridge.exposeInMainWorld('hybridAPI', {
  // Local/Cloud processing toggle
  processing: {
    setLocal: (enabled) => ipcRenderer.invoke('store-set', 'localProcessing', enabled),
    getLocal: () => ipcRenderer.invoke('store-get', 'localProcessing', true),
    setOffline: (enabled) => ipcRenderer.invoke('store-set', 'offlineMode', enabled),
    getOffline: () => ipcRenderer.invoke('store-get', 'offlineMode', false)
  },

  // API endpoint configuration
  api: {
    getEndpoint: () => ipcRenderer.invoke('store-get', 'apiEndpoint', 'http://localhost:3001'),
    setEndpoint: (endpoint) => ipcRenderer.invoke('store-set', 'apiEndpoint', endpoint)
  },

  // Local data management
  data: {
    getDataDir: () => ipcRenderer.invoke('store-get', 'dataDir', '~/.aideon-ai-lite'),
    setDataDir: (dir) => ipcRenderer.invoke('store-set', 'dataDir', dir)
  }
});

// Security: Log any attempts to access Node.js APIs
const originalRequire = window.require;
if (originalRequire) {
  window.require = function(...args) {
    console.warn('Attempt to use require() in renderer process:', args);
    return null;
  };
}

// Prevent access to Node.js globals
delete window.process;
delete window.Buffer;
delete window.global;

// Log successful preload
console.log('Aideon AI Lite preload script loaded successfully');

