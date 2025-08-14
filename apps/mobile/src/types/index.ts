// Core Types
export interface User {
  id: string;
  email: string;
  name: string;
  avatar?: string;
  subscription: SubscriptionTier;
  credits: number;
  preferences: UserPreferences;
  createdAt: string;
  lastLoginAt: string;
}

export interface UserPreferences {
  theme: 'light' | 'dark' | 'auto';
  language: string;
  notifications: NotificationSettings;
  defaultModel: string;
  voiceEnabled: boolean;
  biometricEnabled: boolean;
  autoSave: boolean;
  offlineMode: boolean;
}

export interface NotificationSettings {
  push: boolean;
  email: boolean;
  taskCompletion: boolean;
  systemUpdates: boolean;
  securityAlerts: boolean;
}

export type SubscriptionTier = 'free' | 'basic' | 'pro' | 'expert' | 'enterprise' | 'ultimate' | 'premium' | 'developer';

// Authentication Types
export interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  token: string | null;
  refreshToken: string | null;
  isLoading: boolean;
  error: string | null;
  biometricAvailable: boolean;
  biometricEnabled: boolean;
}

export interface LoginCredentials {
  email: string;
  password: string;
  rememberMe?: boolean;
  biometric?: boolean;
}

export interface RegisterData {
  name: string;
  email: string;
  password: string;
  confirmPassword: string;
  acceptTerms: boolean;
}

// Chat Types
export interface Message {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: Date;
  model?: string;
  tokens?: number;
  cost?: number;
  attachments?: MessageAttachment[];
  metadata?: MessageMetadata;
  status: MessageStatus;
}

export interface MessageAttachment {
  id: string;
  type: 'image' | 'document' | 'audio' | 'video';
  url: string;
  name: string;
  size: number;
  mimeType: string;
}

export interface MessageMetadata {
  processingTime: number;
  confidence: number;
  sources?: string[];
  reasoning?: string;
}

export type MessageStatus = 'sending' | 'sent' | 'delivered' | 'error' | 'processing';

export interface Conversation {
  id: string;
  title: string;
  messages: Message[];
  createdAt: string;
  updatedAt: string;
  model: string;
  totalTokens: number;
  totalCost: number;
  isArchived: boolean;
  tags: string[];
  projectId?: string;
}

export interface ChatState {
  conversations: Conversation[];
  activeConversationId: string | null;
  isLoading: boolean;
  isTyping: boolean;
  error: string | null;
  models: AIModel[];
  selectedModel: string;
}

// AI Model Types
export interface AIModel {
  id: string;
  name: string;
  provider: AIProvider;
  description: string;
  capabilities: ModelCapability[];
  pricing: ModelPricing;
  limits: ModelLimits;
  status: ModelStatus;
  version: string;
  isMultimodal: boolean;
  supportedLanguages: string[];
}

export interface AIProvider {
  id: string;
  name: string;
  logo: string;
  website: string;
  status: 'active' | 'maintenance' | 'deprecated';
}

export type ModelCapability = 'text' | 'image' | 'audio' | 'video' | 'code' | 'reasoning' | 'function_calling';

export interface ModelPricing {
  inputTokens: number; // per 1K tokens
  outputTokens: number; // per 1K tokens
  currency: string;
}

export interface ModelLimits {
  maxTokens: number;
  maxRequestsPerMinute: number;
  maxRequestsPerDay: number;
  contextWindow: number;
}

export type ModelStatus = 'available' | 'busy' | 'maintenance' | 'error';

// Agent Types
export interface Agent {
  id: string;
  name: string;
  description: string;
  type: AgentType;
  capabilities: AgentCapability[];
  status: AgentStatus;
  configuration: AgentConfiguration;
  metrics: AgentMetrics;
  createdAt: string;
  updatedAt: string;
}

export type AgentType = 'planner' | 'execution' | 'verification' | 'security' | 'optimization' | 'learning' | 'custom';

export type AgentCapability = 'task_planning' | 'tool_execution' | 'quality_control' | 'threat_detection' | 'performance_optimization' | 'learning_adaptation';

export type AgentStatus = 'active' | 'idle' | 'busy' | 'error' | 'maintenance';

export interface AgentConfiguration {
  model: string;
  temperature: number;
  maxTokens: number;
  tools: string[];
  permissions: AgentPermission[];
  schedule?: AgentSchedule;
}

export interface AgentPermission {
  resource: string;
  actions: string[];
  restrictions?: string[];
}

export interface AgentSchedule {
  enabled: boolean;
  cron: string;
  timezone: string;
}

export interface AgentMetrics {
  tasksCompleted: number;
  successRate: number;
  averageExecutionTime: number;
  tokensUsed: number;
  costIncurred: number;
  lastActivity: string;
}

// File Types
export interface FileItem {
  id: string;
  name: string;
  type: FileType;
  size: number;
  mimeType: string;
  url: string;
  thumbnailUrl?: string;
  uploadedAt: string;
  uploadedBy: string;
  projectId?: string;
  tags: string[];
  metadata: FileMetadata;
  status: FileStatus;
}

export type FileType = 'document' | 'image' | 'audio' | 'video' | 'archive' | 'code' | 'data';

export interface FileMetadata {
  dimensions?: { width: number; height: number };
  duration?: number; // for audio/video
  pages?: number; // for documents
  encoding?: string;
  checksum: string;
}

export type FileStatus = 'uploading' | 'processing' | 'ready' | 'error';

// Project Types
export interface Project {
  id: string;
  name: string;
  description: string;
  type: ProjectType;
  status: ProjectStatus;
  conversations: string[]; // conversation IDs
  files: string[]; // file IDs
  agents: string[]; // agent IDs
  artifacts: Artifact[];
  settings: ProjectSettings;
  createdAt: string;
  updatedAt: string;
  createdBy: string;
  collaborators: ProjectCollaborator[];
}

export type ProjectType = 'research' | 'development' | 'analysis' | 'automation' | 'creative' | 'business';

export type ProjectStatus = 'active' | 'completed' | 'paused' | 'archived';

export interface ProjectSettings {
  isPublic: boolean;
  allowCollaboration: boolean;
  autoSave: boolean;
  versionControl: boolean;
  backupEnabled: boolean;
}

export interface ProjectCollaborator {
  userId: string;
  role: 'owner' | 'admin' | 'editor' | 'viewer';
  permissions: string[];
  addedAt: string;
}

export interface Artifact {
  id: string;
  name: string;
  type: ArtifactType;
  content: string;
  version: number;
  createdAt: string;
  updatedAt: string;
  createdBy: string;
  tags: string[];
}

export type ArtifactType = 'document' | 'code' | 'image' | 'chart' | 'presentation' | 'report';

// Dashboard Types
export interface DashboardData {
  overview: DashboardOverview;
  usage: UsageMetrics;
  activity: ActivityItem[];
  alerts: AlertItem[];
  performance: PerformanceMetrics;
}

export interface DashboardOverview {
  totalTokens: number;
  totalCost: number;
  conversationsToday: number;
  activeAgents: number;
  systemHealth: SystemHealth;
  creditsRemaining: number;
}

export type SystemHealth = 'excellent' | 'good' | 'warning' | 'critical';

export interface UsageMetrics {
  daily: ChartData;
  weekly: ChartData;
  monthly: ChartData;
  modelUsage: ModelUsageData[];
  costBreakdown: CostBreakdownData[];
}

export interface ChartData {
  labels: string[];
  datasets: ChartDataset[];
}

export interface ChartDataset {
  label: string;
  data: number[];
  color: string;
}

export interface ModelUsageData {
  model: string;
  requests: number;
  tokens: number;
  cost: number;
  percentage: number;
}

export interface CostBreakdownData {
  category: string;
  amount: number;
  percentage: number;
  color: string;
}

export interface ActivityItem {
  id: string;
  type: ActivityType;
  description: string;
  timestamp: string;
  metadata?: Record<string, any>;
}

export type ActivityType = 'chat' | 'file_upload' | 'agent_created' | 'project_created' | 'security_alert' | 'system_update';

export interface AlertItem {
  id: string;
  type: AlertType;
  severity: AlertSeverity;
  title: string;
  message: string;
  timestamp: string;
  isRead: boolean;
  actionRequired: boolean;
  actionUrl?: string;
}

export type AlertType = 'security' | 'billing' | 'system' | 'usage' | 'maintenance';

export type AlertSeverity = 'info' | 'warning' | 'error' | 'critical';

export interface PerformanceMetrics {
  responseTime: number;
  uptime: number;
  errorRate: number;
  throughput: number;
  latency: LatencyMetrics;
}

export interface LatencyMetrics {
  p50: number;
  p95: number;
  p99: number;
}

// Navigation Types
export type RootStackParamList = {
  Splash: undefined;
  Auth: undefined;
  Main: undefined;
  Chat: { conversationId?: string };
  Dashboard: undefined;
  Agents: undefined;
  Files: undefined;
  Settings: undefined;
  Profile: undefined;
  Project: { projectId: string };
  ModelSelection: { onSelect: (modelId: string) => void };
  FileViewer: { fileId: string };
  AgentDetail: { agentId: string };
  Notifications: undefined;
  Billing: undefined;
  Help: undefined;
};

export type TabParamList = {
  Dashboard: undefined;
  Chat: undefined;
  Agents: undefined;
  Files: undefined;
  Settings: undefined;
};

// API Types
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
  pagination?: PaginationInfo;
}

export interface PaginationInfo {
  page: number;
  limit: number;
  total: number;
  totalPages: number;
  hasNext: boolean;
  hasPrev: boolean;
}

export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, any>;
  timestamp: string;
}

// Settings Types
export interface AppSettings {
  theme: ThemeSettings;
  notifications: NotificationSettings;
  privacy: PrivacySettings;
  performance: PerformanceSettings;
  accessibility: AccessibilitySettings;
}

export interface ThemeSettings {
  mode: 'light' | 'dark' | 'auto';
  primaryColor: string;
  accentColor: string;
  fontSize: 'small' | 'medium' | 'large';
}

export interface PrivacySettings {
  dataCollection: boolean;
  analytics: boolean;
  crashReporting: boolean;
  locationTracking: boolean;
  biometricData: boolean;
}

export interface PerformanceSettings {
  cacheSize: number;
  offlineMode: boolean;
  backgroundSync: boolean;
  imageQuality: 'low' | 'medium' | 'high';
  videoQuality: 'low' | 'medium' | 'high';
}

export interface AccessibilitySettings {
  screenReader: boolean;
  highContrast: boolean;
  largeText: boolean;
  reduceMotion: boolean;
  voiceControl: boolean;
}

// Utility Types
export interface LoadingState {
  isLoading: boolean;
  error: string | null;
  lastUpdated: string | null;
}

export interface PaginatedData<T> {
  items: T[];
  pagination: PaginationInfo;
}

export interface SearchFilters {
  query?: string;
  type?: string;
  dateRange?: {
    start: string;
    end: string;
  };
  tags?: string[];
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

export interface UploadProgress {
  fileId: string;
  progress: number;
  status: 'uploading' | 'processing' | 'completed' | 'error';
  error?: string;
}

// Redux Store Types
export interface RootState {
  auth: AuthState;
  chat: ChatState;
  dashboard: DashboardState;
  agents: AgentsState;
  files: FilesState;
  projects: ProjectsState;
  settings: SettingsState;
  ui: UIState;
}

export interface DashboardState extends LoadingState {
  data: DashboardData | null;
}

export interface AgentsState extends LoadingState {
  agents: Agent[];
  selectedAgent: Agent | null;
}

export interface FilesState extends LoadingState {
  files: FileItem[];
  uploadProgress: Record<string, UploadProgress>;
  selectedFiles: string[];
}

export interface ProjectsState extends LoadingState {
  projects: Project[];
  activeProject: Project | null;
}

export interface SettingsState {
  app: AppSettings;
  user: UserPreferences;
  isLoading: boolean;
  error: string | null;
}

export interface UIState {
  theme: 'light' | 'dark';
  isOnline: boolean;
  activeTab: string;
  modals: Record<string, boolean>;
  toasts: ToastMessage[];
}

export interface ToastMessage {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  duration?: number;
  action?: {
    label: string;
    onPress: () => void;
  };
}

