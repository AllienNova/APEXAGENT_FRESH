const { app, BrowserWindow, Menu, shell, dialog, ipcMain } = require('electron');
const { autoUpdater } = require('electron-updater');
const Store = require('electron-store');
const path = require('path');
const express = require('express');
const cors = require('cors');
const { spawn } = require('child_process');

// Initialize electron store for settings
const store = new Store();

// Keep a global reference of the window object
let mainWindow;
let backendProcess;
let expressApp;
let server;

// Backend server configuration
const BACKEND_PORT = 5000;
const EXPRESS_PORT = 3000;

class ApexAgentDesktop {
    constructor() {
        this.isDevMode = process.argv.includes('--dev');
        this.backendReady = false;
        this.setupApp();
    }

    setupApp() {
        // App event handlers
        app.whenReady().then(() => this.createWindow());
        app.on('window-all-closed', () => this.handleWindowsClosed());
        app.on('activate', () => this.handleActivate());
        app.on('before-quit', () => this.cleanup());

        // Auto-updater events
        autoUpdater.checkForUpdatesAndNotify();
        autoUpdater.on('update-available', () => {
            dialog.showMessageBox(mainWindow, {
                type: 'info',
                title: 'Update Available',
                message: 'A new version is available. It will be downloaded in the background.',
                buttons: ['OK']
            });
        });
    }

    async createWindow() {
        // Create the browser window
        mainWindow = new BrowserWindow({
            width: 1400,
            height: 900,
            minWidth: 1200,
            minHeight: 800,
            webPreferences: {
                nodeIntegration: false,
                contextIsolation: true,
                enableRemoteModule: false,
                preload: path.join(__dirname, 'preload.js')
            },
            icon: path.join(__dirname, '../assets/icon.png'),
            titleBarStyle: 'default',
            show: false,
            backgroundColor: '#1a1a2e'
        });

        // Setup menu
        this.createMenu();

        // Start backend services
        await this.startBackend();

        // Load the app
        if (this.isDevMode) {
            mainWindow.loadURL('http://localhost:3000');
            mainWindow.webContents.openDevTools();
        } else {
            await this.startExpressServer();
            mainWindow.loadURL('http://localhost:3000');
        }

        // Show window when ready
        mainWindow.once('ready-to-show', () => {
            mainWindow.show();
            
            // Focus on window
            if (process.platform === 'darwin') {
                app.dock.show();
            }
        });

        // Handle window closed
        mainWindow.on('closed', () => {
            mainWindow = null;
        });

        // Handle external links
        mainWindow.webContents.setWindowOpenHandler(({ url }) => {
            shell.openExternal(url);
            return { action: 'deny' };
        });
    }

    async startBackend() {
        return new Promise((resolve, reject) => {
            try {
                const backendPath = this.isDevMode 
                    ? path.join(__dirname, '../../apexagent_optimized/src/main_production.py')
                    : path.join(process.resourcesPath, 'backend/main_production.py');

                // Start Python backend
                backendProcess = spawn('python', [backendPath], {
                    env: {
                        ...process.env,
                        PORT: BACKEND_PORT.toString(),
                        ELECTRON_MODE: 'true'
                    },
                    stdio: ['pipe', 'pipe', 'pipe']
                });

                backendProcess.stdout.on('data', (data) => {
                    console.log(`Backend: ${data}`);
                    if (data.includes('Running on')) {
                        this.backendReady = true;
                        resolve();
                    }
                });

                backendProcess.stderr.on('data', (data) => {
                    console.error(`Backend Error: ${data}`);
                });

                backendProcess.on('close', (code) => {
                    console.log(`Backend process exited with code ${code}`);
                    this.backendReady = false;
                });

                // Timeout after 30 seconds
                setTimeout(() => {
                    if (!this.backendReady) {
                        reject(new Error('Backend startup timeout'));
                    }
                }, 30000);

            } catch (error) {
                reject(error);
            }
        });
    }

    async startExpressServer() {
        return new Promise((resolve) => {
            expressApp = express();
            
            // Enable CORS
            expressApp.use(cors());
            
            // Serve static files
            const staticPath = this.isDevMode 
                ? path.join(__dirname, '../../apexagent_optimized/src/static')
                : path.join(process.resourcesPath, 'backend/static');
            
            expressApp.use(express.static(staticPath));
            
            // Proxy API requests to backend
            expressApp.use('/api', (req, res) => {
                const axios = require('axios');
                const backendUrl = `http://localhost:${BACKEND_PORT}${req.url}`;
                
                axios({
                    method: req.method,
                    url: backendUrl,
                    data: req.body,
                    headers: req.headers
                }).then(response => {
                    res.status(response.status).json(response.data);
                }).catch(error => {
                    res.status(error.response?.status || 500).json({
                        error: error.message
                    });
                });
            });
            
            // Serve main page
            expressApp.get('/', (req, res) => {
                res.sendFile(path.join(staticPath, 'index.html'));
            });
            
            server = expressApp.listen(EXPRESS_PORT, () => {
                console.log(`Express server running on port ${EXPRESS_PORT}`);
                resolve();
            });
        });
    }

    createMenu() {
        const template = [
            {
                label: 'ApexAgent',
                submenu: [
                    {
                        label: 'About ApexAgent',
                        click: () => this.showAbout()
                    },
                    { type: 'separator' },
                    {
                        label: 'Preferences',
                        accelerator: 'CmdOrCtrl+,',
                        click: () => this.showPreferences()
                    },
                    { type: 'separator' },
                    {
                        label: 'Quit',
                        accelerator: process.platform === 'darwin' ? 'Cmd+Q' : 'Ctrl+Q',
                        click: () => app.quit()
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
                    { role: 'togglefullscreen' }
                ]
            },
            {
                label: 'Window',
                submenu: [
                    { role: 'minimize' },
                    { role: 'close' }
                ]
            },
            {
                label: 'Help',
                submenu: [
                    {
                        label: 'Documentation',
                        click: () => shell.openExternal('https://github.com/AllienNova/ApexAgent')
                    },
                    {
                        label: 'Report Issue',
                        click: () => shell.openExternal('https://github.com/AllienNova/ApexAgent/issues')
                    }
                ]
            }
        ];

        const menu = Menu.buildFromTemplate(template);
        Menu.setApplicationMenu(menu);
    }

    showAbout() {
        dialog.showMessageBox(mainWindow, {
            type: 'info',
            title: 'About ApexAgent',
            message: 'ApexAgent Desktop',
            detail: `Version: 1.0.0\\nThe World's First Hybrid Autonomous AI System\\n\\nBuilt with Electron and powered by advanced AI technology.\\n\\n© 2025 ApexAgent Team`
        });
    }

    showPreferences() {
        // Create preferences window
        const prefsWindow = new BrowserWindow({
            width: 600,
            height: 400,
            parent: mainWindow,
            modal: true,
            webPreferences: {
                nodeIntegration: false,
                contextIsolation: true
            }
        });

        prefsWindow.loadFile(path.join(__dirname, 'preferences.html'));
    }

    handleWindowsClosed() {
        if (process.platform !== 'darwin') {
            app.quit();
        }
    }

    handleActivate() {
        if (BrowserWindow.getAllWindows().length === 0) {
            this.createWindow();
        }
    }

    cleanup() {
        if (backendProcess) {
            backendProcess.kill();
        }
        if (server) {
            server.close();
        }
    }
}

// Initialize the application
new ApexAgentDesktop();

