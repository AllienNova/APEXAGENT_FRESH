// src/App.tsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from './components/theme/ThemeProvider';
import { NotificationProvider } from './components/notifications/NotificationSystem';
import { KeyboardProvider, KeyboardActionType } from './components/accessibility/KeyboardManager';
import { ResponsiveProvider } from './components/responsive/ResponsiveUtils';
import { PluginContext, DefaultPluginManager } from './plugins/PluginSystem';
import MainLayout from './components/layout/MainLayout';
import ConversationInterface from './components/conversation/ConversationInterface';
import DashboardInterface from './components/dashboard/DashboardInterface';
import PluginInterface from './components/plugins/PluginInterface';
import SettingsInterface from './components/settings/SettingsInterface';
import TroubleshootingInterface from './components/dr-tardis/TroubleshootingInterface';
import SystemActivityMonitor from './components/system-integration/SystemActivityMonitor';
import FileSystemNavigator from './components/system-integration/FileSystemNavigator';
import MultiLLMOrchestrator from './components/multi-llm/MultiLLMOrchestrator';

const App: React.FC = () => {
  // Initialize plugin manager
  const pluginManager = new DefaultPluginManager();
  
  // Keyboard shortcut handlers
  const keyboardHandlers: Record<KeyboardActionType, () => void> = {
    new_chat: () => console.log('New chat'),
    save_chat: () => console.log('Save chat'),
    clear_chat: () => console.log('Clear chat'),
    focus_input: () => console.log('Focus input'),
    toggle_sidebar: () => console.log('Toggle sidebar'),
    toggle_settings: () => console.log('Toggle settings'),
    toggle_theme: () => console.log('Toggle theme'),
    navigate_next_tab: () => console.log('Next tab'),
    navigate_prev_tab: () => console.log('Previous tab'),
    search: () => console.log('Search'),
    help: () => console.log('Help'),
    stop_generation: () => console.log('Stop generation'),
    regenerate: () => console.log('Regenerate'),
    copy_last_response: () => console.log('Copy response'),
    toggle_dr_tardis: () => console.log('Toggle Dr. Tardis')
  };
  
  return (
    <ThemeProvider defaultTheme="system" storageKey="apex-theme">
      <ResponsiveProvider>
        <NotificationProvider>
          <KeyboardProvider handlers={keyboardHandlers}>
            <PluginContext.Provider value={pluginManager}>
              <Router>
                <Routes>
                  <Route path="/" element={<MainLayout />}>
                    <Route index element={<DashboardInterface />} />
                    <Route path="chat/:chatId?" element={<ConversationInterface />} />
                    <Route path="plugins" element={<PluginInterface />} />
                    <Route path="settings" element={<SettingsInterface />} />
                    <Route path="dr-tardis" element={<TroubleshootingInterface />} />
                    <Route path="system-monitor" element={<SystemActivityMonitor />} />
                    <Route path="file-system" element={<FileSystemNavigator />} />
                    <Route path="llm-orchestration" element={<MultiLLMOrchestrator />} />
                  </Route>
                </Routes>
              </Router>
            </PluginContext.Provider>
          </KeyboardProvider>
        </NotificationProvider>
      </ResponsiveProvider>
    </ThemeProvider>
  );
};

export default App;
