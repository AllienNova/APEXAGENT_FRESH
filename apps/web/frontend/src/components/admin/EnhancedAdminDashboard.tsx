import React, { useState, useEffect } from 'react';
import { 
  Shield, 
  Key, 
  Users, 
  Activity, 
  Settings, 
  Monitor,
  TrendingUp,
  DollarSign,
  Lock,
  Unlock,
  CheckCircle,
  XCircle,
  AlertTriangle,
  RefreshCw,
  ExternalLink,
  Eye,
  EyeOff,
  Plus,
  Trash2,
  Clock,
  Globe,
  Zap,
  BarChart3,
  PieChart,
  LineChart
} from 'lucide-react';

// Enhanced Admin Dashboard with Authentication Integration
export const EnhancedAdminDashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [systemStats, setSystemStats] = useState({
    totalUsers: 1247,
    activeConnections: 892,
    securityEvents: 23,
    costSavings: 84,
    monthlySpend: 12450,
    previousSpend: 78900
  });

  const [securityMetrics, setSecurityMetrics] = useState({
    threatLevel: 'low',
    blockedIPs: 15,
    failedLogins: 8,
    suspiciousActivities: 3,
    lastThreat: '2 hours ago'
  });

  const [platformConnections, setPlatformConnections] = useState([
    { platform: 'Google', connected: 456, status: 'healthy', uptime: '99.9%' },
    { platform: 'Microsoft', connected: 234, status: 'healthy', uptime: '99.8%' },
    { platform: 'LinkedIn', connected: 189, status: 'warning', uptime: '98.5%' },
    { platform: 'Twitter', connected: 167, status: 'healthy', uptime: '99.7%' },
    { platform: 'Facebook', connected: 145, status: 'healthy', uptime: '99.6%' },
    { platform: 'GitHub', connected: 123, status: 'healthy', uptime: '99.9%' }
  ]);

  const [aiProviders, setAiProviders] = useState([
    { name: 'Together AI', usage: 78, cost: '$1,245', savings: '89%', status: 'active' },
    { name: 'OpenAI GPT-4', usage: 15, cost: '$2,890', savings: '0%', status: 'active' },
    { name: 'Anthropic Claude', usage: 5, cost: '$567', savings: '0%', status: 'active' },
    { name: 'Google Gemini', usage: 2, cost: '$234', savings: '0%', status: 'active' }
  ]);

  const tabs = [
    { id: 'overview', name: 'Overview', icon: Monitor },
    { id: 'authentication', name: 'Authentication', icon: Shield },
    { id: 'security', name: 'Security', icon: Lock },
    { id: 'analytics', name: 'Analytics', icon: BarChart3 },
    { id: 'cost-optimization', name: 'Cost Optimization', icon: DollarSign },
    { id: 'users', name: 'Users', icon: Users },
    { id: 'settings', name: 'Settings', icon: Settings }
  ];

  const getStatusColor = (status) => {
    switch (status) {
      case 'healthy': return 'text-green-600 bg-green-100';
      case 'warning': return 'text-yellow-600 bg-yellow-100';
      case 'error': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getThreatLevelColor = (level) => {
    switch (level) {
      case 'low': return 'text-green-600 bg-green-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'high': return 'text-orange-600 bg-orange-100';
      case 'critical': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-4">
              <Shield className="h-8 w-8 text-indigo-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Aideon AI Lite</h1>
                <p className="text-sm text-gray-600">Enhanced Admin Dashboard</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className="h-2 w-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-sm text-gray-600">System Healthy</span>
              </div>
              <div className="text-right">
                <p className="text-sm font-medium text-gray-900">Admin User</p>
                <p className="text-xs text-gray-500">Last login: 2 min ago</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-8 overflow-x-auto">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`${
                  activeTab === tab.id
                    ? 'border-indigo-500 text-indigo-600 bg-indigo-50'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                } whitespace-nowrap py-4 px-6 border-b-2 font-medium text-sm flex items-center space-x-2 transition-all duration-200`}
              >
                <tab.icon className="h-4 w-4" />
                <span>{tab.name}</span>
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="space-y-8">
            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Total Users</p>
                    <p className="text-3xl font-bold text-gray-900">{systemStats.totalUsers.toLocaleString()}</p>
                  </div>
                  <Users className="h-8 w-8 text-blue-500" />
                </div>
                <div className="mt-4 flex items-center text-sm">
                  <TrendingUp className="h-4 w-4 text-green-500 mr-1" />
                  <span className="text-green-600">+12% from last month</span>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Active Connections</p>
                    <p className="text-3xl font-bold text-gray-900">{systemStats.activeConnections.toLocaleString()}</p>
                  </div>
                  <ExternalLink className="h-8 w-8 text-green-500" />
                </div>
                <div className="mt-4 flex items-center text-sm">
                  <CheckCircle className="h-4 w-4 text-green-500 mr-1" />
                  <span className="text-green-600">98.7% success rate</span>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Cost Savings</p>
                    <p className="text-3xl font-bold text-gray-900">{systemStats.costSavings}%</p>
                  </div>
                  <DollarSign className="h-8 w-8 text-green-500" />
                </div>
                <div className="mt-4 flex items-center text-sm">
                  <TrendingUp className="h-4 w-4 text-green-500 mr-1" />
                  <span className="text-green-600">${(systemStats.previousSpend - systemStats.monthlySpend).toLocaleString()} saved</span>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Security Events</p>
                    <p className="text-3xl font-bold text-gray-900">{systemStats.securityEvents}</p>
                  </div>
                  <Shield className="h-8 w-8 text-yellow-500" />
                </div>
                <div className="mt-4 flex items-center text-sm">
                  <AlertTriangle className="h-4 w-4 text-yellow-500 mr-1" />
                  <span className="text-yellow-600">3 require attention</span>
                </div>
              </div>
            </div>

            {/* Platform Status */}
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-medium text-gray-900">Platform Connections Status</h3>
              </div>
              <div className="p-6">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {platformConnections.map((platform) => (
                    <div key={platform.platform} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-medium text-gray-900">{platform.platform}</h4>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(platform.status)}`}>
                          {platform.status}
                        </span>
                      </div>
                      <div className="space-y-1 text-sm text-gray-600">
                        <p>Connected Users: {platform.connected}</p>
                        <p>Uptime: {platform.uptime}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* AI Provider Usage */}
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-medium text-gray-900">AI Provider Usage & Cost Optimization</h3>
              </div>
              <div className="p-6">
                <div className="space-y-4">
                  {aiProviders.map((provider) => (
                    <div key={provider.name} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                      <div className="flex items-center space-x-4">
                        <div className="flex-shrink-0">
                          <Zap className="h-6 w-6 text-indigo-500" />
                        </div>
                        <div>
                          <h4 className="font-medium text-gray-900">{provider.name}</h4>
                          <p className="text-sm text-gray-600">Usage: {provider.usage}%</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="font-medium text-gray-900">{provider.cost}</p>
                        <p className="text-sm text-green-600">Savings: {provider.savings}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Authentication Tab */}
        {activeTab === 'authentication' && (
          <div className="space-y-8">
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-medium text-gray-900">OAuth 2.0 Platform Management</h3>
              </div>
              <div className="p-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {platformConnections.map((platform) => (
                    <div key={platform.platform} className="border border-gray-200 rounded-lg p-6">
                      <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center space-x-3">
                          <Globe className="h-6 w-6 text-indigo-500" />
                          <h4 className="font-medium text-gray-900">{platform.platform}</h4>
                        </div>
                        <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(platform.status)}`}>
                          {platform.status}
                        </span>
                      </div>
                      <div className="space-y-3">
                        <div className="flex justify-between text-sm">
                          <span className="text-gray-600">Connected Users:</span>
                          <span className="font-medium">{platform.connected}</span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span className="text-gray-600">Uptime:</span>
                          <span className="font-medium">{platform.uptime}</span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span className="text-gray-600">OAuth Version:</span>
                          <span className="font-medium">2.1 + PKCE</span>
                        </div>
                        <div className="pt-3 border-t">
                          <button className="w-full bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 transition-colors">
                            Manage Configuration
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* API Key Management */}
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-medium text-gray-900">API Key Management</h3>
                  <button className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700 transition-colors flex items-center space-x-2">
                    <Plus className="h-4 w-4" />
                    <span>Add API Key</span>
                  </button>
                </div>
              </div>
              <div className="p-6">
                <div className="space-y-4">
                  {aiProviders.map((provider) => (
                    <div key={provider.name} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                      <div className="flex items-center space-x-4">
                        <Key className="h-5 w-5 text-gray-400" />
                        <div>
                          <h4 className="font-medium text-gray-900">{provider.name}</h4>
                          <p className="text-sm text-gray-600">Status: {provider.status}</p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <button className="text-indigo-600 hover:text-indigo-800 text-sm">
                          <RefreshCw className="h-4 w-4" />
                        </button>
                        <button className="text-red-600 hover:text-red-800 text-sm">
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Security Tab */}
        {activeTab === 'security' && (
          <div className="space-y-8">
            {/* Security Overview */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Threat Level</p>
                    <p className="text-2xl font-bold text-gray-900 capitalize">{securityMetrics.threatLevel}</p>
                  </div>
                  <Shield className={`h-8 w-8 ${securityMetrics.threatLevel === 'low' ? 'text-green-500' : 'text-yellow-500'}`} />
                </div>
                <div className="mt-4">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getThreatLevelColor(securityMetrics.threatLevel)}`}>
                    System Secure
                  </span>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Blocked IPs</p>
                    <p className="text-2xl font-bold text-gray-900">{securityMetrics.blockedIPs}</p>
                  </div>
                  <Lock className="h-8 w-8 text-red-500" />
                </div>
                <div className="mt-4 text-sm text-gray-600">
                  Last 24 hours
                </div>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Failed Logins</p>
                    <p className="text-2xl font-bold text-gray-900">{securityMetrics.failedLogins}</p>
                  </div>
                  <XCircle className="h-8 w-8 text-orange-500" />
                </div>
                <div className="mt-4 text-sm text-gray-600">
                  Last hour
                </div>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Suspicious Activities</p>
                    <p className="text-2xl font-bold text-gray-900">{securityMetrics.suspiciousActivities}</p>
                  </div>
                  <AlertTriangle className="h-8 w-8 text-yellow-500" />
                </div>
                <div className="mt-4 text-sm text-gray-600">
                  Requires review
                </div>
              </div>
            </div>

            {/* Security Events */}
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-medium text-gray-900">Recent Security Events</h3>
              </div>
              <div className="p-6">
                <div className="space-y-4">
                  {[
                    { type: 'login_failure', user: 'user@example.com', ip: '192.168.1.100', time: '2 min ago', severity: 'medium' },
                    { type: 'oauth_success', user: 'admin@aideon.ai', ip: '10.0.0.1', time: '5 min ago', severity: 'low' },
                    { type: 'suspicious_activity', user: 'unknown', ip: '203.0.113.1', time: '15 min ago', severity: 'high' },
                    { type: 'rate_limit_exceeded', user: 'api_user', ip: '198.51.100.1', time: '1 hour ago', severity: 'medium' }
                  ].map((event, index) => (
                    <div key={index} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                      <div className="flex items-center space-x-4">
                        <div className={`h-3 w-3 rounded-full ${
                          event.severity === 'high' ? 'bg-red-500' :
                          event.severity === 'medium' ? 'bg-yellow-500' : 'bg-green-500'
                        }`}></div>
                        <div>
                          <h4 className="font-medium text-gray-900">{event.type.replace('_', ' ').toUpperCase()}</h4>
                          <p className="text-sm text-gray-600">User: {event.user} | IP: {event.ip}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-sm text-gray-900">{event.time}</p>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          event.severity === 'high' ? 'text-red-700 bg-red-100' :
                          event.severity === 'medium' ? 'text-yellow-700 bg-yellow-100' : 'text-green-700 bg-green-100'
                        }`}>
                          {event.severity}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Analytics Tab */}
        {activeTab === 'analytics' && (
          <div className="space-y-8">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Usage Analytics */}
              <div className="bg-white rounded-lg shadow">
                <div className="px-6 py-4 border-b border-gray-200">
                  <h3 className="text-lg font-medium text-gray-900">Platform Usage Analytics</h3>
                </div>
                <div className="p-6">
                  <div className="space-y-4">
                    {platformConnections.map((platform) => (
                      <div key={platform.platform} className="flex items-center justify-between">
                        <span className="text-sm font-medium text-gray-900">{platform.platform}</span>
                        <div className="flex items-center space-x-3">
                          <div className="w-32 bg-gray-200 rounded-full h-2">
                            <div 
                              className="bg-indigo-600 h-2 rounded-full" 
                              style={{ width: `${(platform.connected / 500) * 100}%` }}
                            ></div>
                          </div>
                          <span className="text-sm text-gray-600">{platform.connected}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Cost Analytics */}
              <div className="bg-white rounded-lg shadow">
                <div className="px-6 py-4 border-b border-gray-200">
                  <h3 className="text-lg font-medium text-gray-900">Cost Analytics</h3>
                </div>
                <div className="p-6">
                  <div className="space-y-4">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Monthly Spend</span>
                      <span className="text-lg font-bold text-gray-900">${systemStats.monthlySpend.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Previous Month</span>
                      <span className="text-lg font-medium text-gray-600">${systemStats.previousSpend.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between items-center pt-4 border-t">
                      <span className="text-sm font-medium text-green-600">Total Savings</span>
                      <span className="text-xl font-bold text-green-600">
                        ${(systemStats.previousSpend - systemStats.monthlySpend).toLocaleString()}
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm font-medium text-green-600">Savings Percentage</span>
                      <span className="text-xl font-bold text-green-600">{systemStats.costSavings}%</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Cost Optimization Tab */}
        {activeTab === 'cost-optimization' && (
          <div className="space-y-8">
            {/* Cost Overview */}
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-medium text-gray-900">Cost Optimization Dashboard</h3>
              </div>
              <div className="p-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                  <div className="text-center">
                    <div className="text-3xl font-bold text-green-600">{systemStats.costSavings}%</div>
                    <div className="text-sm text-gray-600">Total Savings</div>
                  </div>
                  <div className="text-center">
                    <div className="text-3xl font-bold text-indigo-600">${systemStats.monthlySpend.toLocaleString()}</div>
                    <div className="text-sm text-gray-600">Monthly Spend</div>
                  </div>
                  <div className="text-center">
                    <div className="text-3xl font-bold text-gray-900">${(systemStats.previousSpend - systemStats.monthlySpend).toLocaleString()}</div>
                    <div className="text-sm text-gray-600">Amount Saved</div>
                  </div>
                </div>

                <div className="space-y-4">
                  <h4 className="font-medium text-gray-900">AI Provider Cost Breakdown</h4>
                  {aiProviders.map((provider) => (
                    <div key={provider.name} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                      <div className="flex items-center space-x-4">
                        <div className="flex-shrink-0">
                          <DollarSign className="h-6 w-6 text-green-500" />
                        </div>
                        <div>
                          <h5 className="font-medium text-gray-900">{provider.name}</h5>
                          <p className="text-sm text-gray-600">Usage: {provider.usage}%</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="font-medium text-gray-900">{provider.cost}</p>
                        <p className={`text-sm ${provider.savings === '0%' ? 'text-gray-600' : 'text-green-600'}`}>
                          {provider.savings === '0%' ? 'Premium' : `${provider.savings} savings`}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default EnhancedAdminDashboard;

