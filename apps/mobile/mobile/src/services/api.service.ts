import AsyncStorage from '@react-native-async-storage/async-storage';
import { Platform } from 'react-native';

interface ApiConfig {
  baseUrl: string;
  timeout: number;
  retryAttempts: number;
}

interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

interface ChatMessage {
  message: string;
  model: string;
  conversation_id?: string;
  temperature?: number;
  max_tokens?: number;
}

interface ChatResponse {
  response: string;
  model: string;
  tokens_used: number;
  conversation_id: string;
  cost: number;
}

interface DashboardData {
  totalTokens: number;
  totalCost: number;
  conversationsToday: number;
  activeAgents: number;
  systemHealth: 'excellent' | 'good' | 'warning' | 'critical';
  recentActivity: Array<{
    id: string;
    type: 'chat' | 'file' | 'agent' | 'security';
    description: string;
    timestamp: string;
  }>;
  usageChart: {
    labels: string[];
    datasets: Array<{
      data: number[];
    }>;
  };
}

class ApiService {
  private config: ApiConfig;
  private authToken: string | null = null;

  constructor() {
    this.config = {
      baseUrl: __DEV__ 
        ? (Platform.OS === 'ios' ? 'http://localhost:3001' : 'http://10.0.2.2:3001')
        : 'https://api.aideonlite.com',
      timeout: 30000,
      retryAttempts: 3,
    };
    
    this.initializeAuth();
  }

  private async initializeAuth() {
    try {
      this.authToken = await AsyncStorage.getItem('auth_token');
    } catch (error) {
      console.error('Failed to initialize auth token:', error);
    }
  }

  private async getHeaders(): Promise<Record<string, string>> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      'User-Agent': `AideonLite-Mobile/${Platform.OS}`,
    };

    if (this.authToken) {
      headers['Authorization'] = `Bearer ${this.authToken}`;
    }

    return headers;
  }

  private async makeRequest<T>(
    endpoint: string,
    options: RequestInit = {},
    retryCount = 0
  ): Promise<ApiResponse<T>> {
    try {
      const url = `${this.config.baseUrl}${endpoint}`;
      const headers = await this.getHeaders();

      const response = await fetch(url, {
        ...options,
        headers: {
          ...headers,
          ...options.headers,
        },
        timeout: this.config.timeout,
      });

      if (!response.ok) {
        if (response.status === 401) {
          // Token expired, clear it
          await this.clearAuthToken();
          throw new Error('Authentication required');
        }
        
        if (response.status >= 500 && retryCount < this.config.retryAttempts) {
          // Retry on server errors
          await this.delay(Math.pow(2, retryCount) * 1000);
          return this.makeRequest(endpoint, options, retryCount + 1);
        }

        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return {
        success: true,
        data,
      };

    } catch (error) {
      console.error(`API request failed: ${endpoint}`, error);
      
      if (retryCount < this.config.retryAttempts && this.isRetryableError(error)) {
        await this.delay(Math.pow(2, retryCount) * 1000);
        return this.makeRequest(endpoint, options, retryCount + 1);
      }

      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  private isRetryableError(error: any): boolean {
    return (
      error.name === 'NetworkError' ||
      error.name === 'TimeoutError' ||
      (error.message && error.message.includes('fetch'))
    );
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  // Authentication methods
  async setAuthToken(token: string): Promise<void> {
    this.authToken = token;
    await AsyncStorage.setItem('auth_token', token);
  }

  async clearAuthToken(): Promise<void> {
    this.authToken = null;
    await AsyncStorage.removeItem('auth_token');
  }

  async login(email: string, password: string): Promise<ApiResponse<{ token: string; user: any }>> {
    return this.makeRequest('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  }

  async register(userData: {
    email: string;
    password: string;
    name: string;
  }): Promise<ApiResponse<{ token: string; user: any }>> {
    return this.makeRequest('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  async refreshToken(): Promise<ApiResponse<{ token: string }>> {
    return this.makeRequest('/auth/refresh', {
      method: 'POST',
    });
  }

  // Chat methods
  async sendChatMessage(messageData: ChatMessage): Promise<ChatResponse> {
    const response = await this.makeRequest<ChatResponse>('/chat/send', {
      method: 'POST',
      body: JSON.stringify(messageData),
    });

    if (!response.success || !response.data) {
      throw new Error(response.error || 'Failed to send message');
    }

    return response.data;
  }

  async getChatHistory(conversationId?: string): Promise<any[]> {
    const endpoint = conversationId 
      ? `/chat/history/${conversationId}`
      : '/chat/history';
    
    const response = await this.makeRequest<any[]>(endpoint);
    
    if (!response.success || !response.data) {
      throw new Error(response.error || 'Failed to load chat history');
    }

    return response.data;
  }

  async getConversations(): Promise<any[]> {
    const response = await this.makeRequest<any[]>('/chat/conversations');
    
    if (!response.success || !response.data) {
      throw new Error(response.error || 'Failed to load conversations');
    }

    return response.data;
  }

  // Dashboard methods
  async getDashboardData(): Promise<DashboardData> {
    const response = await this.makeRequest<DashboardData>('/dashboard');
    
    if (!response.success || !response.data) {
      throw new Error(response.error || 'Failed to load dashboard data');
    }

    return response.data;
  }

  // AI Models methods
  async getAvailableModels(): Promise<any[]> {
    const response = await this.makeRequest<any[]>('/models');
    
    if (!response.success || !response.data) {
      throw new Error(response.error || 'Failed to load models');
    }

    return response.data;
  }

  async getModelInfo(modelId: string): Promise<any> {
    const response = await this.makeRequest<any>(`/models/${modelId}`);
    
    if (!response.success || !response.data) {
      throw new Error(response.error || 'Failed to load model info');
    }

    return response.data;
  }

  // File methods
  async uploadFile(file: {
    uri: string;
    type: string;
    name: string;
  }): Promise<{ fileId: string; url: string }> {
    const formData = new FormData();
    formData.append('file', {
      uri: file.uri,
      type: file.type,
      name: file.name,
    } as any);

    const headers = await this.getHeaders();
    delete headers['Content-Type']; // Let fetch set it for FormData

    const response = await this.makeRequest<{ fileId: string; url: string }>('/files/upload', {
      method: 'POST',
      body: formData,
      headers,
    });

    if (!response.success || !response.data) {
      throw new Error(response.error || 'Failed to upload file');
    }

    return response.data;
  }

  async getFiles(): Promise<any[]> {
    const response = await this.makeRequest<any[]>('/files');
    
    if (!response.success || !response.data) {
      throw new Error(response.error || 'Failed to load files');
    }

    return response.data;
  }

  async deleteFile(fileId: string): Promise<void> {
    const response = await this.makeRequest(`/files/${fileId}`, {
      method: 'DELETE',
    });

    if (!response.success) {
      throw new Error(response.error || 'Failed to delete file');
    }
  }

  // Settings methods
  async getUserSettings(): Promise<any> {
    const response = await this.makeRequest<any>('/user/settings');
    
    if (!response.success || !response.data) {
      throw new Error(response.error || 'Failed to load settings');
    }

    return response.data;
  }

  async updateUserSettings(settings: any): Promise<void> {
    const response = await this.makeRequest('/user/settings', {
      method: 'PUT',
      body: JSON.stringify(settings),
    });

    if (!response.success) {
      throw new Error(response.error || 'Failed to update settings');
    }
  }

  // Agent methods
  async getAgents(): Promise<any[]> {
    const response = await this.makeRequest<any[]>('/agents');
    
    if (!response.success || !response.data) {
      throw new Error(response.error || 'Failed to load agents');
    }

    return response.data;
  }

  async createAgent(agentData: any): Promise<any> {
    const response = await this.makeRequest<any>('/agents', {
      method: 'POST',
      body: JSON.stringify(agentData),
    });

    if (!response.success || !response.data) {
      throw new Error(response.error || 'Failed to create agent');
    }

    return response.data;
  }

  async updateAgent(agentId: string, agentData: any): Promise<void> {
    const response = await this.makeRequest(`/agents/${agentId}`, {
      method: 'PUT',
      body: JSON.stringify(agentData),
    });

    if (!response.success) {
      throw new Error(response.error || 'Failed to update agent');
    }
  }

  async deleteAgent(agentId: string): Promise<void> {
    const response = await this.makeRequest(`/agents/${agentId}`, {
      method: 'DELETE',
    });

    if (!response.success) {
      throw new Error(response.error || 'Failed to delete agent');
    }
  }

  // Health check
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    const response = await this.makeRequest<{ status: string; timestamp: string }>('/health');
    
    if (!response.success || !response.data) {
      throw new Error(response.error || 'Health check failed');
    }

    return response.data;
  }
}

export const apiService = new ApiService();

