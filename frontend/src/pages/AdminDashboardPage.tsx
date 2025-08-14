import React, { useState } from 'react';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '../ui/Tabs';
import SystemHealthDashboard from '../dashboard/SystemHealthDashboard';
import ApiKeyManagement from '../dashboard/ApiKeyManagement';
import RealTimeMonitoring from '../dashboard/RealTimeMonitoring';
import BillingSubscriptionsTab from '../dashboard/BillingSubscriptionsTab';
import CreditManagement from '../dashboard/CreditManagement';
import CreditApiIntegration from '../dashboard/CreditApiIntegration';
import SecurityMonitoringInterface from '../security/SecurityMonitoringInterface';
import { Shield, AlertTriangle, FileText, DollarSign, CreditCard, Brain, Lock } from 'lucide-react';

interface ComplianceItem {
  id: string;
  standard: string;
  icon: string;
  description: string;
  status: 'Compliant' | 'Non-Compliant' | 'Pending';
  lastAudit: string;
  nextAudit: string;
}

const AdminDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState('overview');
  
  // Sample data - would be fetched from API in production
  const [complianceItems, setComplianceItems] = useState<ComplianceItem[]>([
    {
      id: '1',
      standard: 'SOC2 Type II',
      icon: 'shield',
      description: 'Security & Availability',
      status: 'Compliant',
      lastAudit: 'March 15, 2025',
      nextAudit: 'March 15, 2026'
    },
    {
      id: '2',
      standard: 'HIPAA',
      icon: 'health',
      description: 'Health Information Privacy',
      status: 'Compliant',
      lastAudit: 'April 10, 2025',
      nextAudit: 'April 10, 2026'
    },
    {
      id: '3',
      standard: 'GDPR',
      icon: 'lock',
      description: 'Data Protection',
      status: 'Compliant',
      lastAudit: 'May 25, 2025',
      nextAudit: 'May 25, 2026'
    }
  ]);

  const getComplianceIcon = (icon: string) => {
    switch (icon) {
      case 'shield':
        return <div className="flex-shrink-0 h-10 w-10 flex items-center justify-center bg-blue-100 rounded-full">
          <Shield className="h-5 w-5 text-blue-600" />
        </div>;
      case 'health':
        return <div className="flex-shrink-0 h-10 w-10 flex items-center justify-center bg-red-100 rounded-full">
          <i className="fas fa-heartbeat text-red-600"></i>
        </div>;
      case 'lock':
        return <div className="flex-shrink-0 h-10 w-10 flex items-center justify-center bg-green-100 rounded-full">
          <i className="fas fa-lock text-green-600"></i>
        </div>;
      default:
        return <div className="flex-shrink-0 h-10 w-10 flex items-center justify-center bg-gray-100 rounded-full">
          <Shield className="h-5 w-5 text-gray-600" />
        </div>;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'Compliant':
        return <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
          Compliant
        </span>;
      case 'Non-Compliant':
        return <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800">
          Non-Compliant
        </span>;
      case 'Pending':
        return <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-yellow-100 text-yellow-800">
          Pending
        </span>;
      default:
        return <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-gray-100 text-gray-800">
          Unknown
        </span>;
    }
  };

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <header className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Admin Dashboard</h1>
        <p className="text-gray-600">Manage your Aideon AI Lite system</p>
      </header>

      <Tabs defaultValue="overview" onValueChange={setActiveTab} className="w-full">
        <TabsList className="mb-6 border-b border-gray-200 w-full">
          <TabsTrigger value="overview" className={`py-4 px-1 border-b-2 font-medium text-sm ${activeTab === 'overview' ? 'border-indigo-500 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}`}>
            System Overview
          </TabsTrigger>
          <TabsTrigger value="security" className={`py-4 px-1 border-b-2 font-medium text-sm ${activeTab === 'security' ? 'border-indigo-500 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}`}>
            Security & Ethics
          </TabsTrigger>
          <TabsTrigger value="agents" className={`py-4 px-1 border-b-2 font-medium text-sm ${activeTab === 'agents' ? 'border-indigo-500 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}`}>
            Agent Management
          </TabsTrigger>
          <TabsTrigger value="billing" className={`py-4 px-1 border-b-2 font-medium text-sm ${activeTab === 'billing' ? 'border-indigo-500 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}`}>
            Billing & Subscriptions
          </TabsTrigger>
          <TabsTrigger value="credits" className={`py-4 px-1 border-b-2 font-medium text-sm ${activeTab === 'credits' ? 'border-indigo-500 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}`}>
            Credit Management
          </TabsTrigger>
          <TabsTrigger value="api-keys" className={`py-4 px-1 border-b-2 font-medium text-sm ${activeTab === 'api-keys' ? 'border-indigo-500 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}`}>
            API Key Management
          </TabsTrigger>
          <TabsTrigger value="monitoring" className={`py-4 px-1 border-b-2 font-medium text-sm ${activeTab === 'monitoring' ? 'border-indigo-500 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}`}>
            Monitoring
          </TabsTrigger>
          <TabsTrigger value="compliance" className={`py-4 px-1 border-b-2 font-medium text-sm ${activeTab === 'compliance' ? 'border-indigo-500 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}`}>
            Compliance
          </TabsTrigger>
          <TabsTrigger value="logs" className={`py-4 px-1 border-b-2 font-medium text-sm ${activeTab === 'logs' ? 'border-indigo-500 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}`}>
            Logs
          </TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          <SystemHealthDashboard />
          <RealTimeMonitoring />
        </TabsContent>

        <TabsContent value="security">
          <SecurityMonitoringInterface />
        </TabsContent>

        <TabsContent value="agents">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold mb-4 flex items-center">
              <Brain className="mr-2" size={20} />
              Agent Management & Prompt Engineering
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {['Planner', 'Execution', 'Verification', 'Security', 'Optimization', 'Learning'].map((agent) => (
                <div key={agent} className="border border-gray-200 rounded-lg p-4">
                  <h3 className="font-medium mb-2">{agent} Agent</h3>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span>Status:</span>
                      <span className="text-green-600">✅ Active</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Prompt Quality:</span>
                      <span className="text-blue-600">90%+</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Security:</span>
                      <span className="text-green-600">✅ Secured</span>
                    </div>
                  </div>
                  <button className="mt-3 w-full px-3 py-1 bg-indigo-50 text-indigo-600 rounded text-sm hover:bg-indigo-100">
                    Configure
                  </button>
                </div>
              ))}
            </div>
          </div>
        </TabsContent>

        <TabsContent value="billing">
          <BillingSubscriptionsTab />
        </TabsContent>

        <TabsContent value="credits">
          <div className="space-y-6">
            <CreditManagement />
            <CreditApiIntegration />
          </div>
        </TabsContent>

        <TabsContent value="api-keys">
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-lg font-semibold mb-4">API Key Management</h2>
            <p className="mb-4 text-gray-600">
              Manage your API keys for various AI providers. You can add, rotate, or revoke keys as needed.
            </p>
            <div className="flex space-x-4">
              <button className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700">
                Add New Key
              </button>
              <button className="px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50">
                View API Usage
              </button>
            </div>
          </div>
          <ApiKeyManagement />
        </TabsContent>

        <TabsContent value="monitoring">
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-lg font-semibold mb-4">System Monitoring</h2>
            <p className="mb-4 text-gray-600">
              Monitor your system's performance in real-time. Track response times, error rates, and resource usage.
            </p>
            <div className="flex space-x-4">
              <button className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700">
                Export Metrics
              </button>
              <button className="px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50">
                Configure Alerts
              </button>
            </div>
          </div>
          <RealTimeMonitoring />
          <div className="bg-white rounded-lg shadow p-6 mt-6">
            <h2 className="text-lg font-semibold mb-4">Resource Usage</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 border border-gray-200 rounded-lg">
                <div className="flex justify-between items-center mb-2">
                  <h3 className="font-medium">API Calls</h3>
                  <div className="text-sm">
                    <span className="font-medium">1,245</span>
                    <span className="text-gray-500"> / 5,000</span>
                  </div>
                </div>
                <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-indigo-600 rounded-full" 
                    style={{ width: '25%' }}
                  ></div>
                </div>
              </div>
              <div className="p-4 border border-gray-200 rounded-lg">
                <div className="flex justify-between items-center mb-2">
                  <h3 className="font-medium">Storage</h3>
                  <div className="text-sm">
                    <span className="font-medium">2.4 GB</span>
                    <span className="text-gray-500"> / 10 GB</span>
                  </div>
                </div>
                <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-indigo-600 rounded-full" 
                    style={{ width: '24%' }}
                  ></div>
                </div>
              </div>
              <div className="p-4 border border-gray-200 rounded-lg">
                <div className="flex justify-between items-center mb-2">
                  <h3 className="font-medium">Processing Time</h3>
                  <div className="text-sm">
                    <span className="font-medium">45 min</span>
                    <span className="text-gray-500"> / 180 min</span>
                  </div>
                </div>
                <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-indigo-600 rounded-full" 
                    style={{ width: '25%' }}
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </TabsContent>

        <TabsContent value="compliance">
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-lg font-semibold mb-4">Compliance Status</h2>
            <div className="flex items-center space-x-2 mb-4">
              <div className="flex items-center bg-green-100 text-green-800 px-3 py-1 rounded-full">
                <Shield className="h-4 w-4 mr-1" />
                <span className="text-sm font-medium">All Standards Compliant</span>
              </div>
              <div className="text-sm text-gray-500">Last verified: June 1, 2025</div>
            </div>
            <p className="mb-4 text-gray-600">
              Aideon AI Lite maintains compliance with all required standards. Regular audits ensure continued compliance.
            </p>
            <div className="flex space-x-4">
              <button className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700">
                Download Certificates
              </button>
              <button className="px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50">
                Schedule Audit
              </button>
            </div>
          </div>
          
          <div className="bg-white shadow overflow-hidden rounded-lg">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Standard
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Last Audit
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Next Audit
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {complianceItems.map((item) => (
                  <tr key={item.id}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        {getComplianceIcon(item.icon)}
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900">{item.standard}</div>
                          <div className="text-sm text-gray-500">{item.description}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {getStatusBadge(item.status)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {item.lastAudit}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {item.nextAudit}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <button className="text-indigo-600 hover:text-indigo-900">View Report</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </TabsContent>

        <TabsContent value="logs">
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold">System Logs</h2>
              <div className="flex space-x-2">
                <select className="border border-gray-300 rounded-md px-3 py-1 text-sm">
                  <option>All Levels</option>
                  <option>Error</option>
                  <option>Warning</option>
                  <option>Info</option>
                  <option>Debug</option>
                </select>
                <button className="px-3 py-1 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 text-sm">
                  Export
                </button>
              </div>
            </div>
            
            <div className="space-y-2">
              <div className="p-3 bg-red-50 border border-red-200 rounded-md flex items-start">
                <div className="flex-shrink-0 mt-0.5">
                  <AlertTriangle className="h-5 w-5 text-red-500" />
                </div>
                <div className="ml-3">
                  <div className="flex items-center">
                    <span className="font-medium text-red-800">Error</span>
                    <span className="ml-2 text-xs text-gray-500">2025-06-08 14:32:15</span>
                  </div>
                  <p className="text-sm text-red-700">
                    Failed to connect to Anthropic API: Authentication error (API key expired)
                  </p>
                </div>
              </div>
              
              <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-md flex items-start">
                <div className="flex-shrink-0 mt-0.5">
                  <AlertTriangle className="h-5 w-5 text-yellow-500" />
                </div>
                <div className="ml-3">
                  <div className="flex items-center">
                    <span className="font-medium text-yellow-800">Warning</span>
                    <span className="ml-2 text-xs text-gray-500">2025-06-08 14:30:22</span>
                  </div>
                  <p className="text-sm text-yellow-700">
                    API rate limit approaching: 80% of quota used for OpenAI
                  </p>
                </div>
              </div>
              
              <div className="p-3 bg-blue-50 border border-blue-200 rounded-md flex items-start">
                <div className="flex-shrink-0 mt-0.5">
                  <FileText className="h-5 w-5 text-blue-500" />
                </div>
                <div className="ml-3">
                  <div className="flex items-center">
                    <span className="font-medium text-blue-800">Info</span>
                    <span className="ml-2 text-xs text-gray-500">2025-06-08 14:28:05</span>
                  </div>
                  <p className="text-sm text-blue-700">
                    System update available: v2.3.2 (security patches and performance improvements)
                  </p>
                </div>
              </div>
              
              <div className="p-3 bg-gray-50 border border-gray-200 rounded-md flex items-start">
                <div className="flex-shrink-0 mt-0.5">
                  <FileText className="h-5 w-5 text-gray-500" />
                </div>
                <div className="ml-3">
                  <div className="flex items-center">
                    <span className="font-medium text-gray-800">Info</span>
                    <span className="ml-2 text-xs text-gray-500">2025-06-08 14:15:32</span>
                  </div>
                  <p className="text-sm text-gray-700">
                    User admin@aideon.ai logged in successfully
                  </p>
                </div>
              </div>
            </div>
            
            <div className="mt-4 flex justify-between items-center">
              <button className="text-sm text-indigo-600 hover:text-indigo-800">
                Load more logs
              </button>
              <div className="text-sm text-gray-500">
                Showing 4 of 1,245 logs
              </div>
            </div>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AdminDashboard;
