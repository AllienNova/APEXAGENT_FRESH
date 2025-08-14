/**
 * ApexAgent Shared Types
 * 
 * Comprehensive TypeScript type definitions shared across all platforms:
 * - Backend API types
 * - Frontend component types
 * - Mobile application types
 * - SDK integration types
 * - WebSocket event types
 * - Analytics and monitoring types
 */

// ===== CORE SYSTEM TYPES =====

export interface User {
  uid: string;
  email: string;
  displayName?: string;
  photoURL?: string;
  emailVerified: boolean;
  isAnonymous: boolean;
  metadata: {
    creationTime: string;
    lastSignInTime: string;
  };
  customClaims?: Record<string, any>;
  preferences?: UserPreferences;
  subscription?: UserSubscription;
}

export interface UserPreferences {
  theme: 'light' | 'dark' | 'auto';
  language: string;
  timezone: string;
  notifications: NotificationSettings;
  privacy: PrivacySettings;
  accessibility: AccessibilitySettings;
}

export interface NotificationSettings {
  email: boolean;
  push: boolean;
  desktop: boolean;
  sound: boolean;
  vibration: boolean;
  types: {
    messages: boolean;
    agents: boolean;
    files: boolean;
    system: boolean;
    marketing: boolean;
  };
}

export interface PrivacySettings {
  analytics: boolean;
  crashReports: boolean;
  dataCollection: boolean;
  personalizedAds: boolean;
  shareUsageData: boolean;
}

export interface AccessibilitySettings {
  fontSize: 'small' | 'medium' | 'large' | 'extra-large';
  highContrast: boolean;
  reduceMotion: boolean;
  screenReader: boolean;
  voiceCommands: boolean;
}

export interface UserSubscription {
  plan: 'free' | 'pro' | 'enterprise';
  status: 'active' | 'canceled' | 'past_due' | 'unpaid';
  currentPeriodStart: string;
  currentPeriodEnd: string;
  cancelAtPeriodEnd: boolean;
  usage: UsageMetrics;
  limits: UsageLimits;
}

export interface UsageMetrics {
  tokensUsed: number;
  messagesCount: number;
  storageUsed: number;
  apiCalls: number;
  period: 'daily' | 'monthly' | 'yearly';
  resetDate: string;
}

export interface UsageLimits {
  maxTokens: number;
  maxMessages: number;
  maxStorage: number;
  maxApiCalls: number;
  maxProjects: number;
  maxAgents: number;
  features: string[];
}

// ===== AI MODEL TYPES =====

export interface AIModel {
  id: string;
  name: string;
  provider: AIProvider;
  description: string;
  capabilities: ModelCapabilities[];
  pricing: ModelPricing;
  limits: ModelLimits;
  status: 'available' | 'deprecated' | 'beta' | 'maintenance';
  metadata: ModelMetadata;
}

export type AIProvider = 
  | 'openai' 
  | 'anthropic' 
  | 'google' 
  | 'together' 
  | 'cohere' 
  | 'mistral' 
  | 'huggingface' 
  | 'custom';

export type ModelCapabilities = 
  | 'text-generation' 
  | 'code-generation' 
  | 'image-understanding' 
  | 'image-generation' 
  | 'audio-understanding' 
  | 'audio-generation' 
  | 'video-understanding' 
  | 'video-generation' 
  | 'function-calling' 
  | 'web-browsing' 
  | 'file-processing' 
  | 'reasoning' 
  | 'math' 
  | 'analysis';

export interface ModelPricing {
  inputTokens: number; // Cost per 1M tokens
  outputTokens: number; // Cost per 1M tokens
  imageInputs?: number; // Cost per image
  imageOutputs?: number; // Cost per image
  audioMinutes?: number; // Cost per minute
  videoMinutes?: number; // Cost per minute
  currency: string;
}

export interface ModelLimits {
  maxTokens: number;
  maxInputTokens: number;
  maxOutputTokens: number;
  maxImages?: number;
  maxAudioDuration?: number;
  maxVideoDuration?: number;
  rateLimits: {
    requestsPerMinute: number;
    tokensPerMinute: number;
    tokensPerDay?: number;
  };
}

export interface ModelMetadata {
  version: string;
  releaseDate: string;
  trainingData?: string;
  languages: string[];
  specializations: string[];
  benchmarks?: Record<string, number>;
  contextWindow: number;
  multimodal: boolean;
  streaming: boolean;
  functionCalling: boolean;
}

// ===== CHAT AND CONVERSATION TYPES =====

export interface Conversation {
  id: string;
  userId: string;
  projectId?: string;
  title: string;
  model: string;
  settings: ConversationSettings;
  createdAt: string;
  updatedAt: string;
  lastActiveAt: string;
  messageCount: number;
  totalTokens: number;
  totalCost: number;
  metadata: ConversationMetadata;
  tags: string[];
  isArchived: boolean;
  isStarred: boolean;
}

export interface ConversationSettings {
  temperature: number;
  maxTokens: number;
  topP?: number;
  frequencyPenalty?: number;
  presencePenalty?: number;
  systemPrompt?: string;
  stream: boolean;
  functions?: FunctionDefinition[];
  tools?: ToolDefinition[];
}

export interface ConversationMetadata {
  language: string;
  category: string;
  complexity: 'simple' | 'medium' | 'complex';
  sentiment: 'positive' | 'neutral' | 'negative';
  topics: string[];
  entities: string[];
  summary?: string;
}

export interface ChatMessage {
  id: string;
  conversationId: string;
  role: MessageRole;
  content: string;
  model?: string;
  timestamp: string;
  tokens?: TokenUsage;
  cost?: number;
  processingTime?: number;
  metadata?: MessageMetadata;
  attachments?: MessageAttachment[];
  reactions?: MessageReaction[];
  replyTo?: string;
  editHistory?: MessageEdit[];
  status: MessageStatus;
}

export type MessageRole = 'system' | 'user' | 'assistant' | 'function' | 'tool';

export type MessageStatus = 'sending' | 'sent' | 'delivered' | 'read' | 'failed' | 'deleted';

export interface TokenUsage {
  input: number;
  output: number;
  total: number;
  cached?: number;
}

export interface MessageMetadata {
  language?: string;
  sentiment?: 'positive' | 'neutral' | 'negative';
  confidence?: number;
  topics?: string[];
  entities?: string[];
  intent?: string;
  urgency?: 'low' | 'medium' | 'high';
  category?: string;
}

export interface MessageAttachment {
  id: string;
  type: 'image' | 'audio' | 'video' | 'document' | 'code' | 'data';
  name: string;
  url: string;
  size: number;
  mimeType: string;
  metadata?: Record<string, any>;
}

export interface MessageReaction {
  emoji: string;
  userId: string;
  timestamp: string;
}

export interface MessageEdit {
  content: string;
  timestamp: string;
  reason?: string;
}

// ===== AGENT TYPES =====

export interface Agent {
  id: string;
  name: string;
  type: AgentType;
  description: string;
  capabilities: AgentCapability[];
  model: string;
  systemPrompt: string;
  settings: AgentSettings;
  status: AgentStatus;
  performance: AgentPerformance;
  createdAt: string;
  updatedAt: string;
  userId: string;
  isPublic: boolean;
  tags: string[];
  version: string;
}

export type AgentType = 
  | 'general' 
  | 'coding' 
  | 'research' 
  | 'writing' 
  | 'analysis' 
  | 'creative' 
  | 'support' 
  | 'automation' 
  | 'specialized';

export type AgentCapability = 
  | 'text-processing' 
  | 'code-generation' 
  | 'web-browsing' 
  | 'file-processing' 
  | 'api-integration' 
  | 'data-analysis' 
  | 'image-processing' 
  | 'audio-processing' 
  | 'task-automation' 
  | 'learning' 
  | 'reasoning' 
  | 'planning';

export type AgentStatus = 
  | 'idle' 
  | 'active' 
  | 'busy' 
  | 'error' 
  | 'maintenance' 
  | 'offline';

export interface AgentSettings {
  temperature: number;
  maxTokens: number;
  timeout: number;
  retryAttempts: number;
  concurrency: number;
  priority: 'low' | 'medium' | 'high';
  resources: AgentResources;
  permissions: AgentPermissions;
}

export interface AgentResources {
  memory: number; // MB
  cpu: number; // Percentage
  storage: number; // MB
  network: boolean;
  gpu?: boolean;
}

export interface AgentPermissions {
  fileSystem: boolean;
  network: boolean;
  systemCommands: boolean;
  userData: boolean;
  externalAPIs: string[];
  restrictions: string[];
}

export interface AgentPerformance {
  totalTasks: number;
  completedTasks: number;
  failedTasks: number;
  averageResponseTime: number;
  successRate: number;
  uptime: number;
  lastActive: string;
  metrics: AgentMetrics;
}

export interface AgentMetrics {
  tokensProcessed: number;
  apiCalls: number;
  errorsCount: number;
  averageCost: number;
  userSatisfaction: number;
  efficiency: number;
}

// ===== PROJECT TYPES =====

export interface Project {
  id: string;
  name: string;
  description: string;
  userId: string;
  type: ProjectType;
  status: ProjectStatus;
  settings: ProjectSettings;
  files: ProjectFile[];
  conversations: string[];
  agents: string[];
  artifacts: ProjectArtifact[];
  collaborators: ProjectCollaborator[];
  createdAt: string;
  updatedAt: string;
  lastActiveAt: string;
  metadata: ProjectMetadata;
  tags: string[];
  isPublic: boolean;
  isArchived: boolean;
}

export type ProjectType = 
  | 'general' 
  | 'coding' 
  | 'research' 
  | 'writing' 
  | 'analysis' 
  | 'creative' 
  | 'business' 
  | 'education' 
  | 'personal';

export type ProjectStatus = 
  | 'active' 
  | 'paused' 
  | 'completed' 
  | 'archived' 
  | 'deleted';

export interface ProjectSettings {
  defaultModel: string;
  defaultAgent?: string;
  autoSave: boolean;
  versionControl: boolean;
  collaboration: boolean;
  privacy: 'private' | 'team' | 'public';
  backup: boolean;
  notifications: boolean;
}

export interface ProjectFile {
  id: string;
  name: string;
  path: string;
  type: FileType;
  size: number;
  mimeType: string;
  url: string;
  uploadedAt: string;
  uploadedBy: string;
  metadata: FileMetadata;
  processed: boolean;
  processingStatus?: ProcessingStatus;
  versions: FileVersion[];
}

export type FileType = 
  | 'document' 
  | 'image' 
  | 'audio' 
  | 'video' 
  | 'code' 
  | 'data' 
  | 'archive' 
  | 'other';

export type ProcessingStatus = 
  | 'pending' 
  | 'processing' 
  | 'completed' 
  | 'failed' 
  | 'skipped';

export interface FileMetadata {
  encoding?: string;
  language?: string;
  pages?: number;
  duration?: number;
  dimensions?: { width: number; height: number };
  extractedText?: string;
  summary?: string;
  tags?: string[];
  checksum: string;
}

export interface FileVersion {
  id: string;
  version: number;
  url: string;
  size: number;
  createdAt: string;
  createdBy: string;
  changes: string;
}

export interface ProjectArtifact {
  id: string;
  name: string;
  type: ArtifactType;
  content: string;
  metadata: ArtifactMetadata;
  createdAt: string;
  createdBy: string;
  conversationId?: string;
  messageId?: string;
  versions: ArtifactVersion[];
}

export type ArtifactType = 
  | 'code' 
  | 'document' 
  | 'image' 
  | 'chart' 
  | 'diagram' 
  | 'presentation' 
  | 'report' 
  | 'analysis' 
  | 'other';

export interface ArtifactMetadata {
  language?: string;
  framework?: string;
  format?: string;
  size: number;
  complexity: 'simple' | 'medium' | 'complex';
  quality: number;
  tags: string[];
}

export interface ArtifactVersion {
  id: string;
  version: number;
  content: string;
  createdAt: string;
  changes: string;
  parentVersion?: number;
}

export interface ProjectCollaborator {
  userId: string;
  role: CollaboratorRole;
  permissions: CollaboratorPermissions;
  addedAt: string;
  addedBy: string;
  lastActive?: string;
}

export type CollaboratorRole = 'owner' | 'admin' | 'editor' | 'viewer';

export interface CollaboratorPermissions {
  read: boolean;
  write: boolean;
  delete: boolean;
  share: boolean;
  admin: boolean;
  files: boolean;
  conversations: boolean;
  agents: boolean;
  settings: boolean;
}

export interface ProjectMetadata {
  category: string;
  complexity: 'simple' | 'medium' | 'complex';
  priority: 'low' | 'medium' | 'high';
  progress: number; // 0-100
  estimatedCompletion?: string;
  actualCompletion?: string;
  budget?: number;
  cost?: number;
  metrics: ProjectMetrics;
}

export interface ProjectMetrics {
  totalMessages: number;
  totalTokens: number;
  totalCost: number;
  totalFiles: number;
  totalArtifacts: number;
  activeAgents: number;
  collaborators: number;
  lastActivity: string;
}

// ===== FUNCTION AND TOOL TYPES =====

export interface FunctionDefinition {
  name: string;
  description: string;
  parameters: {
    type: 'object';
    properties: Record<string, ParameterDefinition>;
    required?: string[];
  };
}

export interface ParameterDefinition {
  type: 'string' | 'number' | 'boolean' | 'array' | 'object';
  description: string;
  enum?: string[];
  items?: ParameterDefinition;
  properties?: Record<string, ParameterDefinition>;
}

export interface ToolDefinition {
  type: 'function' | 'code_interpreter' | 'retrieval' | 'web_browser' | 'file_processor';
  function?: FunctionDefinition;
  config?: Record<string, any>;
}

export interface FunctionCall {
  name: string;
  arguments: string;
  result?: string;
  error?: string;
  executionTime?: number;
}

// ===== API TYPES =====

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: ApiError;
  metadata?: ResponseMetadata;
}

export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, any>;
  timestamp: string;
  requestId: string;
}

export interface ResponseMetadata {
  requestId: string;
  timestamp: string;
  processingTime: number;
  version: string;
  rateLimit?: RateLimitInfo;
}

export interface RateLimitInfo {
  limit: number;
  remaining: number;
  reset: string;
  retryAfter?: number;
}

export interface PaginationParams {
  page?: number;
  limit?: number;
  cursor?: string;
  sort?: string;
  order?: 'asc' | 'desc';
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    pages: number;
    hasNext: boolean;
    hasPrev: boolean;
    nextCursor?: string;
    prevCursor?: string;
  };
}

// ===== WEBSOCKET TYPES =====

export interface WebSocketMessage {
  type: WebSocketMessageType;
  data: any;
  timestamp: string;
  id: string;
}

export type WebSocketMessageType = 
  | 'message_received' 
  | 'message_updated' 
  | 'message_deleted' 
  | 'conversation_updated' 
  | 'agent_status_update' 
  | 'file_uploaded' 
  | 'file_processed' 
  | 'project_updated' 
  | 'user_joined' 
  | 'user_left' 
  | 'typing_start' 
  | 'typing_stop' 
  | 'system_notification' 
  | 'error';

export interface TypingIndicator {
  userId: string;
  conversationId: string;
  isTyping: boolean;
  timestamp: string;
}

export interface SystemNotification {
  type: 'info' | 'warning' | 'error' | 'success';
  title: string;
  message: string;
  action?: NotificationAction;
  persistent?: boolean;
  timestamp: string;
}

export interface NotificationAction {
  label: string;
  url?: string;
  callback?: string;
}

// ===== ANALYTICS TYPES =====

export interface AnalyticsEvent {
  name: string;
  properties: Record<string, any>;
  userId?: string;
  sessionId: string;
  timestamp: string;
  platform: 'web' | 'mobile' | 'desktop' | 'api';
  version: string;
}

export interface UserSession {
  id: string;
  userId?: string;
  startTime: string;
  endTime?: string;
  duration?: number;
  platform: string;
  device: DeviceInfo;
  location?: LocationInfo;
  events: AnalyticsEvent[];
}

export interface DeviceInfo {
  type: 'desktop' | 'mobile' | 'tablet';
  os: string;
  browser?: string;
  version: string;
  screen: {
    width: number;
    height: number;
    density: number;
  };
}

export interface LocationInfo {
  country: string;
  region: string;
  city: string;
  timezone: string;
  coordinates?: {
    latitude: number;
    longitude: number;
  };
}

export interface PerformanceMetrics {
  pageLoadTime?: number;
  apiResponseTime: number;
  renderTime?: number;
  memoryUsage?: number;
  cpuUsage?: number;
  networkLatency?: number;
  errorRate: number;
  uptime: number;
}

// ===== SECURITY TYPES =====

export interface SecurityEvent {
  type: SecurityEventType;
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  userId?: string;
  ip: string;
  userAgent: string;
  timestamp: string;
  metadata: Record<string, any>;
}

export type SecurityEventType = 
  | 'login_attempt' 
  | 'login_success' 
  | 'login_failure' 
  | 'logout' 
  | 'password_change' 
  | 'account_locked' 
  | 'suspicious_activity' 
  | 'data_access' 
  | 'permission_change' 
  | 'api_abuse' 
  | 'injection_attempt' 
  | 'malware_detected';

export interface ThreatDetection {
  id: string;
  type: ThreatType;
  severity: 'low' | 'medium' | 'high' | 'critical';
  confidence: number;
  description: string;
  indicators: string[];
  mitigation: string[];
  timestamp: string;
  resolved: boolean;
}

export type ThreatType = 
  | 'malware' 
  | 'phishing' 
  | 'injection' 
  | 'brute_force' 
  | 'ddos' 
  | 'data_breach' 
  | 'unauthorized_access' 
  | 'privilege_escalation';

// ===== BILLING TYPES =====

export interface BillingInfo {
  customerId: string;
  subscriptionId?: string;
  plan: SubscriptionPlan;
  status: BillingStatus;
  currentPeriod: BillingPeriod;
  usage: BillingUsage;
  paymentMethod?: PaymentMethod;
  invoices: Invoice[];
  credits: number;
}

export interface SubscriptionPlan {
  id: string;
  name: string;
  price: number;
  currency: string;
  interval: 'month' | 'year';
  features: string[];
  limits: UsageLimits;
}

export type BillingStatus = 
  | 'active' 
  | 'past_due' 
  | 'canceled' 
  | 'unpaid' 
  | 'incomplete' 
  | 'trialing';

export interface BillingPeriod {
  start: string;
  end: string;
  daysRemaining: number;
}

export interface BillingUsage {
  tokens: number;
  messages: number;
  storage: number;
  apiCalls: number;
  cost: number;
  period: string;
}

export interface PaymentMethod {
  id: string;
  type: 'card' | 'bank' | 'paypal' | 'crypto';
  last4?: string;
  brand?: string;
  expiryMonth?: number;
  expiryYear?: number;
  isDefault: boolean;
}

export interface Invoice {
  id: string;
  number: string;
  amount: number;
  currency: string;
  status: 'draft' | 'open' | 'paid' | 'void' | 'uncollectible';
  createdAt: string;
  dueDate: string;
  paidAt?: string;
  url: string;
  items: InvoiceItem[];
}

export interface InvoiceItem {
  description: string;
  quantity: number;
  unitPrice: number;
  amount: number;
  period?: {
    start: string;
    end: string;
  };
}

// ===== UTILITY TYPES =====

export type Timestamp = string; // ISO 8601 format
export type UUID = string;
export type URL = string;
export type Email = string;
export type JSONValue = string | number | boolean | null | JSONObject | JSONArray;
export type JSONObject = { [key: string]: JSONValue };
export type JSONArray = JSONValue[];

export interface BaseEntity {
  id: UUID;
  createdAt: Timestamp;
  updatedAt: Timestamp;
}

export interface SoftDeleteEntity extends BaseEntity {
  deletedAt?: Timestamp;
  isDeleted: boolean;
}

export interface AuditableEntity extends BaseEntity {
  createdBy: UUID;
  updatedBy: UUID;
  version: number;
}

// ===== EXPORT ALL TYPES =====

export * from './api';
export * from './auth';
export * from './chat';
export * from './agents';
export * from './projects';
export * from './files';
export * from './analytics';
export * from './websocket';
export * from './security';
export * from './billing';

