// src/components/settings/SettingsInterface.tsx
import React, { useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Switch } from '../ui/switch';
import { Slider } from '../ui/slider';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Input } from '../ui/input';
import { Button } from '../ui/button';
import { 
  User, 
  Monitor, 
  HardDrive, 
  Shield, 
  Bell, 
  Keyboard, 
  Palette, 
  Globe, 
  Cpu, 
  Save
} from 'lucide-react';

const SettingsInterface: React.FC = () => {
  // Account settings
  const [username, setUsername] = useState('John Doe');
  const [email, setEmail] = useState('john.doe@example.com');
  
  // Appearance settings
  const [theme, setTheme] = useState('system');
  const [fontSize, setFontSize] = useState(14);
  const [density, setDensity] = useState('comfortable');
  const [accentColor, setAccentColor] = useState('blue');
  
  // Privacy settings
  const [telemetry, setTelemetry] = useState(true);
  const [crashReports, setCrashReports] = useState(true);
  const [localStorageOnly, setLocalStorageOnly] = useState(true);
  
  // Notification settings
  const [notifications, setNotifications] = useState(true);
  const [notificationSound, setNotificationSound] = useState(true);
  const [taskCompletionNotifications, setTaskCompletionNotifications] = useState(true);
  const [systemNotifications, setSystemNotifications] = useState(true);
  
  // Performance settings
  const [maxConcurrentTasks, setMaxConcurrentTasks] = useState(3);
  const [memoryLimit, setMemoryLimit] = useState(4096);
  const [diskSpaceLimit, setDiskSpaceLimit] = useState(10240);
  
  // LLM settings
  const [defaultModel, setDefaultModel] = useState('gpt-4');
  const [apiProvider, setApiProvider] = useState('openai');
  const [useLocalModels, setUseLocalModels] = useState(false);
  
  // Keyboard shortcuts
  const [enableShortcuts, setEnableShortcuts] = useState(true);
  const [customShortcuts, setCustomShortcuts] = useState({
    newChat: 'Ctrl+N',
    saveChat: 'Ctrl+S',
    clearChat: 'Ctrl+L',
    focusInput: 'Ctrl+/',
    toggleSidebar: 'Ctrl+B',
    toggleSettings: 'Ctrl+,',
  });
  
  // System settings
  const [startOnBoot, setStartOnBoot] = useState(false);
  const [checkForUpdates, setCheckForUpdates] = useState(true);
  const [autoUpdate, setAutoUpdate] = useState(true);
  
  // Accessibility settings
  const [highContrast, setHighContrast] = useState(false);
  const [reducedMotion, setReducedMotion] = useState(false);
  const [screenReader, setScreenReader] = useState(false);
  
  const handleSaveSettings = () => {
    // Implementation would save all settings
    console.log('Settings saved');
  };
  
  return (
    <div className="settings-interface p-6">
      <header className="mb-6">
        <h1 className="text-2xl font-bold">Settings</h1>
        <p className="text-muted-foreground">Customize your ApexAgent experience</p>
      </header>
      
      <Tabs defaultValue="account" className="w-full">
        <TabsList className="mb-6 flex flex-wrap">
          <TabsTrigger value="account" className="flex items-center gap-2">
            <User size={16} />
            <span>Account</span>
          </TabsTrigger>
          <TabsTrigger value="appearance" className="flex items-center gap-2">
            <Palette size={16} />
            <span>Appearance</span>
          </TabsTrigger>
          <TabsTrigger value="privacy" className="flex items-center gap-2">
            <Shield size={16} />
            <span>Privacy</span>
          </TabsTrigger>
          <TabsTrigger value="notifications" className="flex items-center gap-2">
            <Bell size={16} />
            <span>Notifications</span>
          </TabsTrigger>
          <TabsTrigger value="performance" className="flex items-center gap-2">
            <Cpu size={16} />
            <span>Performance</span>
          </TabsTrigger>
          <TabsTrigger value="llm" className="flex items-center gap-2">
            <Globe size={16} />
            <span>LLM</span>
          </TabsTrigger>
          <TabsTrigger value="keyboard" className="flex items-center gap-2">
            <Keyboard size={16} />
            <span>Keyboard</span>
          </TabsTrigger>
          <TabsTrigger value="system" className="flex items-center gap-2">
            <HardDrive size={16} />
            <span>System</span>
          </TabsTrigger>
          <TabsTrigger value="accessibility" className="flex items-center gap-2">
            <Monitor size={16} />
            <span>Accessibility</span>
          </TabsTrigger>
        </TabsList>
        
        {/* Account Settings */}
        <TabsContent value="account" className="space-y-6">
          <div className="space-y-4">
            <h2 className="text-xl font-semibold">Account Information</h2>
            
            <div className="space-y-2">
              <label className="text-sm font-medium">Username</label>
              <Input 
                value={username} 
                onChange={(e) => setUsername(e.target.value)} 
                className="max-w-md"
              />
            </div>
            
            <div className="space-y-2">
              <label className="text-sm font-medium">Email</label>
              <Input 
                type="email" 
                value={email} 
                onChange={(e) => setEmail(e.target.value)} 
                className="max-w-md"
              />
            </div>
            
            <div className="pt-4">
              <Button variant="outline">Change Password</Button>
            </div>
          </div>
          
          <div className="space-y-4">
            <h2 className="text-xl font-semibold">Subscription</h2>
            
            <div className="p-4 bg-card rounded-lg border border-border">
              <div className="flex justify-between items-center">
                <div>
                  <h3 className="font-medium">Pro Plan</h3>
                  <p className="text-sm text-muted-foreground">Unlimited conversations, priority support</p>
                </div>
                <Button variant="outline">Manage Subscription</Button>
              </div>
            </div>
          </div>
        </TabsContent>
        
        {/* Appearance Settings */}
        <TabsContent value="appearance" className="space-y-6">
          <div className="space-y-4">
            <h2 className="text-xl font-semibold">Theme</h2>
            
            <div className="space-y-2">
              <label className="text-sm font-medium">Color Theme</label>
              <Select value={theme} onValueChange={setTheme}>
                <SelectTrigger className="max-w-md">
                  <SelectValue placeholder="Select theme" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="light">Light</SelectItem>
                  <SelectItem value="dark">Dark</SelectItem>
                  <SelectItem value="system">System</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div className="space-y-2">
              <label className="text-sm font-medium">Accent Color</label>
              <Select value={accentColor} onValueChange={setAccentColor}>
                <SelectTrigger className="max-w-md">
                  <SelectValue placeholder="Select accent color" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="blue">Blue</SelectItem>
                  <SelectItem value="purple">Purple</SelectItem>
                  <SelectItem value="green">Green</SelectItem>
                  <SelectItem value="orange">Orange</SelectItem>
                  <SelectItem value="red">Red</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          
          <div className="space-y-4">
            <h2 className="text-xl font-semibold">Text</h2>
            
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <label className="text-sm font-medium">Font Size: {fontSize}px</label>
                <span className="text-sm text-muted-foreground">{fontSize}px</span>
              </div>
              <Slider 
                min={10} 
                max={20} 
                step={1} 
                value={[fontSize]} 
                onValueChange={(value) => setFontSize(value[0])} 
                className="max-w-md"
              />
            </div>
            
            <div className="space-y-2">
              <label className="text-sm font-medium">Interface Density</label>
              <Select value={density} onValueChange={setDensity}>
                <SelectTrigger className="max-w-md">
                  <SelectValue placeholder="Select density" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="compact">Compact</SelectItem>
                  <SelectItem value="comfortable">Comfortable</SelectItem>
                  <SelectItem value="spacious">Spacious</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </TabsContent>
        
        {/* Privacy Settings */}
        <TabsContent value="privacy" className="space-y-6">
          <div className="space-y-4">
            <h2 className="text-xl font-semibold">Data Collection</h2>
            
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-medium">Usage Telemetry</h3>
                <p className="text-sm text-muted-foreground">Send anonymous usage data to help improve ApexAgent</p>
              </div>
              <Switch checked={telemetry} onCheckedChange={setTelemetry} />
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-medium">Crash Reports</h3>
                <p className="text-sm text-muted-foreground">Send crash reports to help fix issues</p>
              </div>
              <Switch checked={crashReports} onCheckedChange={setCrashReports} />
            </div>
          </div>
          
          <div className="space-y-4">
            <h2 className="text-xl font-semibold">Data Storage</h2>
            
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-medium">Local Storage Only</h3>
                <p className="text-sm text-muted-foreground">Store all data locally on your device</p>
              </div>
              <Switch checked={localStorageOnly} onCheckedChange={setLocalStorageOnly} />
            </div>
            
            <div className="pt-2">
              <Button variant="outline">Clear All Data</Button>
            </div>
          </div>
        </TabsContent>
        
        {/* Notification Settings */}
        <TabsContent value="notifications" className="space-y-6">
          <div className="space-y-4">
            <h2 className="text-xl font-semibold">Notification Settings</h2>
            
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-medium">Enable Notifications</h3>
                <p className="text-sm text-muted-foreground">Show notifications for important events</p>
              </div>
              <Switch checked={notifications} onCheckedChange={setNotifications} />
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-medium">Notification Sound</h3>
                <p className="text-sm text-muted-foreground">Play sound when notifications appear</p>
              </div>
              <Switch 
                checked={notificationSound} 
                onCheckedChange={setNotificationSound} 
                disabled={!notifications} 
              />
            </div>
          </div>
          
          <div className="space-y-4">
            <h2 className="text-xl font-semibold">Notification Types</h2>
            
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-medium">Task Completion</h3>
                <p className="text-sm text-muted-foreground">Notify when tasks are completed</p>
              </div>
              <Switch 
                checked={taskCompletionNotifications} 
                onCheckedChange={setTaskCompletionNotifications} 
                disabled={!notifications} 
              />
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-medium">System Notifications</h3>
                <p className="text-sm text-muted-foreground">Notify about system events and updates</p>
              </div>
              <Switch 
                checked={systemNotifications} 
                onCheckedChange={setSystemNotifications} 
                disabled={!notifications} 
              />
            </div>
          </div>
        </TabsContent>
        
        {/* Performance Settings */}
        <TabsContent value="performance" className="space-y-6">
          <div className="space-y-4">
            <h2 className="text-xl font-semibold">Resource Limits</h2>
            
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <label className="text-sm font-medium">Maximum Concurrent Tasks</label>
                <span className="text-sm text-muted-foreground">{maxConcurrentTasks}</span>
              </div>
              <Slider 
                min={1} 
                max={10} 
                step={1} 
                value={[maxConcurrentTasks]} 
                onValueChange={(value) => setMaxConcurrentTasks(value[0])} 
                className="max-w-md"
              />
            </div>
            
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <label className="text-sm font-medium">Memory Limit (MB)</label>
                <span className="text-sm text-muted-foreground">{memoryLimit} MB</span>
              </div>
              <Slider 
                min={1024} 
                max={8192} 
                step={512} 
                value={[memoryLimit]} 
                onValueChange={(value) => setMemoryLimit(value[0])} 
                className="max-w-md"
              />
            </div>
            
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <label className="text-sm font-medium">Disk Space Limit (MB)</label>
                <span className="text-sm text-muted-foreground">{diskSpaceLimit} MB</span>
              </div>
              <Slider 
                min={1024} 
                max={20480} 
                step={1024} 
                value={[diskSpaceLimit]} 
                onValueChange={(value) => setDiskSpaceLimit(value[0])} 
                className="max-w-md"
              />
            </div>
          </div>
        </TabsContent>
        
        {/* LLM Settings */}
        <TabsContent value="llm" className="space-y-6">
          <div className="space-y-4">
            <h2 className="text-xl font-semibold">Model Settings</h2>
            
            <div className="space-y-2">
              <label className="text-sm font-medium">Default Model</label>
              <Select value={defaultModel} onValueChange={setDefaultModel}>
                <SelectTrigger className="max-w-md">
                  <SelectValue placeholder="Select default model" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="gpt-4">GPT-4</SelectItem>
                  <SelectItem value="gpt-3.5-turbo">GPT-3.5 Turbo</SelectItem>
                  <SelectItem value="claude-3-opus">Claude 3 Opus</SelectItem>
                  <SelectItem value="claude-3-sonnet">Claude 3 Sonnet</SelectItem>
                  <SelectItem value="llama-3-70b">Llama 3 (70B)</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div className="space-y-2">
              <label className="text-sm font-medium">API Provider</label>
              <Select value={apiProvider} onValueChange={setApiProvider}>
                <SelectTrigger className="max-w-md">
                  <SelectValue placeholder="Select API provider" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="openai">OpenAI</SelectItem>
                  <SelectItem value="anthropic">Anthropic</SelectItem>
                  <SelectItem value="meta">Meta</SelectItem>
                  <SelectItem value="custom">Custom</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-medium">Use Local Models When Available</h3>
                <p className="text-sm text-muted-foreground">Prioritize locally installed models over API calls</p>
              </div>
              <Switch checked={useLocalModels} onCheckedChange={setUseLocalModels} />
            </div>
          </div>
          
          <div className="space-y-4">
            <h2 className="text-xl font-semibold">API Keys</h2>
            
            <div className="space-y-2">
              <label className="text-sm font-medium">OpenAI API Key</label>
              <div className="flex max-w-md">
                <Input type="password" value="••••••••••••••••••••••••••" className="rounded-r-none" />
                <Button variant="outline" className="rounded-l-none">Update</Button>
              </div>
            </div>
            
            <div className="space-y-2">
              <label className="text-sm font-medium">Anthropic API Key</label>
              <div className="flex max-w-md">
                <Input type="password" value="" placeholder="Not set" className="rounded-r-none" />
                <Button variant="outline" className="rounded-l-none">Set</Button>
              </div>
            </div>
          </div>
        </TabsContent>
        
        {/* Keyboard Settings */}
        <TabsContent value="keyboard" className="space-y-6">
          <div className="space-y-4">
            <h2 className="text-xl font-semibold">Keyboard Shortcuts</h2>
            
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-medium">Enable Keyboard Shortcuts</h3>
                <p className="text-sm text-muted-foreground">Use keyboard shortcuts for faster navigation</p>
              </div>
              <Switch checked={enableShortcuts} onCheckedChange={setEnableShortcuts} />
            </div>
            
            <div className="space-y-4 pt-2">
              <h3 className="font-medium">Customize Shortcuts</h3>
              
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <label className="text-sm">New Chat</label>
                  <Input 
                    value={customShortcuts.newChat} 
                    onChange={(e) => setCustomShortcuts({...customShortcuts, newChat: e.target.value})} 
                    className="max-w-[200px]"
                    disabled={!enableShortcuts}
                  />
                </div>
                
                <div className="flex justify-between items-center">
                  <label className="text-sm">Save Chat</label>
                  <Input 
                    value={customShortcuts.saveChat} 
                    onChange={(e) => setCustomShortcuts({...customShortcuts, saveChat: e.target.value})} 
                    className="max-w-[200px]"
                    disabled={!enableShortcuts}
                  />
                </div>
                
                <div className="flex justify-between items-center">
                  <label className="text-sm">Clear Chat</label>
                  <Input 
                    value={customShortcuts.clearChat} 
                    onChange={(e) => setCustomShortcuts({...customShortcuts, clearChat: e.target.value})} 
                    className="max-w-[200px]"
                    disabled={!enableShortcuts}
                  />
                </div>
                
                <div className="flex justify-between items-center">
                  <label className="text-sm">Focus Input</label>
                  <Input 
                    value={customShortcuts.focusInput} 
                    onChange={(e) => setCustomShortcuts({...customShortcuts, focusInput: e.target.value})} 
                    className="max-w-[200px]"
                    disabled={!enableShortcuts}
                  />
                </div>
                
                <div className="flex justify-between items-center">
                  <label className="text-sm">Toggle Sidebar</label>
                  <Input 
                    value={customShortcuts.toggleSidebar} 
                    onChange={(e) => setCustomShortcuts({...customShortcuts, toggleSidebar: e.target.value})} 
                    className="max-w-[200px]"
                    disabled={!enableShortcuts}
                  />
                </div>
                
                <div className="flex justify-between items-center">
                  <label className="text-sm">Toggle Settings</label>
                  <Input 
                    value={customShortcuts.toggleSettings} 
                    onChange={(e) => setCustomShortcuts({...customShortcuts, toggleSettings: e.target.value})} 
                    className="max-w-[200px]"
                    disabled={!enableShortcuts}
                  />
                </div>
              </div>
              
              <div className="pt-2">
                <Button variant="outline" disabled={!enableShortcuts}>Reset to Defaults</Button>
              </div>
            </div>
          </div>
        </TabsContent>
        
        {/* System Settings */}
        <TabsContent value="system" className="space-y-6">
          <div className="space-y-4">
            <h2 className="text-xl font-semibold">Startup</h2>
            
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-medium">Start on Boot</h3>
                <p className="text-sm text-muted-foreground">Launch ApexAgent when your computer starts</p>
              </div>
              <Switch checked={startOnBoot} onCheckedChange={setStartOnBoot} />
            </div>
          </div>
          
          <div className="space-y-4">
            <h2 className="text-xl font-semibold">Updates</h2>
            
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-medium">Check for Updates</h3>
                <p className="text-sm text-muted-foreground">Periodically check for new versions</p>
              </div>
              <Switch checked={checkForUpdates} onCheckedChange={setCheckForUpdates} />
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-medium">Automatic Updates</h3>
                <p className="text-sm text-muted-foreground">Install updates automatically</p>
              </div>
              <Switch 
                checked={autoUpdate} 
                onCheckedChange={setAutoUpdate} 
                disabled={!checkForUpdates} 
              />
            </div>
            
            <div className="pt-2">
              <Button variant="outline">Check for Updates Now</Button>
            </div>
          </div>
          
          <div className="space-y-4">
            <h2 className="text-xl font-semibold">System Information</h2>
            
            <div className="p-4 bg-card rounded-lg border border-border space-y-2">
              <div className="flex justify-between">
                <span className="text-sm font-medium">Version</span>
                <span className="text-sm">1.5.2</span>
              </div>
              
              <div className="flex justify-between">
                <span className="text-sm font-medium">Build</span>
                <span className="text-sm">2025.05.21.1234</span>
              </div>
              
              <div className="flex justify-between">
                <span className="text-sm font-medium">Platform</span>
                <span className="text-sm">Windows 11</span>
              </div>
              
              <div className="flex justify-between">
                <span className="text-sm font-medium">Architecture</span>
                <span className="text-sm">x64</span>
              </div>
            </div>
          </div>
        </TabsContent>
        
        {/* Accessibility Settings */}
        <TabsContent value="accessibility" className="space-y-6">
          <div className="space-y-4">
            <h2 className="text-xl font-semibold">Visual Accessibility</h2>
            
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-medium">High Contrast Mode</h3>
                <p className="text-sm text-muted-foreground">Increase contrast for better visibility</p>
              </div>
              <Switch checked={highContrast} onCheckedChange={setHighContrast} />
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-medium">Reduced Motion</h3>
                <p className="text-sm text-muted-foreground">Minimize animations and transitions</p>
              </div>
              <Switch checked={reducedMotion} onCheckedChange={setReducedMotion} />
            </div>
          </div>
          
          <div className="space-y-4">
            <h2 className="text-xl font-semibold">Screen Reader</h2>
            
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-medium">Optimize for Screen Readers</h3>
                <p className="text-sm text-muted-foreground">Improve compatibility with screen reader software</p>
              </div>
              <Switch checked={screenReader} onCheckedChange={setScreenReader} />
            </div>
          </div>
        </TabsContent>
      </Tabs>
      
      <div className="mt-8 pt-6 border-t border-border flex justify-end">
        <Button onClick={handleSaveSettings} className="flex items-center gap-2">
          <Save size={16} />
          <span>Save Settings</span>
        </Button>
      </div>
    </div>
  );
};

export default SettingsInterface;
