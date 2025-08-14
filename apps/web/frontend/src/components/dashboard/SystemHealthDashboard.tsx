import React, { useState } from 'react';
import { Shield, Server, Clock, Plug } from 'lucide-react';

const SystemHealthDashboard = () => {
  // Sample data - would be fetched from API in production
  const [healthMetrics, setHealthMetrics] = useState({
    uptime: {
      percentage: 99.99,
      period: 'Last 30 days'
    },
    responseTime: {
      value: 1.2,
      unit: 's',
      period: 'Last 24 hours'
    },
    integrations: {
      active: 124,
      total: 150
    },
    compliance: {
      status: '3/3',
      details: 'SOC2, HIPAA, GDPR'
    }
  });

  return (
    <div className="mb-8">
      <h2 className="text-lg font-semibold mb-4">System Health</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Uptime Card */}
        <div className="bg-white rounded-lg shadow p-4 border-l-4 border-green-500">
          <div className="flex items-center">
            <div className="flex-shrink-0 bg-green-100 rounded-full p-3">
              <Server className="h-5 w-5 text-green-500" />
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-900">System Uptime</h3>
              <p className="text-2xl font-semibold">{healthMetrics.uptime.percentage}%</p>
              <p className="text-sm text-gray-500">{healthMetrics.uptime.period}</p>
            </div>
          </div>
        </div>

        {/* Response Time Card */}
        <div className="bg-white rounded-lg shadow p-4 border-l-4 border-blue-500">
          <div className="flex items-center">
            <div className="flex-shrink-0 bg-blue-100 rounded-full p-3">
              <Clock className="h-5 w-5 text-blue-500" />
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-900">Avg Response Time</h3>
              <p className="text-2xl font-semibold">{healthMetrics.responseTime.value}{healthMetrics.responseTime.unit}</p>
              <p className="text-sm text-gray-500">{healthMetrics.responseTime.period}</p>
            </div>
          </div>
        </div>

        {/* Integrations Card */}
        <div className="bg-white rounded-lg shadow p-4 border-l-4 border-purple-500">
          <div className="flex items-center">
            <div className="flex-shrink-0 bg-purple-100 rounded-full p-3">
              <Plug className="h-5 w-5 text-purple-500" />
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-900">Active Integrations</h3>
              <p className="text-2xl font-semibold">{healthMetrics.integrations.active}</p>
              <p className="text-sm text-gray-500">Of {healthMetrics.integrations.total} available</p>
            </div>
          </div>
        </div>

        {/* Compliance Card */}
        <div className="bg-white rounded-lg shadow p-4 border-l-4 border-yellow-500">
          <div className="flex items-center">
            <div className="flex-shrink-0 bg-yellow-100 rounded-full p-3">
              <Shield className="h-5 w-5 text-yellow-500" />
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-900">Compliance Status</h3>
              <p className="text-2xl font-semibold">{healthMetrics.compliance.status}</p>
              <p className="text-sm text-gray-500">{healthMetrics.compliance.details}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SystemHealthDashboard;
