import React, { useState } from 'react';

/**
 * Dr. TARDIS Diagnostics Component
 * 
 * This component implements the diagnostic interface for Dr. TARDIS,
 * providing system monitoring, troubleshooting, and explanation features.
 */
const DrTardisDiagnostics = () => {
  // State for system health
  const [systemHealth, setSystemHealth] = useState({
    cpu: 32,
    memory: 45,
    disk: 28,
    network: 15,
    uptime: '99.997%',
    responseTime: '1.2s',
    errorRate: '0.03%'
  });
  
  // State for LLM performance
  const [llmPerformance, setLlmPerformance] = useState([
    {
      id: 'gpt4',
      name: 'GPT-4',
      responseTime: '1.8s',
      successRate: '99.2%',
      tokenUsage: '12.5M/20M',
      status: 'operational'
    },
    {
      id: 'gemini',
      name: 'Gemini Pro',
      responseTime: '1.4s',
      successRate: '98.7%',
      tokenUsage: '8.2M/15M',
      status: 'operational'
    },
    {
      id: 'claude',
      name: 'Claude 3',
      responseTime: '1.6s',
      successRate: '99.5%',
      tokenUsage: '10.1M/20M',
      status: 'operational'
    }
  ]);
  
  // State for diagnostic steps
  const [diagnosticSteps, setDiagnosticSteps] = useState([
    { id: 1, name: 'System Check', status: 'completed', result: 'All systems operational' },
    { id: 2, name: 'Network Connectivity', status: 'completed', result: 'Connected (25ms latency)' },
    { id: 3, name: 'API Integration', status: 'completed', result: 'All APIs responding normally' },
    { id: 4, name: 'Model Availability', status: 'in-progress', result: 'Checking model endpoints...' },
    { id: 5, name: 'Storage Verification', status: 'pending', result: '' },
    { id: 6, name: 'Security Audit', status: 'pending', result: '' }
  ]);
  
  // State for active tab
  const [activeTab, setActiveTab] = useState('diagnostics');
  
  // State for recent activities
  const [recentActivities, setRecentActivities] = useState([
    { id: 1, type: 'system', message: 'System update completed successfully', timestamp: '10 minutes ago' },
    { id: 2, type: 'model', message: 'GPT-4 model updated to latest version', timestamp: '1 hour ago' },
    { id: 3, type: 'user', message: 'User John Doe completed Q2 Sales Analysis project', timestamp: '2 hours ago' },
    { id: 4, type: 'error', message: 'Temporary network latency detected and resolved', timestamp: '3 hours ago' },
    { id: 5, type: 'system', message: 'Daily backup completed successfully', timestamp: '12 hours ago' }
  ]);
  
  // Get status color
  const getStatusColor = (status) => {
    switch (status) {
      case 'operational':
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'in-progress':
        return 'bg-blue-100 text-blue-800';
      case 'pending':
        return 'bg-gray-100 text-gray-800';
      case 'warning':
        return 'bg-yellow-100 text-yellow-800';
      case 'error':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };
  
  // Get activity icon
  const getActivityIcon = (type) => {
    switch (type) {
      case 'system':
        return 'fa-server';
      case 'model':
        return 'fa-brain';
      case 'user':
        return 'fa-user';
      case 'error':
        return 'fa-exclamation-triangle';
      default:
        return 'fa-info-circle';
    }
  };
  
  // Handle tab change
  const handleTabChange = (tab) => {
    setActiveTab(tab);
  };
  
  // Handle diagnostic step action
  const handleStepAction = (stepId) => {
    // Simulate step progression
    const updatedSteps = diagnosticSteps.map(step => {
      if (step.id === stepId && step.status === 'in-progress') {
        return { ...step, status: 'completed', result: 'All models available and responding' };
      } else if (step.id === stepId + 1 && step.status === 'pending') {
        return { ...step, status: 'in-progress', result: 'Checking storage integrity...' };
      }
      return step;
    });
    
    setDiagnosticSteps(updatedSteps);
  };
  
  return (
    <div className="h-full">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Dr. TARDIS</h2>
        <p className="text-gray-500">System diagnostics, monitoring, and troubleshooting</p>
      </div>
      
      {/* Tab navigation */}
      <div className="mb-6 border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => handleTabChange('diagnostics')}
            className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'diagnostics'
                ? 'border-indigo-500 text-indigo-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Diagnostics
          </button>
          <button
            onClick={() => handleTabChange('monitoring')}
            className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'monitoring'
                ? 'border-indigo-500 text-indigo-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            System Monitoring
          </button>
          <button
            onClick={() => handleTabChange('llm')}
            className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'llm'
                ? 'border-indigo-500 text-indigo-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            LLM Performance
          </button>
          <button
            onClick={() => handleTabChange('activity')}
            className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'activity'
                ? 'border-indigo-500 text-indigo-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Activity Log
          </button>
        </nav>
      </div>
      
      {/* Tab content */}
      <div className="bg-white rounded-lg shadow-sm overflow-hidden">
        {activeTab === 'diagnostics' && (
          <div className="p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">System Diagnostic Steps</h3>
            <div className="space-y-4">
              {diagnosticSteps.map((step) => (
                <div key={step.id} className="bg-gray-50 p-4 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center">
                      <div className={`h-8 w-8 rounded-full flex items-center justify-center ${
                        step.status === 'completed' 
                          ? 'bg-green-100' 
                          : step.status === 'in-progress' 
                            ? 'bg-blue-100' 
                            : 'bg-gray-100'
                      }`}>
                        {step.status === 'completed' ? (
                          <i className="fas fa-check text-green-600"></i>
                        ) : step.status === 'in-progress' ? (
                          <i className="fas fa-spinner fa-spin text-blue-600"></i>
                        ) : (
                          <i className="fas fa-clock text-gray-600"></i>
                        )}
                      </div>
                      <div className="ml-3">
                        <p className="text-sm font-medium text-gray-900">{step.name}</p>
                        <p className="text-xs text-gray-500">
                          {step.status.charAt(0).toUpperCase() + step.status.slice(1)}
                        </p>
                      </div>
                    </div>
                    <div>
                      {step.status === 'in-progress' && (
                        <button
                          onClick={() => handleStepAction(step.id)}
                          className="px-3 py-1 bg-indigo-100 text-indigo-700 rounded-md text-sm hover:bg-indigo-200"
                        >
                          Check Status
                        </button>
                      )}
                    </div>
                  </div>
                  {step.result && (
                    <div className="ml-11 text-sm text-gray-700">
                      <p>{step.result}</p>
                    </div>
                  )}
                </div>
              ))}
            </div>
            
            <div className="mt-6 flex justify-end">
              <button className="px-4 py-2 bg-indigo-600 text-white rounded-md text-sm hover:bg-indigo-700">
                Run Full Diagnostic
              </button>
            </div>
          </div>
        )}
        
        {activeTab === 'monitoring' && (
          <div className="p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">System Health Monitoring</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-sm text-gray-500 mb-1">CPU Usage</p>
                <div className="flex items-center justify-between">
                  <p className="text-xl font-semibold text-gray-900">{systemHealth.cpu}%</p>
                  <div className="w-16 h-2 bg-gray-200 rounded-full">
                    <div 
                      className="h-2 bg-indigo-600 rounded-full" 
                      style={{ width: `${systemHealth.cpu}%` }}
                    ></div>
                  </div>
                </div>
              </div>
              
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-sm text-gray-500 mb-1">Memory Usage</p>
                <div className="flex items-center justify-between">
                  <p className="text-xl font-semibold text-gray-900">{systemHealth.memory}%</p>
                  <div className="w-16 h-2 bg-gray-200 rounded-full">
                    <div 
                      className="h-2 bg-indigo-600 rounded-full" 
                      style={{ width: `${systemHealth.memory}%` }}
                    ></div>
                  </div>
                </div>
              </div>
              
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-sm text-gray-500 mb-1">Disk Usage</p>
                <div className="flex items-center justify-between">
                  <p className="text-xl font-semibold text-gray-900">{systemHealth.disk}%</p>
                  <div className="w-16 h-2 bg-gray-200 rounded-full">
                    <div 
                      className="h-2 bg-indigo-600 rounded-full" 
                      style={{ width: `${systemHealth.disk}%` }}
                    ></div>
                  </div>
                </div>
              </div>
              
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-sm text-gray-500 mb-1">Network Usage</p>
                <div className="flex items-center justify-between">
                  <p className="text-xl font-semibold text-gray-900">{systemHealth.network}%</p>
                  <div className="w-16 h-2 bg-gray-200 rounded-full">
                    <div 
                      className="h-2 bg-indigo-600 rounded-full" 
                      style={{ width: `${systemHealth.network}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-sm text-gray-500 mb-1">System Uptime</p>
                <div className="flex items-center">
                  <i className="fas fa-check-circle text-green-500 mr-2"></i>
                  <p className="text-xl font-semibold text-gray-900">{systemHealth.uptime}</p>
                </div>
                <p className="text-xs text-gray-500 mt-1">Target: 99.99%</p>
              </div>
              
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-sm text-gray-500 mb-1">Response Time</p>
                <div className="flex items-center">
                  <i className="fas fa-bolt text-yellow-500 mr-2"></i>
                  <p className="text-xl font-semibold text-gray-900">{systemHealth.responseTime}</p>
                </div>
                <p className="text-xs text-gray-500 mt-1">Target: &lt;2s</p>
              </div>
              
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-sm text-gray-500 mb-1">Error Rate</p>
                <div className="flex items-center">
                  <i className="fas fa-exclamation-triangle text-green-500 mr-2"></i>
                  <p className="text-xl font-semibold text-gray-900">{systemHealth.errorRate}</p>
                </div>
                <p className="text-xs text-gray-500 mt-1">Target: &lt;0.1%</p>
              </div>
            </div>
          </div>
        )}
        
        {activeTab === 'llm' && (
          <div className="p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">LLM Performance Monitoring</h3>
            
            <div className="space-y-4">
              {llmPerformance.map((model) => (
                <div key={model.id} className="bg-gray-50 p-4 rounded-lg">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center">
                      <div className="h-10 w-10 rounded-full bg-indigo-100 flex items-center justify-center">
                        <i className="fas fa-brain text-indigo-600"></i>
                      </div>
                      <div className="ml-3">
                        <p className="text-md font-medium text-gray-900">{model.name}</p>
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(model.status)}`}>
                          {model.status.charAt(0).toUpperCase() + model.status.slice(1)}
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 ml-13">
                    <div>
                      <p className="text-xs text-gray-500 mb-1">Response Time</p>
                      <p className="text-sm font-medium text-gray-900">{model.responseTime}</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500 mb-1">Success Rate</p>
                      <p className="text-sm font-medium text-gray-900">{model.successRate}</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500 mb-1">Token Usage</p>
                      <p className="text-sm font-medium text-gray-900">{model.tokenUsage}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
        
        {activeTab === 'activity' && (
          <div className="p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Activity</h3>
            
            <div className="space-y-4">
              {recentActivities.map((activity) => (
                <div key={activity.id} className="flex items-start">
                  <div className={`flex-shrink-0 h-8 w-8 rounded-full flex items-center justify-center ${
                    activity.type === 'error' 
                      ? 'bg-red-100' 
                      : activity.type === 'system' 
                        ? 'bg-blue-100' 
                        : activity.type === 'model' 
                          ? 'bg-purple-100' 
                          : 'bg-green-100'
                  }`}>
                    <i className={`fas ${getActivityIcon(activity.type)} ${
                      activity.type === 'error' 
                        ? 'text-red-600' 
                        : activity.type === 'system' 
                          ? 'text-blue-600' 
                          : activity.type === 'model' 
                            ? 'text-purple-600' 
                            : 'text-green-600'
                    }`}></i>
                  </div>
                  <div className="ml-3">
                    <p className="text-sm text-gray-900">{activity.message}</p>
                    <p className="text-xs text-gray-500">{activity.timestamp}</p>
                  </div>
                </div>
              ))}
            </div>
            
            <div className="mt-6 flex justify-center">
              <button className="px-4 py-2 text-indigo-600 text-sm hover:text-indigo-800">
                View Full Activity Log
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DrTardisDiagnostics;
