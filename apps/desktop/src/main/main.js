const { app, BrowserWindow, Menu, ipcMain, dialog, shell, screen, nativeTheme } = require('electron');

// Enable headless mode for testing environments
if (process.env.NODE_ENV === 'test' || !process.env.DISPLAY) {
  app.disableHardwareAcceleration();
}

const { autoUpdater } = require('electron-updater');
const Store = require('electron-store');
const log = require('electron-log');
const path = require('path');
const fs = require('fs');
const os = require('os');
const { spawn } = require('child_process');

// Configure logging
log.transports.file.level = 'info';
log.transports.console.level = 'debug';

// Initialize secure storage
const store = new Store({
  name: 'aideon-config',
  encryptionKey: 'aideon-ai-lite-secure-key',
  defaults: {
    windowBounds: { width: 1400, height: 900 },
    theme: 'system',
    apiEndpoint: 'http://localhost:3001',
    localProcessing: true,
    offlineMode: false,
    autoUpdates: true,
    telemetry: true
  }
});

class AideonDesktopApp {
  constructor() {
    this.mainWindow = null;
    this.apiServer = null;
    this.isQuitting = false;
    this.isDevelopment = process.env.NODE_ENV === 'development';
    
    // Initialize app
    this.initializeApp();
  }

  initializeApp() {
    // Set app user model ID for Windows
    if (process.platform === 'win32') {
      app.setAppUserModelId('com.aideonai.lite');
    }

    // Handle app events
    app.whenReady().then(() => this.onReady());
    app.on('window-all-closed', () => this.onWindowAllClosed());
    app.on('activate', () => this.onActivate());
    app.on('before-quit', () => this.onBeforeQuit());
    app.on('second-instance', () => this.onSecondInstance());

    // Ensure single instance
    if (!app.requestSingleInstanceLock()) {
      app.quit();
      return;
    }

    // Handle protocol for deep linking
    app.setAsDefaultProtocolClient('aideon');
  }

  async onReady() {
    log.info('Aideon AI Lite starting...');
    
    // Start local API server
    await this.startLocalApiServer();
    
    // Create main window
    this.createMainWindow();
    
    // Setup menu
    this.createMenu();
    
    // Setup IPC handlers
    this.setupIpcHandlers();
    
    // Setup auto updater
    this.setupAutoUpdater();
    
    // Setup theme handling
    this.setupThemeHandling();
    
    log.info('Aideon AI Lite ready');
  }

  async startLocalApiServer() {
    try {
      const apiPath = path.join(__dirname, '../../../api/backend/src/index.js');
      const apiExists = fs.existsSync(apiPath);
      
      if (apiExists && store.get('localProcessing', true)) {
        log.info('Starting local API server...');
        
        this.apiServer = spawn('node', [apiPath], {
          env: {
            ...process.env,
            NODE_ENV: 'production',
            PORT: '3001',
            DESKTOP_MODE: 'true',
            DATA_DIR: path.join(os.homedir(), '.aideon-ai-lite')
          },
          stdio: this.isDevelopment ? 'inherit' : 'pipe'
        });

        this.apiServer.on('error', (error) => {
          log.error('API server error:', error);
        });

        this.apiServer.on('exit', (code) => {
          log.info(`API server exited with code ${code}`);
        });

        // Wait for server to start
        await new Promise(resolve => setTimeout(resolve, 3000));
        log.info('Local API server started');
      } else {
        log.info('Using cloud API endpoint');
      }
    } catch (error) {
      log.error('Failed to start local API server:', error);
    }
  }

  createMainWindow() {
    const bounds = store.get('windowBounds');
    const display = screen.getPrimaryDisplay();
    const { width, height } = display.workAreaSize;

    // Ensure window fits on screen
    const windowWidth = Math.min(bounds.width, width);
    const windowHeight = Math.min(bounds.height, height);

    this.mainWindow = new BrowserWindow({
      width: windowWidth,
      height: windowHeight,
      minWidth: 1000,
      minHeight: 700,
      show: process.env.NODE_ENV !== 'test',
      icon: this.getAppIcon(),
      titleBarStyle: process.platform === 'darwin' ? 'hiddenInset' : 'default',
      webPreferences: {
        nodeIntegration: false,
        contextIsolation: true,
        enableRemoteModule: false,
        preload: path.join(__dirname, '../preload/preload.js'),
        webSecurity: !this.isDevelopment,
        allowRunningInsecureContent: false,
        experimentalFeatures: false,
        offscreen: process.env.NODE_ENV === 'test'
      }
    });

    // Load the app
    const startUrl = this.isDevelopment 
      ? 'http://localhost:3000'
      : `file://${path.join(__dirname, '../../../web/frontend/build/index.html')}`;
    
    this.mainWindow.loadURL(startUrl);

    // Show window when ready
    this.mainWindow.once('ready-to-show', () => {
      this.mainWindow.show();
      
      if (this.isDevelopment) {
        this.mainWindow.webContents.openDevTools();
      }
    });

    // Handle window events
    this.mainWindow.on('closed', () => {
      this.mainWindow = null;
    });

    this.mainWindow.on('close', (event) => {
      if (!this.isQuitting && process.platform === 'darwin') {
        event.preventDefault();
        this.mainWindow.hide();
      } else {
        // Save window bounds
        if (!this.mainWindow.isMaximized()) {
          store.set('windowBounds', this.mainWindow.getBounds());
        }
      }
    });

    // Handle external links
    this.mainWindow.webContents.setWindowOpenHandler(({ url }) => {
      shell.openExternal(url);
      return { action: 'deny' };
    });

    // Security: Prevent navigation to external sites
    this.mainWindow.webContents.on('will-navigate', (event, navigationUrl) => {
      const parsedUrl = new URL(navigationUrl);
      
      if (parsedUrl.origin !== 'http://localhost:3000' && 
          parsedUrl.origin !== 'file://') {
        event.preventDefault();
      }
    });
  }

  getAppIcon() {
    const platform = process.platform;
    const iconPath = path.join(__dirname, '../../assets/icons');
    
    switch (platform) {
      case 'win32':
        return path.join(iconPath, 'win/icon.ico');
      case 'darwin':
        return path.join(iconPath, 'mac/icon.icns');
      case 'linux':
        return path.join(iconPath, 'linux/icon.png');
      default:
        return path.join(iconPath, 'linux/icon.png');
    }
  }

  createMenu() {
    const template = [
      {
        label: 'File',
        submenu: [
          {
            label: 'New Project',
            accelerator: 'CmdOrCtrl+N',
            click: () => this.mainWindow.webContents.send('menu-new-project')
          },
          {
            label: 'Open Project',
            accelerator: 'CmdOrCtrl+O',
            click: () => this.mainWindow.webContents.send('menu-open-project')
          },
          {
            label: 'Save Project',
            accelerator: 'CmdOrCtrl+S',
            click: () => this.mainWindow.webContents.send('menu-save-project')
          },
          { type: 'separator' },
          {
            label: 'Import Data',
            click: () => this.mainWindow.webContents.send('menu-import-data')
          },
          {
            label: 'Export Data',
            click: () => this.mainWindow.webContents.send('menu-export-data')
          },
          { type: 'separator' },
          {
            label: 'Preferences',
            accelerator: 'CmdOrCtrl+,',
            click: () => this.mainWindow.webContents.send('menu-preferences')
          },
          { type: 'separator' },
          {
            label: 'Quit',
            accelerator: process.platform === 'darwin' ? 'Cmd+Q' : 'Ctrl+Q',
            click: () => {
              this.isQuitting = true;
              app.quit();
            }
          }
        ]
      },
      {
        label: 'Edit',
        submenu: [
          { role: 'undo' },
          { role: 'redo' },
          { type: 'separator' },
          { role: 'cut' },
          { role: 'copy' },
          { role: 'paste' },
          { role: 'selectall' }
        ]
      },
      {
        label: 'View',
        submenu: [
          { role: 'reload' },
          { role: 'forceReload' },
          { role: 'toggleDevTools' },
          { type: 'separator' },
          { role: 'resetZoom' },
          { role: 'zoomIn' },
          { role: 'zoomOut' },
          { type: 'separator' },
          { role: 'togglefullscreen' },
          { type: 'separator' },
          {
            label: 'Toggle Theme',
            accelerator: 'CmdOrCtrl+Shift+T',
            click: () => this.toggleTheme()
          }
        ]
      },
      {
        label: 'AI',
        submenu: [
          {
            label: 'Toggle Local Processing',
            type: 'checkbox',
            checked: store.get('localProcessing', true),
            click: (menuItem) => {
              store.set('localProcessing', menuItem.checked);
              this.mainWindow.webContents.send('local-processing-changed', menuItem.checked);
            }
          },
          {
            label: 'Toggle Offline Mode',
            type: 'checkbox',
            checked: store.get('offlineMode', false),
            click: (menuItem) => {
              store.set('offlineMode', menuItem.checked);
              this.mainWindow.webContents.send('offline-mode-changed', menuItem.checked);
            }
          },
          { type: 'separator' },
          {
            label: 'Model Manager',
            click: () => this.mainWindow.webContents.send('menu-model-manager')
          },
          {
            label: 'Agent Monitor',
            click: () => this.mainWindow.webContents.send('menu-agent-monitor')
          }
        ]
      },
      {
        label: 'Tools',
        submenu: [
          {
            label: 'System Information',
            click: () => this.showSystemInfo()
          },
          {
            label: 'Clear Cache',
            click: () => this.clearCache()
          },
          {
            label: 'Reset Settings',
            click: () => this.resetSettings()
          }
        ]
      },
      {
        label: 'Help',
        submenu: [
          {
            label: 'Documentation',
            click: () => shell.openExternal('https://docs.aideonai.com')
          },
          {
            label: 'Keyboard Shortcuts',
            click: () => this.mainWindow.webContents.send('menu-shortcuts')
          },
          { type: 'separator' },
          {
            label: 'Report Issue',
            click: () => shell.openExternal('https://github.com/AllienNova/APEXAGENT_FRESH/issues')
          },
          {
            label: 'About',
            click: () => this.showAbout()
          }
        ]
      }
    ];

    // macOS specific menu adjustments
    if (process.platform === 'darwin') {
      template.unshift({
        label: app.getName(),
        submenu: [
          { role: 'about' },
          { type: 'separator' },
          { role: 'services' },
          { type: 'separator' },
          { role: 'hide' },
          { role: 'hideOthers' },
          { role: 'unhide' },
          { type: 'separator' },
          { role: 'quit' }
        ]
      });
    }

    const menu = Menu.buildFromTemplate(template);
    Menu.setApplicationMenu(menu);
  }

  setupIpcHandlers() {
    // Store operations
    ipcMain.handle('store-get', (event, key, defaultValue) => {
      return store.get(key, defaultValue);
    });

    ipcMain.handle('store-set', (event, key, value) => {
      store.set(key, value);
    });

    // File operations
    ipcMain.handle('show-open-dialog', async (event, options) => {
      const result = await dialog.showOpenDialog(this.mainWindow, options);
      return result;
    });

    ipcMain.handle('show-save-dialog', async (event, options) => {
      const result = await dialog.showSaveDialog(this.mainWindow, options);
      return result;
    });

    // System information
    ipcMain.handle('get-system-info', () => {
      return {
        platform: process.platform,
        arch: process.arch,
        version: app.getVersion(),
        electronVersion: process.versions.electron,
        nodeVersion: process.versions.node,
        chromeVersion: process.versions.chrome
      };
    });

    // App control
    ipcMain.handle('app-quit', () => {
      this.isQuitting = true;
      app.quit();
    });

    ipcMain.handle('app-minimize', () => {
      this.mainWindow.minimize();
    });

    ipcMain.handle('app-maximize', () => {
      if (this.mainWindow.isMaximized()) {
        this.mainWindow.unmaximize();
      } else {
        this.mainWindow.maximize();
      }
    });
  }

  setupAutoUpdater() {
    if (!this.isDevelopment && store.get('autoUpdates', true)) {
      autoUpdater.checkForUpdatesAndNotify();
      
      autoUpdater.on('update-available', () => {
        log.info('Update available');
        this.mainWindow.webContents.send('update-available');
      });

      autoUpdater.on('update-downloaded', () => {
        log.info('Update downloaded');
        this.mainWindow.webContents.send('update-downloaded');
      });
    }
  }

  setupThemeHandling() {
    nativeTheme.on('updated', () => {
      this.mainWindow.webContents.send('theme-changed', nativeTheme.shouldUseDarkColors);
    });
  }

  toggleTheme() {
    const currentTheme = store.get('theme', 'system');
    let newTheme;
    
    switch (currentTheme) {
      case 'light':
        newTheme = 'dark';
        break;
      case 'dark':
        newTheme = 'system';
        break;
      default:
        newTheme = 'light';
    }
    
    store.set('theme', newTheme);
    nativeTheme.themeSource = newTheme;
    this.mainWindow.webContents.send('theme-changed', nativeTheme.shouldUseDarkColors);
  }

  async showSystemInfo() {
    const si = require('systeminformation');
    
    try {
      const [cpu, mem, osInfo] = await Promise.all([
        si.cpu(),
        si.mem(),
        si.osInfo()
      ]);

      const info = {
        cpu: `${cpu.manufacturer} ${cpu.brand} (${cpu.cores} cores)`,
        memory: `${Math.round(mem.total / 1024 / 1024 / 1024)} GB`,
        os: `${osInfo.distro} ${osInfo.release}`,
        platform: process.platform,
        arch: process.arch,
        appVersion: app.getVersion(),
        electronVersion: process.versions.electron
      };

      this.mainWindow.webContents.send('system-info', info);
    } catch (error) {
      log.error('Failed to get system info:', error);
    }
  }

  async clearCache() {
    try {
      await this.mainWindow.webContents.session.clearCache();
      await this.mainWindow.webContents.session.clearStorageData();
      
      dialog.showMessageBox(this.mainWindow, {
        type: 'info',
        title: 'Cache Cleared',
        message: 'Application cache has been cleared successfully.'
      });
    } catch (error) {
      log.error('Failed to clear cache:', error);
    }
  }

  resetSettings() {
    dialog.showMessageBox(this.mainWindow, {
      type: 'warning',
      title: 'Reset Settings',
      message: 'Are you sure you want to reset all settings to default?',
      buttons: ['Cancel', 'Reset'],
      defaultId: 0,
      cancelId: 0
    }).then((result) => {
      if (result.response === 1) {
        store.clear();
        app.relaunch();
        app.exit();
      }
    });
  }

  showAbout() {
    dialog.showMessageBox(this.mainWindow, {
      type: 'info',
      title: 'About Aideon AI Lite',
      message: 'Aideon AI Lite',
      detail: `Version: ${app.getVersion()}\nThe world's first truly hybrid autonomous AI system\n\n© 2025 Aideon AI`
    });
  }

  onWindowAllClosed() {
    if (process.platform !== 'darwin') {
      this.cleanup();
      app.quit();
    }
  }

  onActivate() {
    if (BrowserWindow.getAllWindows().length === 0) {
      this.createMainWindow();
    } else if (this.mainWindow) {
      this.mainWindow.show();
    }
  }

  onBeforeQuit() {
    this.isQuitting = true;
    this.cleanup();
  }

  onSecondInstance() {
    if (this.mainWindow) {
      if (this.mainWindow.isMinimized()) {
        this.mainWindow.restore();
      }
      this.mainWindow.focus();
    }
  }

  cleanup() {
    if (this.apiServer) {
      this.apiServer.kill();
    }
  }
}

// Create app instance
new AideonDesktopApp();

