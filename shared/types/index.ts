/**
 * Aideon Lite AI - Shared Type Definitions
 * 
 * Comprehensive TypeScript definitions used across all platforms:
 * - Frontend (React)
 * - Mobile (React Native)
 * - Desktop (Electron)
 * - Backend (Node.js/TypeScript)
 * - SDKs (All platforms)
 */

// ===== AUTHENTICATION TYPES =====

export interface User {
  id: string;
  email: string;
  name: string;
  avatar?: string;
  role: UserRole;
  subscription: SubscriptionTier;
  preferences: UserPreferences;
  createdAt: Date;
  updatedAt: Date;
}

export type UserRole = 'user' | 'admin' | 'developer' | 'enterprise';

export type SubscriptionTier = 'free' | 'pro' | 'enterprise' | 'custom';

export interface UserPreferences {
  theme: 'light' | 'dark' | 'auto';
  language: string;
  timezone: string;
  notifications: NotificationPreferences;
  defaultModel: string;
  autoSave: boolean;
}

export interface NotificationPreferences {
  email: boolean;
  push: boolean;
  desktop: boolean;
  sound: boolean;
}

export interface AuthToken {
  accessToken: string;
  refreshToken: string;
  expiresAt: Date;
  tokenType: 'Bearer';
}

// ===== AI MODEL TYPES =====

export interface AIModel {
  id: string;
  name: string;
  provider: AIProvider;
  category: ModelCategory;
  capabilities: ModelCapability[];
  pricing: ModelPricing;
  limits: ModelLimits;
  status: ModelStatus;
  description: string;
  version: string;
}

export type AIProvider = 
  | 'openai' 
  | 'anthropic' 
  | 'google' 
  | 'together' 
  | 'cohere' 
  | 'mistral' 
  | 'huggingface';

export type ModelCategory = 
  | 'chat' 
  | 'completion' 
  | 'embedding' 
  | 'image' 
  | 'audio' 
  | 'video' 
  | 'code' 
  | 'reasoning';

export type ModelCapability = 
  | 'text' 
  | 'image' 
  | 'audio' 
  | 'video' 
  | 'code' 
  | 'function_calling' 
  | 'json_mode' 
  | 'streaming';

export interface ModelPricing {
  inputTokens: number; // Cost per 1M input tokens
  outputTokens: number; // Cost per 1M output tokens
  currency: 'USD';
}

export interface ModelLimits {
  maxTokens: number;
  maxRequestsPerMinute: number;
  maxRequestsPerDay: number;
  contextWindow: number;
}

export type ModelStatus = 'active' | 'deprecated' | 'beta' | 'maintenance';

// ===== CHAT TYPES =====

export interface Conversation {
  id: string;
  title: string;
  userId: string;
  projectId?: string;
  messages: Message[];
  model: string;
  settings: ConversationSettings;
  metadata: ConversationMetadata;
  createdAt: Date;
  updatedAt: Date;
}

export interface Message {
  id: string;
  conversationId: string;
  content: string;
  role: MessageRole;
  model?: string;
  tokens?: TokenUsage;
  attachments?: Attachment[];
  metadata: MessageMetadata;
  createdAt: Date;
}

export type MessageRole = 'user' | 'assistant' | 'system' | 'function';

export interface TokenUsage {
  input: number;
  output: number;
  total: number;
  cost: number;
}

export interface ConversationSettings {
  temperature: number;
  maxTokens: number;
  topP: number;
  frequencyPenalty: number;
  presencePenalty: number;
  systemPrompt?: string;
}

export interface ConversationMetadata {
  totalTokens: number;
  totalCost: number;
  messageCount: number;
  lastActiveAt: Date;
  tags: string[];
}

export interface MessageMetadata {
  processingTime: number;
  retryCount: number;
  cached: boolean;
  reasoning?: string;
}

// ===== FILE TYPES =====

export interface FileUpload {
  id: string;
  name: string;
  size: number;
  type: string;
  url: string;
  userId: string;
  projectId?: string;
  status: FileStatus;
  metadata: FileMetadata;
  createdAt: Date;
  updatedAt: Date;
}

export type FileStatus = 'uploading' | 'processing' | 'ready' | 'error';

export interface FileMetadata {
  mimeType: string;
  encoding?: string;
  dimensions?: { width: number; height: number };
  duration?: number; // For audio/video files
  pages?: number; // For document files
  extractedText?: string;
  analysis?: FileAnalysis;
}

export interface FileAnalysis {
  summary: string;
  keyPoints: string[];
  sentiment?: 'positive' | 'negative' | 'neutral';
  language?: string;
  topics?: string[];
}

export interface Attachment {
  id: string;
  fileId: string;
  name: string;
  url: string;
  type: string;
  size: number;
}

// ===== PROJECT TYPES =====

export interface Project {
  id: string;
  name: string;
  description: string;
  userId: string;
  collaborators: ProjectCollaborator[];
  conversations: string[]; // Conversation IDs
  files: string[]; // File IDs
  artifacts: Artifact[];
  settings: ProjectSettings;
  metadata: ProjectMetadata;
  createdAt: Date;
  updatedAt: Date;
}

export interface ProjectCollaborator {
  userId: string;
  role: 'owner' | 'editor' | 'viewer';
  permissions: ProjectPermission[];
  addedAt: Date;
}

export type ProjectPermission = 
  | 'read' 
  | 'write' 
  | 'delete' 
  | 'share' 
  | 'manage_collaborators';

export interface ProjectSettings {
  isPublic: boolean;
  allowCollaboration: boolean;
  autoSave: boolean;
  versionControl: boolean;
  defaultModel: string;
}

export interface ProjectMetadata {
  totalConversations: number;
  totalFiles: number;
  totalTokens: number;
  totalCost: number;
  lastActiveAt: Date;
  tags: string[];
}

// ===== ARTIFACT TYPES =====

export interface Artifact {
  id: string;
  name: string;
  type: ArtifactType;
  content: string;
  language?: string; // For code artifacts
  projectId: string;
  conversationId: string;
  messageId: string;
  version: number;
  versions: ArtifactVersion[];
  metadata: ArtifactMetadata;
  createdAt: Date;
  updatedAt: Date;
}

export type ArtifactType = 
  | 'code' 
  | 'document' 
  | 'image' 
  | 'chart' 
  | 'diagram' 
  | 'presentation' 
  | 'website' 
  | 'data';

export interface ArtifactVersion {
  version: number;
  content: string;
  changes: string;
  createdAt: Date;
}

export interface ArtifactMetadata {
  size: number;
  lineCount?: number; // For code/text artifacts
  wordCount?: number; // For document artifacts
  dependencies?: string[]; // For code artifacts
  exports?: string[]; // For code artifacts
}

// ===== AGENT TYPES =====

export interface Agent {
  id: string;
  name: string;
  description: string;
  type: AgentType;
  capabilities: AgentCapability[];
  model: string;
  prompt: string;
  settings: AgentSettings;
  status: AgentStatus;
  metrics: AgentMetrics;
  createdAt: Date;
  updatedAt: Date;
}

export type AgentType = 
  | 'planner' 
  | 'executor' 
  | 'verifier' 
  | 'security' 
  | 'optimizer' 
  | 'learner' 
  | 'custom';

export type AgentCapability = 
  | 'reasoning' 
  | 'code_execution' 
  | 'file_processing' 
  | 'web_browsing' 
  | 'image_analysis' 
  | 'data_analysis' 
  | 'security_audit';

export interface AgentSettings {
  temperature: number;
  maxTokens: number;
  timeout: number; // in seconds
  retryAttempts: number;
  parallelExecution: boolean;
}

export type AgentStatus = 'idle' | 'active' | 'busy' | 'error' | 'offline';

export interface AgentMetrics {
  totalTasks: number;
  successfulTasks: number;
  failedTasks: number;
  averageResponseTime: number;
  totalTokensUsed: number;
  totalCost: number;
  lastActiveAt: Date;
}

// ===== API TYPES =====

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: ApiError;
  message?: string;
  timestamp: Date;
  requestId: string;
}

export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, any>;
  retryable: boolean;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  hasNext: boolean;
  hasPrevious: boolean;
}

export interface ApiRequestOptions {
  timeout?: number;
  retries?: number;
  headers?: Record<string, string>;
  signal?: AbortSignal;
}

// ===== ANALYTICS TYPES =====

export interface AnalyticsEvent {
  id: string;
  userId: string;
  sessionId: string;
  event: string;
  properties: Record<string, any>;
  timestamp: Date;
}

export interface UsageMetrics {
  totalTokens: number;
  totalCost: number;
  totalConversations: number;
  totalFiles: number;
  activeUsers: number;
  period: 'hour' | 'day' | 'week' | 'month';
  timestamp: Date;
}

export interface SystemHealth {
  status: 'healthy' | 'degraded' | 'down';
  uptime: number;
  responseTime: number;
  errorRate: number;
  activeConnections: number;
  timestamp: Date;
}

// ===== UTILITY TYPES =====

export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

export type RequiredFields<T, K extends keyof T> = T & Required<Pick<T, K>>;

export type OptionalFields<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;

export type Timestamp = Date | string | number;

export interface BaseEntity {
  id: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface AuditableEntity extends BaseEntity {
  createdBy: string;
  updatedBy: string;
}

// ===== CONFIGURATION TYPES =====

export interface AppConfig {
  api: {
    baseUrl: string;
    timeout: number;
    retries: number;
  };
  features: {
    enableOfflineMode: boolean;
    enableAnalytics: boolean;
    enableBiometricAuth: boolean;
    enablePushNotifications: boolean;
  };
  limits: {
    maxFileSize: number;
    maxFilesPerProject: number;
    maxConversationsPerProject: number;
  };
}

export interface Environment {
  NODE_ENV: 'development' | 'staging' | 'production';
  API_BASE_URL: string;
  WS_BASE_URL: string;
  SENTRY_DSN?: string;
  ANALYTICS_KEY?: string;
}

// ===== EXPORT ALL TYPES =====

export * from './auth';
export * from './chat';
export * from './files';
export * from './projects';
export * from './agents';
export * from './analytics';

