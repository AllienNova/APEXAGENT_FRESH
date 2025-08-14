/**
 * VSCodeIntegration.js
 * 
 * Integration with Visual Studio Code IDE for Aideon AI Lite.
 * Enables seamless interaction with VS Code for code editing, debugging, and more.
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

class VSCodeIntegration extends BaseIDEIntegration {
  constructor(core) {
    super(core);
    this.extensionPath = path.join(this.core.configManager.getDataDir(), 'extensions', 'vscode');
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
      'startDebugging',
      'stopDebugging',
      'installExtension',
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
    return 'VSCode';
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
      extensionManagement: true
    };
  }

  /**
   * Connect to VS Code
   * @param {Object} options - Connection options
   * @returns {Promise<Object>} Connection object
   */
  async connect(options = {}) {
    this.logger.info('Connecting to VS Code');
    
    try {
      // Check if VS Code is installed
      await this._checkVSCodeInstallation();
      
      // Generate a unique connection ID
      const connectionId = uuidv4();
      
      // Create connection object
      const connection = {
        id: connectionId,
        type: options.type || 'extension', // 'extension' or 'cli'
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
      } else {
        // Connect via CLI
        await this._connectViaCLI(connection, options);
      }
      
      connection.status = 'connected';
      connection.lastActivity = Date.now();
      
      this.logger.info(`Connected to VS Code (ID: ${connectionId})`);
      
      return connection;
    } catch (error) {
      this.logger.error(`Failed to connect to VS Code: ${error.message}`);
      throw error;
    }
  }

  /**
   * Disconnect from VS Code
   * @param {Object} connection - Connection object
   * @returns {Promise<boolean>} Success status
   */
  async disconnect(connection) {
    this.logger.info(`Disconnecting from VS Code (ID: ${connection.id})`);
    
    try {
      if (connection.socket && connection.socket.readyState === WebSocket.OPEN) {
        connection.socket.close();
      }
      
      if (connection.type === 'cli' && connection.process) {
        connection.process.kill();
      }
      
      this.connections.delete(connection.id);
      
      this.logger.info(`Disconnected from VS Code (ID: ${connection.id})`);
      return true;
    } catch (error) {
      this.logger.error(`Failed to disconnect from VS Code: ${error.message}`);
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
   * Execute a command in VS Code
   * @param {Object} connection - Connection object
   * @param {string} command - Command name
   * @param {Object} params - Command parameters
   * @returns {Promise<Object>} Command result
   */
  async executeCommand(connection, command, params = {}) {
    if (!this.supportsCommand(command)) {
      throw new Error(`Command ${command} not supported by VS Code integration`);
    }
    
    this.logger.debug(`Executing command ${command} in VS Code (ID: ${connection.id})`);
    
    try {
      // Update last activity timestamp
      connection.lastActivity = Date.now();
      
      // Execute the command based on connection type
      if (connection.type === 'extension') {
        return await this._executeExtensionCommand(connection, command, params);
      } else {
        return await this._executeCLICommand(connection, command, params);
      }
    } catch (error) {
      this.logger.error(`Failed to execute command ${command}: ${error.message}`);
      throw error;
    }
  }

  /**
   * Start a server for VS Code extension communication
   * @param {number} port - Port to listen on
   * @returns {Promise<Object>} Server object
   */
  async startServer(port) {
    this.logger.info(`Starting VS Code extension server on port ${port}`);
    
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
        this.logger.debug('New WebSocket connection from VS Code extension');
        
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
                  
                  this.logger.info(`VS Code extension authenticated (ID: ${connectionId})`);
                } else {
                  // Authentication failed
                  ws.send(JSON.stringify({
                    type: 'auth_response',
                    success: false,
                    error: 'Invalid authentication token'
                  }));
                  
                  this.logger.warn('VS Code extension authentication failed');
                  ws.close();
                }
              } else {
                // Not authenticated and not an auth message
                ws.send(JSON.stringify({
                  type: 'error',
                  error: 'Not authenticated'
                }));
                
                this.logger.warn('Unauthenticated message from VS Code extension');
                ws.close();
              }
            } else {
              // Handle authenticated messages
              if (data.type === 'event') {
                // Handle events from VS Code
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
          this.logger.info(`VS Code extension server listening on port ${port}`);
          resolve();
        });
      });
      
      this.server = server;
      this.wss = wss;
      
      return server;
    } catch (error) {
      this.logger.error(`Failed to start VS Code extension server: ${error.message}`);
      throw error;
    }
  }

  /**
   * Install the VS Code extension
   * @param {Object} options - Installation options
   * @returns {Promise<Object>} Installation result
   */
  async installExtension(options = {}) {
    this.logger.info('Installing VS Code extension');
    
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
        this.logger.info('VS Code extension is already installed');
        return { success: true, status: 'already_installed' };
      }
      
      // Generate extension files
      await this._generateExtensionFiles();
      
      // Install the extension in VS Code
      if (options.installInVSCode !== false) {
        await this._installExtensionInVSCode();
      }
      
      this.logger.info('VS Code extension installed successfully');
      
      return { success: true, status: 'installed' };
    } catch (error) {
      this.logger.error(`Failed to install VS Code extension: ${error.message}`);
      throw error;
    }
  }

  /**
   * Check if VS Code is installed
   * @private
   */
  async _checkVSCodeInstallation() {
    return new Promise((resolve, reject) => {
      exec('code --version', (error, stdout, stderr) => {
        if (error) {
          reject(new Error('VS Code is not installed or not in PATH'));
          return;
        }
        
        resolve(stdout.trim());
      });
    });
  }

  /**
   * Connect to VS Code via extension
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
      await this.installExtension({ installInVSCode: true });
    }
    
    // Generate a token for this connection
    const token = this._generateToken();
    
    // Store token for authentication
    connection.token = token;
    connection.pendingConnectionId = connection.id;
    connection.pendingCommands = {};
    
    // Launch VS Code with our extension if requested
    if (options.launchVSCode) {
      const args = ['--extensionDevelopmentPath', this.extensionPath];
      
      if (options.workspace) {
        args.push(options.workspace);
      }
      
      const vscodePath = await this._getVSCodePath();
      
      const process = spawn(vscodePath, args, {
        detached: true,
        stdio: 'ignore'
      });
      
      process.unref();
      
      // Wait for connection
      await new Promise((resolve, reject) => {
        const timeout = setTimeout(() => {
          reject(new Error('Timed out waiting for VS Code extension to connect'));
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
      this.logger.info('Waiting for VS Code extension to connect...');
      
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
   * Connect to VS Code via CLI
   * @param {Object} connection - Connection object
   * @param {Object} options - Connection options
   * @private
   */
  async _connectViaCLI(connection, options) {
    // For CLI connection, we'll use VS Code's command-line interface
    const vscodePath = await this._getVSCodePath();
    
    // Store CLI process
    connection.process = null;
    connection.stdout = '';
    connection.stderr = '';
    
    // If workspace is specified, open it
    if (options.workspace) {
      const process = spawn(vscodePath, [options.workspace], {
        detached: true,
        stdio: 'ignore'
      });
      
      process.unref();
    }
  }

  /**
   * Execute a command via VS Code extension
   * @param {Object} connection - Connection object
   * @param {string} command - Command name
   * @param {Object} params - Command parameters
   * @returns {Promise<Object>} Command result
   * @private
   */
  async _executeExtensionCommand(connection, command, params) {
    if (!connection.socket || connection.socket.readyState !== WebSocket.OPEN) {
      throw new Error('VS Code extension not connected');
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
   * Execute a command via VS Code CLI
   * @param {Object} connection - Connection object
   * @param {string} command - Command name
   * @param {Object} params - Command parameters
   * @returns {Promise<Object>} Command result
   * @private
   */
  async _executeCLICommand(connection, command, params) {
    const vscodePath = await this._getVSCodePath();
    
    // Map our commands to VS Code CLI commands
    let cliArgs = [];
    
    switch (command) {
      case 'openFile':
        cliArgs = ['--goto', params.filePath];
        break;
      case 'runCommand':
        cliArgs = ['--command', params.commandId];
        break;
      case 'installExtension':
        cliArgs = ['--install-extension', params.extensionId];
        break;
      default:
        throw new Error(`Command ${command} not supported via CLI`);
    }
    
    // Execute the command
    return new Promise((resolve, reject) => {
      exec(`${vscodePath} ${cliArgs.join(' ')}`, (error, stdout, stderr) => {
        if (error) {
          reject(new Error(`Failed to execute VS Code CLI command: ${error.message}`));
          return;
        }
        
        resolve({ stdout, stderr });
      });
    });
  }

  /**
   * Get the path to VS Code executable
   * @returns {Promise<string>} Path to VS Code
   * @private
   */
  async _getVSCodePath() {
    // Default paths by platform
    const defaultPaths = {
      win32: 'code',
      darwin: '/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code',
      linux: 'code'
    };
    
    const platform = process.platform;
    
    // Try to get from config
    const configPath = this.config.vscodePath;
    
    if (configPath) {
      try {
        await fs.access(configPath);
        return configPath;
      } catch (error) {
        this.logger.warn(`Configured VS Code path not found: ${configPath}`);
      }
    }
    
    // Use default path
    return defaultPaths[platform] || 'code';
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
   * Generate VS Code extension files
   * @returns {Promise<void>}
   * @private
   */
  async _generateExtensionFiles() {
    // Create extension.json
    const extensionJson = {
      name: 'aideon-ai-lite',
      displayName: 'Aideon AI Lite',
      description: 'Aideon AI Lite integration for VS Code',
      version: '1.0.0',
      publisher: 'aideon-ai',
      engines: {
        vscode: '^1.60.0'
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
    
    // Create extension.js
    const extensionJs = `
const vscode = require('vscode');
const WebSocket = require('ws');

let connection = null;
let statusBarItem = null;

/**
 * Activate the extension
 * @param {vscode.ExtensionContext} context
 */
function activate(context) {
  console.log('Aideon AI Lite extension activated');
  
  // Create status bar item
  statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
  statusBarItem.text = 'Aideon: Disconnected';
  statusBarItem.command = 'aideon.connect';
  statusBarItem.show();
  
  // Register commands
  context.subscriptions.push(
    vscode.commands.registerCommand('aideon.connect', connectToAideon),
    vscode.commands.registerCommand('aideon.disconnect', disconnectFromAideon)
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
    vscode.window.showInformationMessage('Already connected to Aideon AI Lite');
    return;
  }
  
  try {
    // Get connection details
    const serverUrl = 'ws://localhost:10500';
    const token = await getAuthToken();
    
    if (!token) {
      vscode.window.showErrorMessage('Failed to get authentication token for Aideon AI Lite');
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
            
            vscode.window.showInformationMessage('Connected to Aideon AI Lite');
          } else {
            // Authentication failed
            vscode.window.showErrorMessage('Failed to authenticate with Aideon AI Lite: ' + (message.error || 'Unknown error'));
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
      vscode.window.showErrorMessage('Error connecting to Aideon AI Lite: ' + error.message);
    });
  } catch (error) {
    vscode.window.showErrorMessage('Failed to connect to Aideon AI Lite: ' + error.message);
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
    
    vscode.window.showInformationMessage('Disconnected from Aideon AI Lite');
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
  return 'aideon-vscode-token';
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
    const document = await vscode.workspace.openTextDocument(filePath);
    const editor = await vscode.window.showTextDocument(document, viewColumn || vscode.ViewColumn.Active);
    
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
    const document = vscode.workspace.textDocuments.find(doc => doc.fileName === filePath);
    
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
    let document = vscode.workspace.textDocuments.find(doc => doc.fileName === filePath);
    
    if (!document) {
      document = await vscode.workspace.openTextDocument(filePath);
      await vscode.window.showTextDocument(document);
    }
    
    // Apply edits
    const editor = vscode.window.activeTextEditor;
    
    if (!editor || editor.document.fileName !== filePath) {
      throw new Error('Failed to get editor for file: ' + filePath);
    }
    
    await editor.edit(editBuilder => {
      for (const edit of edits) {
        const { range, text } = edit;
        const vscodeRange = new vscode.Range(
          new vscode.Position(range.start.line, range.start.character),
          new vscode.Position(range.end.line, range.end.character)
        );
        
        editBuilder.replace(vscodeRange, text);
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
    const files = vscode.workspace.textDocuments
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
    const workspaceFolders = vscode.workspace.workspaceFolders || [];
    
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
 * Run a VS Code command
 * @param {Object} params - Command parameters
 * @returns {Promise<Object>} Command result
 */
async function runCommand(params) {
  const { commandId, args } = params;
  
  try {
    const result = await vscode.commands.executeCommand(commandId, ...(args || []));
    
    return {
      success: true,
      result
    };
  } catch (error) {
    throw new Error('Failed to run command: ' + error.message);
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
      description: 'Aideon AI Lite integration for VS Code',
      version: '1.0.0',
      publisher: 'aideon-ai',
      engines: {
        vscode: '^1.60.0'
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
   * Install the extension in VS Code
   * @returns {Promise<void>}
   * @private
   */
  async _installExtensionInVSCode() {
    // In a real implementation, this would install the extension in VS Code
    // For now, we'll just simulate success
    this.logger.info('Simulating VS Code extension installation');
    
    // Wait a bit to simulate installation
    await new Promise(resolve => setTimeout(resolve, 1000));
  }
}

module.exports = VSCodeIntegration;
