/**
 * GitHubIntegration.js
 * 
 * Integration with GitHub for Aideon AI Lite.
 * Enables seamless interaction with GitHub repositories, issues, pull requests, and more.
 * 
 * @author Aideon AI Team
 * @version 1.0.0
 */

const BaseIDEIntegration = require('../BaseIDEIntegration');
const { Octokit } = require('@octokit/rest');
const { createAppAuth } = require('@octokit/auth-app');
const fs = require('fs').promises;
const path = require('path');
const { spawn, exec } = require('child_process');
const { v4: uuidv4 } = require('uuid');
const axios = require('axios');

class GitHubIntegration extends BaseIDEIntegration {
  constructor(core) {
    super(core);
    this.connections = new Map();
    this.supportedCommands = [
      'getRepositories',
      'getRepository',
      'createRepository',
      'forkRepository',
      'cloneRepository',
      'getBranches',
      'createBranch',
      'getIssues',
      'createIssue',
      'updateIssue',
      'getPullRequests',
      'createPullRequest',
      'mergePullRequest',
      'getCommits',
      'createCommit',
      'getContents',
      'updateContents',
      'getGists',
      'createGist',
      'updateGist',
      'searchCode',
      'searchRepositories',
      'searchIssues',
      'getWorkflows',
      'triggerWorkflow'
    ];
  }

  /**
   * Get the name of the IDE
   * @returns {string} IDE name
   */
  getIDEName() {
    return 'GitHub';
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
      debugging: false,
      terminalAccess: false,
      codeCompletion: false,
      codeNavigation: true,
      refactoring: false,
      versionControl: true,
      extensionManagement: false,
      issueTracking: true,
      pullRequests: true,
      codeReview: true,
      cicd: true,
      collaboration: true
    };
  }

  /**
   * Connect to GitHub
   * @param {Object} options - Connection options
   * @returns {Promise<Object>} Connection object
   */
  async connect(options = {}) {
    this.logger.info('Connecting to GitHub');
    
    try {
      // Generate a unique connection ID
      const connectionId = uuidv4();
      
      // Create connection object
      const connection = {
        id: connectionId,
        type: options.type || 'api', // 'api' or 'cli'
        status: 'connecting',
        lastActivity: Date.now()
      };
      
      // Store the connection
      this.connections.set(connectionId, connection);
      
      if (connection.type === 'api') {
        // Connect via API
        await this._connectViaAPI(connection, options);
      } else {
        // Connect via CLI
        await this._connectViaCLI(connection, options);
      }
      
      connection.status = 'connected';
      connection.lastActivity = Date.now();
      
      this.logger.info(`Connected to GitHub (ID: ${connectionId})`);
      
      return connection;
    } catch (error) {
      this.logger.error(`Failed to connect to GitHub: ${error.message}`);
      throw error;
    }
  }

  /**
   * Disconnect from GitHub
   * @param {Object} connection - Connection object
   * @returns {Promise<boolean>} Success status
   */
  async disconnect(connection) {
    this.logger.info(`Disconnecting from GitHub (ID: ${connection.id})`);
    
    try {
      // Clean up resources
      if (connection.type === 'cli' && connection.process) {
        connection.process.kill();
      }
      
      this.connections.delete(connection.id);
      
      this.logger.info(`Disconnected from GitHub (ID: ${connection.id})`);
      return true;
    } catch (error) {
      this.logger.error(`Failed to disconnect from GitHub: ${error.message}`);
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
   * Execute a command in GitHub
   * @param {Object} connection - Connection object
   * @param {string} command - Command name
   * @param {Object} params - Command parameters
   * @returns {Promise<Object>} Command result
   */
  async executeCommand(connection, command, params = {}) {
    if (!this.supportsCommand(command)) {
      throw new Error(`Command ${command} not supported by GitHub integration`);
    }
    
    this.logger.debug(`Executing command ${command} in GitHub (ID: ${connection.id})`);
    
    try {
      // Update last activity timestamp
      connection.lastActivity = Date.now();
      
      // Execute the command based on connection type
      if (connection.type === 'api') {
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
   * Start a server for GitHub webhook communication
   * @param {number} port - Port to listen on
   * @returns {Promise<Object>} Server object
   */
  async startServer(port) {
    this.logger.info(`Starting GitHub webhook server on port ${port}`);
    
    try {
      // Create HTTP server for webhooks
      const http = require('http');
      const crypto = require('crypto');
      
      const server = http.createServer(async (req, res) => {
        if (req.method === 'POST' && req.url === '/webhook') {
          let body = '';
          
          req.on('data', chunk => {
            body += chunk.toString();
          });
          
          req.on('end', async () => {
            try {
              // Verify webhook signature if secret is configured
              const webhookSecret = this.core.configManager.getConfig().github?.webhookSecret;
              
              if (webhookSecret) {
                const signature = req.headers['x-hub-signature-256'];
                
                if (!signature) {
                  res.writeHead(401);
                  res.end('Unauthorized');
                  return;
                }
                
                const hmac = crypto.createHmac('sha256', webhookSecret);
                const digest = 'sha256=' + hmac.update(body).digest('hex');
                
                if (signature !== digest) {
                  res.writeHead(401);
                  res.end('Unauthorized');
                  return;
                }
              }
              
              // Parse webhook payload
              const event = req.headers['x-github-event'];
              const payload = JSON.parse(body);
              
              // Process webhook
              await this._processWebhook(event, payload);
              
              res.writeHead(200);
              res.end('OK');
            } catch (error) {
              this.logger.error(`Error processing webhook: ${error.message}`);
              res.writeHead(500);
              res.end('Internal Server Error');
            }
          });
        } else if (req.url === '/health') {
          res.writeHead(200);
          res.end('OK');
        } else {
          res.writeHead(404);
          res.end('Not found');
        }
      });
      
      // Start the server
      await new Promise((resolve) => {
        server.listen(port, () => {
          this.logger.info(`GitHub webhook server listening on port ${port}`);
          resolve();
        });
      });
      
      this.server = server;
      
      return server;
    } catch (error) {
      this.logger.error(`Failed to start GitHub webhook server: ${error.message}`);
      throw error;
    }
  }

  /**
   * Install the GitHub integration
   * @param {Object} options - Installation options
   * @returns {Promise<Object>} Installation result
   */
  async installExtension(options = {}) {
    this.logger.info('Installing GitHub integration');
    
    try {
      // Check if GitHub CLI is installed
      try {
        await this._checkGitHubCLIInstallation();
        this.logger.info('GitHub CLI is already installed');
      } catch (error) {
        // Install GitHub CLI if requested
        if (options.installCLI) {
          await this._installGitHubCLI();
          this.logger.info('GitHub CLI installed successfully');
        } else {
          this.logger.warn('GitHub CLI is not installed. Some features may not be available.');
        }
      }
      
      // Configure GitHub CLI if requested
      if (options.configureAuth && options.token) {
        await this._configureGitHubCLIAuth(options.token);
        this.logger.info('GitHub CLI authentication configured successfully');
      }
      
      return { success: true, status: 'installed' };
    } catch (error) {
      this.logger.error(`Failed to install GitHub integration: ${error.message}`);
      throw error;
    }
  }

  /**
   * Connect to GitHub via API
   * @param {Object} connection - Connection object
   * @param {Object} options - Connection options
   * @private
   */
  async _connectViaAPI(connection, options) {
    // Check authentication options
    if (!options.token && !options.appId) {
      throw new Error('GitHub API connection requires either a token or app credentials');
    }
    
    let octokit;
    
    if (options.token) {
      // Connect with personal access token
      octokit = new Octokit({
        auth: options.token
      });
      
      // Test the connection
      const user = await octokit.users.getAuthenticated();
      connection.username = user.data.login;
      
      this.logger.info(`Authenticated with GitHub API as ${connection.username}`);
    } else if (options.appId) {
      // Connect with GitHub App
      const appAuth = createAppAuth({
        appId: options.appId,
        privateKey: options.privateKey,
        clientId: options.clientId,
        clientSecret: options.clientSecret
      });
      
      const appAuthentication = await appAuth({ type: 'app' });
      
      octokit = new Octokit({
        auth: appAuthentication.token
      });
      
      // Store app details
      connection.appId = options.appId;
      
      this.logger.info(`Authenticated with GitHub API as App ${options.appId}`);
    }
    
    // Store Octokit instance
    connection.octokit = octokit;
  }

  /**
   * Connect to GitHub via CLI
   * @param {Object} connection - Connection object
   * @param {Object} options - Connection options
   * @private
   */
  async _connectViaCLI(connection, options) {
    // Check if GitHub CLI is installed
    await this._checkGitHubCLIInstallation();
    
    // Check authentication status
    const authStatus = await this._getGitHubCLIAuthStatus();
    
    if (!authStatus.authenticated) {
      if (options.token) {
        // Authenticate with token
        await this._configureGitHubCLIAuth(options.token);
      } else {
        throw new Error('GitHub CLI is not authenticated and no token was provided');
      }
    }
    
    // Store CLI auth status
    connection.username = authStatus.user;
    connection.authStatus = authStatus;
  }

  /**
   * Execute a command via GitHub API
   * @param {Object} connection - Connection object
   * @param {string} command - Command name
   * @param {Object} params - Command parameters
   * @returns {Promise<Object>} Command result
   * @private
   */
  async _executeAPICommand(connection, command, params) {
    if (!connection.octokit) {
      throw new Error('GitHub API client not initialized');
    }
    
    const octokit = connection.octokit;
    
    // Execute the command
    switch (command) {
      case 'getRepositories': {
        const { username = connection.username, page = 1, perPage = 30, visibility = 'all' } = params;
        
        const response = await octokit.repos.listForUser({
          username,
          page,
          per_page: perPage,
          type: visibility
        });
        
        return {
          repositories: response.data,
          totalCount: response.data.length,
          hasNextPage: response.data.length === perPage
        };
      }
      
      case 'getRepository': {
        const { owner, repo } = params;
        
        const response = await octokit.repos.get({
          owner,
          repo
        });
        
        return {
          repository: response.data
        };
      }
      
      case 'createRepository': {
        const { name, description, isPrivate = false, hasIssues = true, hasProjects = true, hasWiki = true } = params;
        
        const response = await octokit.repos.createForAuthenticatedUser({
          name,
          description,
          private: isPrivate,
          has_issues: hasIssues,
          has_projects: hasProjects,
          has_wiki: hasWiki
        });
        
        return {
          repository: response.data
        };
      }
      
      case 'forkRepository': {
        const { owner, repo, organization } = params;
        
        const requestParams = {
          owner,
          repo
        };
        
        if (organization) {
          requestParams.organization = organization;
        }
        
        const response = await octokit.repos.createFork(requestParams);
        
        return {
          repository: response.data
        };
      }
      
      case 'getBranches': {
        const { owner, repo, protected: protectedOnly = false } = params;
        
        const response = await octokit.repos.listBranches({
          owner,
          repo,
          protected: protectedOnly
        });
        
        return {
          branches: response.data
        };
      }
      
      case 'createBranch': {
        const { owner, repo, name, sha } = params;
        
        // Get the SHA of the reference to base the new branch on
        let baseSha = sha;
        
        if (!baseSha) {
          const defaultBranch = await octokit.repos.get({
            owner,
            repo
          });
          
          const reference = await octokit.git.getRef({
            owner,
            repo,
            ref: `heads/${defaultBranch.data.default_branch}`
          });
          
          baseSha = reference.data.object.sha;
        }
        
        // Create the new branch
        const response = await octokit.git.createRef({
          owner,
          repo,
          ref: `refs/heads/${name}`,
          sha: baseSha
        });
        
        return {
          reference: response.data
        };
      }
      
      case 'getIssues': {
        const { owner, repo, state = 'open', labels, assignee, creator, mentioned, since, page = 1, perPage = 30 } = params;
        
        const response = await octokit.issues.listForRepo({
          owner,
          repo,
          state,
          labels,
          assignee,
          creator,
          mentioned,
          since,
          page,
          per_page: perPage
        });
        
        return {
          issues: response.data,
          totalCount: response.data.length,
          hasNextPage: response.data.length === perPage
        };
      }
      
      case 'createIssue': {
        const { owner, repo, title, body, assignees, labels, milestone } = params;
        
        const response = await octokit.issues.create({
          owner,
          repo,
          title,
          body,
          assignees,
          labels,
          milestone
        });
        
        return {
          issue: response.data
        };
      }
      
      case 'updateIssue': {
        const { owner, repo, issueNumber, title, body, state, assignees, labels, milestone } = params;
        
        const response = await octokit.issues.update({
          owner,
          repo,
          issue_number: issueNumber,
          title,
          body,
          state,
          assignees,
          labels,
          milestone
        });
        
        return {
          issue: response.data
        };
      }
      
      case 'getPullRequests': {
        const { owner, repo, state = 'open', head, base, sort = 'created', direction = 'desc', page = 1, perPage = 30 } = params;
        
        const response = await octokit.pulls.list({
          owner,
          repo,
          state,
          head,
          base,
          sort,
          direction,
          page,
          per_page: perPage
        });
        
        return {
          pullRequests: response.data,
          totalCount: response.data.length,
          hasNextPage: response.data.length === perPage
        };
      }
      
      case 'createPullRequest': {
        const { owner, repo, title, body, head, base, draft = false, maintainerCanModify = true } = params;
        
        const response = await octokit.pulls.create({
          owner,
          repo,
          title,
          body,
          head,
          base,
          draft,
          maintainer_can_modify: maintainerCanModify
        });
        
        return {
          pullRequest: response.data
        };
      }
      
      case 'mergePullRequest': {
        const { owner, repo, pullNumber, commitTitle, commitMessage, mergeMethod = 'merge', sha } = params;
        
        const response = await octokit.pulls.merge({
          owner,
          repo,
          pull_number: pullNumber,
          commit_title: commitTitle,
          commit_message: commitMessage,
          merge_method: mergeMethod,
          sha
        });
        
        return {
          merged: response.data.merged,
          message: response.data.message
        };
      }
      
      case 'getCommits': {
        const { owner, repo, sha, path, author, since, until, page = 1, perPage = 30 } = params;
        
        const response = await octokit.repos.listCommits({
          owner,
          repo,
          sha,
          path,
          author,
          since,
          until,
          page,
          per_page: perPage
        });
        
        return {
          commits: response.data,
          totalCount: response.data.length,
          hasNextPage: response.data.length === perPage
        };
      }
      
      case 'getContents': {
        const { owner, repo, path, ref } = params;
        
        const response = await octokit.repos.getContent({
          owner,
          repo,
          path,
          ref
        });
        
        // Handle directory vs file
        if (Array.isArray(response.data)) {
          // Directory
          return {
            type: 'directory',
            contents: response.data
          };
        } else {
          // File
          let content = response.data.content;
          
          if (response.data.encoding === 'base64') {
            content = Buffer.from(content, 'base64').toString('utf8');
          }
          
          return {
            type: 'file',
            content,
            sha: response.data.sha,
            size: response.data.size,
            name: response.data.name,
            path: response.data.path,
            url: response.data.html_url
          };
        }
      }
      
      case 'updateContents': {
        const { owner, repo, path, message, content, sha, branch } = params;
        
        // Encode content to base64
        const contentBase64 = Buffer.from(content).toString('base64');
        
        const response = await octokit.repos.createOrUpdateFileContents({
          owner,
          repo,
          path,
          message,
          content: contentBase64,
          sha,
          branch
        });
        
        return {
          content: response.data.content,
          commit: response.data.commit
        };
      }
      
      case 'searchCode': {
        const { query, page = 1, perPage = 30 } = params;
        
        const response = await octokit.search.code({
          q: query,
          page,
          per_page: perPage
        });
        
        return {
          items: response.data.items,
          totalCount: response.data.total_count,
          hasNextPage: response.data.items.length === perPage
        };
      }
      
      case 'searchRepositories': {
        const { query, sort, order, page = 1, perPage = 30 } = params;
        
        const response = await octokit.search.repos({
          q: query,
          sort,
          order,
          page,
          per_page: perPage
        });
        
        return {
          items: response.data.items,
          totalCount: response.data.total_count,
          hasNextPage: response.data.items.length === perPage
        };
      }
      
      case 'getWorkflows': {
        const { owner, repo } = params;
        
        const response = await octokit.actions.listRepoWorkflows({
          owner,
          repo
        });
        
        return {
          workflows: response.data.workflows,
          totalCount: response.data.total_count
        };
      }
      
      case 'triggerWorkflow': {
        const { owner, repo, workflowId, ref, inputs } = params;
        
        const response = await octokit.actions.createWorkflowDispatch({
          owner,
          repo,
          workflow_id: workflowId,
          ref,
          inputs
        });
        
        return {
          success: response.status === 204
        };
      }
      
      default:
        throw new Error(`Command ${command} not implemented for GitHub API`);
    }
  }

  /**
   * Execute a command via GitHub CLI
   * @param {Object} connection - Connection object
   * @param {string} command - Command name
   * @param {Object} params - Command parameters
   * @returns {Promise<Object>} Command result
   * @private
   */
  async _executeCLICommand(connection, command, params) {
    // Map our commands to GitHub CLI commands
    let cliCommand = '';
    let cliArgs = [];
    let parseJson = true;
    
    switch (command) {
      case 'getRepositories': {
        const { visibility = 'all' } = params;
        cliCommand = 'gh repo list';
        cliArgs = [`--limit=${params.perPage || 30}`, `--json=name,description,url,visibility,isPrivate`, `--visibility=${visibility}`];
        break;
      }
      
      case 'getRepository': {
        const { owner, repo } = params;
        cliCommand = 'gh repo view';
        cliArgs = [`${owner}/${repo}`, '--json=name,description,url,visibility,isPrivate,defaultBranchRef,forkCount,stargazerCount'];
        break;
      }
      
      case 'createRepository': {
        const { name, description, isPrivate = false } = params;
        cliCommand = 'gh repo create';
        cliArgs = [name, `--description=${description || ''}`];
        
        if (isPrivate) {
          cliArgs.push('--private');
        } else {
          cliArgs.push('--public');
        }
        
        cliArgs.push('--json=name,description,url,visibility,isPrivate');
        break;
      }
      
      case 'cloneRepository': {
        const { repository, directory } = params;
        cliCommand = 'gh repo clone';
        cliArgs = [repository];
        
        if (directory) {
          cliArgs.push(directory);
        }
        
        parseJson = false;
        break;
      }
      
      case 'getIssues': {
        const { owner, repo, state = 'open' } = params;
        cliCommand = 'gh issue list';
        cliArgs = [`--repo=${owner}/${repo}`, `--state=${state}`, `--limit=${params.perPage || 30}`, '--json=number,title,state,author,createdAt,assignees,labels'];
        break;
      }
      
      case 'createIssue': {
        const { owner, repo, title, body } = params;
        cliCommand = 'gh issue create';
        cliArgs = [`--repo=${owner}/${repo}`, `--title=${title}`];
        
        if (body) {
          cliArgs.push(`--body=${body}`);
        }
        
        cliArgs.push('--json=number,title,url');
        break;
      }
      
      case 'getPullRequests': {
        const { owner, repo, state = 'open' } = params;
        cliCommand = 'gh pr list';
        cliArgs = [`--repo=${owner}/${repo}`, `--state=${state}`, `--limit=${params.perPage || 30}`, '--json=number,title,state,author,createdAt,assignees,labels'];
        break;
      }
      
      case 'createPullRequest': {
        const { owner, repo, title, body, head, base } = params;
        cliCommand = 'gh pr create';
        cliArgs = [`--repo=${owner}/${repo}`, `--title=${title}`];
        
        if (body) {
          cliArgs.push(`--body=${body}`);
        }
        
        if (head) {
          cliArgs.push(`--head=${head}`);
        }
        
        if (base) {
          cliArgs.push(`--base=${base}`);
        }
        
        cliArgs.push('--json=number,title,url');
        break;
      }
      
      default:
        throw new Error(`Command ${command} not implemented for GitHub CLI`);
    }
    
    // Execute the command
    return new Promise((resolve, reject) => {
      exec(cliCommand + ' ' + cliArgs.join(' '), (error, stdout, stderr) => {
        if (error) {
          reject(new Error(`Failed to execute GitHub CLI command: ${error.message}`));
          return;
        }
        
        if (parseJson) {
          try {
            const result = JSON.parse(stdout);
            resolve(result);
          } catch (parseError) {
            reject(new Error(`Failed to parse GitHub CLI output: ${parseError.message}`));
          }
        } else {
          resolve({ output: stdout.trim() });
        }
      });
    });
  }

  /**
   * Check if GitHub CLI is installed
   * @returns {Promise<string>} GitHub CLI version
   * @private
   */
  async _checkGitHubCLIInstallation() {
    return new Promise((resolve, reject) => {
      exec('gh --version', (error, stdout, stderr) => {
        if (error) {
          reject(new Error('GitHub CLI is not installed or not in PATH'));
          return;
        }
        
        resolve(stdout.trim());
      });
    });
  }

  /**
   * Install GitHub CLI
   * @returns {Promise<void>}
   * @private
   */
  async _installGitHubCLI() {
    const platform = process.platform;
    
    let installCommand = '';
    
    switch (platform) {
      case 'darwin':
        installCommand = 'brew install gh';
        break;
      case 'linux':
        // For Ubuntu/Debian
        installCommand = 'apt-key adv --keyserver keyserver.ubuntu.com --recv-key C99B11DEB97541F0 && apt-add-repository https://cli.github.com/packages && apt update && apt install gh';
        break;
      case 'win32':
        installCommand = 'winget install --id GitHub.cli';
        break;
      default:
        throw new Error(`Unsupported platform: ${platform}`);
    }
    
    return new Promise((resolve, reject) => {
      exec(installCommand, (error, stdout, stderr) => {
        if (error) {
          reject(new Error(`Failed to install GitHub CLI: ${error.message}`));
          return;
        }
        
        resolve();
      });
    });
  }

  /**
   * Get GitHub CLI authentication status
   * @returns {Promise<Object>} Authentication status
   * @private
   */
  async _getGitHubCLIAuthStatus() {
    return new Promise((resolve, reject) => {
      exec('gh auth status', (error, stdout, stderr) => {
        if (error) {
          // Not authenticated
          resolve({ authenticated: false });
          return;
        }
        
        // Parse output to get username
        const match = stdout.match(/Logged in to github\.com as (\S+)/);
        const user = match ? match[1] : null;
        
        resolve({
          authenticated: true,
          user
        });
      });
    });
  }

  /**
   * Configure GitHub CLI authentication
   * @param {string} token - GitHub personal access token
   * @returns {Promise<void>}
   * @private
   */
  async _configureGitHubCLIAuth(token) {
    return new Promise((resolve, reject) => {
      // Create a process to provide the token
      const process = spawn('gh', ['auth', 'login', '--with-token']);
      
      process.stdin.write(token);
      process.stdin.end();
      
      let stdout = '';
      let stderr = '';
      
      process.stdout.on('data', (data) => {
        stdout += data.toString();
      });
      
      process.stderr.on('data', (data) => {
        stderr += data.toString();
      });
      
      process.on('close', (code) => {
        if (code === 0) {
          resolve();
        } else {
          reject(new Error(`Failed to configure GitHub CLI authentication: ${stderr}`));
        }
      });
    });
  }

  /**
   * Process a GitHub webhook
   * @param {string} event - Webhook event type
   * @param {Object} payload - Webhook payload
   * @returns {Promise<void>}
   * @private
   */
  async _processWebhook(event, payload) {
    this.logger.debug(`Processing GitHub webhook: ${event}`);
    
    // Trigger event for all connections
    for (const connection of this.connections.values()) {
      this._triggerEvent(connection, `github:${event}`, payload);
    }
  }
}

module.exports = GitHubIntegration;
