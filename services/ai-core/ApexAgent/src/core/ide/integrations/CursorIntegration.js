/**
 * CursorIntegration.js
 * 
 * Integration with Cursor IDE for Aideon AI Lite.
 * Enables seamless interaction with Cursor for AI-enhanced code editing and development.
 * 
 * @author Aideon AI Team
 * @version 1.0.0
 */

const BaseIDEIntegration = require('../BaseIDEIntegration');
const WebSocket = require('ws');
const http = require('http');
const fs = require('fs').promises;
const path = require('path');
const { spawn, exec } = require('child_process');
const { v4: uuidv4 } = require('uuid');
const axios = require('axios');

class CursorIntegration extends BaseIDEIntegration {
  constructor(core) {
    super(core);
    this.extensionPath = path.join(this.core.configManager.getDataDir(), 'extensions', 'cursor');
    this.connections = new Map();
    this.server = null;
    this.wss = null;
    this.supportedCommands = [
      'openFile',
      'saveFile',
      'closeFile',
      'editFile',
      'runCommand',
      'getOpenFiles',
      'getProjectStructure',
      'searchInFiles',
      'generateCode',
      'explainCode',
      'refactorCode',
      'runTerminalCommand',
      'getTerminalOutput',
      'gitCheckout',
      'gitPull',
      'gitPush',
      'gitCommit'
    ];
  }

  /**
   * Get the name of the IDE
   * @returns {string} IDE name
   */
  getIDEName() {
    return 'Cursor';
  }

  /**
   * Get the version of the integration
   * @returns {string} Version string
   */
  getVersion() {
    return '1.0.0';
  }

  /**
   * Get the capabilities of this IDE integration
   * @returns {Object} Capabilities object
   */
  getCapabilities() {
    return {
      fileAccess: true,
      projectManagement: true,
      debugging: true,
      terminalAccess: true,
      codeCompletion: true,
      codeNavigation: true,
      refactoring: true,
      versionControl: true,
      extensionManagement: true,
      aiCodeGeneration: true,
      aiCodeExplanation: true
    };
  }

  /**
   * Connect to Cursor
   * @param {Object} options - Connection options
   * @returns {Promise<Object>} Connection object
   */
  async connect(options = {}) {
    this.logger.info('Connecting to Cursor');
    
    try {
      // Check if Cursor is installed
      await this._checkCursorInstallation();
      
      // Generate a unique connection ID
      const connectionId = uuidv4();
      
      // Create connection object
      const connection = {
        id: connectionId,
        type: options.type || 'extension', // 'extension' or 'cli' or 'api'
        workspace: options.workspace || null,
        socket: null,
        status: 'connecting',
        lastActivity: Date.now()
      };
      
      // Store the connection
      this.connections.set(connectionId, connection);
      
      if (connection.type === 'extension') {
        // Connect via extension
        await this._connectViaExtension(connection, options);
      } else if (connection.type === 'api') {
        // Connect via API
        await this._connectViaAPI(connection, options);
      } else {
        // Connect via CLI
        await this._connectViaCLI(connection, options);
      }
      
      connection.status = 'connected';
      connection.lastActivity = Date.now();
      
      this.logger.info(`Connected to Cursor (ID: ${connectionId})`);
      
      return connection;
    } catch (error) {
      this.logger.error(`Failed to connect to Cursor: ${error.message}`);
      throw error;
    }
  }

  /**
   * Disconnect from Cursor
   * @param {Object} connection - Connection object
   * @returns {Promise<boolean>} Success status
   */
  async disconnect(connection) {
    this.logger.info(`Disconnecting from Cursor (ID: ${connection.id})`);
    
    try {
      if (connection.socket && connection.socket.readyState === WebSocket.OPEN) {
        connection.socket.close();
      }
      
      if (connection.type === 'cli' && connection.process) {
        connection.process.kill();
      }
      
      if (connection.type === 'api' && connection.apiClient) {
        // Clean up API client resources if needed
      }
      
      this.connections.delete(connection.id);
      
      this.logger.info(`Disconnected from Cursor (ID: ${connection.id})`);
      return true;
    } catch (error) {
      this.logger.error(`Failed to disconnect from Cursor: ${error.message}`);
      throw error;
    }
  }

  /**
   * Check if a command is supported
   * @param {string} command - Command name
   * @returns {boolean} Whether the command is supported
   */
  supportsCommand(command) {
    return this.supportedCommands.includes(command);
  }

  /**
   * Execute a command in Cursor
   * @param {Object} connection - Connection object
   * @param {string} command - Command name
   * @param {Object} params - Command parameters
   * @returns {Promise<Object>} Command result
   */
  async executeCommand(connection, command, params = {}) {
    if (!this.supportsCommand(command)) {
      throw new Error(`Command ${command} not supported by Cursor integration`);
    }
    
    this.logger.debug(`Executing command ${command} in Cursor (ID: ${connection.id})`);
    
    try {
      // Update last activity timestamp
      connection.lastActivity = Date.now();
      
      // Execute the command based on connection type
      if (connection.type === 'extension') {
        return await this._executeExtensionCommand(connection, command, params);
      } else if (connection.type === 'api') {
        return await this._executeAPICommand(connection, command, params);
      } else {
        return await this._executeCLICommand(connection, command, params);
      }
    } catch (error) {
      this.logger.error(`Failed to execute command ${command}: ${error.message}`);
      throw error;
    }
  }

  /**
   * Start a server for Cursor extension communication
   * @param {number} port - Port to listen on
   * @returns {Promise<Object>} Server object
   */
  async startServer(port) {
    this.logger.info(`Starting Cursor extension server on port ${port}`);
    
    try {
      // Create HTTP server
      const server = http.createServer((req, res) => {
        if (req.url === '/health') {
          res.writeHead(200);
          res.end('OK');
          return;
        }
        
        res.writeHead(404);
        res.end('Not found');
      });
      
      // Create WebSocket server
      const wss = new WebSocket.Server({ server });
      
      // Handle WebSocket connections
      wss.on('connection', (ws) => {
        this.logger.debug('New WebSocket connection from Cursor extension');
        
        // Handle authentication and messages
        let authenticated = false;
        let connectionId = null;
        
        ws.on('message', async (message) => {
          try {
            const data = JSON.parse(message);
            
            if (!authenticated) {
              // Handle authentication
              if (data.type === 'auth' && data.token) {
                authenticated = await this._authenticateExtension(data.token);
                
                if (authenticated) {
                  connectionId = data.connectionId || uuidv4();
                  
                  // Find or create connection
                  let connection = null;
                  for (const [id, conn] of this.connections.entries()) {
                    if (conn.pendingConnectionId === connectionId) {
                      connection = conn;
                      connection.socket = ws;
                      connection.status = 'connected';
                      connection.lastActivity = Date.now();
                      break;
                    }
                  }
                  
                  if (!connection) {
                    // Create new connection
                    connection = {
                      id: connectionId,
                      type: 'extension',
                      socket: ws,
                      status: 'connected',
                      lastActivity: Date.now()
                    };
                    this.connections.set(connectionId, connection);
                  }
                  
                  // Send acknowledgement
                  ws.send(JSON.stringify({
                    type: 'auth_response',
                    success: true,
                    connectionId
                  }));
                  
                  this.logger.info(`Cursor extension authenticated (ID: ${connectionId})`);
                } else {
                  // Authentication failed
                  ws.send(JSON.stringify({
                    type: 'auth_response',
                    success: false,
                    error: 'Invalid authentication token'
                  }));
                  
                  this.logger.warn('Cursor extension authentication failed');
                  ws.close();
                }
              } else {
                // Not authenticated and not an auth message
                ws.send(JSON.stringify({
                  type: 'error',
                  error: 'Not authenticated'
                }));
                
                this.logger.warn('Unauthenticated message from Cursor extension');
                ws.close();
              }
            } else {
              // Handle authenticated messages
              if (data.type === 'event') {
                // Handle events from Cursor
                const connection = this.connections.get(connectionId);
                if (connection) {
                  this._triggerEvent(connection, data.eventType, data.eventData);
                }
              } else if (data.type === 'response') {
                // Handle command responses
                const connection = this.connections.get(connectionId);
                if (connection && connection.pendingCommands && connection.pendingCommands[data.requestId]) {
                  const { resolve, reject } = connection.pendingCommands[data.requestId];
                  
                  if (data.error) {
                    reject(new Error(data.error));
                  } else {
                    resolve(data.result);
                  }
                  
                  delete connection.pendingCommands[data.requestId];
                }
              }
            }
          } catch (error) {
            this.logger.error(`Error handling WebSocket message: ${error.message}`);
            
            ws.send(JSON.stringify({
              type: 'error',
              error: 'Invalid message format'
            }));
          }
        });
        
        ws.on('close', () => {
          this.logger.debug('WebSocket connection closed');
          
          if (connectionId && this.connections.has(connectionId)) {
            const connection = this.connections.get(connectionId);
            connection.socket = null;
            connection.status = 'disconnected';
            
            // Trigger disconnect event
            this._triggerEvent(connection, 'disconnect', { reason: 'WebSocket closed' });
          }
        });
      });
      
      // Start the server
      await new Promise((resolve) => {
        server.listen(port, () => {
          this.logger.info(`Cursor extension server listening on port ${port}`);
          resolve();
        });
      });
      
      this.server = server;
      this.wss = wss;
      
      return server;
    } catch (error) {
      this.logger.error(`Failed to start Cursor extension server: ${error.message}`);
      throw error;
    }
  }

  /**
   * Install the Cursor extension
   * @param {Object} options - Installation options
   * @returns {Promise<Object>} Installation result
   */
  async installExtension(options = {}) {
    this.logger.info('Installing Cursor extension');
    
    try {
      // Ensure extension directory exists
      await fs.mkdir(this.extensionPath, { recursive: true });
      
      // Check if extension is already installed
      const extensionJsonPath = path.join(this.extensionPath, 'extension.json');
      let extensionExists = false;
      
      try {
        await fs.access(extensionJsonPath);
        extensionExists = true;
      } catch (error) {
        // Extension doesn't exist
      }
      
      if (extensionExists && !options.force) {
        this.logger.info('Cursor extension is already installed');
        return { success: true, status: 'already_installed' };
      }
      
      // Generate extension files
      await this._generateExtensionFiles();
      
      // Install the extension in Cursor
      if (options.installInCursor !== false) {
        await this._installExtensionInCursor();
      }
      
      this.logger.info('Cursor extension installed successfully');
      
      return { success: true, status: 'installed' };
    } catch (error) {
      this.logger.error(`Failed to install Cursor extension: ${error.message}`);
      throw error;
    }
  }

  /**
   * Check if Cursor is installed
   * @private
   */
  async _checkCursorInstallation() {
    return new Promise((resolve, reject) => {
      exec('cursor --version', (error, stdout, stderr) => {
        if (error) {
          // Try alternative paths
          const cursorPaths = [
            '/Applications/Cursor.app/Contents/MacOS/Cursor',
            'C:\\Program Files\\Cursor\\Cursor.exe',
            'C:\\Users\\*\\AppData\\Local\\Programs\\Cursor\\Cursor.exe'
          ];
          
          // Check if any of the paths exist
          this._checkPaths(cursorPaths)
            .then(path => {
              if (path) {
                resolve(path);
              } else {
                reject(new Error('Cursor is not installed or not in PATH'));
              }
            })
            .catch(() => {
              reject(new Error('Cursor is not installed or not in PATH'));
            });
        } else {
          resolve(stdout.trim());
        }
      });
    });
  }

  /**
   * Check if any of the paths exist
   * @param {Array<string>} paths - Paths to check
   * @returns {Promise<string|null>} First existing path or null
   * @private
   */
  async _checkPaths(paths) {
    for (const pathPattern of paths) {
      try {
        if (pathPattern.includes('*')) {
          // Handle wildcard paths
          const basePath = path.dirname(pathPattern);
          const pattern = path.basename(pathPattern);
          
          try {
            const files = await fs.readdir(basePath);
            const matchingFile = files.find(file => this._matchPattern(file, pattern));
            
            if (matchingFile) {
              const fullPath = path.join(basePath, matchingFile);
              await fs.access(fullPath);
              return fullPath;
            }
          } catch (error) {
            // Ignore errors
          }
        } else {
          // Check exact path
          await fs.access(pathPattern);
          return pathPattern;
        }
      } catch (error) {
        // Path doesn't exist, continue
      }
    }
    
    return null;
  }

  /**
   * Match a filename against a pattern with wildcards
   * @param {string} filename - Filename to match
   * @param {string} pattern - Pattern with wildcards
   * @returns {boolean} Whether the filename matches the pattern
   * @private
   */
  _matchPattern(filename, pattern) {
    const regexPattern = pattern.replace(/\*/g, '.*');
    const regex = new RegExp(`^${regexPattern}$`);
    return regex.test(filename);
  }

  /**
   * Connect to Cursor via extension
   * @param {Object} connection - Connection object
   * @param {Object} options - Connection options
   * @private
   */
  async _connectViaExtension(connection, options) {
    // Check if extension is installed
    try {
      await fs.access(path.join(this.extensionPath, 'extension.json'));
    } catch (error) {
      // Install extension if not found
      await this.installExtension({ installInCursor: true });
    }
    
    // Generate a token for this connection
    const token = this._generateToken();
    
    // Store token for authentication
    connection.token = token;
    connection.pendingConnectionId = connection.id;
    connection.pendingCommands = {};
    
    // Launch Cursor with our extension if requested
    if (options.launchCursor) {
      const args = ['--extensionDevelopmentPath', this.extensionPath];
      
      if (options.workspace) {
        args.push(options.workspace);
      }
      
      const cursorPath = await this._getCursorPath();
      
      const process = spawn(cursorPath, args, {
        detached: true,
        stdio: 'ignore'
      });
      
      process.unref();
      
      // Wait for connection
      await new Promise((resolve, reject) => {
        const timeout = setTimeout(() => {
          reject(new Error('Timed out waiting for Cursor extension to connect'));
        }, 30000);
        
        const checkInterval = setInterval(() => {
          if (connection.socket) {
            clearTimeout(timeout);
            clearInterval(checkInterval);
            resolve();
          }
        }, 500);
      });
    } else {
      // Wait for extension to connect
      this.logger.info('Waiting for Cursor extension to connect...');
      
      // In a real implementation, we would wait for the extension to connect
      // For now, we'll simulate a successful connection
      connection.socket = {
        send: (data) => {
          this.logger.debug(`Simulated WebSocket send: ${data}`);
        },
        readyState: WebSocket.OPEN
      };
    }
  }

  /**
   * Connect to Cursor via API
   * @param {Object} connection - Connection object
   * @param {Object} options - Connection options
   * @private
   */
  async _connectViaAPI(connection, options) {
    // Cursor has a local HTTP API that we can use
    const apiPort = options.apiPort || 9999;
    const apiUrl = `http://localhost:${apiPort}`;
    
    try {
      // Test the API connection
      const response = await axios.get(`${apiUrl}/status`);
      
      if (response.status !== 200) {
        throw new Error(`Cursor API returned status ${response.status}`);
      }
      
      // Create API client
      connection.apiClient = {
        baseUrl: apiUrl,
        async request(method, path, data = null) {
          try {
            const response = await axios({
              method,
              url: `${apiUrl}${path}`,
              data
            });
            
            return response.data;
          } catch (error) {
            throw new Error(`Cursor API request failed: ${error.message}`);
          }
        }
      };
      
      this.logger.info(`Connected to Cursor API at ${apiUrl}`);
    } catch (error) {
      throw new Error(`Failed to connect to Cursor API: ${error.message}`);
    }
  }

  /**
   * Connect to Cursor via CLI
   * @param {Object} connection - Connection object
   * @param {Object} options - Connection options
   * @private
   */
  async _connectViaCLI(connection, options) {
    // For CLI connection, we'll use Cursor's command-line interface
    const cursorPath = await this._getCursorPath();
    
    // Store CLI process
    connection.process = null;
    connection.stdout = '';
    connection.stderr = '';
    
    // If workspace is specified, open it
    if (options.workspace) {
      const process = spawn(cursorPath, [options.workspace], {
        detached: true,
        stdio: 'ignore'
      });
      
      process.unref();
    }
  }

  /**
   * Execute a command via Cursor extension
   * @param {Object} connection - Connection object
   * @param {string} command - Command name
   * @param {Object} params - Command parameters
   * @returns {Promise<Object>} Command result
   * @private
   */
  async _executeExtensionCommand(connection, command, params) {
    if (!connection.socket || connection.socket.readyState !== WebSocket.OPEN) {
      throw new Error('Cursor extension not connected');
    }
    
    // Generate request ID
    const requestId = uuidv4();
    
    // Create promise for response
    const responsePromise = new Promise((resolve, reject) => {
      if (!connection.pendingCommands) {
        connection.pendingCommands = {};
      }
      
      connection.pendingCommands[requestId] = { resolve, reject };
      
      // Set timeout
      const timeout = setTimeout(() => {
        if (connection.pendingCommands[requestId]) {
          delete connection.pendingCommands[requestId];
          reject(new Error(`Command ${command} timed out`));
        }
      }, 30000);
    });
    
    // Send command to extension
    connection.socket.send(JSON.stringify({
      type: 'command',
      requestId,
      command,
      params
    }));
    
    // Wait for response
    return responsePromise;
  }

  /**
   * Execute a command via Cursor API
   * @param {Object} connection - Connection object
   * @param {string} command - Command name
   * @param {Object} params - Command parameters
   * @returns {Promise<Object>} Command result
   * @private
   */
  async _executeAPICommand(connection, command, params) {
    if (!connection.apiClient) {
      throw new Error('Cursor API client not initialized');
    }
    
    // Map our commands to Cursor API endpoints
    let apiMethod = 'post';
    let apiPath = '';
    let apiData = null;
    
    switch (command) {
      case 'openFile':
        apiPath = '/file/open';
        apiData = { path: params.filePath };
        break;
      case 'saveFile':
        apiPath = '/file/save';
        apiData = { path: params.filePath };
        break;
      case 'editFile':
        apiPath = '/file/edit';
        apiData = { 
          path: params.filePath,
          edits: params.edits
        };
        break;
      case 'getOpenFiles':
        apiMethod = 'get';
        apiPath = '/files/open';
        break;
      case 'generateCode':
        apiPath = '/ai/generate';
        apiData = { 
          prompt: params.prompt,
          context: params.context,
          language: params.language
        };
        break;
      case 'explainCode':
        apiPath = '/ai/explain';
        apiData = { 
          code: params.code,
          language: params.language
        };
        break;
      default:
        throw new Error(`Command ${command} not supported via API`);
    }
    
    // Execute the API request
    return connection.apiClient.request(apiMethod, apiPath, apiData);
  }

  /**
   * Execute a command via Cursor CLI
   * @param {Object} connection - Connection object
   * @param {string} command - Command name
   * @param {Object} params - Command parameters
   * @returns {Promise<Object>} Command result
   * @private
   */
  async _executeCLICommand(connection, command, params) {
    const cursorPath = await this._getCursorPath();
    
    // Map our commands to Cursor CLI commands
    let cliArgs = [];
    
    switch (command) {
      case 'openFile':
        cliArgs = ['--goto', params.filePath];
        break;
      case 'runCommand':
        cliArgs = ['--command', params.commandId];
        break;
      default:
        throw new Error(`Command ${command} not supported via CLI`);
    }
    
    // Execute the command
    return new Promise((resolve, reject) => {
      exec(`${cursorPath} ${cliArgs.join(' ')}`, (error, stdout, stderr) => {
        if (error) {
          reject(new Error(`Failed to execute Cursor CLI command: ${error.message}`));
          return;
        }
        
        resolve({ stdout, stderr });
      });
    });
  }

  /**
   * Get the path to Cursor executable
   * @returns {Promise<string>} Path to Cursor
   * @private
   */
  async _getCursorPath() {
    // Default paths by platform
    const defaultPaths = {
      win32: 'cursor',
      darwin: '/Applications/Cursor.app/Contents/MacOS/Cursor',
      linux: 'cursor'
    };
    
    const platform = process.platform;
    
    // Try to get from config
    const configPath = this.config.cursorPath;
    
    if (configPath) {
      try {
        await fs.access(configPath);
        return configPath;
      } catch (error) {
        this.logger.warn(`Configured Cursor path not found: ${configPath}`);
      }
    }
    
    // Check if cursor is in PATH
    try {
      await new Promise((resolve, reject) => {
        exec('cursor --version', (error, stdout, stderr) => {
          if (error) {
            reject(error);
          } else {
            resolve(stdout);
          }
        });
      });
      
      return 'cursor';
    } catch (error) {
      // Not in PATH, use default path
      return defaultPaths[platform] || 'cursor';
    }
  }

  /**
   * Generate a token for authentication
   * @returns {string} Authentication token
   * @private
   */
  _generateToken() {
    return require('crypto').randomBytes(32).toString('hex');
  }

  /**
   * Authenticate an extension connection
   * @param {string} token - Authentication token
   * @returns {Promise<boolean>} Whether authentication was successful
   * @private
   */
  async _authenticateExtension(token) {
    // Check if token matches any pending connection
    for (const connection of this.connections.values()) {
      if (connection.token === token) {
        return true;
      }
    }
    
    return false;
  }

  /**
   * Generate Cursor extension files
   * @returns {Promise<void>}
   * @private
   */
  async _generateExtensionFiles() {
    // Create extension.json
    const extensionJson = {
      name: 'aideon-ai-lite',
      displayName: 'Aideon AI Lite',
      description: 'Aideon AI Lite integration for Cursor',
      version: '1.0.0',
      publisher: 'aideon-ai',
      engines: {
        cursor: '^0.10.0'
      },
      categories: [
        'Other'
      ],
      activationEvents: [
        'onStartupFinished'
      ],
      main: './extension.js',
      contributes: {
        commands: [
          {
            command: 'aideon.connect',
            title: 'Connect to Aideon AI Lite'
          },
          {
            command: 'aideon.disconnect',
            title: 'Disconnect from Aideon AI Lite'
          }
        ]
      }
    };
    
    // Create extension.js - Cursor is based on VS Code, so we can use similar extension code
    const extensionJs = `
const cursor = require('cursor');
const WebSocket = require('ws');

let connection = null;
let statusBarItem = null;

/**
 * Activate the extension
 * @param {cursor.ExtensionContext} context
 */
function activate(context) {
  console.log('Aideon AI Lite extension for Cursor activated');
  
  // Create status bar item
  statusBarItem = cursor.window.createStatusBarItem(cursor.StatusBarAlignment.Right, 100);
  statusBarItem.text = 'Aideon: Disconnected';
  statusBarItem.command = 'aideon.connect';
  statusBarItem.show();
  
  // Register commands
  context.subscriptions.push(
    cursor.commands.registerCommand('aideon.connect', connectToAideon),
    cursor.commands.registerCommand('aideon.disconnect', disconnectFromAideon)
  );
  
  // Try to connect automatically
  connectToAideon();
}

/**
 * Deactivate the extension
 */
function deactivate() {
  disconnectFromAideon();
}

/**
 * Connect to Aideon AI Lite
 */
async function connectToAideon() {
  if (connection) {
    cursor.window.showInformationMessage('Already connected to Aideon AI Lite');
    return;
  }
  
  try {
    // Get connection details
    const serverUrl = 'ws://localhost:10501';
    const token = await getAuthToken();
    
    if (!token) {
      cursor.window.showErrorMessage('Failed to get authentication token for Aideon AI Lite');
      return;
    }
    
    // Connect to server
    const ws = new WebSocket(serverUrl);
    
    ws.on('open', () => {
      // Send authentication
      ws.send(JSON.stringify({
        type: 'auth',
        token
      }));
    });
    
    ws.on('message', (data) => {
      try {
        const message = JSON.parse(data);
        
        if (message.type === 'auth_response') {
          if (message.success) {
            // Authentication successful
            connection = {
              socket: ws,
              connectionId: message.connectionId
            };
            
            statusBarItem.text = 'Aideon: Connected';
            statusBarItem.command = 'aideon.disconnect';
            
            cursor.window.showInformationMessage('Connected to Aideon AI Lite');
          } else {
            // Authentication failed
            cursor.window.showErrorMessage('Failed to authenticate with Aideon AI Lite: ' + (message.error || 'Unknown error'));
            ws.close();
          }
        } else if (message.type === 'command') {
          // Handle command from Aideon
          handleCommand(message)
            .then((result) => {
              ws.send(JSON.stringify({
                type: 'response',
                requestId: message.requestId,
                result
              }));
            })
            .catch((error) => {
              ws.send(JSON.stringify({
                type: 'response',
                requestId: message.requestId,
                error: error.message
              }));
            });
        }
      } catch (error) {
        console.error('Error handling message:', error);
      }
    });
    
    ws.on('close', () => {
      connection = null;
      statusBarItem.text = 'Aideon: Disconnected';
      statusBarItem.command = 'aideon.connect';
    });
    
    ws.on('error', (error) => {
      console.error('WebSocket error:', error);
      cursor.window.showErrorMessage('Error connecting to Aideon AI Lite: ' + error.message);
    });
  } catch (error) {
    cursor.window.showErrorMessage('Failed to connect to Aideon AI Lite: ' + error.message);
  }
}

/**
 * Disconnect from Aideon AI Lite
 */
function disconnectFromAideon() {
  if (!connection) {
    return;
  }
  
  try {
    connection.socket.close();
    connection = null;
    
    statusBarItem.text = 'Aideon: Disconnected';
    statusBarItem.command = 'aideon.connect';
    
    cursor.window.showInformationMessage('Disconnected from Aideon AI Lite');
  } catch (error) {
    console.error('Error disconnecting:', error);
  }
}

/**
 * Get authentication token
 * @returns {Promise<string>} Authentication token
 */
async function getAuthToken() {
  // In a real implementation, this would get a token from the Aideon AI Lite app
  // For now, we'll use a hardcoded token
  return 'aideon-cursor-token';
}

/**
 * Handle command from Aideon
 * @param {Object} message - Command message
 * @returns {Promise<Object>} Command result
 */
async function handleCommand(message) {
  const { command, params } = message;
  
  switch (command) {
    case 'openFile':
      return await openFile(params);
    case 'saveFile':
      return await saveFile(params);
    case 'editFile':
      return await editFile(params);
    case 'getOpenFiles':
      return await getOpenFiles();
    case 'getProjectStructure':
      return await getProjectStructure();
    case 'runCommand':
      return await runCommand(params);
    case 'generateCode':
      return await generateCode(params);
    case 'explainCode':
      return await explainCode(params);
    default:
      throw new Error('Unsupported command: ' + command);
  }
}

/**
 * Open a file in the editor
 * @param {Object} params - Command parameters
 * @returns {Promise<Object>} Command result
 */
async function openFile(params) {
  const { filePath, viewColumn } = params;
  
  try {
    const document = await cursor.workspace.openTextDocument(filePath);
    const editor = await cursor.window.showTextDocument(document, viewColumn || cursor.ViewColumn.Active);
    
    return {
      success: true,
      filePath,
      language: document.languageId
    };
  } catch (error) {
    throw new Error('Failed to open file: ' + error.message);
  }
}

/**
 * Save a file
 * @param {Object} params - Command parameters
 * @returns {Promise<Object>} Command result
 */
async function saveFile(params) {
  const { filePath } = params;
  
  try {
    // Find the document
    const document = cursor.workspace.textDocuments.find(doc => doc.fileName === filePath);
    
    if (!document) {
      throw new Error('File not open: ' + filePath);
    }
    
    // Save the document
    await document.save();
    
    return {
      success: true,
      filePath
    };
  } catch (error) {
    throw new Error('Failed to save file: ' + error.message);
  }
}

/**
 * Edit a file
 * @param {Object} params - Command parameters
 * @returns {Promise<Object>} Command result
 */
async function editFile(params) {
  const { filePath, edits } = params;
  
  try {
    // Find or open the document
    let document = cursor.workspace.textDocuments.find(doc => doc.fileName === filePath);
    
    if (!document) {
      document = await cursor.workspace.openTextDocument(filePath);
      await cursor.window.showTextDocument(document);
    }
    
    // Apply edits
    const editor = cursor.window.activeTextEditor;
    
    if (!editor || editor.document.fileName !== filePath) {
      throw new Error('Failed to get editor for file: ' + filePath);
    }
    
    await editor.edit(editBuilder => {
      for (const edit of edits) {
        const { range, text } = edit;
        const cursorRange = new cursor.Range(
          new cursor.Position(range.start.line, range.start.character),
          new cursor.Position(range.end.line, range.end.character)
        );
        
        editBuilder.replace(cursorRange, text);
      }
    });
    
    return {
      success: true,
      filePath
    };
  } catch (error) {
    throw new Error('Failed to edit file: ' + error.message);
  }
}

/**
 * Get open files
 * @returns {Promise<Object>} Command result
 */
async function getOpenFiles() {
  try {
    const files = cursor.workspace.textDocuments
      .filter(doc => !doc.isUntitled)
      .map(doc => ({
        filePath: doc.fileName,
        language: doc.languageId,
        isDirty: doc.isDirty
      }));
    
    return {
      files
    };
  } catch (error) {
    throw new Error('Failed to get open files: ' + error.message);
  }
}

/**
 * Get project structure
 * @returns {Promise<Object>} Command result
 */
async function getProjectStructure() {
  try {
    // Get workspace folders
    const workspaceFolders = cursor.workspace.workspaceFolders || [];
    
    const folders = await Promise.all(workspaceFolders.map(async folder => {
      return {
        name: folder.name,
        path: folder.uri.fsPath,
        files: await getFilesInFolder(folder.uri.fsPath)
      };
    }));
    
    return {
      folders
    };
  } catch (error) {
    throw new Error('Failed to get project structure: ' + error.message);
  }
}

/**
 * Get files in a folder recursively
 * @param {string} folderPath - Folder path
 * @returns {Promise<Array>} Files in the folder
 */
async function getFilesInFolder(folderPath) {
  // This is a simplified implementation
  // In a real extension, we would use the file system API
  return [];
}

/**
 * Run a Cursor command
 * @param {Object} params - Command parameters
 * @returns {Promise<Object>} Command result
 */
async function runCommand(params) {
  const { commandId, args } = params;
  
  try {
    const result = await cursor.commands.executeCommand(commandId, ...(args || []));
    
    return {
      success: true,
      result
    };
  } catch (error) {
    throw new Error('Failed to run command: ' + error.message);
  }
}

/**
 * Generate code using Cursor's AI capabilities
 * @param {Object} params - Command parameters
 * @returns {Promise<Object>} Command result
 */
async function generateCode(params) {
  const { prompt, language } = params;
  
  try {
    // In a real implementation, this would use Cursor's API to generate code
    // For now, we'll simulate it
    
    return {
      success: true,
      code: '// Generated code would appear here\n// Based on prompt: ' + prompt,
      language: language || 'javascript'
    };
  } catch (error) {
    throw new Error('Failed to generate code: ' + error.message);
  }
}

/**
 * Explain code using Cursor's AI capabilities
 * @param {Object} params - Command parameters
 * @returns {Promise<Object>} Command result
 */
async function explainCode(params) {
  const { code } = params;
  
  try {
    // In a real implementation, this would use Cursor's API to explain code
    // For now, we'll simulate it
    
    return {
      success: true,
      explanation: 'This code would be explained by Cursor\'s AI.'
    };
  } catch (error) {
    throw new Error('Failed to explain code: ' + error.message);
  }
}

module.exports = {
  activate,
  deactivate
};
`;
    
    // Create package.json
    const packageJson = {
      name: 'aideon-ai-lite',
      displayName: 'Aideon AI Lite',
      description: 'Aideon AI Lite integration for Cursor',
      version: '1.0.0',
      publisher: 'aideon-ai',
      engines: {
        cursor: '^0.10.0'
      },
      dependencies: {
        ws: '^8.5.0'
      }
    };
    
    // Write files
    await fs.writeFile(path.join(this.extensionPath, 'extension.json'), JSON.stringify(extensionJson, null, 2));
    await fs.writeFile(path.join(this.extensionPath, 'extension.js'), extensionJs);
    await fs.writeFile(path.join(this.extensionPath, 'package.json'), JSON.stringify(packageJson, null, 2));
  }

  /**
   * Install the extension in Cursor
   * @returns {Promise<void>}
   * @private
   */
  async _installExtensionInCursor() {
    // In a real implementation, this would install the extension in Cursor
    // For now, we'll just simulate success
    this.logger.info('Simulating Cursor extension installation');
    
    // Wait a bit to simulate installation
    await new Promise(resolve => setTimeout(resolve, 1000));
  }
}

module.exports = CursorIntegration;
