# Expanded IDE Integration Guide for Aideon AI Lite

## Overview

Aideon AI Lite now provides comprehensive integration with major development environments, allowing users to leverage Aideon's powerful AI capabilities directly within their preferred IDE. This guide covers the setup, configuration, and usage of Aideon's IDE integrations for:

- Visual Studio Code
- JetBrains IDEs (IntelliJ IDEA, PyCharm, WebStorm, etc.)
- Eclipse
- Sublime Text
- GitHub

## Common Features Across All IDE Integrations

All IDE integrations provide the following core capabilities:

- **Code Generation**: Generate code snippets, functions, classes, or entire files based on natural language descriptions
- **Code Completion**: Context-aware code suggestions that understand your project structure
- **Code Refactoring**: Intelligent refactoring suggestions and automated implementations
- **Documentation Generation**: Create documentation for your code automatically
- **Error Analysis**: Identify and fix bugs or potential issues in your code
- **Project Navigation**: Quickly navigate complex codebases with AI assistance
- **Version Control Integration**: Seamless interaction with Git and other VCS systems
- **Testing Support**: Generate unit tests and test cases automatically

## Visual Studio Code Integration

### Installation

1. Open VS Code
2. Go to Extensions (Ctrl+Shift+X)
3. Search for "Aideon AI Lite"
4. Click Install
5. Restart VS Code when prompted

### Configuration

1. Open VS Code settings (File > Preferences > Settings)
2. Search for "Aideon"
3. Configure the following settings:
   - `aideon.core.path`: Path to Aideon AI Lite installation
   - `aideon.api.key`: Your Aideon API key (if using cloud features)
   - `aideon.models.local`: Enable/disable local model processing
   - `aideon.models.cloud`: Enable/disable cloud model processing

### Usage

- **Command Palette**: Access Aideon features via the command palette (Ctrl+Shift+P)
  - `Aideon: Generate Code`
  - `Aideon: Explain Code`
  - `Aideon: Refactor Code`
  - `Aideon: Generate Tests`
  - `Aideon: Optimize Code`

- **Context Menu**: Right-click in the editor to access Aideon features
  - Select code and right-click for context-specific options

- **Sidebar**: Use the Aideon sidebar for advanced features
  - Click the Aideon icon in the activity bar

### Example: Generating Code in VS Code

```javascript
// To generate a function, type a comment like this:
// @aideon Generate a function that calculates the Fibonacci sequence up to n terms

// Aideon will generate:
function fibonacci(n) {
  const sequence = [0, 1];
  
  if (n <= 0) {
    return [];
  } else if (n === 1) {
    return [0];
  }
  
  for (let i = 2; i < n; i++) {
    sequence.push(sequence[i-1] + sequence[i-2]);
  }
  
  return sequence;
}
```

## JetBrains IDEs Integration

### Supported IDEs

- IntelliJ IDEA
- PyCharm
- WebStorm
- PhpStorm
- RubyMine
- CLion
- GoLand
- DataGrip
- Rider
- Android Studio

### Installation

1. Open your JetBrains IDE
2. Go to Settings/Preferences > Plugins
3. Click "Browse repositories..."
4. Search for "Aideon AI Lite"
5. Click Install
6. Restart the IDE when prompted

### Configuration

1. Go to Settings/Preferences > Tools > Aideon AI Lite
2. Configure the following settings:
   - Core Settings: Path to Aideon AI Lite installation
   - API Settings: Your Aideon API key (if using cloud features)
   - Model Settings: Configure local and cloud model usage
   - Performance Settings: Adjust resource allocation

### Usage

- **Tool Window**: Access the Aideon tool window via View > Tool Windows > Aideon
- **Actions Menu**: Use Aideon actions via the Code menu or right-click context menu
- **Keyboard Shortcuts**:
  - Generate Code: Alt+A, G
  - Explain Code: Alt+A, E
  - Refactor Code: Alt+A, R
  - Generate Tests: Alt+A, T
  - Optimize Code: Alt+A, O

### Example: Refactoring Code in JetBrains IDEs

1. Select the code you want to refactor
2. Press Alt+A, R or right-click and select "Aideon: Refactor Code"
3. Choose the type of refactoring you want to perform
4. Review the suggested changes in the diff viewer
5. Apply the changes

## Eclipse Integration

### Installation

1. Open Eclipse
2. Go to Help > Eclipse Marketplace
3. Search for "Aideon AI Lite"
4. Click Install
5. Follow the installation wizard
6. Restart Eclipse when prompted

### Configuration

1. Go to Window > Preferences > Aideon AI Lite
2. Configure the following settings:
   - Core Settings: Path to Aideon AI Lite installation
   - API Settings: Your Aideon API key (if using cloud features)
   - Model Settings: Configure local and cloud model usage
   - Project Settings: Configure per-project settings

### Usage

- **Views**: Access Aideon views via Window > Show View > Aideon
- **Context Menu**: Right-click in the editor or project explorer for Aideon options
- **Main Menu**: Use the Aideon menu in the main menu bar

### Example: Generating Tests in Eclipse

1. Right-click on a Java class in the Project Explorer
2. Select "Aideon > Generate Tests"
3. Configure test generation options in the dialog
4. Click "Generate"
5. Review and save the generated tests

## Sublime Text Integration

### Installation

1. Open Sublime Text
2. Open the Command Palette (Ctrl+Shift+P)
3. Select "Package Control: Install Package"
4. Search for "Aideon AI Lite"
5. Press Enter to install

### Configuration

1. Go to Preferences > Package Settings > Aideon AI Lite > Settings
2. Configure the following settings:
```json
{
  "aideon_core_path": "/path/to/aideon",
  "api_key": "your_api_key",
  "use_local_models": true,
  "use_cloud_models": true,
  "auto_connect": true
}
```

### Usage

- **Command Palette**: Access Aideon features via the command palette (Ctrl+Shift+P)
  - `Aideon: Generate Code`
  - `Aideon: Explain Selection`
  - `Aideon: Refactor Selection`
  - `Aideon: Generate Tests`

- **Context Menu**: Right-click in the editor for Aideon options
- **Key Bindings**: Configure custom key bindings in the Aideon settings

### Example: Explaining Code in Sublime Text

1. Select the code you want to understand
2. Open the Command Palette (Ctrl+Shift+P)
3. Type "Aideon: Explain Selection"
4. Press Enter
5. View the explanation in the output panel

## GitHub Integration

### Setup

1. Install the Aideon AI Lite GitHub App from the GitHub Marketplace
2. Authorize the app for your repositories
3. Configure the integration settings in your repository

### Features

- **Pull Request Reviews**: Automated code reviews on pull requests
- **Issue Management**: AI-powered issue triage and suggestions
- **Code Quality Checks**: Automated quality checks on commits
- **Documentation Updates**: Automated documentation updates
- **Workflow Automation**: Custom GitHub Actions integration

### Example: Automated PR Reviews

When a pull request is opened or updated, Aideon will:

1. Analyze the changes
2. Provide code quality feedback
3. Suggest improvements
4. Check for potential bugs or security issues
5. Comment directly on the PR with its findings

## Advanced Integration Features

### Cross-IDE Synchronization

Aideon AI Lite can synchronize your settings, preferences, and context across different IDEs:

1. Enable synchronization in Aideon settings
2. Sign in with your Aideon account in each IDE
3. Your AI context and preferences will be synchronized automatically

### Custom Tool Integration

Extend Aideon's IDE integration with your own custom tools:

1. Create a custom tool definition in `~/.aideon/custom_tools.json`
2. Implement the tool interface as specified in the documentation
3. Restart your IDE
4. Your custom tool will appear in the Aideon menu

### Multi-Language Support

Aideon IDE integrations support all major programming languages:

- JavaScript/TypeScript
- Python
- Java
- C/C++
- C#
- Go
- Ruby
- PHP
- Swift
- Kotlin
- Rust
- And many more

## Troubleshooting

### Connection Issues

If Aideon fails to connect to your IDE:

1. Check that Aideon AI Lite is running
2. Verify the port settings in your IDE configuration
3. Check firewall settings
4. Restart both Aideon and your IDE

### Plugin Conflicts

If you experience conflicts with other plugins:

1. Disable other AI-related plugins temporarily
2. Check the Aideon logs for conflict information
3. Update to the latest version of Aideon and your IDE

### Performance Issues

If you experience performance issues:

1. Adjust the resource allocation in Aideon settings
2. Consider using local models for faster response times
3. Disable features you don't use regularly

## Best Practices

1. **Start Small**: Begin with code generation and explanation features
2. **Customize Your Workflow**: Configure Aideon to match your development style
3. **Use Context-Aware Features**: Let Aideon learn from your codebase for better suggestions
4. **Combine with Other Tools**: Aideon works well alongside other development tools
5. **Provide Feedback**: Use the feedback mechanism to improve Aideon's suggestions

## Future Enhancements

The Aideon IDE integration roadmap includes:

- Support for additional IDEs and editors
- Enhanced real-time collaboration features
- Deeper integration with build systems and CI/CD pipelines
- Advanced code visualization tools
- Custom model fine-tuning for your specific codebase

## Support and Resources

- Documentation: [https://docs.aideon.ai/ide-integration](https://docs.aideon.ai/ide-integration)
- Community Forum: [https://community.aideon.ai/ide-integration](https://community.aideon.ai/ide-integration)
- Issue Tracker: [https://github.com/aideon/ide-integration/issues](https://github.com/aideon/ide-integration/issues)
- Video Tutorials: [https://learn.aideon.ai/ide-integration](https://learn.aideon.ai/ide-integration)
