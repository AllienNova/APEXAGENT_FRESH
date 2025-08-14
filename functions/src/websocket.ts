// WebSocket connection management
const connections = new Map<string, any>();

// Real-time event types
export enum EventType {
  SYSTEM_STATUS = 'system_status',
  SECURITY_ALERT = 'security_alert',
  AGENT_UPDATE = 'agent_update',
  CHAT_MESSAGE = 'chat_message',
  TASK_COMPLETE = 'task_complete',
  FILE_UPLOAD = 'file_upload',
  ANALYTICS_UPDATE = 'analytics_update'
}

// WebSocket message interface
interface WebSocketMessage {
  type: EventType;
  data: any;
  timestamp: string;
  userId?: string;
}

// Broadcast message to all connected clients
export function broadcastMessage(message: WebSocketMessage) {
  const messageStr = JSON.stringify(message);
  
  connections.forEach((connection, connectionId) => {
    try {
      if (connection.readyState === 1) { // WebSocket.OPEN
        connection.send(messageStr);
      } else {
        // Remove closed connections
        connections.delete(connectionId);
      }
    } catch (error) {
      console.error(`Error sending message to connection ${connectionId}:`, error);
      connections.delete(connectionId);
    }
  });
}

// Send message to specific user
export function sendToUser(userId: string, message: WebSocketMessage) {
  const messageStr = JSON.stringify(message);
  
  connections.forEach((connection, connectionId) => {
    if (connection.userId === userId) {
      try {
        if (connection.readyState === 1) {
          connection.send(messageStr);
        } else {
          connections.delete(connectionId);
        }
      } catch (error) {
        console.error(`Error sending message to user ${userId}:`, error);
        connections.delete(connectionId);
      }
    }
  });
}

// System status updates
export function broadcastSystemStatus() {
  const statusMessage: WebSocketMessage = {
    type: EventType.SYSTEM_STATUS,
    data: {
      status: 'online',
      uptime: process.uptime(),
      activeConnections: connections.size,
      timestamp: new Date().toISOString()
    },
    timestamp: new Date().toISOString()
  };
  
  broadcastMessage(statusMessage);
}

// Security alert notifications
export function broadcastSecurityAlert(alert: any) {
  const alertMessage: WebSocketMessage = {
    type: EventType.SECURITY_ALERT,
    data: {
      level: alert.level,
      message: alert.message,
      source: alert.source,
      timestamp: alert.timestamp
    },
    timestamp: new Date().toISOString()
  };
  
  broadcastMessage(alertMessage);
}

// Agent status updates
export function broadcastAgentUpdate(agentId: string, status: string, data: any) {
  const updateMessage: WebSocketMessage = {
    type: EventType.AGENT_UPDATE,
    data: {
      agentId,
      status,
      ...data
    },
    timestamp: new Date().toISOString()
  };
  
  broadcastMessage(updateMessage);
}

// Task completion notifications
export function notifyTaskComplete(userId: string, taskId: string, result: any) {
  const taskMessage: WebSocketMessage = {
    type: EventType.TASK_COMPLETE,
    data: {
      taskId,
      result,
      completedAt: new Date().toISOString()
    },
    timestamp: new Date().toISOString(),
    userId
  };
  
  sendToUser(userId, taskMessage);
}

// File upload progress
export function notifyFileUpload(userId: string, fileId: string, progress: number) {
  const fileMessage: WebSocketMessage = {
    type: EventType.FILE_UPLOAD,
    data: {
      fileId,
      progress,
      status: progress === 100 ? 'completed' : 'uploading'
    },
    timestamp: new Date().toISOString(),
    userId
  };
  
  sendToUser(userId, fileMessage);
}

// Analytics updates
export function broadcastAnalyticsUpdate(analytics: any) {
  const analyticsMessage: WebSocketMessage = {
    type: EventType.ANALYTICS_UPDATE,
    data: analytics,
    timestamp: new Date().toISOString()
  };
  
  broadcastMessage(analyticsMessage);
}

// Periodic system updates
setInterval(() => {
  broadcastSystemStatus();
}, 30000); // Every 30 seconds

// Simulate security monitoring
setInterval(() => {
  // Simulate random security events
  if (Math.random() < 0.1) { // 10% chance
    const alerts = [
      { level: 'info', message: 'Routine security scan completed', source: 'SecurityAgent' },
      { level: 'warning', message: 'Unusual network activity detected', source: 'NetworkMonitor' },
      { level: 'info', message: 'Firewall rules updated', source: 'FirewallManager' }
    ];
    
    const alert = {
      ...alerts[Math.floor(Math.random() * alerts.length)],
      timestamp: new Date().toISOString()
    };
    
    broadcastSecurityAlert(alert);
  }
}, 60000); // Every minute

// Simulate agent updates
setInterval(() => {
  const agents = ['planner-agent', 'execution-agent', 'security-agent', 'verification-agent'];
  const statuses = ['processing', 'idle', 'completed_task'];
  
  const agentId = agents[Math.floor(Math.random() * agents.length)];
  const status = statuses[Math.floor(Math.random() * statuses.length)];
  
  broadcastAgentUpdate(agentId, status, {
    lastActivity: new Date().toISOString(),
    performance: {
      tasksCompleted: Math.floor(Math.random() * 100),
      successRate: 95 + Math.random() * 5
    }
  });
}, 45000); // Every 45 seconds

export { connections };

