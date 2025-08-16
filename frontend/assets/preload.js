const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
    // App information
    getVersion: () => ipcRenderer.invoke('get-version'),
    
    // Settings
    getSetting: (key) => ipcRenderer.invoke('get-setting', key),
    setSetting: (key, value) => ipcRenderer.invoke('set-setting', key, value),
    
    // System information
    getSystemInfo: () => ipcRenderer.invoke('get-system-info'),
    
    // Backend communication
    backendRequest: (endpoint, options) => ipcRenderer.invoke('backend-request', endpoint, options),
    
    // File operations
    selectFile: (options) => ipcRenderer.invoke('select-file', options),
    selectDirectory: (options) => ipcRenderer.invoke('select-directory', options),
    
    // Notifications
    showNotification: (title, body) => ipcRenderer.invoke('show-notification', title, body),
    
    // Window controls
    minimizeWindow: () => ipcRenderer.invoke('minimize-window'),
    maximizeWindow: () => ipcRenderer.invoke('maximize-window'),
    closeWindow: () => ipcRenderer.invoke('close-window'),
    
    // Events
    onBackendStatus: (callback) => ipcRenderer.on('backend-status', callback),
    onUpdateAvailable: (callback) => ipcRenderer.on('update-available', callback),
    onUpdateDownloaded: (callback) => ipcRenderer.on('update-downloaded', callback),
    
    // Remove listeners
    removeAllListeners: (channel) => ipcRenderer.removeAllListeners(channel)
});

// Expose ApexAgent specific APIs
contextBridge.exposeInMainWorld('apexAgent', {
    // AI Operations
    sendAIRequest: (provider, message, options) => 
        ipcRenderer.invoke('ai-request', provider, message, options),
    
    // Project Management
    createProject: (projectData) => ipcRenderer.invoke('create-project', projectData),
    getProjects: () => ipcRenderer.invoke('get-projects'),
    updateProject: (id, data) => ipcRenderer.invoke('update-project', id, data),
    deleteProject: (id) => ipcRenderer.invoke('delete-project', id),
    
    // Security Operations
    getSecurityStatus: () => ipcRenderer.invoke('get-security-status'),
    runSecurityScan: () => ipcRenderer.invoke('run-security-scan'),
    getSecurityLogs: (limit) => ipcRenderer.invoke('get-security-logs', limit),
    
    // System Monitoring
    getSystemMetrics: () => ipcRenderer.invoke('get-system-metrics'),
    getPerformanceData: () => ipcRenderer.invoke('get-performance-data'),
    
    // Agent Management
    getAgents: () => ipcRenderer.invoke('get-agents'),
    createAgent: (agentData) => ipcRenderer.invoke('create-agent', agentData),
    startAgent: (id) => ipcRenderer.invoke('start-agent', id),
    stopAgent: (id) => ipcRenderer.invoke('stop-agent', id),
    
    // File Management
    uploadFile: (file) => ipcRenderer.invoke('upload-file', file),
    downloadFile: (id) => ipcRenderer.invoke('download-file', id),
    getFiles: () => ipcRenderer.invoke('get-files'),
    
    // Analytics
    getAnalytics: (timeRange) => ipcRenderer.invoke('get-analytics', timeRange),
    exportData: (format, data) => ipcRenderer.invoke('export-data', format, data)
});

// Desktop-specific enhancements
contextBridge.exposeInMainWorld('desktop', {
    // Platform information
    platform: process.platform,
    arch: process.arch,
    
    // Desktop features
    isDesktop: true,
    hasNativeMenus: true,
    hasSystemTray: process.platform !== 'linux',
    
    // Performance optimizations
    enableHardwareAcceleration: () => ipcRenderer.invoke('enable-hardware-acceleration'),
    disableHardwareAcceleration: () => ipcRenderer.invoke('disable-hardware-acceleration'),
    
    // Desktop integration
    setProgressBar: (progress) => ipcRenderer.invoke('set-progress-bar', progress),
    setBadgeCount: (count) => ipcRenderer.invoke('set-badge-count', count),
    flashFrame: () => ipcRenderer.invoke('flash-frame'),
    
    // System integration
    registerProtocol: (protocol) => ipcRenderer.invoke('register-protocol', protocol),
    setAsDefaultProtocolClient: (protocol) => ipcRenderer.invoke('set-default-protocol', protocol)
});

// Enhanced error handling
window.addEventListener('error', (event) => {
    console.error('Renderer Error:', event.error);
    ipcRenderer.send('renderer-error', {
        message: event.error.message,
        stack: event.error.stack,
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno
    });
});

window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled Promise Rejection:', event.reason);
    ipcRenderer.send('renderer-promise-rejection', {
        reason: event.reason,
        promise: event.promise
    });
});

// Desktop-specific CSS injection
document.addEventListener('DOMContentLoaded', () => {
    // Add desktop-specific styles
    const style = document.createElement('style');
    style.textContent = `
        /* Desktop-specific styles */
        body {
            -webkit-user-select: none;
            -webkit-app-region: no-drag;
        }
        
        .title-bar {
            -webkit-app-region: drag;
        }
        
        .title-bar button {
            -webkit-app-region: no-drag;
        }
        
        /* Scrollbar styling for desktop */
        ::-webkit-scrollbar {
            width: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: #2a2a3e;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #4a4a6e;
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: #5a5a7e;
        }
        
        /* Desktop performance optimizations */
        * {
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }
        
        /* Desktop-specific animations */
        .desktop-fade-in {
            animation: desktopFadeIn 0.3s ease-out;
        }
        
        @keyframes desktopFadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
    `;
    document.head.appendChild(style);
    
    // Add desktop class to body
    document.body.classList.add('desktop-app');
    
    // Initialize desktop-specific features
    if (window.apexAgent) {
        // Set up desktop-specific event listeners
        window.apexAgent.onBackendStatus?.((status) => {
            document.body.setAttribute('data-backend-status', status);
        });
    }
});

