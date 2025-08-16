// src/plugins/PluginSystem.ts
import { createContext, useContext } from 'react';

// Plugin capability types
export enum PluginCapability {
  FILE_ACCESS = 'file_access',
  NETWORK_ACCESS = 'network_access',
  UI_EXTENSION = 'ui_extension',
  LLM_ACCESS = 'llm_access',
  SYSTEM_ACCESS = 'system_access',
  DATA_PROCESSING = 'data_processing',
  VISUALIZATION = 'visualization'
}

// Plugin permission level
export enum PermissionLevel {
  NONE = 'none',
  READ = 'read',
  WRITE = 'write',
  FULL = 'full'
}

// Plugin status
export enum PluginStatus {
  ACTIVE = 'active',
  INACTIVE = 'inactive',
  DISABLED = 'disabled',
  UPDATING = 'updating',
  ERROR = 'error'
}

// Plugin manifest interface
export interface PluginManifest {
  id: string;
  name: string;
  description: string;
  version: string;
  author: string;
  icon: string;
  capabilities: PluginCapability[];
  permissions: Record<PluginCapability, PermissionLevel>;
  entryPoint: string;
  configSchema?: Record<string, any>;
  dependencies?: string[];
  minAppVersion?: string;
  homepage?: string;
  repository?: string;
}

// Plugin instance interface
export interface Plugin {
  manifest: PluginManifest;
  status: PluginStatus;
  instance?: any;
  config: Record<string, any>;
  lastError?: string;
  lastUpdated: Date;
}

// Plugin event types
export enum PluginEventType {
  INSTALLED = 'installed',
  UNINSTALLED = 'uninstalled',
  ACTIVATED = 'activated',
  DEACTIVATED = 'deactivated',
  UPDATED = 'updated',
  ERROR = 'error',
  CONFIG_CHANGED = 'config_changed'
}

// Plugin event interface
export interface PluginEvent {
  type: PluginEventType;
  pluginId: string;
  timestamp: Date;
  data?: any;
}

// Plugin API interface
export interface PluginAPI {
  // Core methods
  registerHook: (hookName: string, callback: Function) => void;
  unregisterHook: (hookName: string, callback: Function) => void;
  
  // UI methods
  registerComponent: (slot: string, component: any) => void;
  unregisterComponent: (slot: string, component: any) => void;
  
  // Data methods
  getData: (key: string) => Promise<any>;
  setData: (key: string, value: any) => Promise<void>;
  
  // System methods
  getCapabilities: () => PluginCapability[];
  getPermissions: () => Record<PluginCapability, PermissionLevel>;
  
  // Configuration methods
  getConfig: () => Record<string, any>;
  updateConfig: (config: Record<string, any>) => Promise<void>;
  
  // Utility methods
  log: (message: string, level?: 'info' | 'warn' | 'error') => void;
  showNotification: (message: string, type?: 'info' | 'success' | 'warning' | 'error') => void;
}

// Plugin manager interface
export interface PluginManager {
  // Plugin lifecycle methods
  installPlugin: (source: string | File) => Promise<Plugin>;
  uninstallPlugin: (pluginId: string) => Promise<void>;
  activatePlugin: (pluginId: string) => Promise<void>;
  deactivatePlugin: (pluginId: string) => Promise<void>;
  updatePlugin: (pluginId: string, source?: string | File) => Promise<Plugin>;
  
  // Plugin query methods
  getPlugin: (pluginId: string) => Plugin | undefined;
  getAllPlugins: () => Plugin[];
  getActivePlugins: () => Plugin[];
  getPluginsByCapability: (capability: PluginCapability) => Plugin[];
  
  // Plugin configuration methods
  getPluginConfig: (pluginId: string) => Record<string, any>;
  updatePluginConfig: (pluginId: string, config: Record<string, any>) => Promise<void>;
  
  // Plugin event methods
  addEventListener: (type: PluginEventType, callback: (event: PluginEvent) => void) => void;
  removeEventListener: (type: PluginEventType, callback: (event: PluginEvent) => void) => void;
  
  // Plugin API methods
  getPluginAPI: (pluginId: string) => PluginAPI;
}

// Create context for plugin system
export const PluginContext = createContext<PluginManager | null>(null);

// Hook for using plugin system
export const usePluginSystem = () => {
  const context = useContext(PluginContext);
  if (!context) {
    throw new Error('usePluginSystem must be used within a PluginProvider');
  }
  return context;
};

// Default implementation of plugin manager
export class DefaultPluginManager implements PluginManager {
  private plugins: Map<string, Plugin> = new Map();
  private eventListeners: Map<PluginEventType, Set<(event: PluginEvent) => void>> = new Map();
  
  // Plugin lifecycle methods
  async installPlugin(source: string | File): Promise<Plugin> {
    // Implementation would load the plugin from source, validate manifest, and install
    // This is a simplified mock implementation
    const mockPlugin: Plugin = {
      manifest: {
        id: `plugin-${Date.now()}`,
        name: 'New Plugin',
        description: 'A newly installed plugin',
        version: '1.0.0',
        author: 'ApexAgent User',
        icon: '🔌',
        capabilities: [PluginCapability.UI_EXTENSION],
        permissions: {
          [PluginCapability.UI_EXTENSION]: PermissionLevel.READ,
          [PluginCapability.FILE_ACCESS]: PermissionLevel.NONE,
          [PluginCapability.NETWORK_ACCESS]: PermissionLevel.NONE,
          [PluginCapability.LLM_ACCESS]: PermissionLevel.NONE,
          [PluginCapability.SYSTEM_ACCESS]: PermissionLevel.NONE,
          [PluginCapability.DATA_PROCESSING]: PermissionLevel.NONE,
          [PluginCapability.VISUALIZATION]: PermissionLevel.NONE,
        },
        entryPoint: 'index.js'
      },
      status: PluginStatus.INACTIVE,
      config: {},
      lastUpdated: new Date()
    };
    
    this.plugins.set(mockPlugin.manifest.id, mockPlugin);
    this.dispatchEvent({
      type: PluginEventType.INSTALLED,
      pluginId: mockPlugin.manifest.id,
      timestamp: new Date()
    });
    
    return mockPlugin;
  }
  
  async uninstallPlugin(pluginId: string): Promise<void> {
    if (!this.plugins.has(pluginId)) {
      throw new Error(`Plugin ${pluginId} not found`);
    }
    
    // Deactivate if active
    const plugin = this.plugins.get(pluginId)!;
    if (plugin.status === PluginStatus.ACTIVE) {
      await this.deactivatePlugin(pluginId);
    }
    
    this.plugins.delete(pluginId);
    this.dispatchEvent({
      type: PluginEventType.UNINSTALLED,
      pluginId,
      timestamp: new Date()
    });
  }
  
  async activatePlugin(pluginId: string): Promise<void> {
    if (!this.plugins.has(pluginId)) {
      throw new Error(`Plugin ${pluginId} not found`);
    }
    
    const plugin = this.plugins.get(pluginId)!;
    
    try {
      // In a real implementation, this would load and initialize the plugin
      plugin.status = PluginStatus.ACTIVE;
      this.plugins.set(pluginId, plugin);
      
      this.dispatchEvent({
        type: PluginEventType.ACTIVATED,
        pluginId,
        timestamp: new Date()
      });
    } catch (error) {
      plugin.status = PluginStatus.ERROR;
      plugin.lastError = error instanceof Error ? error.message : String(error);
      this.plugins.set(pluginId, plugin);
      
      this.dispatchEvent({
        type: PluginEventType.ERROR,
        pluginId,
        timestamp: new Date(),
        data: { error: plugin.lastError }
      });
      
      throw error;
    }
  }
  
  async deactivatePlugin(pluginId: string): Promise<void> {
    if (!this.plugins.has(pluginId)) {
      throw new Error(`Plugin ${pluginId} not found`);
    }
    
    const plugin = this.plugins.get(pluginId)!;
    
    try {
      // In a real implementation, this would clean up and unload the plugin
      plugin.status = PluginStatus.INACTIVE;
      this.plugins.set(pluginId, plugin);
      
      this.dispatchEvent({
        type: PluginEventType.DEACTIVATED,
        pluginId,
        timestamp: new Date()
      });
    } catch (error) {
      plugin.status = PluginStatus.ERROR;
      plugin.lastError = error instanceof Error ? error.message : String(error);
      this.plugins.set(pluginId, plugin);
      
      this.dispatchEvent({
        type: PluginEventType.ERROR,
        pluginId,
        timestamp: new Date(),
        data: { error: plugin.lastError }
      });
      
      throw error;
    }
  }
  
  async updatePlugin(pluginId: string, source?: string | File): Promise<Plugin> {
    if (!this.plugins.has(pluginId)) {
      throw new Error(`Plugin ${pluginId} not found`);
    }
    
    const plugin = this.plugins.get(pluginId)!;
    const wasActive = plugin.status === PluginStatus.ACTIVE;
    
    try {
      // In a real implementation, this would update the plugin from source
      plugin.status = PluginStatus.UPDATING;
      this.plugins.set(pluginId, plugin);
      
      // Mock update
      plugin.manifest.version = incrementVersion(plugin.manifest.version);
      plugin.lastUpdated = new Date();
      plugin.status = wasActive ? PluginStatus.ACTIVE : PluginStatus.INACTIVE;
      
      this.plugins.set(pluginId, plugin);
      
      this.dispatchEvent({
        type: PluginEventType.UPDATED,
        pluginId,
        timestamp: new Date(),
        data: { version: plugin.manifest.version }
      });
      
      return plugin;
    } catch (error) {
      plugin.status = PluginStatus.ERROR;
      plugin.lastError = error instanceof Error ? error.message : String(error);
      this.plugins.set(pluginId, plugin);
      
      this.dispatchEvent({
        type: PluginEventType.ERROR,
        pluginId,
        timestamp: new Date(),
        data: { error: plugin.lastError }
      });
      
      throw error;
    }
  }
  
  // Plugin query methods
  getPlugin(pluginId: string): Plugin | undefined {
    return this.plugins.get(pluginId);
  }
  
  getAllPlugins(): Plugin[] {
    return Array.from(this.plugins.values());
  }
  
  getActivePlugins(): Plugin[] {
    return Array.from(this.plugins.values()).filter(
      plugin => plugin.status === PluginStatus.ACTIVE
    );
  }
  
  getPluginsByCapability(capability: PluginCapability): Plugin[] {
    return Array.from(this.plugins.values()).filter(
      plugin => plugin.manifest.capabilities.includes(capability)
    );
  }
  
  // Plugin configuration methods
  getPluginConfig(pluginId: string): Record<string, any> {
    if (!this.plugins.has(pluginId)) {
      throw new Error(`Plugin ${pluginId} not found`);
    }
    
    return this.plugins.get(pluginId)!.config;
  }
  
  async updatePluginConfig(pluginId: string, config: Record<string, any>): Promise<void> {
    if (!this.plugins.has(pluginId)) {
      throw new Error(`Plugin ${pluginId} not found`);
    }
    
    const plugin = this.plugins.get(pluginId)!;
    plugin.config = { ...plugin.config, ...config };
    this.plugins.set(pluginId, plugin);
    
    this.dispatchEvent({
      type: PluginEventType.CONFIG_CHANGED,
      pluginId,
      timestamp: new Date(),
      data: { config: plugin.config }
    });
  }
  
  // Plugin event methods
  addEventListener(type: PluginEventType, callback: (event: PluginEvent) => void): void {
    if (!this.eventListeners.has(type)) {
      this.eventListeners.set(type, new Set());
    }
    
    this.eventListeners.get(type)!.add(callback);
  }
  
  removeEventListener(type: PluginEventType, callback: (event: PluginEvent) => void): void {
    if (!this.eventListeners.has(type)) {
      return;
    }
    
    this.eventListeners.get(type)!.delete(callback);
  }
  
  private dispatchEvent(event: PluginEvent): void {
    // Dispatch to specific event type listeners
    if (this.eventListeners.has(event.type)) {
      for (const callback of this.eventListeners.get(event.type)!) {
        callback(event);
      }
    }
    
    // Dispatch to all event listeners
    if (this.eventListeners.has(PluginEventType.ERROR) && event.type === PluginEventType.ERROR) {
      for (const callback of this.eventListeners.get(PluginEventType.ERROR)!) {
        callback(event);
      }
    }
  }
  
  // Plugin API methods
  getPluginAPI(pluginId: string): PluginAPI {
    if (!this.plugins.has(pluginId)) {
      throw new Error(`Plugin ${pluginId} not found`);
    }
    
    const plugin = this.plugins.get(pluginId)!;
    
    // Create a sandboxed API for the plugin
    const api: PluginAPI = {
      // Core methods
      registerHook: (hookName: string, callback: Function) => {
        // Implementation would register a hook
        console.log(`Plugin ${pluginId} registered hook: ${hookName}`);
      },
      
      unregisterHook: (hookName: string, callback: Function) => {
        // Implementation would unregister a hook
        console.log(`Plugin ${pluginId} unregistered hook: ${hookName}`);
      },
      
      // UI methods
      registerComponent: (slot: string, component: any) => {
        // Implementation would register a UI component
        console.log(`Plugin ${pluginId} registered component in slot: ${slot}`);
      },
      
      unregisterComponent: (slot: string, component: any) => {
        // Implementation would unregister a UI component
        console.log(`Plugin ${pluginId} unregistered component from slot: ${slot}`);
      },
      
      // Data methods
      getData: async (key: string) => {
        // Implementation would get data from storage
        return null;
      },
      
      setData: async (key: string, value: any) => {
        // Implementation would set data in storage
        console.log(`Plugin ${pluginId} set data for key: ${key}`);
      },
      
      // System methods
      getCapabilities: () => {
        return plugin.manifest.capabilities;
      },
      
      getPermissions: () => {
        return plugin.manifest.permissions;
      },
      
      // Configuration methods
      getConfig: () => {
        return plugin.config;
      },
      
      updateConfig: async (config: Record<string, any>) => {
        await this.updatePluginConfig(pluginId, config);
      },
      
      // Utility methods
      log: (message: string, level: 'info' | 'warn' | 'error' = 'info') => {
        console[level](`[Plugin ${pluginId}] ${message}`);
      },
      
      showNotification: (message: string, type: 'info' | 'success' | 'warning' | 'error' = 'info') => {
        // Implementation would show a notification
        console.log(`[Plugin ${pluginId}] Notification (${type}): ${message}`);
      }
    };
    
    return api;
  }
}

// Helper function to increment version
function incrementVersion(version: string): string {
  const parts = version.split('.');
  if (parts.length !== 3) {
    return version;
  }
  
  const patch = parseInt(parts[2], 10) + 1;
  return `${parts[0]}.${parts[1]}.${patch}`;
}
