import React, { useState, useEffect, useContext, createContext } from 'react';
import { 
  Shield, 
  Key, 
  Users, 
  Activity, 
  Settings, 
  Plus, 
  Trash2, 
  RefreshCw, 
  CheckCircle, 
  XCircle, 
  AlertTriangle,
  Eye,
  EyeOff,
  ExternalLink,
  Clock,
  Lock,
  Unlock
} from 'lucide-react';

// Authentication Context
const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Authentication Provider
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('aideon_auth_token'));
  const [loading, setLoading] = useState(true);

  const API_BASE = 'http://localhost:8000/api';

  useEffect(() => {
    if (token) {
      verifyToken();
    } else {
      setLoading(false);
    }
  }, [token]);

  const verifyToken = async () => {
    try {
      const response = await fetch(`${API_BASE}/auth/verify`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setUser(data);
      } else {
        logout();
      }
    } catch (error) {
      console.error('Token verification failed:', error);
      logout();
    } finally {
      setLoading(false);
    }
  };

  const login = async (username, password) => {
    try {
      const response = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
      });

      const data = await response.json();

      if (response.ok) {
        setToken(data.token);
        setUser(data);
        localStorage.setItem('aideon_auth_token', data.token);
        return { success: true };
      } else {
        return { success: false, error: data.error };
      }
    } catch (error) {
      return { success: false, error: 'Login failed' };
    }
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('aideon_auth_token');
  };

  const apiCall = async (endpoint, options = {}) => {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        ...options.headers
      }
    });

    if (response.status === 401) {
      logout();
      throw new Error('Authentication required');
    }

    return response;
  };

  return (
    <AuthContext.Provider value={{
      user,
      token,
      loading,
      login,
      logout,
      apiCall,
      isAuthenticated: !!user,
      isAdmin: user?.role === 'admin'
    }}>
      {children}
    </AuthContext.Provider>
  );
};

// Login Component
export const LoginForm = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    const result = await login(username, password);

    if (!result.success) {
      setError(result.error);
    }

    setLoading(false);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="max-w-md w-full space-y-8 p-8 bg-white rounded-xl shadow-lg">
        <div className="text-center">
          <Shield className="mx-auto h-12 w-12 text-indigo-600" />
          <h2 className="mt-6 text-3xl font-bold text-gray-900">
            Aideon AI Lite
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Sign in to your account
          </p>
        </div>

        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-md p-4">
              <div className="flex">
                <XCircle className="h-5 w-5 text-red-400" />
                <div className="ml-3">
                  <p className="text-sm text-red-800">{error}</p>
                </div>
              </div>
            </div>
          )}

          <div>
            <label htmlFor="username" className="block text-sm font-medium text-gray-700">
              Username
            </label>
            <input
              id="username"
              name="username"
              type="text"
              required
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              placeholder="Enter your username"
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700">
              Password
            </label>
            <div className="mt-1 relative">
              <input
                id="password"
                name="password"
                type={showPassword ? "text" : "password"}
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                placeholder="Enter your password"
              />
              <button
                type="button"
                className="absolute inset-y-0 right-0 pr-3 flex items-center"
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? (
                  <EyeOff className="h-5 w-5 text-gray-400" />
                ) : (
                  <Eye className="h-5 w-5 text-gray-400" />
                )}
              </button>
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={loading}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <RefreshCw className="h-5 w-5 animate-spin" />
              ) : (
                'Sign in'
              )}
            </button>
          </div>

          <div className="text-center text-sm text-gray-600">
            <p>Demo credentials:</p>
            <p><strong>Admin:</strong> admin / admin123</p>
            <p><strong>User:</strong> user / user123</p>
          </div>
        </form>
      </div>
    </div>
  );
};

// OAuth Connection Component
export const OAuthConnections = () => {
  const [connections, setConnections] = useState({});
  const [providers, setProviders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState({});
  const { apiCall } = useAuth();

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [connectionsRes, providersRes] = await Promise.all([
        apiCall('/auth/connections'),
        apiCall('/auth/oauth/providers')
      ]);

      const connectionsData = await connectionsRes.json();
      const providersData = await providersRes.json();

      if (connectionsData.success) {
        setConnections(connectionsData.connections);
      }

      if (providersData.success) {
        setProviders(providersData.providers);
      }
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  };

  const initiateOAuth = async (provider, scopes = []) => {
    try {
      setActionLoading(prev => ({ ...prev, [provider]: true }));

      const response = await apiCall('/auth/oauth/initiate', {
        method: 'POST',
        body: JSON.stringify({ provider, scopes })
      });

      const data = await response.json();

      if (data.success && data.authorization_url) {
        window.open(data.authorization_url, '_blank', 'width=600,height=700');
      }
    } catch (error) {
      console.error('OAuth initiation failed:', error);
    } finally {
      setActionLoading(prev => ({ ...prev, [provider]: false }));
    }
  };

  const refreshConnection = async (credentialId) => {
    try {
      setActionLoading(prev => ({ ...prev, [credentialId]: true }));

      const response = await apiCall('/auth/connections/refresh', {
        method: 'POST',
        body: JSON.stringify({ credential_id: credentialId })
      });

      const data = await response.json();

      if (data.success) {
        loadData(); // Reload connections
      }
    } catch (error) {
      console.error('Connection refresh failed:', error);
    } finally {
      setActionLoading(prev => ({ ...prev, [credentialId]: false }));
    }
  };

  const revokeConnection = async (credentialId) => {
    if (!confirm('Are you sure you want to revoke this connection?')) {
      return;
    }

    try {
      setActionLoading(prev => ({ ...prev, [credentialId]: true }));

      const response = await apiCall('/auth/connections/revoke', {
        method: 'DELETE',
        body: JSON.stringify({ credential_id: credentialId })
      });

      const data = await response.json();

      if (data.success) {
        loadData(); // Reload connections
      }
    } catch (error) {
      console.error('Connection revocation failed:', error);
    } finally {
      setActionLoading(prev => ({ ...prev, [credentialId]: false }));
    }
  };

  const getStatusIcon = (status, isExpired, expiresSoon) => {
    if (status === 'revoked') {
      return <XCircle className="h-5 w-5 text-red-500" />;
    }
    if (isExpired) {
      return <XCircle className="h-5 w-5 text-red-500" />;
    }
    if (expiresSoon) {
      return <AlertTriangle className="h-5 w-5 text-yellow-500" />;
    }
    if (status === 'active') {
      return <CheckCircle className="h-5 w-5 text-green-500" />;
    }
    return <Clock className="h-5 w-5 text-gray-500" />;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <RefreshCw className="h-8 w-8 animate-spin text-indigo-600" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
            Platform Connections
          </h3>

          {/* Available Providers */}
          <div className="mb-6">
            <h4 className="text-sm font-medium text-gray-700 mb-3">Available Platforms</h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {providers.map((provider) => {
                const hasConnection = connections[provider.name]?.length > 0;
                return (
                  <div
                    key={provider.name}
                    className="border border-gray-200 rounded-lg p-4 hover:border-indigo-300 transition-colors"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <h5 className="font-medium text-gray-900">{provider.display_name}</h5>
                      {hasConnection && (
                        <CheckCircle className="h-5 w-5 text-green-500" />
                      )}
                    </div>
                    <p className="text-sm text-gray-600 mb-3">
                      {hasConnection ? 'Connected' : 'Not connected'}
                    </p>
                    <button
                      onClick={() => initiateOAuth(provider.name)}
                      disabled={actionLoading[provider.name]}
                      className="w-full inline-flex items-center justify-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
                    >
                      {actionLoading[provider.name] ? (
                        <RefreshCw className="h-4 w-4 animate-spin" />
                      ) : (
                        <>
                          <ExternalLink className="h-4 w-4 mr-2" />
                          {hasConnection ? 'Reconnect' : 'Connect'}
                        </>
                      )}
                    </button>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Active Connections */}
          {Object.keys(connections).length > 0 && (
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-3">Active Connections</h4>
              <div className="space-y-4">
                {Object.entries(connections).map(([provider, providerConnections]) =>
                  providerConnections.map((connection) => (
                    <div
                      key={connection.credential_id}
                      className="border border-gray-200 rounded-lg p-4"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          {getStatusIcon(
                            connection.status,
                            connection.is_expired,
                            connection.expires_soon
                          )}
                          <div>
                            <h5 className="font-medium text-gray-900">
                              {provider.charAt(0).toUpperCase() + provider.slice(1)}
                            </h5>
                            <p className="text-sm text-gray-600">
                              {connection.type === 'oauth_token' ? 'OAuth Connection' : 'API Key'}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          {connection.type === 'oauth_token' && connection.expires_soon && (
                            <button
                              onClick={() => refreshConnection(connection.credential_id)}
                              disabled={actionLoading[connection.credential_id]}
                              className="inline-flex items-center px-3 py-1 border border-transparent text-xs font-medium rounded text-indigo-700 bg-indigo-100 hover:bg-indigo-200"
                            >
                              {actionLoading[connection.credential_id] ? (
                                <RefreshCw className="h-3 w-3 animate-spin" />
                              ) : (
                                <>
                                  <RefreshCw className="h-3 w-3 mr-1" />
                                  Refresh
                                </>
                              )}
                            </button>
                          )}
                          <button
                            onClick={() => revokeConnection(connection.credential_id)}
                            disabled={actionLoading[connection.credential_id]}
                            className="inline-flex items-center px-3 py-1 border border-transparent text-xs font-medium rounded text-red-700 bg-red-100 hover:bg-red-200"
                          >
                            {actionLoading[connection.credential_id] ? (
                              <RefreshCw className="h-3 w-3 animate-spin" />
                            ) : (
                              <>
                                <Trash2 className="h-3 w-3 mr-1" />
                                Revoke
                              </>
                            )}
                          </button>
                        </div>
                      </div>
                      
                      <div className="mt-3 grid grid-cols-2 gap-4 text-sm text-gray-600">
                        <div>
                          <span className="font-medium">Status:</span> {connection.status}
                        </div>
                        <div>
                          <span className="font-medium">Created:</span>{' '}
                          {new Date(connection.created_at).toLocaleDateString()}
                        </div>
                        {connection.expires_at && (
                          <div>
                            <span className="font-medium">Expires:</span>{' '}
                            {new Date(connection.expires_at).toLocaleDateString()}
                          </div>
                        )}
                        {connection.last_used_at && (
                          <div>
                            <span className="font-medium">Last Used:</span>{' '}
                            {new Date(connection.last_used_at).toLocaleDateString()}
                          </div>
                        )}
                      </div>

                      {connection.scopes && connection.scopes.length > 0 && (
                        <div className="mt-3">
                          <span className="text-sm font-medium text-gray-700">Scopes:</span>
                          <div className="mt-1 flex flex-wrap gap-1">
                            {connection.scopes.map((scope) => (
                              <span
                                key={scope}
                                className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800"
                              >
                                {scope}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// API Key Management Component
export const APIKeyManagement = () => {
  const [apiKeys, setApiKeys] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [newKey, setNewKey] = useState({ provider: '', api_key: '' });
  const [actionLoading, setActionLoading] = useState({});
  const { apiCall } = useAuth();

  useEffect(() => {
    loadApiKeys();
  }, []);

  const loadApiKeys = async () => {
    try {
      const response = await apiCall('/auth/api-keys');
      const data = await response.json();

      if (data.success) {
        setApiKeys(data.api_keys);
      }
    } catch (error) {
      console.error('Failed to load API keys:', error);
    } finally {
      setLoading(false);
    }
  };

  const addApiKey = async (e) => {
    e.preventDefault();
    
    try {
      setActionLoading(prev => ({ ...prev, add: true }));

      const response = await apiCall('/auth/api-keys', {
        method: 'POST',
        body: JSON.stringify(newKey)
      });

      const data = await response.json();

      if (data.success) {
        setNewKey({ provider: '', api_key: '' });
        setShowAddForm(false);
        loadApiKeys();
      }
    } catch (error) {
      console.error('Failed to add API key:', error);
    } finally {
      setActionLoading(prev => ({ ...prev, add: false }));
    }
  };

  const deleteApiKey = async (credentialId) => {
    if (!confirm('Are you sure you want to delete this API key?')) {
      return;
    }

    try {
      setActionLoading(prev => ({ ...prev, [credentialId]: true }));

      const response = await apiCall(`/auth/api-keys/${credentialId}`, {
        method: 'DELETE'
      });

      const data = await response.json();

      if (data.success) {
        loadApiKeys();
      }
    } catch (error) {
      console.error('Failed to delete API key:', error);
    } finally {
      setActionLoading(prev => ({ ...prev, [credentialId]: false }));
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <RefreshCw className="h-8 w-8 animate-spin text-indigo-600" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg leading-6 font-medium text-gray-900">
              API Key Management
            </h3>
            <button
              onClick={() => setShowAddForm(!showAddForm)}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
            >
              <Plus className="h-4 w-4 mr-2" />
              Add API Key
            </button>
          </div>

          {showAddForm && (
            <div className="mb-6 p-4 border border-gray-200 rounded-lg bg-gray-50">
              <form onSubmit={addApiKey} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Provider
                  </label>
                  <select
                    value={newKey.provider}
                    onChange={(e) => setNewKey(prev => ({ ...prev, provider: e.target.value }))}
                    required
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                  >
                    <option value="">Select a provider</option>
                    <option value="openai">OpenAI</option>
                    <option value="anthropic">Anthropic</option>
                    <option value="together_ai">Together AI</option>
                    <option value="google">Google AI</option>
                    <option value="aws_bedrock">AWS Bedrock</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    API Key
                  </label>
                  <input
                    type="password"
                    value={newKey.api_key}
                    onChange={(e) => setNewKey(prev => ({ ...prev, api_key: e.target.value }))}
                    required
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    placeholder="Enter your API key"
                  />
                </div>
                <div className="flex items-center space-x-3">
                  <button
                    type="submit"
                    disabled={actionLoading.add}
                    className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50"
                  >
                    {actionLoading.add ? (
                      <RefreshCw className="h-4 w-4 animate-spin mr-2" />
                    ) : (
                      <Plus className="h-4 w-4 mr-2" />
                    )}
                    Add API Key
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowAddForm(false)}
                    className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          )}

          {apiKeys.length === 0 ? (
            <div className="text-center py-8">
              <Key className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No API keys</h3>
              <p className="mt-1 text-sm text-gray-500">
                Get started by adding your first API key.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {apiKeys.map((apiKey) => (
                <div
                  key={apiKey.credential_id}
                  className="border border-gray-200 rounded-lg p-4"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <Key className="h-5 w-5 text-gray-400" />
                      <div>
                        <h5 className="font-medium text-gray-900">
                          {apiKey.provider.charAt(0).toUpperCase() + apiKey.provider.slice(1)}
                        </h5>
                        <p className="text-sm text-gray-600">
                          Status: {apiKey.status}
                        </p>
                      </div>
                    </div>
                    <button
                      onClick={() => deleteApiKey(apiKey.credential_id)}
                      disabled={actionLoading[apiKey.credential_id]}
                      className="inline-flex items-center px-3 py-1 border border-transparent text-xs font-medium rounded text-red-700 bg-red-100 hover:bg-red-200"
                    >
                      {actionLoading[apiKey.credential_id] ? (
                        <RefreshCw className="h-3 w-3 animate-spin" />
                      ) : (
                        <>
                          <Trash2 className="h-3 w-3 mr-1" />
                          Delete
                        </>
                      )}
                    </button>
                  </div>
                  
                  <div className="mt-3 grid grid-cols-2 gap-4 text-sm text-gray-600">
                    <div>
                      <span className="font-medium">Created:</span>{' '}
                      {new Date(apiKey.created_at).toLocaleDateString()}
                    </div>
                    {apiKey.last_used_at && (
                      <div>
                        <span className="font-medium">Last Used:</span>{' '}
                        {new Date(apiKey.last_used_at).toLocaleDateString()}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Admin Dashboard Component
export const AdminDashboard = () => {
  const [users, setUsers] = useState([]);
  const [auditLog, setAuditLog] = useState([]);
  const [systemStatus, setSystemStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('users');
  const { apiCall } = useAuth();

  useEffect(() => {
    loadAdminData();
  }, []);

  const loadAdminData = async () => {
    try {
      const [usersRes, auditRes, statusRes] = await Promise.all([
        apiCall('/admin/users'),
        apiCall('/admin/audit-log?limit=50'),
        apiCall('/admin/system-status')
      ]);

      const [usersData, auditData, statusData] = await Promise.all([
        usersRes.json(),
        auditRes.json(),
        statusRes.json()
      ]);

      if (usersData.success) setUsers(usersData.users);
      if (auditData.success) setAuditLog(auditData.audit_log);
      if (statusData.success) setSystemStatus(statusData.system_status);
    } catch (error) {
      console.error('Failed to load admin data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <RefreshCw className="h-8 w-8 animate-spin text-indigo-600" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* System Status */}
      {systemStatus && (
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
              System Status
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-green-50 p-4 rounded-lg">
                <div className="flex items-center">
                  <CheckCircle className="h-8 w-8 text-green-500" />
                  <div className="ml-3">
                    <p className="text-sm font-medium text-green-800">Status</p>
                    <p className="text-lg font-semibold text-green-900">
                      {systemStatus.status}
                    </p>
                  </div>
                </div>
              </div>
              <div className="bg-blue-50 p-4 rounded-lg">
                <div className="flex items-center">
                  <Users className="h-8 w-8 text-blue-500" />
                  <div className="ml-3">
                    <p className="text-sm font-medium text-blue-800">Total Credentials</p>
                    <p className="text-lg font-semibold text-blue-900">
                      {systemStatus.total_credentials}
                    </p>
                  </div>
                </div>
              </div>
              <div className="bg-indigo-50 p-4 rounded-lg">
                <div className="flex items-center">
                  <Activity className="h-8 w-8 text-indigo-500" />
                  <div className="ml-3">
                    <p className="text-sm font-medium text-indigo-800">Active Credentials</p>
                    <p className="text-lg font-semibold text-indigo-900">
                      {systemStatus.active_credentials}
                    </p>
                  </div>
                </div>
              </div>
              <div className="bg-purple-50 p-4 rounded-lg">
                <div className="flex items-center">
                  <Clock className="h-8 w-8 text-purple-500" />
                  <div className="ml-3">
                    <p className="text-sm font-medium text-purple-800">Recent Activity</p>
                    <p className="text-lg font-semibold text-purple-900">
                      {systemStatus.recent_activity}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="bg-white shadow rounded-lg">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8 px-6">
            {[
              { id: 'users', name: 'Users', icon: Users },
              { id: 'audit', name: 'Audit Log', icon: Activity }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`${
                  activeTab === tab.id
                    ? 'border-indigo-500 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center`}
              >
                <tab.icon className="h-5 w-5 mr-2" />
                {tab.name}
              </button>
            ))}
          </nav>
        </div>

        <div className="px-4 py-5 sm:p-6">
          {activeTab === 'users' && (
            <div>
              <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                User Management
              </h3>
              <div className="space-y-4">
                {users.map((user) => (
                  <div
                    key={user.user_id}
                    className="border border-gray-200 rounded-lg p-4"
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <h5 className="font-medium text-gray-900">{user.username}</h5>
                        <p className="text-sm text-gray-600">
                          Role: {user.role} | Status: {user.status}
                        </p>
                      </div>
                      <div className="text-sm text-gray-500">
                        Last login: {new Date(user.last_login).toLocaleDateString()}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'audit' && (
            <div>
              <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                Audit Log
              </h3>
              <div className="space-y-2">
                {auditLog.map((entry) => (
                  <div
                    key={entry.entry_id}
                    className="border border-gray-200 rounded p-3 text-sm"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        {entry.success ? (
                          <CheckCircle className="h-4 w-4 text-green-500" />
                        ) : (
                          <XCircle className="h-4 w-4 text-red-500" />
                        )}
                        <span className="font-medium">{entry.action}</span>
                        <span className="text-gray-600">by {entry.user_id}</span>
                      </div>
                      <span className="text-gray-500">
                        {new Date(entry.timestamp).toLocaleString()}
                      </span>
                    </div>
                    {entry.error_message && (
                      <p className="mt-1 text-red-600">{entry.error_message}</p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Main Dashboard Component
export const Dashboard = () => {
  const [activeTab, setActiveTab] = useState('connections');
  const { user, logout, isAdmin } = useAuth();

  const tabs = [
    { id: 'connections', name: 'Connections', icon: ExternalLink, component: OAuthConnections },
    { id: 'api-keys', name: 'API Keys', icon: Key, component: APIKeyManagement },
    ...(isAdmin ? [{ id: 'admin', name: 'Admin', icon: Settings, component: AdminDashboard }] : [])
  ];

  const ActiveComponent = tabs.find(tab => tab.id === activeTab)?.component || OAuthConnections;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <Shield className="h-8 w-8 text-indigo-600 mr-3" />
              <h1 className="text-2xl font-bold text-gray-900">
                Aideon AI Lite
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-700">
                Welcome, {user?.user_id}
              </span>
              {isAdmin && (
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800">
                  Admin
                </span>
              )}
              <button
                onClick={logout}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700"
              >
                <Lock className="h-4 w-4 mr-2" />
                Logout
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="-mb-px flex space-x-8">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`${
                  activeTab === tab.id
                    ? 'border-indigo-500 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center`}
              >
                <tab.icon className="h-5 w-5 mr-2" />
                {tab.name}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <ActiveComponent />
      </div>
    </div>
  );
};

// Main App Component
export const AuthenticationApp = () => {
  const { loading, isAuthenticated } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <RefreshCw className="h-8 w-8 animate-spin text-indigo-600" />
      </div>
    );
  }

  return isAuthenticated ? <Dashboard /> : <LoginForm />;
};

// Export the complete app with provider
export default function App() {
  return (
    <AuthProvider>
      <AuthenticationApp />
    </AuthProvider>
  );
}

