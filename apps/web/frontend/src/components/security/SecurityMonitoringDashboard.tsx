import React, { useState, useEffect } from 'react';
import { 
  Shield, 
  AlertTriangle, 
  XCircle, 
  CheckCircle,
  Eye,
  Lock,
  Unlock,
  Activity,
  TrendingUp,
  TrendingDown,
  Globe,
  Clock,
  User,
  MapPin,
  Filter,
  Download,
  RefreshCw,
  Search,
  Calendar,
  BarChart3,
  PieChart,
  LineChart,
  Zap,
  Ban,
  UserX,
  AlertCircle,
  Info,
  Settings,
  Bell,
  BellOff
} from 'lucide-react';

// Security Monitoring Dashboard
export const SecurityMonitoringDashboard = () => {
  const [timeRange, setTimeRange] = useState('24h');
  const [threatFilter, setThreatFilter] = useState('all');
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [selectedEvent, setSelectedEvent] = useState(null);

  const [securityMetrics, setSecurityMetrics] = useState({
    threatLevel: 'low',
    totalEvents: 1247,
    blockedIPs: 23,
    failedLogins: 45,
    suspiciousActivities: 8,
    activeThreats: 2,
    resolvedThreats: 156,
    lastUpdate: new Date().toISOString()
  });

  const [recentEvents, setRecentEvents] = useState([
    {
      id: 1,
      type: 'failed_login',
      severity: 'medium',
      timestamp: '2025-01-11T10:30:00Z',
      ip: '192.168.1.100',
      location: 'New York, US',
      user: 'user@example.com',
      details: 'Multiple failed login attempts detected',
      status: 'investigating'
    },
    {
      id: 2,
      type: 'suspicious_oauth',
      severity: 'high',
      timestamp: '2025-01-11T10:25:00Z',
      ip: '203.0.113.1',
      location: 'Unknown',
      user: 'admin@aideon.ai',
      details: 'OAuth request from unusual location',
      status: 'blocked'
    },
    {
      id: 3,
      type: 'rate_limit_exceeded',
      severity: 'low',
      timestamp: '2025-01-11T10:20:00Z',
      ip: '198.51.100.1',
      location: 'London, UK',
      user: 'api_user',
      details: 'API rate limit exceeded',
      status: 'resolved'
    },
    {
      id: 4,
      type: 'brute_force_attempt',
      severity: 'high',
      timestamp: '2025-01-11T10:15:00Z',
      ip: '192.0.2.1',
      location: 'Moscow, RU',
      user: 'unknown',
      details: 'Brute force attack detected and blocked',
      status: 'blocked'
    },
    {
      id: 5,
      type: 'successful_login',
      severity: 'low',
      timestamp: '2025-01-11T10:10:00Z',
      ip: '10.0.0.1',
      location: 'San Francisco, US',
      user: 'admin@aideon.ai',
      details: 'Successful admin login',
      status: 'resolved'
    }
  ]);

  const [blockedIPs, setBlockedIPs] = useState([
    { ip: '203.0.113.1', reason: 'Suspicious OAuth activity', blockedAt: '2025-01-11T10:25:00Z', attempts: 15 },
    { ip: '192.0.2.1', reason: 'Brute force attack', blockedAt: '2025-01-11T10:15:00Z', attempts: 50 },
    { ip: '198.51.100.2', reason: 'Rate limit exceeded', blockedAt: '2025-01-11T09:45:00Z', attempts: 8 },
    { ip: '203.0.113.5', reason: 'Malicious activity', blockedAt: '2025-01-11T09:30:00Z', attempts: 25 }
  ]);

  const [threatTrends, setThreatTrends] = useState([
    { time: '00:00', threats: 5, blocked: 3 },
    { time: '04:00', threats: 8, blocked: 6 },
    { time: '08:00', threats: 12, blocked: 10 },
    { time: '12:00', threats: 15, blocked: 12 },
    { time: '16:00', threats: 18, blocked: 15 },
    { time: '20:00', threats: 10, blocked: 8 },
    { time: '24:00', threats: 7, blocked: 5 }
  ]);

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical': return 'text-red-700 bg-red-100 border-red-200';
      case 'high': return 'text-orange-700 bg-orange-100 border-orange-200';
      case 'medium': return 'text-yellow-700 bg-yellow-100 border-yellow-200';
      case 'low': return 'text-green-700 bg-green-100 border-green-200';
      default: return 'text-gray-700 bg-gray-100 border-gray-200';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'blocked': return 'text-red-700 bg-red-100';
      case 'investigating': return 'text-yellow-700 bg-yellow-100';
      case 'resolved': return 'text-green-700 bg-green-100';
      default: return 'text-gray-700 bg-gray-100';
    }
  };

  const getThreatLevelColor = (level) => {
    switch (level) {
      case 'critical': return 'text-red-600 bg-red-100';
      case 'high': return 'text-orange-600 bg-orange-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'low': return 'text-green-600 bg-green-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleString();
  };

  const getEventIcon = (type) => {
    switch (type) {
      case 'failed_login': return UserX;
      case 'suspicious_oauth': return AlertTriangle;
      case 'rate_limit_exceeded': return Zap;
      case 'brute_force_attempt': return Ban;
      case 'successful_login': return CheckCircle;
      default: return AlertCircle;
    }
  };

  const filteredEvents = recentEvents.filter(event => {
    if (threatFilter === 'all') return true;
    return event.severity === threatFilter;
  });

  useEffect(() => {
    if (autoRefresh) {
      const interval = setInterval(() => {
        setSecurityMetrics(prev => ({
          ...prev,
          lastUpdate: new Date().toISOString()
        }));
      }, 30000); // Refresh every 30 seconds

      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-8">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Security Monitoring Dashboard</h1>
            <p className="text-gray-600 mt-1">Real-time threat detection and security analytics</p>
          </div>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setAutoRefresh(!autoRefresh)}
                className={`p-2 rounded-lg ${autoRefresh ? 'bg-green-100 text-green-600' : 'bg-gray-100 text-gray-600'}`}
              >
                {autoRefresh ? <Bell className="h-4 w-4" /> : <BellOff className="h-4 w-4" />}
              </button>
              <span className="text-sm text-gray-600">
                Auto-refresh {autoRefresh ? 'ON' : 'OFF'}
              </span>
            </div>
            <div className="text-right">
              <p className="text-sm font-medium text-gray-900">
                Threat Level: <span className={`px-2 py-1 rounded-full text-xs ${getThreatLevelColor(securityMetrics.threatLevel)}`}>
                  {securityMetrics.threatLevel.toUpperCase()}
                </span>
              </p>
              <p className="text-xs text-gray-500">Last updated: {formatTimestamp(securityMetrics.lastUpdate)}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Security Metrics Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Events</p>
              <p className="text-3xl font-bold text-gray-900">{securityMetrics.totalEvents.toLocaleString()}</p>
            </div>
            <Activity className="h-8 w-8 text-blue-500" />
          </div>
          <div className="mt-4 flex items-center text-sm">
            <TrendingUp className="h-4 w-4 text-green-500 mr-1" />
            <span className="text-green-600">+5% from yesterday</span>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Blocked IPs</p>
              <p className="text-3xl font-bold text-red-600">{securityMetrics.blockedIPs}</p>
            </div>
            <Ban className="h-8 w-8 text-red-500" />
          </div>
          <div className="mt-4 flex items-center text-sm">
            <TrendingDown className="h-4 w-4 text-green-500 mr-1" />
            <span className="text-green-600">-12% from yesterday</span>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Failed Logins</p>
              <p className="text-3xl font-bold text-yellow-600">{securityMetrics.failedLogins}</p>
            </div>
            <UserX className="h-8 w-8 text-yellow-500" />
          </div>
          <div className="mt-4 flex items-center text-sm">
            <TrendingUp className="h-4 w-4 text-yellow-500 mr-1" />
            <span className="text-yellow-600">+8% from yesterday</span>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Active Threats</p>
              <p className="text-3xl font-bold text-orange-600">{securityMetrics.activeThreats}</p>
            </div>
            <AlertTriangle className="h-8 w-8 text-orange-500" />
          </div>
          <div className="mt-4 flex items-center text-sm">
            <AlertCircle className="h-4 w-4 text-orange-500 mr-1" />
            <span className="text-orange-600">Requires attention</span>
          </div>
        </div>
      </div>

      {/* Threat Trends Chart */}
      <div className="bg-white rounded-lg shadow-sm border">
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">Threat Trends (24h)</h2>
            <div className="flex items-center space-x-2">
              <select 
                value={timeRange}
                onChange={(e) => setTimeRange(e.target.value)}
                className="border border-gray-300 rounded-md px-3 py-1 text-sm"
              >
                <option value="1h">Last Hour</option>
                <option value="24h">Last 24 Hours</option>
                <option value="7d">Last 7 Days</option>
                <option value="30d">Last 30 Days</option>
              </select>
            </div>
          </div>
        </div>
        <div className="p-6">
          <div className="h-64 flex items-end justify-between space-x-2">
            {threatTrends.map((data, index) => (
              <div key={index} className="flex-1 flex flex-col items-center">
                <div className="w-full flex flex-col space-y-1">
                  <div 
                    className="bg-red-500 rounded-t"
                    style={{ height: `${(data.threats / 20) * 200}px` }}
                    title={`Threats: ${data.threats}`}
                  ></div>
                  <div 
                    className="bg-green-500 rounded-b"
                    style={{ height: `${(data.blocked / 20) * 200}px` }}
                    title={`Blocked: ${data.blocked}`}
                  ></div>
                </div>
                <span className="text-xs text-gray-600 mt-2">{data.time}</span>
              </div>
            ))}
          </div>
          <div className="flex items-center justify-center space-x-6 mt-4">
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-red-500 rounded"></div>
              <span className="text-sm text-gray-600">Threats Detected</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-green-500 rounded"></div>
              <span className="text-sm text-gray-600">Threats Blocked</span>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Security Events */}
      <div className="bg-white rounded-lg shadow-sm border">
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">Recent Security Events</h2>
            <div className="flex items-center space-x-2">
              <select 
                value={threatFilter}
                onChange={(e) => setThreatFilter(e.target.value)}
                className="border border-gray-300 rounded-md px-3 py-1 text-sm"
              >
                <option value="all">All Severities</option>
                <option value="critical">Critical</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </select>
              <button className="bg-indigo-600 text-white px-3 py-1 rounded-md hover:bg-indigo-700 transition-colors text-sm">
                <Download className="h-4 w-4 inline mr-1" />
                Export
              </button>
            </div>
          </div>
        </div>
        <div className="p-6">
          <div className="space-y-4">
            {filteredEvents.map((event) => {
              const EventIcon = getEventIcon(event.type);
              return (
                <div 
                  key={event.id} 
                  className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow cursor-pointer"
                  onClick={() => setSelectedEvent(event)}
                >
                  <div className="flex items-center space-x-4">
                    <div className={`p-2 rounded-lg ${getSeverityColor(event.severity)}`}>
                      <EventIcon className="h-5 w-5" />
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-900">
                        {event.type.replace(/_/g, ' ').toUpperCase()}
                      </h4>
                      <p className="text-sm text-gray-600">{event.details}</p>
                      <div className="flex items-center space-x-4 text-xs text-gray-500 mt-1">
                        <span className="flex items-center">
                          <Globe className="h-3 w-3 mr-1" />
                          {event.ip}
                        </span>
                        <span className="flex items-center">
                          <MapPin className="h-3 w-3 mr-1" />
                          {event.location}
                        </span>
                        <span className="flex items-center">
                          <User className="h-3 w-3 mr-1" />
                          {event.user}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="flex items-center space-x-2 mb-2">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSeverityColor(event.severity)}`}>
                        {event.severity}
                      </span>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(event.status)}`}>
                        {event.status}
                      </span>
                    </div>
                    <p className="text-xs text-gray-500">{formatTimestamp(event.timestamp)}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Blocked IPs */}
      <div className="bg-white rounded-lg shadow-sm border">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Blocked IP Addresses</h2>
        </div>
        <div className="p-6">
          <div className="space-y-3">
            {blockedIPs.map((blockedIP, index) => (
              <div key={index} className="flex items-center justify-between p-3 border border-gray-200 rounded-lg">
                <div className="flex items-center space-x-4">
                  <Ban className="h-5 w-5 text-red-500" />
                  <div>
                    <h4 className="font-medium text-gray-900">{blockedIP.ip}</h4>
                    <p className="text-sm text-gray-600">{blockedIP.reason}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium text-gray-900">{blockedIP.attempts} attempts</p>
                  <p className="text-xs text-gray-500">Blocked: {formatTimestamp(blockedIP.blockedAt)}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Event Details Modal */}
      {selectedEvent && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="px-6 py-4 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-900">Security Event Details</h3>
                <button 
                  onClick={() => setSelectedEvent(null)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  <XCircle className="h-6 w-6" />
                </button>
              </div>
            </div>
            
            <div className="p-6 space-y-6">
              {/* Event Overview */}
              <div>
                <h4 className="font-medium text-gray-900 mb-3">Event Overview</h4>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm text-gray-600">Event Type</label>
                    <p className="font-medium">{selectedEvent.type.replace(/_/g, ' ').toUpperCase()}</p>
                  </div>
                  <div>
                    <label className="text-sm text-gray-600">Severity</label>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSeverityColor(selectedEvent.severity)}`}>
                      {selectedEvent.severity}
                    </span>
                  </div>
                  <div>
                    <label className="text-sm text-gray-600">Status</label>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(selectedEvent.status)}`}>
                      {selectedEvent.status}
                    </span>
                  </div>
                  <div>
                    <label className="text-sm text-gray-600">Timestamp</label>
                    <p className="font-medium">{formatTimestamp(selectedEvent.timestamp)}</p>
                  </div>
                </div>
              </div>

              {/* Source Information */}
              <div>
                <h4 className="font-medium text-gray-900 mb-3">Source Information</h4>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm text-gray-600">IP Address</label>
                    <p className="font-medium">{selectedEvent.ip}</p>
                  </div>
                  <div>
                    <label className="text-sm text-gray-600">Location</label>
                    <p className="font-medium">{selectedEvent.location}</p>
                  </div>
                  <div>
                    <label className="text-sm text-gray-600">User</label>
                    <p className="font-medium">{selectedEvent.user}</p>
                  </div>
                </div>
              </div>

              {/* Event Details */}
              <div>
                <h4 className="font-medium text-gray-900 mb-3">Details</h4>
                <p className="text-gray-700 bg-gray-50 p-3 rounded-lg">{selectedEvent.details}</p>
              </div>

              {/* Actions */}
              <div className="flex space-x-3 pt-4 border-t">
                <button className="flex-1 bg-red-600 text-white py-2 px-4 rounded-md hover:bg-red-700 transition-colors">
                  Block IP
                </button>
                <button className="flex-1 bg-yellow-600 text-white py-2 px-4 rounded-md hover:bg-yellow-700 transition-colors">
                  Mark as False Positive
                </button>
                <button className="flex-1 bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 transition-colors">
                  Resolve
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SecurityMonitoringDashboard;

