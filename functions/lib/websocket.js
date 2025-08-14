"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.connections = exports.EventType = void 0;
exports.broadcastMessage = broadcastMessage;
exports.sendToUser = sendToUser;
exports.broadcastSystemStatus = broadcastSystemStatus;
exports.broadcastSecurityAlert = broadcastSecurityAlert;
exports.broadcastAgentUpdate = broadcastAgentUpdate;
exports.notifyTaskComplete = notifyTaskComplete;
exports.notifyFileUpload = notifyFileUpload;
exports.broadcastAnalyticsUpdate = broadcastAnalyticsUpdate;
// WebSocket connection management
const connections = new Map();
exports.connections = connections;
// Real-time event types
var EventType;
(function (EventType) {
    EventType["SYSTEM_STATUS"] = "system_status";
    EventType["SECURITY_ALERT"] = "security_alert";
    EventType["AGENT_UPDATE"] = "agent_update";
    EventType["CHAT_MESSAGE"] = "chat_message";
    EventType["TASK_COMPLETE"] = "task_complete";
    EventType["FILE_UPLOAD"] = "file_upload";
    EventType["ANALYTICS_UPDATE"] = "analytics_update";
})(EventType || (exports.EventType = EventType = {}));
// Broadcast message to all connected clients
function broadcastMessage(message) {
    const messageStr = JSON.stringify(message);
    connections.forEach((connection, connectionId) => {
        try {
            if (connection.readyState === 1) { // WebSocket.OPEN
                connection.send(messageStr);
            }
            else {
                // Remove closed connections
                connections.delete(connectionId);
            }
        }
        catch (error) {
            console.error(`Error sending message to connection ${connectionId}:`, error);
            connections.delete(connectionId);
        }
    });
}
// Send message to specific user
function sendToUser(userId, message) {
    const messageStr = JSON.stringify(message);
    connections.forEach((connection, connectionId) => {
        if (connection.userId === userId) {
            try {
                if (connection.readyState === 1) {
                    connection.send(messageStr);
                }
                else {
                    connections.delete(connectionId);
                }
            }
            catch (error) {
                console.error(`Error sending message to user ${userId}:`, error);
                connections.delete(connectionId);
            }
        }
    });
}
// System status updates
function broadcastSystemStatus() {
    const statusMessage = {
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
function broadcastSecurityAlert(alert) {
    const alertMessage = {
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
function broadcastAgentUpdate(agentId, status, data) {
    const updateMessage = {
        type: EventType.AGENT_UPDATE,
        data: Object.assign({ agentId,
            status }, data),
        timestamp: new Date().toISOString()
    };
    broadcastMessage(updateMessage);
}
// Task completion notifications
function notifyTaskComplete(userId, taskId, result) {
    const taskMessage = {
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
function notifyFileUpload(userId, fileId, progress) {
    const fileMessage = {
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
function broadcastAnalyticsUpdate(analytics) {
    const analyticsMessage = {
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
        const alert = Object.assign(Object.assign({}, alerts[Math.floor(Math.random() * alerts.length)]), { timestamp: new Date().toISOString() });
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
//# sourceMappingURL=websocket.js.map