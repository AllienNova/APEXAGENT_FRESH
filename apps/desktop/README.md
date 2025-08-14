# Aideon AI Lite Desktop Application

The desktop application component of the Aideon AI Lite hybrid system, built with Electron to provide native desktop integration with local processing capabilities.

## Overview

This desktop application serves as the local component of the hybrid Aideon AI Lite system, providing:

- **Local Processing**: Run AI models locally for privacy and offline capability
- **Native Integration**: Deep integration with the operating system
- **Hybrid Architecture**: Seamless switching between local and cloud processing
- **Offline Mode**: Full functionality without internet connectivity
- **File System Access**: Direct access to local files and projects
- **System Integration**: Native notifications, menu bar, and system tray

## Architecture

### Hybrid System Design

```
┌─────────────────────────────────────────────────────────────┐
│                    Desktop Application                       │
├─────────────────────────────────────────────────────────────┤
│  Main Process (Node.js)     │  Renderer Process (React)     │
│  ├─ Local API Server        │  ├─ Web Frontend              │
│  ├─ File System Access      │  ├─ UI Components             │
│  ├─ System Integration      │  ├─ State Management          │
│  └─ Process Management      │  └─ API Communication         │
├─────────────────────────────────────────────────────────────┤
│                    Preload Script                           │
│  ├─ Secure IPC Bridge       │  ├─ API Exposure              │
│  ├─ Context Isolation       │  └─ Security Enforcement      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Local Services                           │
├─────────────────────────────────────────────────────────────┤
│  Local API Server          │  Cloud API Gateway            │
│  ├─ AI Model Execution     │  ├─ Remote Model Access       │
│  ├─ Data Processing        │  ├─ Cloud Services            │
│  ├─ File Operations        │  ├─ Synchronization           │
│  └─ System Monitoring      │  └─ Backup & Recovery         │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

1. **Main Process** (`src/main/main.js`)
   - Electron main process
   - Window management
   - Local API server startup
   - System integration
   - Security enforcement

2. **Preload Script** (`src/preload/preload.js`)
   - Secure IPC communication
   - API exposure to renderer
   - Context isolation
   - Security boundaries

3. **Renderer Process**
   - React web application (shared with web version)
   - Desktop-specific adaptations
   - Local API communication
   - File system integration

## Features

### Local Processing
- **AI Model Execution**: Run AI models locally using CPU/GPU
- **Offline Capability**: Full functionality without internet
- **Privacy Protection**: Data never leaves the local machine
- **Performance Optimization**: Optimized for local hardware

### System Integration
- **Native Menus**: Platform-specific menu bars and context menus
- **File System Access**: Direct file operations and project management
- **System Notifications**: Native notification system integration
- **Auto-start**: Optional system startup integration
- **System Tray**: Background operation with system tray icon

### Hybrid Capabilities
- **Intelligent Routing**: Automatic local/cloud processing decisions
- **Seamless Fallback**: Graceful degradation when local resources unavailable
- **Sync Management**: Synchronization between local and cloud data
- **Resource Monitoring**: Real-time monitoring of local resources

### Security Features
- **Context Isolation**: Secure separation between main and renderer processes
- **IPC Security**: Validated inter-process communication
- **File System Sandboxing**: Controlled file system access
- **Auto-updates**: Secure automatic updates with signature verification

## Development

### Prerequisites
- Node.js 18+
- npm 8+
- Python 3.8+ (for native modules)
- Platform-specific build tools

### Setup
```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Package for distribution
npm run dist
```

### Development Scripts
- `npm start` - Start the desktop app
- `npm run dev` - Development mode with hot reload
- `npm run build` - Build for production
- `npm run pack` - Package without distribution
- `npm run dist` - Build and package for distribution
- `npm run dist:win` - Build for Windows
- `npm run dist:mac` - Build for macOS
- `npm run dist:linux` - Build for Linux

### Project Structure
```
apps/desktop/
├── src/
│   ├── main/           # Main process code
│   │   └── main.js     # Main application entry
│   ├── preload/        # Preload scripts
│   │   └── preload.js  # IPC bridge
│   └── renderer/       # Renderer process (if needed)
├── assets/             # Application assets
│   ├── icons/          # Platform-specific icons
│   └── images/         # Application images
├── build/              # Build configuration
├── dist/               # Distribution files
├── package.json        # Dependencies and scripts
├── electron-builder.yml # Build configuration
└── README.md           # This file
```

## Configuration

### Application Settings
Settings are stored securely using `electron-store`:

```javascript
// Default configuration
{
  windowBounds: { width: 1400, height: 900 },
  theme: 'system',
  apiEndpoint: 'http://localhost:3001',
  localProcessing: true,
  offlineMode: false,
  autoUpdates: true,
  telemetry: true
}
```

### Environment Variables
- `NODE_ENV` - Development/production mode
- `DESKTOP_MODE` - Enables desktop-specific features
- `DATA_DIR` - Local data directory
- `API_PORT` - Local API server port

## Building and Distribution

### Build Configuration
The application uses `electron-builder` for packaging and distribution. Configuration is in `electron-builder.yml`.

### Supported Platforms
- **Windows**: NSIS installer, portable executable
- **macOS**: DMG installer, Mac App Store
- **Linux**: AppImage, Debian package, RPM package

### Code Signing
Production builds should be code signed:
- Windows: Authenticode certificate
- macOS: Apple Developer certificate
- Linux: GPG signing

### Auto-updates
The application supports automatic updates using `electron-updater`:
- Secure update delivery
- Background downloads
- User-controlled installation
- Rollback capability

## API Integration

### Local API Server
The desktop app starts a local API server that provides:
- AI model execution
- File system operations
- System information
- Process management

### Hybrid API Routing
```javascript
// Example: Intelligent routing
const result = await hybridAPI.process({
  task: 'text-generation',
  preferLocal: true,
  fallbackToCloud: true,
  data: inputData
});
```

### IPC Communication
Secure communication between main and renderer processes:
```javascript
// Renderer process
const result = await window.electronAPI.store.get('setting', 'default');
await window.electronAPI.store.set('setting', 'value');

// File operations
const files = await window.electronAPI.dialog.showOpenDialog({
  properties: ['openFile', 'multiSelections'],
  filters: [{ name: 'Documents', extensions: ['txt', 'md'] }]
});
```

## Security

### Security Model
- **Process Isolation**: Main and renderer processes are isolated
- **Context Isolation**: Renderer context is isolated from Node.js
- **IPC Validation**: All IPC messages are validated
- **File System Sandboxing**: Controlled file system access
- **Network Security**: HTTPS-only external communications

### Best Practices
- Never expose Node.js APIs to renderer
- Validate all IPC inputs
- Use secure storage for sensitive data
- Implement proper error handling
- Regular security audits

## Troubleshooting

### Common Issues

1. **App won't start**
   - Check Node.js version (18+)
   - Verify all dependencies installed
   - Check for port conflicts (3001)

2. **Local API server fails**
   - Verify API server files exist
   - Check port availability
   - Review server logs

3. **Build failures**
   - Clear node_modules and reinstall
   - Check platform-specific build tools
   - Verify code signing certificates

### Debug Mode
Enable debug mode for detailed logging:
```bash
DEBUG=* npm start
```

### Logs Location
- Windows: `%APPDATA%/aideon-ai-lite/logs/`
- macOS: `~/Library/Logs/aideon-ai-lite/`
- Linux: `~/.config/aideon-ai-lite/logs/`

## Contributing

1. Follow the existing code style
2. Add tests for new features
3. Update documentation
4. Test on all supported platforms
5. Submit pull request with detailed description

## License

MIT License - see LICENSE file for details.

## Support

- Documentation: https://docs.aideonai.com
- Issues: https://github.com/AllienNova/APEXAGENT_FRESH/issues
- Support: support@aideonai.com

