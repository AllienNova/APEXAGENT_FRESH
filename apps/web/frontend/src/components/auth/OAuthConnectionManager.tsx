import React, { useState, useEffect } from 'react';
import { 
  ExternalLink, 
  CheckCircle, 
  XCircle, 
  AlertTriangle,
  RefreshCw,
  Settings,
  Shield,
  Key,
  Clock,
  Globe,
  User,
  Mail,
  Calendar,
  MessageSquare,
  Github,
  Linkedin,
  Twitter,
  Facebook,
  Plus,
  Trash2,
  Eye,
  EyeOff,
  Copy,
  Check,
  Info,
  Zap,
  Lock,
  Unlock
} from 'lucide-react';

// OAuth Connection Management Interface
export const OAuthConnectionManager = () => {
  const [connections, setConnections] = useState([
    {
      id: 'google',
      name: 'Google',
      icon: Globe,
      connected: true,
      status: 'healthy',
      lastSync: '2 minutes ago',
      scopes: ['Gmail', 'Calendar', 'Drive'],
      userEmail: 'user@gmail.com',
      expiresAt: '2025-01-15T10:30:00Z',
      permissions: ['read', 'write', 'send'],
      description: 'Access Gmail, Google Calendar, and Google Drive'
    },
    {
      id: 'microsoft',
      name: 'Microsoft',
      icon: Mail,
      connected: true,
      status: 'healthy',
      lastSync: '5 minutes ago',
      scopes: ['Outlook', 'Calendar', 'OneDrive'],
      userEmail: 'user@outlook.com',
      expiresAt: '2025-01-20T14:15:00Z',
      permissions: ['read', 'write', 'send'],
      description: 'Access Outlook, Microsoft Calendar, and OneDrive'
    },
    {
      id: 'linkedin',
      name: 'LinkedIn',
      icon: Linkedin,
      connected: true,
      status: 'warning',
      lastSync: '2 hours ago',
      scopes: ['Profile', 'Connections', 'Posts'],
      userEmail: 'user@linkedin.com',
      expiresAt: '2025-01-12T09:00:00Z',
      permissions: ['read', 'write'],
      description: 'Manage LinkedIn profile and professional connections'
    },
    {
      id: 'twitter',
      name: 'Twitter',
      icon: Twitter,
      connected: false,
      status: 'disconnected',
      lastSync: 'Never',
      scopes: ['Tweets', 'Profile', 'DMs'],
      userEmail: null,
      expiresAt: null,
      permissions: ['read', 'write'],
      description: 'Manage Twitter posts and direct messages'
    },
    {
      id: 'facebook',
      name: 'Facebook',
      icon: Facebook,
      connected: false,
      status: 'disconnected',
      lastSync: 'Never',
      scopes: ['Profile', 'Pages', 'Posts'],
      userEmail: null,
      expiresAt: null,
      permissions: ['read', 'write'],
      description: 'Manage Facebook profile and pages'
    },
    {
      id: 'github',
      name: 'GitHub',
      icon: Github,
      connected: true,
      status: 'healthy',
      lastSync: '1 minute ago',
      scopes: ['Repositories', 'Issues', 'Actions'],
      userEmail: 'user@github.com',
      expiresAt: '2025-02-01T16:45:00Z',
      permissions: ['read', 'write'],
      description: 'Access GitHub repositories and development tools'
    }
  ]);

  const [selectedConnection, setSelectedConnection] = useState(null);
  const [showApiKeys, setShowApiKeys] = useState(false);
  const [copiedKey, setCopiedKey] = useState(null);

  const getStatusColor = (status) => {
    switch (status) {
      case 'healthy': return 'text-green-600 bg-green-100';
      case 'warning': return 'text-yellow-600 bg-yellow-100';
      case 'error': return 'text-red-600 bg-red-100';
      case 'disconnected': return 'text-gray-600 bg-gray-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'healthy': return CheckCircle;
      case 'warning': return AlertTriangle;
      case 'error': return XCircle;
      case 'disconnected': return XCircle;
      default: return XCircle;
    }
  };

  const handleConnect = (connectionId) => {
    // Simulate OAuth flow initiation
    console.log(`Initiating OAuth flow for ${connectionId}`);
    // In real implementation, this would redirect to OAuth provider
  };

  const handleDisconnect = (connectionId) => {
    setConnections(connections.map(conn => 
      conn.id === connectionId 
        ? { ...conn, connected: false, status: 'disconnected', userEmail: null, lastSync: 'Never' }
        : conn
    ));
  };

  const handleRefresh = (connectionId) => {
    setConnections(connections.map(conn => 
      conn.id === connectionId 
        ? { ...conn, lastSync: 'Just now', status: 'healthy' }
        : conn
    ));
  };

  const copyToClipboard = (text, keyId) => {
    navigator.clipboard.writeText(text);
    setCopiedKey(keyId);
    setTimeout(() => setCopiedKey(null), 2000);
  };

  const formatExpiryDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
  };

  const isExpiringSoon = (dateString) => {
    if (!dateString) return false;
    const expiryDate = new Date(dateString);
    const now = new Date();
    const daysUntilExpiry = (expiryDate - now) / (1000 * 60 * 60 * 24);
    return daysUntilExpiry <= 7;
  };

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-8">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">OAuth Connection Manager</h1>
            <p className="text-gray-600 mt-1">Manage your platform connections and API integrations</p>
          </div>
          <div className="flex items-center space-x-4">
            <div className="text-right">
              <p className="text-sm font-medium text-gray-900">
                {connections.filter(c => c.connected).length} of {connections.length} Connected
              </p>
              <p className="text-xs text-gray-500">Last updated: Just now</p>
            </div>
            <button className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition-colors flex items-center space-x-2">
              <Plus className="h-4 w-4" />
              <span>Add Connection</span>
            </button>
          </div>
        </div>
      </div>

      {/* Connection Status Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Active Connections</p>
              <p className="text-3xl font-bold text-green-600">{connections.filter(c => c.connected && c.status === 'healthy').length}</p>
            </div>
            <CheckCircle className="h-8 w-8 text-green-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Needs Attention</p>
              <p className="text-3xl font-bold text-yellow-600">{connections.filter(c => c.status === 'warning').length}</p>
            </div>
            <AlertTriangle className="h-8 w-8 text-yellow-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Disconnected</p>
              <p className="text-3xl font-bold text-gray-600">{connections.filter(c => !c.connected).length}</p>
            </div>
            <XCircle className="h-8 w-8 text-gray-500" />
          </div>
        </div>
      </div>

      {/* Platform Connections */}
      <div className="bg-white rounded-lg shadow-sm border">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Platform Connections</h2>
          <p className="text-sm text-gray-600">Manage OAuth 2.0 connections with external platforms</p>
        </div>
        
        <div className="p-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {connections.map((connection) => {
              const StatusIcon = getStatusIcon(connection.status);
              const PlatformIcon = connection.icon;
              
              return (
                <div key={connection.id} className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
                  {/* Connection Header */}
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center space-x-3">
                      <div className="p-2 bg-gray-100 rounded-lg">
                        <PlatformIcon className="h-6 w-6 text-gray-700" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-gray-900">{connection.name}</h3>
                        <p className="text-sm text-gray-600">{connection.description}</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(connection.status)}`}>
                        {connection.status}
                      </span>
                      <StatusIcon className={`h-5 w-5 ${
                        connection.status === 'healthy' ? 'text-green-500' :
                        connection.status === 'warning' ? 'text-yellow-500' :
                        connection.status === 'error' ? 'text-red-500' : 'text-gray-500'
                      }`} />
                    </div>
                  </div>

                  {/* Connection Details */}
                  {connection.connected ? (
                    <div className="space-y-3">
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600">Connected Account:</span>
                        <span className="font-medium text-gray-900">{connection.userEmail}</span>
                      </div>
                      
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600">Last Sync:</span>
                        <span className="font-medium text-gray-900">{connection.lastSync}</span>
                      </div>
                      
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600">Token Expires:</span>
                        <span className={`font-medium ${isExpiringSoon(connection.expiresAt) ? 'text-yellow-600' : 'text-gray-900'}`}>
                          {formatExpiryDate(connection.expiresAt)}
                        </span>
                      </div>

                      <div className="text-sm">
                        <span className="text-gray-600">Scopes:</span>
                        <div className="flex flex-wrap gap-1 mt-1">
                          {connection.scopes.map((scope) => (
                            <span key={scope} className="px-2 py-1 bg-indigo-100 text-indigo-700 rounded text-xs">
                              {scope}
                            </span>
                          ))}
                        </div>
                      </div>

                      <div className="text-sm">
                        <span className="text-gray-600">Permissions:</span>
                        <div className="flex flex-wrap gap-1 mt-1">
                          {connection.permissions.map((permission) => (
                            <span key={permission} className="px-2 py-1 bg-green-100 text-green-700 rounded text-xs">
                              {permission}
                            </span>
                          ))}
                        </div>
                      </div>

                      {/* Action Buttons */}
                      <div className="flex space-x-2 pt-3 border-t">
                        <button 
                          onClick={() => handleRefresh(connection.id)}
                          className="flex-1 bg-indigo-600 text-white py-2 px-3 rounded-md hover:bg-indigo-700 transition-colors flex items-center justify-center space-x-2"
                        >
                          <RefreshCw className="h-4 w-4" />
                          <span>Refresh</span>
                        </button>
                        <button 
                          onClick={() => setSelectedConnection(connection)}
                          className="flex-1 bg-gray-600 text-white py-2 px-3 rounded-md hover:bg-gray-700 transition-colors flex items-center justify-center space-x-2"
                        >
                          <Settings className="h-4 w-4" />
                          <span>Settings</span>
                        </button>
                        <button 
                          onClick={() => handleDisconnect(connection.id)}
                          className="bg-red-600 text-white py-2 px-3 rounded-md hover:bg-red-700 transition-colors"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      <p className="text-sm text-gray-600">Not connected to {connection.name}</p>
                      
                      <div className="text-sm">
                        <span className="text-gray-600">Available Scopes:</span>
                        <div className="flex flex-wrap gap-1 mt-1">
                          {connection.scopes.map((scope) => (
                            <span key={scope} className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs">
                              {scope}
                            </span>
                          ))}
                        </div>
                      </div>

                      <button 
                        onClick={() => handleConnect(connection.id)}
                        className="w-full bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 transition-colors flex items-center justify-center space-x-2"
                      >
                        <ExternalLink className="h-4 w-4" />
                        <span>Connect to {connection.name}</span>
                      </button>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* API Key Management Section */}
      <div className="bg-white rounded-lg shadow-sm border">
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold text-gray-900">API Key Management</h2>
              <p className="text-sm text-gray-600">Manage API keys for AI providers and services</p>
            </div>
            <button 
              onClick={() => setShowApiKeys(!showApiKeys)}
              className="flex items-center space-x-2 text-indigo-600 hover:text-indigo-800"
            >
              {showApiKeys ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              <span>{showApiKeys ? 'Hide' : 'Show'} API Keys</span>
            </button>
          </div>
        </div>
        
        <div className="p-6">
          <div className="space-y-4">
            {[
              { name: 'Together AI', key: 'sk-together-abc123...', status: 'active', usage: '78%', cost: '$1,245' },
              { name: 'OpenAI', key: 'sk-openai-def456...', status: 'active', usage: '15%', cost: '$2,890' },
              { name: 'Anthropic', key: 'sk-ant-ghi789...', status: 'active', usage: '5%', cost: '$567' },
              { name: 'Google AI', key: 'AIza-google-jkl012...', status: 'inactive', usage: '2%', cost: '$234' }
            ].map((provider, index) => (
              <div key={index} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                <div className="flex items-center space-x-4">
                  <div className="p-2 bg-gray-100 rounded-lg">
                    <Key className="h-5 w-5 text-gray-700" />
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900">{provider.name}</h4>
                    <div className="flex items-center space-x-4 text-sm text-gray-600">
                      <span>Usage: {provider.usage}</span>
                      <span>Cost: {provider.cost}</span>
                      <span className={`px-2 py-1 rounded-full text-xs ${
                        provider.status === 'active' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'
                      }`}>
                        {provider.status}
                      </span>
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  {showApiKeys && (
                    <div className="flex items-center space-x-2">
                      <code className="bg-gray-100 px-2 py-1 rounded text-sm font-mono">
                        {provider.key}
                      </code>
                      <button 
                        onClick={() => copyToClipboard(provider.key, index)}
                        className="text-gray-500 hover:text-gray-700"
                      >
                        {copiedKey === index ? <Check className="h-4 w-4 text-green-500" /> : <Copy className="h-4 w-4" />}
                      </button>
                    </div>
                  )}
                  <button className="text-indigo-600 hover:text-indigo-800">
                    <Settings className="h-4 w-4" />
                  </button>
                  <button className="text-red-600 hover:text-red-800">
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Connection Details Modal */}
      {selectedConnection && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="px-6 py-4 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-900">
                  {selectedConnection.name} Connection Details
                </h3>
                <button 
                  onClick={() => setSelectedConnection(null)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  <XCircle className="h-6 w-6" />
                </button>
              </div>
            </div>
            
            <div className="p-6 space-y-6">
              {/* Connection Status */}
              <div>
                <h4 className="font-medium text-gray-900 mb-3">Connection Status</h4>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm text-gray-600">Status</label>
                    <p className="font-medium">{selectedConnection.status}</p>
                  </div>
                  <div>
                    <label className="text-sm text-gray-600">Last Sync</label>
                    <p className="font-medium">{selectedConnection.lastSync}</p>
                  </div>
                  <div>
                    <label className="text-sm text-gray-600">Connected Account</label>
                    <p className="font-medium">{selectedConnection.userEmail || 'Not connected'}</p>
                  </div>
                  <div>
                    <label className="text-sm text-gray-600">Token Expires</label>
                    <p className="font-medium">{formatExpiryDate(selectedConnection.expiresAt)}</p>
                  </div>
                </div>
              </div>

              {/* OAuth Configuration */}
              <div>
                <h4 className="font-medium text-gray-900 mb-3">OAuth Configuration</h4>
                <div className="space-y-3">
                  <div>
                    <label className="text-sm text-gray-600">OAuth Version</label>
                    <p className="font-medium">2.1 with PKCE</p>
                  </div>
                  <div>
                    <label className="text-sm text-gray-600">Scopes</label>
                    <div className="flex flex-wrap gap-2 mt-1">
                      {selectedConnection.scopes.map((scope) => (
                        <span key={scope} className="px-2 py-1 bg-indigo-100 text-indigo-700 rounded text-sm">
                          {scope}
                        </span>
                      ))}
                    </div>
                  </div>
                  <div>
                    <label className="text-sm text-gray-600">Permissions</label>
                    <div className="flex flex-wrap gap-2 mt-1">
                      {selectedConnection.permissions.map((permission) => (
                        <span key={permission} className="px-2 py-1 bg-green-100 text-green-700 rounded text-sm">
                          {permission}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* Actions */}
              <div className="flex space-x-3 pt-4 border-t">
                <button 
                  onClick={() => handleRefresh(selectedConnection.id)}
                  className="flex-1 bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 transition-colors"
                >
                  Refresh Connection
                </button>
                <button 
                  onClick={() => {
                    handleDisconnect(selectedConnection.id);
                    setSelectedConnection(null);
                  }}
                  className="flex-1 bg-red-600 text-white py-2 px-4 rounded-md hover:bg-red-700 transition-colors"
                >
                  Disconnect
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default OAuthConnectionManager;

