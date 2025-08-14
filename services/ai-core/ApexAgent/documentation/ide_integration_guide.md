# IDE Integration Guide for Aideon AI Lite

This document provides comprehensive documentation on how to use Aideon AI Lite's IDE integration capabilities, allowing seamless interaction with popular development environments including Visual Studio Code, Cursor, and GitHub.

## Overview

Aideon AI Lite offers powerful integration with modern development environments, enabling AI-assisted coding, project management, and version control directly within your preferred IDE. These integrations enhance developer productivity by bringing Aideon's capabilities directly into your workflow.

## Supported IDEs and Platforms

Aideon AI Lite currently supports the following development environments:

1. **Visual Studio Code** - Microsoft's popular code editor
2. **Cursor** - AI-enhanced code editor built for pair programming
3. **GitHub** - Web-based version control and collaboration platform

## Architecture

The IDE integration system is built on a modular architecture:

- **IDEIntegrationManager** - Core manager that handles registration, discovery, and access to all IDE integrations
- **BaseIDEIntegration** - Abstract base class that defines the common interface for all IDE integrations
- **Specific Integration Modules** - Concrete implementations for each supported IDE/platform

## Setup Instructions

### Prerequisites

- Aideon AI Lite core system installed and configured
- Appropriate IDE/platform installed on your system
- Required permissions for extension installation and API access

### Installation

#### Visual Studio Code Integration

1. Install the Aideon AI Lite extension for VS Code:

```bash
# From the Aideon AI Lite root directory
npm run install-vscode-extension
```

2. Configure the extension in VS Code:
   - Open VS Code
   - Go to Extensions (Ctrl+Shift+X)
   - Find "Aideon AI Lite" in the installed extensions
   - Click on the gear icon and select "Extension Settings"
   - Set your Aideon API key and other configuration options

#### Cursor Integration

1. Install the Aideon AI Lite plugin for Cursor:

```bash
# From the Aideon AI Lite root directory
npm run install-cursor-plugin
```

2. Configure the plugin in Cursor:
   - Open Cursor
   - Navigate to Settings > Plugins
   - Find "Aideon AI Lite" and click "Configure"
   - Enter your Aideon API key and adjust settings as needed

#### GitHub Integration

1. Set up the GitHub integration:

```bash
# From the Aideon AI Lite root directory
node src/core/ide/setup-github-integration.js
```

2. Follow the prompts to:
   - Authenticate with GitHub
   - Select repositories to enable integration with
   - Configure webhook settings (for real-time event handling)

## Usage Guide

### Visual Studio Code Integration

#### AI-Assisted Coding

1. **Code Generation**
   - Select a portion of code or place cursor where you want to generate code
   - Press `Ctrl+Shift+A` or right-click and select "Aideon: Generate Code"
   - Enter a natural language description of what you want to create
   - Aideon will generate the code and insert it at the cursor position

2. **Code Explanation**
   - Select code you want explained
   - Press `Ctrl+Shift+E` or right-click and select "Aideon: Explain Code"
   - View the explanation in the Aideon panel

3. **Code Refactoring**
   - Select code to refactor
   - Press `Ctrl+Shift+R` or right-click and select "Aideon: Refactor Code"
   - Choose the type of refactoring (performance, readability, etc.)
   - Review and accept the suggested changes

#### Project Management

1. **Task Management**
   - Open the Aideon sidebar (`Ctrl+Shift+A`)
   - Click on "Tasks" to view project tasks
   - Create, assign, and track tasks directly from VS Code

2. **Documentation Generation**
   - Select a function, class, or module
   - Right-click and select "Aideon: Generate Documentation"
   - Choose documentation style (JSDoc, DocString, etc.)
   - Documentation will be inserted automatically

#### Debugging Assistance

1. **Error Analysis**
   - When encountering an error, click on the Aideon icon in the error message
   - Aideon will analyze the error and suggest potential fixes
   - Apply the suggested fix directly or use it as guidance

2. **Test Generation**
   - Right-click on a function and select "Aideon: Generate Tests"
   - Aideon will create comprehensive test cases for the selected function
   - Tests will be added to your test directory following project conventions

### Cursor Integration

#### AI-Enhanced Editing

1. **Pair Programming Mode**
   - Enable Aideon pair programming with `/aideon pair`
   - Aideon will actively suggest completions and improvements as you code
   - Accept suggestions with `Tab` or dismiss with `Esc`

2. **Code Transformation**
   - Select code and use `/aideon transform` followed by a description
   - Example: `/aideon transform convert this to async/await syntax`
   - Review and accept the transformation

3. **Context-Aware Assistance**
   - Aideon maintains awareness of your entire project structure
   - Ask project-specific questions with `/aideon ask`
   - Example: `/aideon ask how does the authentication system work in this project?`

#### Advanced Features

1. **Multi-File Operations**
   - Use `/aideon multi-file` to perform operations across multiple files
   - Example: `/aideon multi-file update all API endpoints to use the new error handling pattern`

2. **Architecture Visualization**
   - Generate project architecture diagrams with `/aideon visualize architecture`
   - The diagram will open in a new tab with interactive elements

3. **Performance Profiling**
   - Analyze code performance with `/aideon profile`
   - Receive suggestions for performance improvements based on static analysis

### GitHub Integration

#### Repository Management

1. **Automated Code Reviews**
   - Aideon automatically reviews pull requests when configured
   - View AI-generated code review comments directly in the PR
   - Configure review focus in the Aideon settings (security, performance, style, etc.)

2. **Issue Management**
   - Connect issues to code with `/aideon link-issue #123`
   - Generate issue summaries with `/aideon summarize-issue`
   - Get AI-suggested fixes for issues with `/aideon suggest-fix #123`

3. **Documentation Maintenance**
   - Keep documentation in sync with code changes
   - Use `/aideon update-docs` to automatically update affected documentation
   - Generate new documentation for new features with `/aideon document-feature`

#### Collaboration Features

1. **PR Description Generation**
   - Generate comprehensive PR descriptions with `/aideon pr-description`
   - Includes summary of changes, affected components, and potential impacts

2. **Code Explanation for Reviewers**
   - Help reviewers understand complex changes with `/aideon explain-for-review`
   - Generates in-line comments explaining the rationale behind changes

3. **Merge Conflict Resolution**
   - Get assistance with merge conflicts using `/aideon resolve-conflict`
   - Aideon analyzes both versions and suggests optimal resolution strategies

## API Reference

### IDEIntegrationManager API

```javascript
// Get an instance of the integration manager
const integrationManager = core.getIDEIntegrationManager();

// Get all available integrations
const availableIntegrations = integrationManager.getAllIntegrations();

// Get a specific integration
const vscodeIntegration = integrationManager.getIntegration('vscode');

// Register a custom integration
integrationManager.registerIntegration(myCustomIntegration);

// Check if a specific integration is available
const isVSCodeAvailable = integrationManager.hasIntegration('vscode');

// Execute a command across all integrations
integrationManager.broadcastCommand('refresh-views');
```

### BaseIDEIntegration API

All specific IDE integrations implement these common methods:

```javascript
// Initialize the integration
await integration.initialize();

// Check if the integration is properly connected
const isConnected = integration.isConnected();

// Execute an IDE-specific command
await integration.executeCommand('command-name', parameters);

// Get information about the current file/project
const fileInfo = await integration.getCurrentFileInfo();
const projectInfo = await integration.getProjectInfo();

// Subscribe to IDE events
integration.subscribeToEvent('file-changed', callback);

// Clean up resources when done
await integration.dispose();
```

### VS Code Integration Specific API

```javascript
// Get the VS Code extension API instance
const vscode = vscodeIntegration.getVSCodeAPI();

// Insert text at current cursor position
await vscodeIntegration.insertTextAtCursor('text to insert');

// Get the selected text
const selectedText = await vscodeIntegration.getSelectedText();

// Open a file in the editor
await vscodeIntegration.openFile('/path/to/file.js');

// Show a notification in VS Code
vscodeIntegration.showNotification('info', 'Operation completed successfully');

// Create or update a custom view
await vscodeIntegration.updateCustomView('aideon-tasks', taskData);
```

### Cursor Integration Specific API

```javascript
// Get the Cursor API instance
const cursor = cursorIntegration.getCursorAPI();

// Enable AI pair programming mode
await cursorIntegration.enablePairProgramming(options);

// Get project-wide context for AI operations
const projectContext = await cursorIntegration.getProjectContext();

// Apply a transformation to selected code
await cursorIntegration.transformCode(selectedCode, transformationDescription);

// Generate completions with project context
const completions = await cursorIntegration.generateCompletions(prefix, options);
```

### GitHub Integration Specific API

```javascript
// Get the GitHub API client
const github = githubIntegration.getGitHubClient();

// Get information about the current repository
const repoInfo = await githubIntegration.getCurrentRepository();

// Create a new pull request
const pr = await githubIntegration.createPullRequest(title, description, base, head);

// Add a comment to a pull request
await githubIntegration.addPRComment(prNumber, comment);

// Get the list of issues for the current repository
const issues = await githubIntegration.getRepositoryIssues(filters);

// Create a new issue
const issue = await githubIntegration.createIssue(title, body, labels);
```

## Configuration Reference

### Common Configuration Options

These options apply to all IDE integrations:

```javascript
{
  "enabled": true,                    // Enable/disable the integration
  "apiKey": "your-aideon-api-key",    // Your Aideon API key
  "logLevel": "info",                 // Logging level (debug, info, warn, error)
  "features": {                       // Enable/disable specific features
    "codeGeneration": true,
    "codeExplanation": true,
    "codeRefactoring": true,
    "testGeneration": true,
    "documentationGeneration": true
  },
  "modelPreferences": {               // AI model preferences
    "preferredModel": "default",      // Model to use for operations
    "temperature": 0.7,               // Creativity level (0.0-1.0)
    "maxTokens": 2048                 // Maximum response length
  }
}
```

### VS Code Specific Configuration

```javascript
{
  "keybindings": {
    "generateCode": "ctrl+shift+a",
    "explainCode": "ctrl+shift+e",
    "refactorCode": "ctrl+shift+r"
  },
  "sidebar": {
    "defaultView": "tasks",
    "showOnStartup": true
  },
  "inlineCompletions": {
    "enabled": true,
    "triggerCharacters": [".", "(", " "]
  }
}
```

### Cursor Specific Configuration

```javascript
{
  "pairProgramming": {
    "enabled": true,
    "suggestionFrequency": "medium",
    "focusAreas": ["logic", "performance", "security"]
  },
  "contextWindow": {
    "includeOpenFiles": true,
    "includeProjectStructure": true,
    "maxFilesToInclude": 10
  },
  "customCommands": [
    {
      "name": "generateComponent",
      "description": "Generate a new React component",
      "template": "Create a React functional component named {name} that {description}"
    }
  ]
}
```

### GitHub Specific Configuration

```javascript
{
  "authentication": {
    "method": "oauth",           // oauth or personal_access_token
    "scope": ["repo", "user"]    // Required OAuth scopes
  },
  "repositories": [
    {
      "owner": "username",
      "name": "repo-name",
      "features": {
        "automaticCodeReviews": true,
        "issueManagement": true,
        "documentationUpdates": true
      }
    }
  ],
  "codeReviews": {
    "enabled": true,
    "focusAreas": ["security", "performance", "style"],
    "maxCommentsPerReview": 10,
    "commentStyle": "constructive"
  },
  "webhooks": {
    "enabled": true,
    "events": ["push", "pull_request", "issues"]
  }
}
```

## Troubleshooting

### Common Issues

#### Connection Problems

**Issue**: IDE integration fails to connect to Aideon AI Lite.
**Solution**:
1. Verify that the Aideon AI Lite core service is running
2. Check your API key configuration
3. Ensure network connectivity between the IDE and Aideon service
4. Check logs at `~/.aideon/logs/ide-integration.log`

#### Authentication Failures

**Issue**: GitHub integration authentication fails.
**Solution**:
1. Verify your GitHub credentials
2. Check that you have the required permissions for the repositories
3. For OAuth issues, try regenerating the token with `node src/core/ide/reset-github-auth.js`
4. Ensure your token has the necessary scopes (repo, user)

#### Extension Loading Errors

**Issue**: VS Code extension fails to load.
**Solution**:
1. Check the VS Code extension host logs (Help > Toggle Developer Tools)
2. Verify VS Code version compatibility (requires VS Code 1.60+)
3. Try reinstalling the extension with `npm run reinstall-vscode-extension`
4. Check for conflicts with other AI coding extensions

### Logging and Diagnostics

To enable detailed logging for troubleshooting:

1. Set the log level to "debug" in the configuration
2. Check the log files:
   - VS Code: `~/.aideon/logs/vscode-integration.log`
   - Cursor: `~/.aideon/logs/cursor-integration.log`
   - GitHub: `~/.aideon/logs/github-integration.log`
   - General: `~/.aideon/logs/ide-integration.log`

3. Generate a diagnostic report:
```bash
node src/core/ide/generate-diagnostic-report.js
```

This will create a comprehensive report at `~/.aideon/diagnostics/ide-integration-report.json`

## Advanced Topics

### Creating Custom IDE Integrations

You can extend Aideon AI Lite to support additional IDEs by creating a custom integration:

1. Create a new class that extends `BaseIDEIntegration`:

```javascript
const { BaseIDEIntegration } = require('../BaseIDEIntegration');

class MyCustomIDEIntegration extends BaseIDEIntegration {
  constructor(core) {
    super(core, 'my-custom-ide');
    this.logger = core.logManager.getLogger('ide:my-custom-ide');
  }
  
  async initialize() {
    // Implementation specific to your IDE
    this.logger.info('Initializing custom IDE integration');
    // Connect to IDE's extension API, etc.
    return true;
  }
  
  // Implement other required methods...
}

module.exports = { MyCustomIDEIntegration };
```

2. Register your custom integration with the `IDEIntegrationManager`:

```javascript
const { MyCustomIDEIntegration } = require('./integrations/MyCustomIDEIntegration');

// In your application initialization code:
const customIntegration = new MyCustomIDEIntegration(core);
core.getIDEIntegrationManager().registerIntegration(customIntegration);
```

### Extending Existing Integrations

You can extend the functionality of existing integrations:

```javascript
const { VSCodeIntegration } = require('../integrations/VSCodeIntegration');

class EnhancedVSCodeIntegration extends VSCodeIntegration {
  constructor(core) {
    super(core);
    this.additionalFeatures = new Map();
  }
  
  registerAdditionalFeature(name, implementation) {
    this.additionalFeatures.set(name, implementation);
  }
  
  async executeCommand(command, parameters) {
    if (this.additionalFeatures.has(command)) {
      return this.additionalFeatures.get(command)(parameters);
    }
    return super.executeCommand(command, parameters);
  }
}
```

### Integration with CI/CD Pipelines

Aideon AI Lite's IDE integrations can be incorporated into CI/CD pipelines:

1. **GitHub Actions Integration**:
```yaml
# .github/workflows/aideon-code-review.yml
name: Aideon AI Code Review
on:
  pull_request:
    types: [opened, synchronize]
jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Aideon AI Lite
        uses: aideon/setup-action@v1
        with:
          api-key: ${{ secrets.AIDEON_API_KEY }}
      - name: Run Aideon Code Review
        uses: aideon/code-review-action@v1
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          focus-areas: "security,performance,best-practices"
```

2. **Jenkins Pipeline Integration**:
```groovy
pipeline {
    agent any
    stages {
        stage('Aideon Code Analysis') {
            steps {
                sh 'npm install -g @aideon/cli'
                sh 'aideon analyze --repo-path . --output-format junit > aideon-analysis.xml'
                junit 'aideon-analysis.xml'
            }
        }
    }
}
```

## Best Practices

### Optimizing IDE Integration Performance

1. **Limit Context Window Size**:
   - Configure the maximum number of files to include in context
   - Focus on relevant files for better performance

2. **Use Appropriate Trigger Points**:
   - Configure when AI assistance is triggered to balance helpfulness with performance
   - Consider using explicit triggers rather than constant background analysis

3. **Cache Results Where Appropriate**:
   - For operations like code explanations that may be repeated
   - Clear cache when files are modified

### Security Considerations

1. **API Key Management**:
   - Store API keys securely, never commit them to version control
   - Use environment variables or secure credential storage

2. **Code Data Privacy**:
   - Configure which files/directories should be excluded from AI processing
   - Be aware of sensitive information in code comments

3. **Permission Scopes**:
   - Limit GitHub integration permissions to only what's necessary
   - Review webhook configurations regularly

### Team Collaboration

1. **Shared Configurations**:
   - Store team-wide IDE integration configurations in version control
   - Document custom commands and workflows

2. **Consistent Conventions**:
   - Establish team guidelines for AI-assisted code contributions
   - Define when and how to use AI suggestions in code reviews

3. **Feedback Loop**:
   - Collect team feedback on AI suggestions
   - Use feedback to refine integration configurations

## Future Roadmap

The Aideon AI Lite IDE integration system will continue to evolve with these planned enhancements:

1. **Additional IDE Support**:
   - JetBrains IDEs (IntelliJ, PyCharm, WebStorm)
   - Eclipse
   - Sublime Text

2. **Enhanced Collaboration Features**:
   - Real-time collaborative coding with AI assistance
   - Team knowledge sharing through AI

3. **Advanced Code Understanding**:
   - Full repository semantic understanding
   - Cross-repository knowledge integration
   - Custom domain-specific knowledge integration

4. **Expanded CI/CD Integration**:
   - More comprehensive pipeline integration
   - Automated code optimization suggestions
   - Security vulnerability prevention

## Conclusion

Aideon AI Lite's IDE integration capabilities transform your development environment into an AI-enhanced workspace, significantly boosting productivity and code quality. By bringing Aideon's powerful tools directly into your preferred IDE, you can focus on solving problems while the AI handles routine tasks and provides intelligent assistance.

For additional support or to report issues, please contact the Aideon AI support team or open an issue in the GitHub repository.
