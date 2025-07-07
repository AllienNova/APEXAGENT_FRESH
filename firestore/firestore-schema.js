/**
 * Aideon AI Lite Firestore Data Model
 * Purpose: Real-time analytics, user sessions, and NoSQL data storage
 * Complements: Cloud SQL (transactional) + BigQuery (analytics warehouse)
 */

// =============================================
// COLLECTION STRUCTURE OVERVIEW
// =============================================

/*
Root Collections:
├── users/{userId}                          - User profiles and real-time data
│   ├── sessions/{sessionId}               - Active user sessions
│   ├── preferences/{category}             - User preferences and settings
│   ├── activity/{activityId}              - Real-time user activity
│   └── notifications/{notificationId}     - Real-time notifications
├── projects/{projectId}                   - Project real-time data
│   ├── collaborators/{userId}             - Real-time collaboration
│   ├── activity/{activityId}              - Project activity feed
│   └── files/{fileId}                     - File metadata and versions
├── analytics/{type}                       - Real-time analytics data
│   ├── events/{eventId}                   - Real-time event tracking
│   ├── metrics/{metricId}                 - Live performance metrics
│   └── dashboards/{dashboardId}           - Dashboard configurations
├── chat/{conversationId}                  - AI chat conversations
│   └── messages/{messageId}               - Individual chat messages
├── system/{component}                     - System-wide real-time data
│   ├── health/{checkId}                   - System health monitoring
│   ├── alerts/{alertId}                   - Real-time system alerts
│   └── config/{configKey}                 - Dynamic configuration
└── realtime/{dataType}                    - General real-time data streams
    ├── usage/{timestamp}                  - Real-time usage statistics
    ├── performance/{timestamp}            - Live performance data
    └── errors/{errorId}                   - Real-time error tracking
*/

// =============================================
// DOCUMENT SCHEMAS AND VALIDATION RULES
// =============================================

const firestoreSchema = {
  // User real-time data
  users: {
    // Document ID: userId (matches Cloud SQL users.id)
    schema: {
      // Basic profile (synced from Cloud SQL)
      email: "string",
      displayName: "string",
      avatarUrl: "string",
      status: "string", // 'online', 'away', 'busy', 'offline'
      
      // Real-time presence
      lastSeen: "timestamp",
      currentSession: "string", // sessionId
      activeProjects: ["string"], // array of projectIds
      
      // Real-time preferences
      preferences: {
        theme: "string",
        language: "string",
        notifications: {
          email: "boolean",
          push: "boolean",
          desktop: "boolean",
          sound: "boolean"
        },
        dashboard: {
          layout: "string",
          widgets: ["object"]
        }
      },
      
      // Real-time statistics
      stats: {
        totalSessions: "number",
        totalApiCalls: "number",
        totalCreditsUsed: "number",
        averageSessionDuration: "number",
        lastActivityType: "string",
        streakDays: "number"
      },
      
      // Metadata
      createdAt: "timestamp",
      updatedAt: "timestamp"
    },
    
    // Subcollections
    subcollections: {
      sessions: {
        // Document ID: sessionId
        schema: {
          sessionToken: "string",
          deviceInfo: {
            type: "string", // 'desktop', 'mobile', 'tablet'
            os: "string",
            browser: "string",
            userAgent: "string"
          },
          location: {
            ip: "string",
            country: "string",
            city: "string",
            timezone: "string"
          },
          startTime: "timestamp",
          lastActivity: "timestamp",
          isActive: "boolean",
          activities: ["object"], // Recent activities in this session
          apiCallsCount: "number",
          creditsUsed: "number"
        }
      },
      
      activity: {
        // Document ID: activityId
        schema: {
          type: "string", // 'login', 'api_call', 'project_create', 'file_upload', etc.
          description: "string",
          metadata: "object", // Activity-specific data
          projectId: "string", // Optional
          sessionId: "string",
          timestamp: "timestamp",
          impact: "string" // 'low', 'medium', 'high'
        }
      },
      
      notifications: {
        // Document ID: notificationId
        schema: {
          type: "string", // 'info', 'warning', 'error', 'success'
          title: "string",
          message: "string",
          actionUrl: "string", // Optional
          actionText: "string", // Optional
          isRead: "boolean",
          isPersistent: "boolean", // Whether to keep after reading
          expiresAt: "timestamp", // Optional
          createdAt: "timestamp"
        }
      }
    }
  },
  
  // Project real-time collaboration
  projects: {
    // Document ID: projectId (matches Cloud SQL projects.id)
    schema: {
      // Basic info (synced from Cloud SQL)
      name: "string",
      description: "string",
      ownerId: "string",
      
      // Real-time collaboration
      activeCollaborators: ["string"], // userIds currently active
      lastActivity: "timestamp",
      activityCount: "number",
      
      // Real-time statistics
      stats: {
        totalFiles: "number",
        totalSize: "number",
        totalApiCalls: "number",
        totalCreditsUsed: "number",
        collaboratorCount: "number",
        lastModified: "timestamp"
      },
      
      // Real-time settings
      settings: {
        isPublic: "boolean",
        allowComments: "boolean",
        autoSave: "boolean",
        collaborationMode: "string", // 'open', 'restricted', 'private'
        notifications: {
          onFileChange: "boolean",
          onCollaboratorJoin: "boolean",
          onComment: "boolean"
        }
      },
      
      // Metadata
      createdAt: "timestamp",
      updatedAt: "timestamp"
    },
    
    subcollections: {
      collaborators: {
        // Document ID: userId
        schema: {
          role: "string", // 'owner', 'editor', 'viewer'
          permissions: ["string"],
          joinedAt: "timestamp",
          lastSeen: "timestamp",
          isActive: "boolean",
          currentFile: "string", // fileId currently editing
          cursor: {
            fileId: "string",
            position: "object" // Line/column or coordinates
          },
          stats: {
            totalEdits: "number",
            totalComments: "number",
            timeSpent: "number" // milliseconds
          }
        }
      },
      
      activity: {
        // Document ID: activityId
        schema: {
          userId: "string",
          type: "string", // 'file_create', 'file_edit', 'comment_add', 'collaborator_join'
          description: "string",
          fileId: "string", // Optional
          metadata: "object",
          timestamp: "timestamp"
        }
      },
      
      files: {
        // Document ID: fileId
        schema: {
          name: "string",
          path: "string",
          type: "string",
          size: "number",
          
          // Real-time editing
          isLocked: "boolean",
          lockedBy: "string", // userId
          lockExpires: "timestamp",
          currentEditors: ["string"], // userIds
          
          // Version control
          version: "number",
          lastModified: "timestamp",
          lastModifiedBy: "string",
          
          // Content preview (for small files)
          preview: "string", // First 1000 chars
          
          // Metadata
          metadata: "object",
          tags: ["string"]
        }
      }
    }
  },
  
  // Real-time analytics
  analytics: {
    events: {
      // Document ID: eventId
      schema: {
        userId: "string",
        sessionId: "string",
        projectId: "string", // Optional
        
        // Event details
        type: "string", // 'page_view', 'api_call', 'error', 'conversion'
        category: "string", // 'user_action', 'system_event', 'business_metric'
        action: "string",
        label: "string", // Optional
        value: "number", // Optional
        
        // Context
        page: "string",
        referrer: "string",
        userAgent: "string",
        
        // Custom properties
        properties: "object",
        
        // Timing
        timestamp: "timestamp",
        duration: "number" // milliseconds
      }
    },
    
    metrics: {
      // Document ID: metricId (timestamp-based for time series)
      schema: {
        // Metric identification
        name: "string", // 'active_users', 'api_calls_per_minute', 'error_rate'
        category: "string", // 'performance', 'usage', 'business', 'system'
        
        // Metric values
        value: "number",
        unit: "string", // 'count', 'percentage', 'milliseconds', 'bytes'
        
        // Dimensions
        dimensions: {
          userId: "string", // Optional
          projectId: "string", // Optional
          provider: "string", // Optional
          region: "string", // Optional
          custom: "object" // Additional dimensions
        },
        
        // Aggregation info
        aggregationType: "string", // 'sum', 'avg', 'count', 'max', 'min'
        timeWindow: "string", // '1m', '5m', '1h', '1d'
        
        // Metadata
        timestamp: "timestamp",
        source: "string" // 'frontend', 'backend', 'system'
      }
    },
    
    dashboards: {
      // Document ID: dashboardId
      schema: {
        userId: "string",
        name: "string",
        description: "string",
        
        // Dashboard configuration
        layout: "object", // Grid layout configuration
        widgets: [{
          id: "string",
          type: "string", // 'chart', 'metric', 'table', 'text'
          title: "string",
          config: "object", // Widget-specific configuration
          position: {
            x: "number",
            y: "number",
            width: "number",
            height: "number"
          },
          dataSource: {
            type: "string", // 'firestore', 'bigquery', 'cloudsql'
            query: "string",
            refreshInterval: "number" // seconds
          }
        }],
        
        // Settings
        isPublic: "boolean",
        autoRefresh: "boolean",
        refreshInterval: "number", // seconds
        
        // Metadata
        createdAt: "timestamp",
        updatedAt: "timestamp",
        lastViewed: "timestamp"
      }
    }
  },
  
  // AI Chat conversations
  chat: {
    // Document ID: conversationId
    schema: {
      userId: "string",
      projectId: "string", // Optional
      
      // Conversation metadata
      title: "string",
      model: "string", // AI model used
      provider: "string", // 'openai', 'anthropic', etc.
      
      // Statistics
      messageCount: "number",
      totalTokens: "number",
      totalCost: "number",
      
      // Settings
      settings: {
        temperature: "number",
        maxTokens: "number",
        systemPrompt: "string"
      },
      
      // Status
      isActive: "boolean",
      lastMessage: "timestamp",
      
      // Metadata
      createdAt: "timestamp",
      updatedAt: "timestamp"
    },
    
    subcollections: {
      messages: {
        // Document ID: messageId
        schema: {
          role: "string", // 'user', 'assistant', 'system'
          content: "string",
          
          // AI response metadata
          model: "string",
          tokens: {
            input: "number",
            output: "number",
            total: "number"
          },
          cost: "number",
          responseTime: "number", // milliseconds
          
          // Message metadata
          timestamp: "timestamp",
          edited: "boolean",
          editHistory: ["object"], // Previous versions
          
          // Attachments
          attachments: [{
            type: "string", // 'file', 'image', 'code'
            url: "string",
            name: "string",
            size: "number"
          }]
        }
      }
    }
  },
  
  // System monitoring
  system: {
    health: {
      // Document ID: checkId (timestamp-based)
      schema: {
        component: "string", // 'database', 'api', 'storage', 'auth'
        status: "string", // 'healthy', 'degraded', 'unhealthy'
        
        // Metrics
        responseTime: "number", // milliseconds
        uptime: "number", // percentage
        errorRate: "number", // percentage
        
        // Details
        message: "string",
        details: "object",
        
        // Metadata
        timestamp: "timestamp",
        region: "string"
      }
    },
    
    alerts: {
      // Document ID: alertId
      schema: {
        type: "string", // 'error', 'warning', 'info'
        severity: "string", // 'critical', 'high', 'medium', 'low'
        component: "string",
        
        // Alert details
        title: "string",
        message: "string",
        details: "object",
        
        // Status
        status: "string", // 'active', 'acknowledged', 'resolved'
        acknowledgedBy: "string", // userId
        acknowledgedAt: "timestamp",
        resolvedAt: "timestamp",
        
        // Metadata
        createdAt: "timestamp",
        updatedAt: "timestamp"
      }
    },
    
    config: {
      // Document ID: configKey
      schema: {
        key: "string",
        value: "object", // Any JSON value
        description: "string",
        
        // Validation
        schema: "object", // JSON schema for validation
        
        // Access control
        isPublic: "boolean",
        requiredRole: "string", // Minimum role to modify
        
        // Metadata
        createdAt: "timestamp",
        updatedAt: "timestamp",
        updatedBy: "string" // userId
      }
    }
  },
  
  // Real-time data streams
  realtime: {
    usage: {
      // Document ID: timestamp (minute-based: YYYY-MM-DD-HH-MM)
      schema: {
        // Usage metrics
        activeUsers: "number",
        totalSessions: "number",
        apiCallsPerMinute: "number",
        creditsUsedPerMinute: "number",
        
        // Performance metrics
        averageResponseTime: "number",
        errorRate: "number",
        
        // Business metrics
        newSignups: "number",
        conversions: "number",
        revenue: "number",
        
        // System metrics
        cpuUsage: "number",
        memoryUsage: "number",
        diskUsage: "number",
        
        // Metadata
        timestamp: "timestamp",
        region: "string"
      }
    },
    
    performance: {
      // Document ID: timestamp (second-based for high frequency)
      schema: {
        // Response times
        apiResponseTime: "number",
        databaseResponseTime: "number",
        cacheHitRate: "number",
        
        // Throughput
        requestsPerSecond: "number",
        queriesPerSecond: "number",
        
        // Errors
        errorCount: "number",
        errorRate: "number",
        
        // Resource usage
        cpuUsage: "number",
        memoryUsage: "number",
        networkIO: "number",
        diskIO: "number",
        
        // Metadata
        timestamp: "timestamp",
        source: "string" // 'frontend', 'backend', 'database'
      }
    },
    
    errors: {
      // Document ID: errorId
      schema: {
        // Error details
        type: "string", // 'javascript', 'api', 'database', 'system'
        message: "string",
        stack: "string",
        
        // Context
        userId: "string", // Optional
        sessionId: "string", // Optional
        url: "string",
        userAgent: "string",
        
        // Request details
        method: "string",
        endpoint: "string",
        statusCode: "number",
        
        // Additional data
        metadata: "object",
        
        // Status
        status: "string", // 'new', 'investigating', 'resolved'
        assignedTo: "string", // userId
        
        // Metadata
        timestamp: "timestamp",
        count: "number", // How many times this error occurred
        lastOccurrence: "timestamp"
      }
    }
  }
};

// =============================================
// FIRESTORE SECURITY RULES TEMPLATE
// =============================================

const securityRules = `
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    
    // Helper functions
    function isAuthenticated() {
      return request.auth != null;
    }
    
    function isOwner(userId) {
      return isAuthenticated() && request.auth.uid == userId;
    }
    
    function isAdmin() {
      return isAuthenticated() && 
             get(/databases/$(database)/documents/users/$(request.auth.uid)).data.role == 'admin';
    }
    
    function isProjectCollaborator(projectId) {
      return isAuthenticated() && 
             exists(/databases/$(database)/documents/projects/$(projectId)/collaborators/$(request.auth.uid));
    }
    
    // User documents - users can read/write their own data
    match /users/{userId} {
      allow read, write: if isOwner(userId) || isAdmin();
      
      // User subcollections
      match /sessions/{sessionId} {
        allow read, write: if isOwner(userId) || isAdmin();
      }
      
      match /activity/{activityId} {
        allow read, write: if isOwner(userId) || isAdmin();
      }
      
      match /notifications/{notificationId} {
        allow read, write: if isOwner(userId) || isAdmin();
      }
    }
    
    // Project documents - collaborators can read, owners can write
    match /projects/{projectId} {
      allow read: if isProjectCollaborator(projectId) || isAdmin();
      allow write: if isOwner(resource.data.ownerId) || isAdmin();
      
      // Project subcollections
      match /collaborators/{userId} {
        allow read: if isProjectCollaborator(projectId) || isAdmin();
        allow write: if isOwner(resource.data.ownerId) || isAdmin();
      }
      
      match /activity/{activityId} {
        allow read: if isProjectCollaborator(projectId) || isAdmin();
        allow create: if isProjectCollaborator(projectId);
        allow update, delete: if isOwner(resource.data.userId) || isAdmin();
      }
      
      match /files/{fileId} {
        allow read: if isProjectCollaborator(projectId) || isAdmin();
        allow write: if isProjectCollaborator(projectId) || isAdmin();
      }
    }
    
    // Analytics - users can read their own data, admins can read all
    match /analytics/events/{eventId} {
      allow read: if isOwner(resource.data.userId) || isAdmin();
      allow create: if isAuthenticated();
      allow update, delete: if isAdmin();
    }
    
    match /analytics/metrics/{metricId} {
      allow read: if isAuthenticated();
      allow write: if isAdmin();
    }
    
    match /analytics/dashboards/{dashboardId} {
      allow read: if isOwner(resource.data.userId) || resource.data.isPublic || isAdmin();
      allow write: if isOwner(resource.data.userId) || isAdmin();
    }
    
    // Chat conversations - users can access their own chats
    match /chat/{conversationId} {
      allow read, write: if isOwner(resource.data.userId) || isAdmin();
      
      match /messages/{messageId} {
        allow read, write: if isOwner(resource.data.userId) || isAdmin();
      }
    }
    
    // System data - admin only
    match /system/{document=**} {
      allow read, write: if isAdmin();
    }
    
    // Real-time data - read for authenticated users, write for admins
    match /realtime/{document=**} {
      allow read: if isAuthenticated();
      allow write: if isAdmin();
    }
  }
}
`;

// =============================================
// FIRESTORE INDEXES CONFIGURATION
// =============================================

const indexesConfig = {
  indexes: [
    // User activity queries
    {
      collectionGroup: "activity",
      queryScope: "COLLECTION",
      fields: [
        { fieldPath: "userId", order: "ASCENDING" },
        { fieldPath: "timestamp", order: "DESCENDING" }
      ]
    },
    {
      collectionGroup: "activity",
      queryScope: "COLLECTION",
      fields: [
        { fieldPath: "type", order: "ASCENDING" },
        { fieldPath: "timestamp", order: "DESCENDING" }
      ]
    },
    
    // Analytics events queries
    {
      collectionGroup: "events",
      queryScope: "COLLECTION",
      fields: [
        { fieldPath: "userId", order: "ASCENDING" },
        { fieldPath: "timestamp", order: "DESCENDING" }
      ]
    },
    {
      collectionGroup: "events",
      queryScope: "COLLECTION",
      fields: [
        { fieldPath: "type", order: "ASCENDING" },
        { fieldPath: "timestamp", order: "DESCENDING" }
      ]
    },
    {
      collectionGroup: "events",
      queryScope: "COLLECTION",
      fields: [
        { fieldPath: "category", order: "ASCENDING" },
        { fieldPath: "timestamp", order: "DESCENDING" }
      ]
    },
    
    // Metrics time series queries
    {
      collectionGroup: "metrics",
      queryScope: "COLLECTION",
      fields: [
        { fieldPath: "name", order: "ASCENDING" },
        { fieldPath: "timestamp", order: "DESCENDING" }
      ]
    },
    {
      collectionGroup: "metrics",
      queryScope: "COLLECTION",
      fields: [
        { fieldPath: "category", order: "ASCENDING" },
        { fieldPath: "timestamp", order: "DESCENDING" }
      ]
    },
    
    // Chat message queries
    {
      collectionGroup: "messages",
      queryScope: "COLLECTION",
      fields: [
        { fieldPath: "timestamp", order: "ASCENDING" }
      ]
    },
    
    // Project collaboration queries
    {
      collectionGroup: "collaborators",
      queryScope: "COLLECTION",
      fields: [
        { fieldPath: "isActive", order: "ASCENDING" },
        { fieldPath: "lastSeen", order: "DESCENDING" }
      ]
    },
    
    // System health queries
    {
      collectionGroup: "health",
      queryScope: "COLLECTION",
      fields: [
        { fieldPath: "component", order: "ASCENDING" },
        { fieldPath: "timestamp", order: "DESCENDING" }
      ]
    },
    {
      collectionGroup: "health",
      queryScope: "COLLECTION",
      fields: [
        { fieldPath: "status", order: "ASCENDING" },
        { fieldPath: "timestamp", order: "DESCENDING" }
      ]
    },
    
    // Real-time usage queries
    {
      collectionGroup: "usage",
      queryScope: "COLLECTION",
      fields: [
        { fieldPath: "timestamp", order: "DESCENDING" }
      ]
    },
    
    // Error tracking queries
    {
      collectionGroup: "errors",
      queryScope: "COLLECTION",
      fields: [
        { fieldPath: "type", order: "ASCENDING" },
        { fieldPath: "timestamp", order: "DESCENDING" }
      ]
    },
    {
      collectionGroup: "errors",
      queryScope: "COLLECTION",
      fields: [
        { fieldPath: "status", order: "ASCENDING" },
        { fieldPath: "timestamp", order: "DESCENDING" }
      ]
    }
  ],
  
  fieldOverrides: [
    {
      collectionGroup: "events",
      fieldPath: "properties",
      indexes: [
        {
          queryScope: "COLLECTION",
          fields: [
            { fieldPath: "properties", order: "ASCENDING" }
          ]
        }
      ]
    }
  ]
};

module.exports = {
  firestoreSchema,
  securityRules,
  indexesConfig
};

