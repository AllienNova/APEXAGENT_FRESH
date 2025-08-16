// Enterprise Security Features Component
import React, { useState, useEffect } from 'react';
import { Shield, Lock, AlertTriangle, CheckCircle, Eye, EyeOff, FileText, Users, Server, Database, Globe, RefreshCw, Search, Filter, Download, Calendar, ChevronDown, Bell, Settings, Info, HelpCircle, XCircle, CheckSquare, Clock, ArrowRight } from 'lucide-react';

// Mock data for demonstration
const securityMetrics = {
  threatDetections: [
    { date: '2025-05-20', value: 12 },
    { date: '2025-05-21', value: 8 },
    { date: '2025-05-22', value: 15 },
    { date: '2025-05-23', value: 7 },
    { date: '2025-05-24', value: 5 },
    { date: '2025-05-25', value: 9 },
    { date: '2025-05-26', value: 6 },
  ],
  complianceScore: 94,
  vulnerabilities: {
    critical: 0,
    high: 2,
    medium: 5,
    low: 8
  },
  securityIncidents: [
    { id: 1, type: 'Unusual Access Pattern', severity: 'medium', status: 'resolved', timestamp: '2025-05-26 08:23:15', description: 'Multiple failed login attempts detected from unusual location', resolution: 'IP address blocked, account secured' },
    { id: 2, type: 'Data Access Anomaly', severity: 'low', status: 'resolved', timestamp: '2025-05-25 14:17:42', description: 'Unusual pattern of sensitive data access detected', resolution: 'Verified as legitimate user activity' },
    { id: 3, type: 'API Rate Limit', severity: 'low', status: 'resolved', timestamp: '2025-05-24 11:05:33', description: 'API rate limit exceeded for authentication endpoint', resolution: 'Rate limiting adjusted, monitoring in place' }
  ],
  auditLogs: [
    { id: 1, action: 'User Authentication', user: 'john.doe@example.com', timestamp: '2025-05-27 09:12:45', status: 'success', details: 'Successful login from known device and location' },
    { id: 2, action: 'Sensitive Data Access', user: 'admin@example.com', timestamp: '2025-05-27 08:45:12', status: 'success', details: 'Accessed financial report data with proper authorization' },
    { id: 3, action: 'Configuration Change', user: 'system.admin@example.com', timestamp: '2025-05-26 16:30:27', status: 'success', details: 'Updated security policy for data retention' },
    { id: 4, action: 'API Key Generation', user: 'developer@example.com', timestamp: '2025-05-26 14:22:18', status: 'success', details: 'Generated new API key with restricted permissions' },
    { id: 5, action: 'User Authentication', user: 'jane.smith@example.com', timestamp: '2025-05-26 10:05:33', status: 'failure', details: 'Failed login attempt from unknown location' }
  ],
  complianceFrameworks: [
    { id: 'gdpr', name: 'GDPR', status: 'compliant', score: 96, lastAudit: '2025-05-15', nextAudit: '2025-08-15' },
    { id: 'hipaa', name: 'HIPAA', status: 'compliant', score: 98, lastAudit: '2025-05-10', nextAudit: '2025-08-10' },
    { id: 'soc2', name: 'SOC2 Type II', status: 'compliant', score: 94, lastAudit: '2025-04-22', nextAudit: '2025-07-22' },
    { id: 'pci', name: 'PCI DSS', status: 'in_progress', score: 87, lastAudit: '2025-05-05', nextAudit: '2025-06-05' }
  ],
  regions: [
    { id: 'us-east', name: 'US East', status: 'secure', threatLevel: 'low', complianceStatus: 'compliant' },
    { id: 'us-west', name: 'US West', status: 'secure', threatLevel: 'low', complianceStatus: 'compliant' },
    { id: 'eu-central', name: 'EU Central', status: 'secure', threatLevel: 'low', complianceStatus: 'compliant' },
    { id: 'ap-southeast', name: 'Asia Pacific', status: 'secure', threatLevel: 'medium', complianceStatus: 'compliant' },
    { id: 'sa-east', name: 'South America', status: 'secure', threatLevel: 'low', complianceStatus: 'compliant' }
  ]
};

const EnterpriseSecurityFeatures = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [timeRange, setTimeRange] = useState('week');
  const [showPolicyModal, setShowPolicyModal] = useState(false);
  const [selectedPolicy, setSelectedPolicy] = useState(null);
  
  // Simple line chart component
  const LineChart = ({ data, height = 100, color = '#3B82F6' }) => {
    const max = Math.max(...data.map(d => d.value)) * 1.1;
    const min = Math.min(...data.map(d => d.value)) * 0.9;
    const range = max - min;
    
    const points = data.map((d, i) => {
      const x = (i / (data.length - 1)) * 100;
      const y = 100 - ((d.value - min) / range) * 100;
      return `${x},${y}`;
    }).join(' ');
    
    return (
      <svg width="100%" height={height} className="overflow-visible">
        <polyline
          points={points}
          fill="none"
          stroke={color}
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        {data.map((d, i) => (
          <circle
            key={i}
            cx={`${(i / (data.length - 1)) * 100}%`}
            cy={`${100 - ((d.value - min) / range) * 100}%`}
            r="3"
            fill="white"
            stroke={color}
            strokeWidth="2"
          />
        ))}
      </svg>
    );
  };
  
  // Circular progress component
  const CircularProgress = ({ value, size = 120, strokeWidth = 8, color = '#3B82F6' }) => {
    const radius = (size - strokeWidth) / 2;
    const circumference = radius * 2 * Math.PI;
    const offset = circumference - (value / 100) * circumference;
    
    return (
      <svg width={size} height={size} className="transform -rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="#E5E7EB"
          strokeWidth={strokeWidth}
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
        />
        <text
          x="50%"
          y="50%"
          dy=".3em"
          textAnchor="middle"
          fill="currentColor"
          className="text-lg font-bold transform rotate-90"
        >
          {value}%
        </text>
      </svg>
    );
  };

  const SecurityDashboard = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold">Security Dashboard</h2>
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg p-1">
            <button 
              className={`px-3 py-1.5 text-xs rounded ${timeRange === 'day' ? 'bg-blue-500 text-white' : 'text-gray-600 dark:text-gray-300'}`}
              onClick={() => setTimeRange('day')}
            >
              Day
            </button>
            <button 
              className={`px-3 py-1.5 text-xs rounded ${timeRange === 'week' ? 'bg-blue-500 text-white' : 'text-gray-600 dark:text-gray-300'}`}
              onClick={() => setTimeRange('week')}
            >
              Week
            </button>
            <button 
              className={`px-3 py-1.5 text-xs rounded ${timeRange === 'month' ? 'bg-blue-500 text-white' : 'text-gray-600 dark:text-gray-300'}`}
              onClick={() => setTimeRange('month')}
            >
              Month
            </button>
          </div>
          
          <button className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg">
            <RefreshCw className="w-5 h-5" />
          </button>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-medium text-sm">Security Status</h3>
            <Shield className="w-5 h-5 text-green-500" />
          </div>
          <p className="text-2xl font-bold mb-1">Secure</p>
          <div className="flex items-center text-xs text-green-600">
            <CheckCircle className="w-3 h-3 mr-1" />
            <span>All systems protected</span>
          </div>
        </div>
        
        <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-medium text-sm">Compliance Score</h3>
            <CheckSquare className="w-5 h-5 text-blue-500" />
          </div>
          <p className="text-2xl font-bold mb-1">{securityMetrics.complianceScore}%</p>
          <div className="flex items-center text-xs text-green-600">
            <ArrowRight className="w-3 h-3 mr-1" />
            <span>Meets all requirements</span>
          </div>
        </div>
        
        <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-medium text-sm">Active Threats</h3>
            <AlertTriangle className="w-5 h-5 text-yellow-500" />
          </div>
          <p className="text-2xl font-bold mb-1">{securityMetrics.vulnerabilities.high + securityMetrics.vulnerabilities.critical}</p>
          <div className="flex items-center text-xs text-yellow-600">
            <Clock className="w-3 h-3 mr-1" />
            <span>2 high priority issues</span>
          </div>
        </div>
        
        <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-medium text-sm">Protected Regions</h3>
            <Globe className="w-5 h-5 text-purple-500" />
          </div>
          <p className="text-2xl font-bold mb-1">{securityMetrics.regions.length}</p>
          <div className="flex items-center text-xs text-green-600">
            <CheckCircle className="w-3 h-3 mr-1" />
            <span>All regions compliant</span>
          </div>
        </div>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="p-4 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold">Threat Detection Trend</h3>
              <button className="text-xs text-blue-600 dark:text-blue-400 hover:underline">
                View Details
              </button>
            </div>
          </div>
          <div className="p-4">
            <div className="h-64">
              <LineChart data={securityMetrics.threatDetections} height={250} color="#EF4444" />
            </div>
            <div className="flex justify-between mt-2 text-xs text-gray-500">
              {securityMetrics.threatDetections.map((d, i) => (
                <span key={i}>{d.date.split('-')[2]}</span>
              ))}
            </div>
          </div>
        </div>
        
        <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="p-4 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold">Vulnerability Summary</h3>
              <button className="text-xs text-blue-600 dark:text-blue-400 hover:underline">
                Run Scan
              </button>
            </div>
          </div>
          <div className="p-4">
            <div className="grid grid-cols-2 gap-6">
              <div className="flex flex-col items-center justify-center">
                <CircularProgress value={securityMetrics.complianceScore} size={150} color="#10B981" />
                <p className="mt-4 text-sm font-medium">Overall Security Score</p>
              </div>
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="flex items-center">
                      <div className="w-2 h-2 rounded-full bg-red-500 mr-2"></div>
                      Critical
                    </span>
                    <span className="font-medium">{securityMetrics.vulnerabilities.critical}</span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div className="h-2 rounded-full bg-red-500" style={{width: `${(securityMetrics.vulnerabilities.critical / 10) * 100}%`}}></div>
                  </div>
                </div>
                
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="flex items-center">
                      <div className="w-2 h-2 rounded-full bg-orange-500 mr-2"></div>
                      High
                    </span>
                    <span className="font-medium">{securityMetrics.vulnerabilities.high}</span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div className="h-2 rounded-full bg-orange-500" style={{width: `${(securityMetrics.vulnerabilities.high / 10) * 100}%`}}></div>
                  </div>
                </div>
                
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="flex items-center">
                      <div className="w-2 h-2 rounded-full bg-yellow-500 mr-2"></div>
                      Medium
                    </span>
                    <span className="font-medium">{securityMetrics.vulnerabilities.medium}</span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div className="h-2 rounded-full bg-yellow-500" style={{width: `${(securityMetrics.vulnerabilities.medium / 10) * 100}%`}}></div>
                  </div>
                </div>
                
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="flex items-center">
                      <div className="w-2 h-2 rounded-full bg-blue-500 mr-2"></div>
                      Low
                    </span>
                    <span className="font-medium">{securityMetrics.vulnerabilities.low}</span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div className="h-2 rounded-full bg-blue-500" style={{width: `${(securityMetrics.vulnerabilities.low / 10) * 100}%`}}></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div className="grid grid-cols-1 gap-6">
        <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="p-4 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold">Recent Security Incidents</h3>
              <button className="text-xs text-blue-600 dark:text-blue-400 hover:underline">
                View All
              </button>
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 dark:bg-gray-800 text-xs text-gray-700 dark:text-gray-300">
                <tr>
                  <th className="px-4 py-2 text-left">Type</th>
                  <th className="px-4 py-2 text-left">Severity</th>
                  <th className="px-4 py-2 text-left">Status</th>
                  <th className="px-4 py-2 text-left">Timestamp</th>
                  <th className="px-4 py-2 text-left">Description</th>
                  <th className="px-4 py-2 text-left">Resolution</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                {securityMetrics.securityIncidents.map(incident => (
                  <tr key={incident.id} className="text-sm">
                    <td className="px-4 py-3">{incident.type}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 rounded-full text-xs ${
                        incident.severity === 'critical' ? 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-300' :
                        incident.severity === 'high' ? 'bg-orange-100 text-orange-800 dark:bg-orange-900/20 dark:text-orange-300' :
                        incident.severity === 'medium' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-300' :
                        'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-300'
                      }`}>
                        {incident.severity.charAt(0).toUpperCase() + incident.severity.slice(1)}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 rounded-full text-xs ${
                        incident.status === 'resolved' ? 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-300' :
                        incident.status === 'in_progress' ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-300' :
                        'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
                      }`}>
                        {incident.status.charAt(0).toUpperCase() + incident.status.slice(1)}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-gray-500">{incident.timestamp}</td>
                    <td className="px-4 py-3">{incident.description}</td>
                    <td className="px-4 py-3">{incident.resolution}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
  
  const ZeroTrustConfiguration = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold">Zero-Trust Configuration</h2>
        <div className="flex items-center space-x-3">
          <button className="px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 flex items-center space-x-2">
            <RefreshCw className="w-4 h-4" />
            <span>Reset Defaults</span>
          </button>
          <button className="px-3 py-2 text-sm bg-blue-500 text-white rounded-lg hover:bg-blue-600 flex items-center space-x-2">
            <Shield className="w-4 h-4" />
            <span>Apply Configuration</span>
          </button>
        </div>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
            <div className="p-4 border-b border-gray-200 dark:border-gray-700">
              <h3 className="font-semibold">Security Policies</h3>
            </div>
            <div className="p-4">
              <div className="space-y-3">
                <div 
                  className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer border border-gray-200 dark:border-gray-700"
                  onClick={() => {
                    setSelectedPolicy({
                      id: 'authentication',
                      name: 'Authentication Policy',
                      description: 'Controls how users and services authenticate to the system',
                      status: 'enabled'
                    });
                    setShowPolicyModal(true);
                  }}
                >
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 rounded-lg bg-blue-100 dark:bg-blue-900/20 flex items-center justify-center text-blue-500">
                      <Lock className="w-4 h-4" />
                    </div>
                    <div>
                      <h4 className="text-sm font-medium">Authentication Policy</h4>
                      <p className="text-xs text-gray-500">Multi-factor, risk-based</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 rounded-full bg-green-500"></div>
                    <span className="text-xs text-gray-500">Enabled</span>
                  </div>
                </div>
                
                <div 
                  className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer border border-gray-200 dark:border-gray-700"
                  onClick={() => {
                    setSelectedPolicy({
                      id: 'authorization',
                      name: 'Authorization Policy',
                      description: 'Defines access control and permissions for resources',
                      status: 'enabled'
                    });
                    setShowPolicyModal(true);
                  }}
                >
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 rounded-lg bg-purple-100 dark:bg-purple-900/20 flex items-center justify-center text-purple-500">
                      <Users className="w-4 h-4" />
                    </div>
                    <div>
                      <h4 className="text-sm font-medium">Authorization Policy</h4>
                      <p className="text-xs text-gray-500">Least privilege, RBAC</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 rounded-full bg-green-500"></div>
                    <span className="text-xs text-gray-500">Enabled</span>
                  </div>
                </div>
                
                <div 
                  className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer border border-gray-200 dark:border-gray-700"
                  onClick={() => {
                    setSelectedPolicy({
                      id: 'data_protection',
                      name: 'Data Protection Policy',
                      description: 'Controls encryption and data handling requirements',
                      status: 'enabled'
                    });
                    setShowPolicyModal(true);
                  }}
                >
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 rounded-lg bg-green-100 dark:bg-green-900/20 flex items-center justify-center text-green-500">
                      <Database className="w-4 h-4" />
                    </div>
                    <div>
                      <h4 className="text-sm font-medium">Data Protection Policy</h4>
                      <p className="text-xs text-gray-500">Encryption, masking</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 rounded-full bg-green-500"></div>
                    <span className="text-xs text-gray-500">Enabled</span>
                  </div>
                </div>
                
                <div 
                  className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer border border-gray-200 dark:border-gray-700"
                  onClick={() => {
                    setSelectedPolicy({
                      id: 'network_security',
                      name: 'Network Security Policy',
                      description: 'Defines network access controls and traffic policies',
                      status: 'enabled'
                    });
                    setShowPolicyModal(true);
                  }}
                >
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 rounded-lg bg-orange-100 dark:bg-orange-900/20 flex items-center justify-center text-orange-500">
                      <Globe className="w-4 h-4" />
                    </div>
                    <div>
                      <h4 className="text-sm font-medium">Network Security Policy</h4>
                      <p className="text-xs text-gray-500">Micro-segmentation</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 rounded-full bg-green-500"></div>
                    <span className="text-xs text-gray-500">Enabled</span>
                  </div>
                </div>
                
                <div 
                  className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer border border-gray-200 dark:border-gray-700"
                  onClick={() => {
                    setSelectedPolicy({
                      id: 'monitoring',
                      name: 'Monitoring & Logging Policy',
                      description: 'Defines security monitoring and audit logging requirements',
                      status: 'enabled'
                    });
                    setShowPolicyModal(true);
                  }}
                >
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 rounded-lg bg-red-100 dark:bg-red-900/20 flex items-center justify-center text-red-500">
                      <Eye className="w-4 h-4" />
                    </div>
                    <div>
                      <h4 className="text-sm font-medium">Monitoring & Logging</h4>
                      <p className="text-xs text-gray-500">Continuous monitoring</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 rounded-full bg-green-500"></div>
                    <span className="text-xs text-gray-500">Enabled</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div className="lg:col-span-2">
          <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
            <div className="p-4 border-b border-gray-200 dark:border-gray-700">
              <h3 className="font-semibold">Zero-Trust Architecture</h3>
            </div>
            <div className="p-4">
              <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-6 mb-6">
                <div className="relative h-[300px]">
                  {/* This is a simplified visualization - in a real implementation, this would be a proper architecture diagram */}
                  <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
                    <div className="w-20 h-20 rounded-full bg-blue-100 dark:bg-blue-900/20 flex items-center justify-center text-blue-500 border-2 border-blue-500">
                      <Shield className="w-10 h-10" />
                    </div>
                    <div className="text-center mt-2 font-medium">Zero-Trust Core</div>
                  </div>
                  
                  <div className="absolute top-1/4 left-1/4">
                    <div className="w-16 h-16 rounded-full bg-purple-100 dark:bg-purple-900/20 flex items-center justify-center text-purple-500 border-2 border-purple-500">
                      <Users className="w-8 h-8" />
                    </div>
                    <div className="text-center mt-2 font-medium text-sm">Identity</div>
                  </div>
                  
                  <div className="absolute top-1/4 right-1/4">
                    <div className="w-16 h-16 rounded-full bg-green-100 dark:bg-green-900/20 flex items-center justify-center text-green-500 border-2 border-green-500">
                      <Database className="w-8 h-8" />
                    </div>
                    <div className="text-center mt-2 font-medium text-sm">Data</div>
                  </div>
                  
                  <div className="absolute bottom-1/4 left-1/4">
                    <div className="w-16 h-16 rounded-full bg-orange-100 dark:bg-orange-900/20 flex items-center justify-center text-orange-500 border-2 border-orange-500">
                      <Globe className="w-8 h-8" />
                    </div>
                    <div className="text-center mt-2 font-medium text-sm">Network</div>
                  </div>
                  
                  <div className="absolute bottom-1/4 right-1/4">
                    <div className="w-16 h-16 rounded-full bg-red-100 dark:bg-red-900/20 flex items-center justify-center text-red-500 border-2 border-red-500">
                      <Server className="w-8 h-8" />
                    </div>
                    <div className="text-center mt-2 font-medium text-sm">Workloads</div>
                  </div>
                  
                  {/* Connection lines would be SVG paths in a real implementation */}
                  <svg className="absolute inset-0 w-full h-full pointer-events-none" style={{ zIndex: 0 }}>
                    <path d="M 200,150 L 150,75" stroke="#8B5CF6" strokeWidth="2" fill="none" />
                    <path d="M 200,150 L 350,75" stroke="#10B981" strokeWidth="2" fill="none" />
                    <path d="M 200,150 L 150,225" stroke="#F97316" strokeWidth="2" fill="none" />
                    <path d="M 200,150 L 350,225" stroke="#EF4444" strokeWidth="2" fill="none" />
                  </svg>
                </div>
              </div>
              
              <div className="space-y-4">
                <div>
                  <h4 className="text-sm font-medium mb-2">Zero-Trust Principles</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-3">
                      <div className="flex items-start space-x-3">
                        <div className="flex-shrink-0 mt-0.5">
                          <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400" />
                        </div>
                        <div>
                          <h5 className="text-sm font-medium">Never Trust, Always Verify</h5>
                          <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                            All access requests are fully authenticated, authorized, and encrypted
                          </p>
                        </div>
                      </div>
                    </div>
                    
                    <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-3">
                      <div className="flex items-start space-x-3">
                        <div className="flex-shrink-0 mt-0.5">
                          <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400" />
                        </div>
                        <div>
                          <h5 className="text-sm font-medium">Least Privilege Access</h5>
                          <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                            Access is limited to only what is needed for specific tasks
                          </p>
                        </div>
                      </div>
                    </div>
                    
                    <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-3">
                      <div className="flex items-start space-x-3">
                        <div className="flex-shrink-0 mt-0.5">
                          <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400" />
                        </div>
                        <div>
                          <h5 className="text-sm font-medium">Assume Breach</h5>
                          <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                            Segment access, verify continuously, and minimize blast radius
                          </p>
                        </div>
                      </div>
                    </div>
                    
                    <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-3">
                      <div className="flex items-start space-x-3">
                        <div className="flex-shrink-0 mt-0.5">
                          <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400" />
                        </div>
                        <div>
                          <h5 className="text-sm font-medium">Continuous Monitoring</h5>
                          <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                            All resources and access are continuously monitored and validated
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div>
                  <h4 className="text-sm font-medium mb-2">Global Settings</h4>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Enforce Multi-Factor Authentication</span>
                      <div className="relative inline-block w-10 mr-2 align-middle select-none">
                        <input type="checkbox" name="toggle1" id="toggle1" className="toggle-checkbox absolute block w-6 h-6 rounded-full bg-white border-4 border-gray-300 appearance-none cursor-pointer" defaultChecked />
                        <label htmlFor="toggle1" className="toggle-label block overflow-hidden h-6 rounded-full bg-gray-300 cursor-pointer"></label>
                      </div>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Continuous Access Evaluation</span>
                      <div className="relative inline-block w-10 mr-2 align-middle select-none">
                        <input type="checkbox" name="toggle2" id="toggle2" className="toggle-checkbox absolute block w-6 h-6 rounded-full bg-white border-4 border-gray-300 appearance-none cursor-pointer" defaultChecked />
                        <label htmlFor="toggle2" className="toggle-label block overflow-hidden h-6 rounded-full bg-gray-300 cursor-pointer"></label>
                      </div>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <span className="text-sm">End-to-End Encryption</span>
                      <div className="relative inline-block w-10 mr-2 align-middle select-none">
                        <input type="checkbox" name="toggle3" id="toggle3" className="toggle-checkbox absolute block w-6 h-6 rounded-full bg-white border-4 border-gray-300 appearance-none cursor-pointer" defaultChecked />
                        <label htmlFor="toggle3" className="toggle-label block overflow-hidden h-6 rounded-full bg-gray-300 cursor-pointer"></label>
                      </div>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Micro-Segmentation</span>
                      <div className="relative inline-block w-10 mr-2 align-middle select-none">
                        <input type="checkbox" name="toggle4" id="toggle4" className="toggle-checkbox absolute block w-6 h-6 rounded-full bg-white border-4 border-gray-300 appearance-none cursor-pointer" defaultChecked />
                        <label htmlFor="toggle4" className="toggle-label block overflow-hidden h-6 rounded-full bg-gray-300 cursor-pointer"></label>
                      </div>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Just-In-Time Access</span>
                      <div className="relative inline-block w-10 mr-2 align-middle select-none">
                        <input type="checkbox" name="toggle5" id="toggle5" className="toggle-checkbox absolute block w-6 h-6 rounded-full bg-white border-4 border-gray-300 appearance-none cursor-pointer" defaultChecked />
                        <label htmlFor="toggle5" className="toggle-label block overflow-hidden h-6 rounded-full bg-gray-300 cursor-pointer"></label>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
  
  const ComplianceMonitoring = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold">Compliance Monitoring</h2>
        <div className="flex items-center space-x-3">
          <button className="px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 flex items-center space-x-2">
            <Download className="w-4 h-4" />
            <span>Export Report</span>
          </button>
          <button className="px-3 py-2 text-sm bg-blue-500 text-white rounded-lg hover:bg-blue-600 flex items-center space-x-2">
            <RefreshCw className="w-4 h-4" />
            <span>Run Assessment</span>
          </button>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {securityMetrics.complianceFrameworks.map(framework => (
          <div key={framework.id} className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
            <div className="flex items-center justify-between mb-2">
              <h3 className="font-medium text-sm">{framework.name}</h3>
              <div className={`px-2 py-1 rounded-full text-xs ${
                framework.status === 'compliant' ? 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-300' :
                framework.status === 'in_progress' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-300' :
                'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-300'
              }`}>
                {framework.status === 'compliant' ? 'Compliant' : 
                 framework.status === 'in_progress' ? 'In Progress' : 'Non-Compliant'}
              </div>
            </div>
            <p className="text-2xl font-bold mb-1">{framework.score}%</p>
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1.5 mb-3">
              <div className={`h-1.5 rounded-full ${
                framework.score >= 90 ? 'bg-green-500' : 
                framework.score >= 80 ? 'bg-yellow-500' : 
                'bg-red-500'
              }`} style={{width: `${framework.score}%`}}></div>
            </div>
            <div className="flex justify-between text-xs text-gray-500">
              <span>Last audit: {framework.lastAudit}</span>
              <span>Next: {framework.nextAudit}</span>
            </div>
          </div>
        ))}
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="p-4 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold">GDPR Compliance</h3>
              <div className="px-2 py-1 rounded-full text-xs bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-300">
                Compliant
              </div>
            </div>
          </div>
          <div className="p-4">
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Data Protection</span>
                  <span className="font-medium">100%</span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div className="h-2 rounded-full bg-green-500" style={{width: '100%'}}></div>
                </div>
              </div>
              
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Consent Management</span>
                  <span className="font-medium">100%</span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div className="h-2 rounded-full bg-green-500" style={{width: '100%'}}></div>
                </div>
              </div>
              
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Data Subject Rights</span>
                  <span className="font-medium">95%</span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div className="h-2 rounded-full bg-green-500" style={{width: '95%'}}></div>
                </div>
              </div>
              
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Records of Processing</span>
                  <span className="font-medium">90%</span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div className="h-2 rounded-full bg-green-500" style={{width: '90%'}}></div>
                </div>
              </div>
              
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Data Breach Notification</span>
                  <span className="font-medium">100%</span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div className="h-2 rounded-full bg-green-500" style={{width: '100%'}}></div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="p-4 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold">HIPAA Compliance</h3>
              <div className="px-2 py-1 rounded-full text-xs bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-300">
                Compliant
              </div>
            </div>
          </div>
          <div className="p-4">
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Privacy Rule</span>
                  <span className="font-medium">100%</span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div className="h-2 rounded-full bg-green-500" style={{width: '100%'}}></div>
                </div>
              </div>
              
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Security Rule</span>
                  <span className="font-medium">98%</span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div className="h-2 rounded-full bg-green-500" style={{width: '98%'}}></div>
                </div>
              </div>
              
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Breach Notification</span>
                  <span className="font-medium">100%</span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div className="h-2 rounded-full bg-green-500" style={{width: '100%'}}></div>
                </div>
              </div>
              
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Enforcement Rule</span>
                  <span className="font-medium">95%</span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div className="h-2 rounded-full bg-green-500" style={{width: '95%'}}></div>
                </div>
              </div>
              
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Business Associate Agreements</span>
                  <span className="font-medium">100%</span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div className="h-2 rounded-full bg-green-500" style={{width: '100%'}}></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="p-4 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold">SOC2 Type II Compliance</h3>
              <div className="px-2 py-1 rounded-full text-xs bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-300">
                Compliant
              </div>
            </div>
          </div>
          <div className="p-4">
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Security</span>
                  <span className="font-medium">95%</span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div className="h-2 rounded-full bg-green-500" style={{width: '95%'}}></div>
                </div>
              </div>
              
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Availability</span>
                  <span className="font-medium">98%</span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div className="h-2 rounded-full bg-green-500" style={{width: '98%'}}></div>
                </div>
              </div>
              
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Processing Integrity</span>
                  <span className="font-medium">92%</span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div className="h-2 rounded-full bg-green-500" style={{width: '92%'}}></div>
                </div>
              </div>
              
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Confidentiality</span>
                  <span className="font-medium">94%</span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div className="h-2 rounded-full bg-green-500" style={{width: '94%'}}></div>
                </div>
              </div>
              
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Privacy</span>
                  <span className="font-medium">90%</span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div className="h-2 rounded-full bg-green-500" style={{width: '90%'}}></div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="p-4 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold">PCI DSS Compliance</h3>
              <div className="px-2 py-1 rounded-full text-xs bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-300">
                In Progress
              </div>
            </div>
          </div>
          <div className="p-4">
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Secure Network</span>
                  <span className="font-medium">90%</span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div className="h-2 rounded-full bg-green-500" style={{width: '90%'}}></div>
                </div>
              </div>
              
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Cardholder Data Protection</span>
                  <span className="font-medium">95%</span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div className="h-2 rounded-full bg-green-500" style={{width: '95%'}}></div>
                </div>
              </div>
              
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Vulnerability Management</span>
                  <span className="font-medium">85%</span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div className="h-2 rounded-full bg-yellow-500" style={{width: '85%'}}></div>
                </div>
              </div>
              
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Access Control</span>
                  <span className="font-medium">88%</span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div className="h-2 rounded-full bg-yellow-500" style={{width: '88%'}}></div>
                </div>
              </div>
              
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Security Testing</span>
                  <span className="font-medium">80%</span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div className="h-2 rounded-full bg-yellow-500" style={{width: '80%'}}></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
  
  const AuditLogging = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold">Audit Logging</h2>
        <div className="flex items-center space-x-3">
          <div className="relative">
            <input 
              type="text" 
              placeholder="Search logs..."
              className="px-3 py-2 pr-8 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <Search className="w-4 h-4 absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
          </div>
          
          <div className="relative">
            <button className="flex items-center space-x-2 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg px-3 py-2 text-sm">
              <Filter className="w-4 h-4" />
              <span>Filters</span>
              <ChevronDown className="w-4 h-4" />
            </button>
          </div>
          
          <button className="px-3 py-2 text-sm bg-blue-500 text-white rounded-lg hover:bg-blue-600 flex items-center space-x-2">
            <Download className="w-4 h-4" />
            <span>Export Logs</span>
          </button>
        </div>
      </div>
      
      <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold">Security Audit Logs</h3>
            <div className="flex items-center space-x-2">
              <span className="text-xs text-gray-500">Showing last 24 hours</span>
              <button className="text-xs text-blue-600 dark:text-blue-400 hover:underline">
                Change
              </button>
            </div>
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 dark:bg-gray-800 text-xs text-gray-700 dark:text-gray-300">
              <tr>
                <th className="px-4 py-2 text-left">Timestamp</th>
                <th className="px-4 py-2 text-left">Action</th>
                <th className="px-4 py-2 text-left">User</th>
                <th className="px-4 py-2 text-left">Status</th>
                <th className="px-4 py-2 text-left">Details</th>
                <th className="px-4 py-2 text-left">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
              {securityMetrics.auditLogs.map(log => (
                <tr key={log.id} className="text-sm">
                  <td className="px-4 py-3 text-gray-500">{log.timestamp}</td>
                  <td className="px-4 py-3">{log.action}</td>
                  <td className="px-4 py-3">{log.user}</td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-1 rounded-full text-xs ${
                      log.status === 'success' ? 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-300' :
                      'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-300'
                    }`}>
                      {log.status.charAt(0).toUpperCase() + log.status.slice(1)}
                    </span>
                  </td>
                  <td className="px-4 py-3">{log.details}</td>
                  <td className="px-4 py-3">
                    <button className="text-xs text-blue-600 dark:text-blue-400 hover:underline">
                      View Details
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="p-4 border-t border-gray-200 dark:border-gray-700 flex items-center justify-between">
          <div className="text-xs text-gray-500">
            Showing 5 of 1,247 logs
          </div>
          <div className="flex items-center space-x-2">
            <button className="px-3 py-1 text-xs border border-gray-300 dark:border-gray-600 rounded hover:bg-gray-50 dark:hover:bg-gray-800">
              Previous
            </button>
            <button className="px-3 py-1 text-xs bg-blue-500 text-white rounded hover:bg-blue-600">
              1
            </button>
            <button className="px-3 py-1 text-xs border border-gray-300 dark:border-gray-600 rounded hover:bg-gray-50 dark:hover:bg-gray-800">
              2
            </button>
            <button className="px-3 py-1 text-xs border border-gray-300 dark:border-gray-600 rounded hover:bg-gray-50 dark:hover:bg-gray-800">
              3
            </button>
            <button className="px-3 py-1 text-xs border border-gray-300 dark:border-gray-600 rounded hover:bg-gray-50 dark:hover:bg-gray-800">
              Next
            </button>
          </div>
        </div>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="p-4 border-b border-gray-200 dark:border-gray-700">
            <h3 className="font-semibold">Log Retention Policy</h3>
          </div>
          <div className="p-4">
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Security Logs Retention</label>
                <select className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800">
                  <option>90 days</option>
                  <option>180 days</option>
                  <option>1 year</option>
                  <option>2 years</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1">Compliance Logs Retention</label>
                <select className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800">
                  <option>1 year</option>
                  <option>2 years</option>
                  <option>3 years</option>
                  <option>5 years</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1">Access Logs Retention</label>
                <select className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800">
                  <option>90 days</option>
                  <option>180 days</option>
                  <option>1 year</option>
                  <option>2 years</option>
                </select>
              </div>
              
              <div className="flex items-center space-x-2 pt-2">
                <input type="checkbox" id="encrypt" className="rounded border-gray-300 text-blue-600 focus:ring-blue-500" defaultChecked />
                <label htmlFor="encrypt" className="text-sm">Encrypt all audit logs</label>
              </div>
              
              <div className="flex items-center space-x-2">
                <input type="checkbox" id="immutable" className="rounded border-gray-300 text-blue-600 focus:ring-blue-500" defaultChecked />
                <label htmlFor="immutable" className="text-sm">Enable immutable logs</label>
              </div>
            </div>
          </div>
        </div>
        
        <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="p-4 border-b border-gray-200 dark:border-gray-700">
            <h3 className="font-semibold">Log Monitoring Configuration</h3>
          </div>
          <div className="p-4">
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Alert Threshold</label>
                <select className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800">
                  <option>High Severity Only</option>
                  <option>Medium and High Severity</option>
                  <option>All Severity Levels</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1">Notification Method</label>
                <select className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800">
                  <option>Email + Dashboard</option>
                  <option>Email Only</option>
                  <option>Dashboard Only</option>
                  <option>SMS + Email + Dashboard</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1">Notification Recipients</label>
                <input 
                  type="text" 
                  placeholder="security@example.com, admin@example.com"
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800"
                />
              </div>
              
              <div className="flex items-center space-x-2 pt-2">
                <input type="checkbox" id="realtime" className="rounded border-gray-300 text-blue-600 focus:ring-blue-500" defaultChecked />
                <label htmlFor="realtime" className="text-sm">Enable real-time monitoring</label>
              </div>
              
              <div className="flex items-center space-x-2">
                <input type="checkbox" id="anomaly" className="rounded border-gray-300 text-blue-600 focus:ring-blue-500" defaultChecked />
                <label htmlFor="anomaly" className="text-sm">Enable anomaly detection</label>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
  
  // Modal for security policy configuration
  const SecurityPolicyModal = () => (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-900 rounded-lg w-full max-w-2xl p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">{selectedPolicy.name}</h3>
          <button 
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            onClick={() => setShowPolicyModal(false)}
          >
            <XCircle className="w-5 h-5" />
          </button>
        </div>
        
        <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
          {selectedPolicy.description}
        </p>
        
        <div className="space-y-4 mb-6">
          <div>
            <label className="block text-sm font-medium mb-1">Policy Status</label>
            <select className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800">
              <option value="enabled">Enabled</option>
              <option value="disabled">Disabled</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">Enforcement Level</label>
            <select className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800">
              <option value="strict">Strict (Block)</option>
              <option value="moderate">Moderate (Alert)</option>
              <option value="permissive">Permissive (Log Only)</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">Scope</label>
            <select className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800">
              <option value="global">Global (All Regions)</option>
              <option value="selected">Selected Regions</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">Exception Handling</label>
            <select className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800">
              <option value="none">No Exceptions</option>
              <option value="approval">Require Approval</option>
              <option value="auto">Automatic for Trusted Sources</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">Notification Settings</label>
            <select className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800">
              <option value="all">All Events</option>
              <option value="violations">Violations Only</option>
              <option value="critical">Critical Events Only</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">Advanced Configuration</label>
            <textarea 
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 h-32"
              placeholder="Enter JSON configuration..."
              defaultValue={`{
  "policy_version": "1.2.0",
  "update_frequency": "daily",
  "compliance_frameworks": ["GDPR", "HIPAA", "SOC2"],
  "exceptions": [],
  "audit_level": "comprehensive"
}`}
            ></textarea>
          </div>
        </div>
        
        <div className="flex items-center justify-end space-x-3">
          <button 
            className="px-4 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800"
            onClick={() => setShowPolicyModal(false)}
          >
            Cancel
          </button>
          <button 
            className="px-4 py-2 text-sm bg-blue-500 text-white rounded-lg hover:bg-blue-600"
            onClick={() => setShowPolicyModal(false)}
          >
            Save Policy
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <div className="h-full">
      <div className="flex border-b border-gray-200 dark:border-gray-700 mb-6">
        <button 
          className={`px-4 py-2 font-medium text-sm ${activeTab === 'dashboard' ? 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-500' : 'text-gray-600 dark:text-gray-400'}`}
          onClick={() => setActiveTab('dashboard')}
        >
          Dashboard
        </button>
        <button 
          className={`px-4 py-2 font-medium text-sm ${activeTab === 'zero-trust' ? 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-500' : 'text-gray-600 dark:text-gray-400'}`}
          onClick={() => setActiveTab('zero-trust')}
        >
          Zero-Trust
        </button>
        <button 
          className={`px-4 py-2 font-medium text-sm ${activeTab === 'compliance' ? 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-500' : 'text-gray-600 dark:text-gray-400'}`}
          onClick={() => setActiveTab('compliance')}
        >
          Compliance
        </button>
        <button 
          className={`px-4 py-2 font-medium text-sm ${activeTab === 'audit' ? 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-500' : 'text-gray-600 dark:text-gray-400'}`}
          onClick={() => setActiveTab('audit')}
        >
          Audit Logs
        </button>
      </div>
      
      {activeTab === 'dashboard' && <SecurityDashboard />}
      {activeTab === 'zero-trust' && <ZeroTrustConfiguration />}
      {activeTab === 'compliance' && <ComplianceMonitoring />}
      {activeTab === 'audit' && <AuditLogging />}
      
      {showPolicyModal && selectedPolicy && <SecurityPolicyModal />}
    </div>
  );
};

export default EnterpriseSecurityFeatures;
