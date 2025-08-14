/**
 * Aideon Lite AI - Unified API Client
 * 
 * Cross-platform API client used by:
 * - Frontend (React)
 * - Mobile (React Native)
 * - Desktop (Electron)
 * - SDKs (All platforms)
 */

import { 
  ApiResponse, 
  ApiError, 
  ApiRequestOptions, 
  PaginatedResponse,
  User,
  Conversation,
  Message,
  AIModel,
  Project,
  Agent,
  FileUpload,
  Artifact,
  UsageMetrics,
  SystemHealth
} from '../types';

export interface AideonClientConfig {
  baseUrl: string;
  apiKey?: string;
  timeout?: number;
  retries?: number;
  userAgent?: string;
  environment?: 'development' | 'staging' | 'production';
}

export interface ChatRequest {
  message: string;
  model: string;
  conversationId?: string;
  temperature?: number;
  maxTokens?: number;
  stream?: boolean;
  systemPrompt?: string;
}

export interface ChatResponse {
  response: string;
  model: string;
  tokensUsed: number;
  cost: number;
  conversationId: string;
  messageId: string;
}

export class AideonClient {
  private config: Required<AideonClientConfig>;
  private authToken?: string;

  constructor(config: AideonClientConfig) {
    this.config = {
      baseUrl: config.baseUrl,
      apiKey: config.apiKey || '',
      timeout: config.timeout || 30000,
      retries: config.retries || 3,
      userAgent: config.userAgent || 'AideonClient/1.0.0',
      environment: config.environment || 'production',
    };
  }

  // ===== AUTHENTICATION =====

  async login(email: string, password: string): Promise<ApiResponse<{ token: string; user: User }>> {
    return this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  }

  async register(userData: {
    email: string;
    password: string;
    name: string;
  }): Promise<ApiResponse<{ token: string; user: User }>> {
    return this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  async refreshToken(): Promise<ApiResponse<{ token: string }>> {
    return this.request('/auth/refresh', {
      method: 'POST',
    });
  }

  async logout(): Promise<ApiResponse<void>> {
    const response = await this.request('/auth/logout', {
      method: 'POST',
    });
    
    if (response.success) {
      this.authToken = undefined;
    }
    
    return response;
  }

  setAuthToken(token: string): void {
    this.authToken = token;
  }

  clearAuthToken(): void {
    this.authToken = undefined;
  }

  // ===== CHAT =====

  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    const response = await this.request<ChatResponse>('/chat/send', {
      method: 'POST',
      body: JSON.stringify(request),
    });

    if (!response.success || !response.data) {
      throw new Error(response.error?.message || 'Failed to send message');
    }

    return response.data;
  }

  async *streamMessage(request: ChatRequest): AsyncGenerator<string, void, unknown> {
    const response = await fetch(`${this.config.baseUrl}/chat/stream`, {
      method: 'POST',
      headers: await this.getHeaders(),
      body: JSON.stringify({ ...request, stream: true }),
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('No response body');
    }

    const decoder = new TextDecoder();
    let buffer = '';

    try {
      while (true) {
        const { done, value } = await reader.read();
        
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data === '[DONE]') return;
            
            try {
              const parsed = JSON.parse(data);
              if (parsed.content) {
                yield parsed.content;
              }
            } catch (e) {
              console.warn('Failed to parse streaming response:', e);
            }
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  }

  async getConversations(options?: {
    page?: number;
    pageSize?: number;
    projectId?: string;
  }): Promise<PaginatedResponse<Conversation>> {
    const params = new URLSearchParams();
    if (options?.page) params.set('page', options.page.toString());
    if (options?.pageSize) params.set('pageSize', options.pageSize.toString());
    if (options?.projectId) params.set('projectId', options.projectId);

    const response = await this.request<PaginatedResponse<Conversation>>(
      `/chat/conversations?${params.toString()}`
    );

    if (!response.success || !response.data) {
      throw new Error(response.error?.message || 'Failed to get conversations');
    }

    return response.data;
  }

  async getConversation(conversationId: string): Promise<Conversation> {
    const response = await this.request<Conversation>(`/chat/conversations/${conversationId}`);

    if (!response.success || !response.data) {
      throw new Error(response.error?.message || 'Failed to get conversation');
    }

    return response.data;
  }

  async deleteConversation(conversationId: string): Promise<void> {
    const response = await this.request(`/chat/conversations/${conversationId}`, {
      method: 'DELETE',
    });

    if (!response.success) {
      throw new Error(response.error?.message || 'Failed to delete conversation');
    }
  }

  // ===== AI MODELS =====

  async getModels(): Promise<AIModel[]> {
    const response = await this.request<AIModel[]>('/models');

    if (!response.success || !response.data) {
      throw new Error(response.error?.message || 'Failed to get models');
    }

    return response.data;
  }

  async getModel(modelId: string): Promise<AIModel> {
    const response = await this.request<AIModel>(`/models/${modelId}`);

    if (!response.success || !response.data) {
      throw new Error(response.error?.message || 'Failed to get model');
    }

    return response.data;
  }

  // ===== PROJECTS =====

  async getProjects(options?: {
    page?: number;
    pageSize?: number;
  }): Promise<PaginatedResponse<Project>> {
    const params = new URLSearchParams();
    if (options?.page) params.set('page', options.page.toString());
    if (options?.pageSize) params.set('pageSize', options.pageSize.toString());

    const response = await this.request<PaginatedResponse<Project>>(
      `/projects?${params.toString()}`
    );

    if (!response.success || !response.data) {
      throw new Error(response.error?.message || 'Failed to get projects');
    }

    return response.data;
  }

  async createProject(projectData: {
    name: string;
    description: string;
  }): Promise<Project> {
    const response = await this.request<Project>('/projects', {
      method: 'POST',
      body: JSON.stringify(projectData),
    });

    if (!response.success || !response.data) {
      throw new Error(response.error?.message || 'Failed to create project');
    }

    return response.data;
  }

  async updateProject(projectId: string, updates: Partial<Project>): Promise<Project> {
    const response = await this.request<Project>(`/projects/${projectId}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    });

    if (!response.success || !response.data) {
      throw new Error(response.error?.message || 'Failed to update project');
    }

    return response.data;
  }

  async deleteProject(projectId: string): Promise<void> {
    const response = await this.request(`/projects/${projectId}`, {
      method: 'DELETE',
    });

    if (!response.success) {
      throw new Error(response.error?.message || 'Failed to delete project');
    }
  }

  // ===== FILES =====

  async uploadFile(file: File | Blob, options?: {
    projectId?: string;
    name?: string;
  }): Promise<FileUpload> {
    const formData = new FormData();
    formData.append('file', file);
    if (options?.projectId) formData.append('projectId', options.projectId);
    if (options?.name) formData.append('name', options.name);

    const headers = await this.getHeaders();
    delete headers['Content-Type']; // Let browser set it for FormData

    const response = await this.request<FileUpload>('/files/upload', {
      method: 'POST',
      body: formData,
      headers,
    });

    if (!response.success || !response.data) {
      throw new Error(response.error?.message || 'Failed to upload file');
    }

    return response.data;
  }

  async getFiles(options?: {
    projectId?: string;
    page?: number;
    pageSize?: number;
  }): Promise<PaginatedResponse<FileUpload>> {
    const params = new URLSearchParams();
    if (options?.projectId) params.set('projectId', options.projectId);
    if (options?.page) params.set('page', options.page.toString());
    if (options?.pageSize) params.set('pageSize', options.pageSize.toString());

    const response = await this.request<PaginatedResponse<FileUpload>>(
      `/files?${params.toString()}`
    );

    if (!response.success || !response.data) {
      throw new Error(response.error?.message || 'Failed to get files');
    }

    return response.data;
  }

  async deleteFile(fileId: string): Promise<void> {
    const response = await this.request(`/files/${fileId}`, {
      method: 'DELETE',
    });

    if (!response.success) {
      throw new Error(response.error?.message || 'Failed to delete file');
    }
  }

  // ===== AGENTS =====

  async getAgents(): Promise<Agent[]> {
    const response = await this.request<Agent[]>('/agents');

    if (!response.success || !response.data) {
      throw new Error(response.error?.message || 'Failed to get agents');
    }

    return response.data;
  }

  async createAgent(agentData: Partial<Agent>): Promise<Agent> {
    const response = await this.request<Agent>('/agents', {
      method: 'POST',
      body: JSON.stringify(agentData),
    });

    if (!response.success || !response.data) {
      throw new Error(response.error?.message || 'Failed to create agent');
    }

    return response.data;
  }

  async updateAgent(agentId: string, updates: Partial<Agent>): Promise<Agent> {
    const response = await this.request<Agent>(`/agents/${agentId}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    });

    if (!response.success || !response.data) {
      throw new Error(response.error?.message || 'Failed to update agent');
    }

    return response.data;
  }

  async deleteAgent(agentId: string): Promise<void> {
    const response = await this.request(`/agents/${agentId}`, {
      method: 'DELETE',
    });

    if (!response.success) {
      throw new Error(response.error?.message || 'Failed to delete agent');
    }
  }

  // ===== ANALYTICS =====

  async getUsageMetrics(period: 'hour' | 'day' | 'week' | 'month'): Promise<UsageMetrics[]> {
    const response = await this.request<UsageMetrics[]>(`/analytics/usage?period=${period}`);

    if (!response.success || !response.data) {
      throw new Error(response.error?.message || 'Failed to get usage metrics');
    }

    return response.data;
  }

  async getSystemHealth(): Promise<SystemHealth> {
    const response = await this.request<SystemHealth>('/health');

    if (!response.success || !response.data) {
      throw new Error(response.error?.message || 'Failed to get system health');
    }

    return response.data;
  }

  // ===== PRIVATE METHODS =====

  private async request<T = any>(
    endpoint: string,
    options: RequestInit & ApiRequestOptions = {}
  ): Promise<ApiResponse<T>> {
    const url = `${this.config.baseUrl}${endpoint}`;
    const headers = await this.getHeaders(options.headers);

    const requestOptions: RequestInit = {
      ...options,
      headers,
      signal: options.signal || AbortSignal.timeout(this.config.timeout),
    };

    let lastError: Error | null = null;

    for (let attempt = 0; attempt <= this.config.retries; attempt++) {
      try {
        const response = await fetch(url, requestOptions);
        
        if (!response.ok) {
          if (response.status === 401) {
            this.authToken = undefined;
            throw new Error('Authentication required');
          }
          
          const errorData = await response.json().catch(() => ({}));
          throw new Error(errorData.message || `HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        return {
          success: true,
          data,
          timestamp: new Date(),
          requestId: response.headers.get('x-request-id') || '',
        };

      } catch (error) {
        lastError = error instanceof Error ? error : new Error('Unknown error');
        
        if (attempt < this.config.retries && this.isRetryableError(lastError)) {
          await this.delay(Math.pow(2, attempt) * 1000);
          continue;
        }
        
        break;
      }
    }

    return {
      success: false,
      error: {
        code: 'REQUEST_FAILED',
        message: lastError?.message || 'Request failed',
        retryable: this.isRetryableError(lastError),
      },
      timestamp: new Date(),
      requestId: '',
    };
  }

  private async getHeaders(additionalHeaders?: Record<string, string>): Promise<Record<string, string>> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      'User-Agent': this.config.userAgent,
      ...additionalHeaders,
    };

    if (this.authToken) {
      headers['Authorization'] = `Bearer ${this.authToken}`;
    } else if (this.config.apiKey) {
      headers['X-API-Key'] = this.config.apiKey;
    }

    return headers;
  }

  private isRetryableError(error: Error | null): boolean {
    if (!error) return false;
    
    return (
      error.name === 'NetworkError' ||
      error.name === 'TimeoutError' ||
      error.message.includes('fetch') ||
      error.message.includes('network') ||
      error.message.includes('timeout')
    );
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

// ===== FACTORY FUNCTIONS =====

export function createAideonClient(config: AideonClientConfig): AideonClient {
  return new AideonClient(config);
}

export function createAideonClientWithDefaults(apiKey: string, environment?: 'development' | 'staging' | 'production'): AideonClient {
  const baseUrls = {
    development: 'http://localhost:3001',
    staging: 'https://api-staging.aideonlite.com',
    production: 'https://api.aideonlite.com',
  };

  return new AideonClient({
    baseUrl: baseUrls[environment || 'production'],
    apiKey,
    environment,
  });
}

// ===== EXPORTS =====

export default AideonClient;
export type { AideonClientConfig, ChatRequest, ChatResponse };

