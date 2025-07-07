import React from 'react';

// Define API service interfaces
interface ApiResponse<T> {
  data: T;
  status: number;
  message: string;
}

interface ApiError {
  status: number;
  message: string;
  details?: string;
}

// API endpoints configuration
const API_CONFIG = {
  baseUrl: '/api',
  endpoints: {
    // System endpoints
    system: {
      status: '/system/status',
      resources: '/system/resources',
      permissions: '/system/permissions',
      activity: '/system/activity'
    },
    // File system endpoints
    files: {
      list: '/files/list',
      read: '/files/read',
      write: '/files/write',
      delete: '/files/delete',
      move: '/files/move',
      copy: '/files/copy'
    },
    // Conversation endpoints
    conversation: {
      list: '/conversation/list',
      get: '/conversation/get',
      create: '/conversation/create',
      message: '/conversation/message',
      delete: '/conversation/delete'
    },
    // Project endpoints
    projects: {
      list: '/projects/list',
      get: '/projects/get',
      create: '/projects/create',
      update: '/projects/update',
      delete: '/projects/delete'
    },
    // LLM endpoints
    llm: {
      models: '/llm/models',
      orchestration: '/llm/orchestration',
      settings: '/llm/settings',
      analytics: '/llm/analytics'
    },
    // Plugin endpoints
    plugins: {
      list: '/plugins/list',
      install: '/plugins/install',
      uninstall: '/plugins/uninstall',
      enable: '/plugins/enable',
      disable: '/plugins/disable',
      settings: '/plugins/settings'
    }
  }
};

// Generic API request function
async function apiRequest<T>(
  endpoint: string,
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' = 'GET',
  data?: any
): Promise<ApiResponse<T>> {
  try {
    const url = `${API_CONFIG.baseUrl}${endpoint}`;
    
    const options: RequestInit = {
      method,
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include' // Include cookies for authentication
    };
    
    if (data) {
      options.body = JSON.stringify(data);
    }
    
    const response = await fetch(url, options);
    const responseData = await response.json();
    
    if (!response.ok) {
      throw {
        status: response.status,
        message: responseData.message || 'An error occurred',
        details: responseData.details
      };
    }
    
    return {
      data: responseData.data,
      status: response.status,
      message: responseData.message || 'Success'
    };
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
}

// System API service
export const SystemApi = {
  getStatus: async () => {
    return apiRequest(API_CONFIG.endpoints.system.status);
  },
  
  getResources: async () => {
    return apiRequest(API_CONFIG.endpoints.system.resources);
  },
  
  getPermissions: async () => {
    return apiRequest(API_CONFIG.endpoints.system.permissions);
  },
  
  getActivity: async (limit: number = 20, offset: number = 0, type?: string) => {
    const queryParams = new URLSearchParams();
    queryParams.append('limit', limit.toString());
    queryParams.append('offset', offset.toString());
    if (type) queryParams.append('type', type);
    
    return apiRequest(`${API_CONFIG.endpoints.system.activity}?${queryParams.toString()}`);
  },
  
  updatePermissions: async (permissions: any) => {
    return apiRequest(API_CONFIG.endpoints.system.permissions, 'PUT', permissions);
  }
};

// File system API service
export const FileSystemApi = {
  listFiles: async (path: string) => {
    const queryParams = new URLSearchParams();
    queryParams.append('path', path);
    
    return apiRequest(`${API_CONFIG.endpoints.files.list}?${queryParams.toString()}`);
  },
  
  readFile: async (path: string) => {
    const queryParams = new URLSearchParams();
    queryParams.append('path', path);
    
    return apiRequest(`${API_CONFIG.endpoints.files.read}?${queryParams.toString()}`);
  },
  
  writeFile: async (path: string, content: string) => {
    return apiRequest(API_CONFIG.endpoints.files.write, 'POST', { path, content });
  },
  
  deleteFile: async (path: string) => {
    return apiRequest(API_CONFIG.endpoints.files.delete, 'DELETE', { path });
  },
  
  moveFile: async (sourcePath: string, destinationPath: string) => {
    return apiRequest(API_CONFIG.endpoints.files.move, 'POST', { sourcePath, destinationPath });
  },
  
  copyFile: async (sourcePath: string, destinationPath: string) => {
    return apiRequest(API_CONFIG.endpoints.files.copy, 'POST', { sourcePath, destinationPath });
  }
};

// Conversation API service
export const ConversationApi = {
  listConversations: async (limit: number = 20, offset: number = 0) => {
    const queryParams = new URLSearchParams();
    queryParams.append('limit', limit.toString());
    queryParams.append('offset', offset.toString());
    
    return apiRequest(`${API_CONFIG.endpoints.conversation.list}?${queryParams.toString()}`);
  },
  
  getConversation: async (id: string) => {
    const queryParams = new URLSearchParams();
    queryParams.append('id', id);
    
    return apiRequest(`${API_CONFIG.endpoints.conversation.get}?${queryParams.toString()}`);
  },
  
  createConversation: async (title: string, projectId?: string) => {
    return apiRequest(API_CONFIG.endpoints.conversation.create, 'POST', { title, projectId });
  },
  
  sendMessage: async (conversationId: string, message: string, attachments?: string[]) => {
    return apiRequest(API_CONFIG.endpoints.conversation.message, 'POST', { 
      conversationId, 
      message,
      attachments
    });
  },
  
  deleteConversation: async (id: string) => {
    return apiRequest(API_CONFIG.endpoints.conversation.delete, 'DELETE', { id });
  }
};

// Project API service
export const ProjectApi = {
  listProjects: async (status?: string) => {
    const queryParams = new URLSearchParams();
    if (status) queryParams.append('status', status);
    
    return apiRequest(`${API_CONFIG.endpoints.projects.list}?${queryParams.toString()}`);
  },
  
  getProject: async (id: string) => {
    const queryParams = new URLSearchParams();
    queryParams.append('id', id);
    
    return apiRequest(`${API_CONFIG.endpoints.projects.get}?${queryParams.toString()}`);
  },
  
  createProject: async (name: string, description?: string) => {
    return apiRequest(API_CONFIG.endpoints.projects.create, 'POST', { name, description });
  },
  
  updateProject: async (id: string, data: any) => {
    return apiRequest(API_CONFIG.endpoints.projects.update, 'PUT', { id, ...data });
  },
  
  deleteProject: async (id: string) => {
    return apiRequest(API_CONFIG.endpoints.projects.delete, 'DELETE', { id });
  }
};

// LLM API service
export const LLMApi = {
  getModels: async () => {
    return apiRequest(API_CONFIG.endpoints.llm.models);
  },
  
  getOrchestrationConfig: async () => {
    return apiRequest(API_CONFIG.endpoints.llm.orchestration);
  },
  
  updateOrchestrationConfig: async (config: any) => {
    return apiRequest(API_CONFIG.endpoints.llm.orchestration, 'PUT', config);
  },
  
  getSettings: async () => {
    return apiRequest(API_CONFIG.endpoints.llm.settings);
  },
  
  updateSettings: async (settings: any) => {
    return apiRequest(API_CONFIG.endpoints.llm.settings, 'PUT', settings);
  },
  
  getAnalytics: async (timeframe: 'day' | 'week' | 'month' = 'day') => {
    const queryParams = new URLSearchParams();
    queryParams.append('timeframe', timeframe);
    
    return apiRequest(`${API_CONFIG.endpoints.llm.analytics}?${queryParams.toString()}`);
  }
};

// Plugin API service
export const PluginApi = {
  listPlugins: async () => {
    return apiRequest(API_CONFIG.endpoints.plugins.list);
  },
  
  installPlugin: async (pluginId: string) => {
    return apiRequest(API_CONFIG.endpoints.plugins.install, 'POST', { pluginId });
  },
  
  uninstallPlugin: async (pluginId: string) => {
    return apiRequest(API_CONFIG.endpoints.plugins.uninstall, 'DELETE', { pluginId });
  },
  
  enablePlugin: async (pluginId: string) => {
    return apiRequest(API_CONFIG.endpoints.plugins.enable, 'POST', { pluginId });
  },
  
  disablePlugin: async (pluginId: string) => {
    return apiRequest(API_CONFIG.endpoints.plugins.disable, 'POST', { pluginId });
  },
  
  getPluginSettings: async (pluginId: string) => {
    const queryParams = new URLSearchParams();
    queryParams.append('pluginId', pluginId);
    
    return apiRequest(`${API_CONFIG.endpoints.plugins.settings}?${queryParams.toString()}`);
  },
  
  updatePluginSettings: async (pluginId: string, settings: any) => {
    return apiRequest(API_CONFIG.endpoints.plugins.settings, 'PUT', { pluginId, settings });
  }
};

export default {
  SystemApi,
  FileSystemApi,
  ConversationApi,
  ProjectApi,
  LLMApi,
  PluginApi
};
