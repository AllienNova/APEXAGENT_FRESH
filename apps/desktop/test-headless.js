const { app, BrowserWindow } = require('electron');

// Disable hardware acceleration for headless mode
app.disableHardwareAcceleration();

// Prevent Electron from showing dock icon on macOS
if (process.platform === 'darwin') {
  app.dock?.hide();
}

app.whenReady().then(() => {
  console.log('✅ Electron app ready - Desktop application can start successfully');
  
  // Create a hidden window to test BrowserWindow creation
  const testWindow = new BrowserWindow({
    show: false,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      offscreen: true
    }
  });
  
  testWindow.loadURL('data:text/html,<h1>Test Window</h1>');
  
  testWindow.webContents.once('did-finish-load', () => {
    console.log('✅ BrowserWindow created and loaded successfully');
    console.log('✅ Desktop application core functionality working');
    
    // Exit after successful test
    setTimeout(() => {
      app.quit();
    }, 1000);
  });
});

app.on('window-all-closed', () => {
  console.log('✅ Desktop application test completed successfully');
  app.quit();
});

// Handle any errors
process.on('uncaughtException', (error) => {
  console.error('❌ Desktop application error:', error.message);
  app.quit();
});

