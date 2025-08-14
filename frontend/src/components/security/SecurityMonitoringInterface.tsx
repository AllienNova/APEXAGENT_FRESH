import React, { useState, useEffect } from 'react';

const SecurityMonitoringInterface = () => {
  const [securityData, setSecurityData] = useState({
    totalRequests: 0,
    blockedRequests: 0,
    violations: [],
    complianceScore: 100
  });

  const [alerts, setAlerts] = useState([]);

  useEffect(() => {
    // Simulate real-time security monitoring
    const interval = setInterval(() => {
      setSecurityData(prev => ({
        ...prev,
        totalRequests: prev.totalRequests + Math.floor(Math.random() * 5),
        blockedRequests: prev.blockedRequests + (Math.random() > 0.95 ? 1 : 0)
      }));
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  const SecurityMetrics = () => (
    <div className="grid grid-cols-4 gap-4 mb-6">
      <div className="bg-green-50 p-4 rounded-lg">
        <h3 className="text-sm font-medium text-green-800">Total Requests</h3>
        <p className="text-2xl font-bold text-green-900">{securityData.totalRequests}</p>
      </div>
      <div className="bg-red-50 p-4 rounded-lg">
        <h3 className="text-sm font-medium text-red-800">Blocked</h3>
        <p className="text-2xl font-bold text-red-900">{securityData.blockedRequests}</p>
      </div>
      <div className="bg-blue-50 p-4 rounded-lg">
        <h3 className="text-sm font-medium text-blue-800">Block Rate</h3>
        <p className="text-2xl font-bold text-blue-900">
          {securityData.totalRequests > 0 ? 
            ((securityData.blockedRequests / securityData.totalRequests) * 100).toFixed(1) : 0}%
        </p>
      </div>
      <div className="bg-purple-50 p-4 rounded-lg">
        <h3 className="text-sm font-medium text-purple-800">Compliance</h3>
        <p className="text-2xl font-bold text-purple-900">{securityData.complianceScore}%</p>
      </div>
    </div>
  );

  const ViolationLog = () => (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold mb-4">Security Violations</h3>
      <div className="space-y-2">
        {securityData.blockedRequests === 0 ? (
          <p className="text-green-600">✅ No violations detected</p>
        ) : (
          Array.from({length: securityData.blockedRequests}, (_, i) => (
            <div key={i} className="flex items-center justify-between p-3 bg-red-50 rounded">
              <span className="text-sm text-red-800">Proprietary disclosure attempt</span>
              <span className="text-xs text-red-600">HIGH</span>
            </div>
          ))
        )}
      </div>
    </div>
  );

  const SecurityConstraints = () => (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold mb-4">Active Constraints</h3>
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <span>Proprietary Info Protection</span>
          <span className="text-green-600">✅ Active</span>
        </div>
        <div className="flex items-center justify-between">
          <span>Ethical Content Filter</span>
          <span className="text-green-600">✅ Active</span>
        </div>
        <div className="flex items-center justify-between">
          <span>Harmful Request Blocking</span>
          <span className="text-green-600">✅ Active</span>
        </div>
        <div className="flex items-center justify-between">
          <span>Privacy Protection</span>
          <span className="text-green-600">✅ Active</span>
        </div>
      </div>
    </div>
  );

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Security Monitoring</h1>
        <p className="text-gray-600">Real-time security and compliance monitoring</p>
      </div>

      <SecurityMetrics />

      <div className="grid grid-cols-2 gap-6">
        <ViolationLog />
        <SecurityConstraints />
      </div>

      {securityData.blockedRequests > 0 && (
        <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <h4 className="font-medium text-yellow-800">Security Alert</h4>
          <p className="text-yellow-700">
            {securityData.blockedRequests} security violation(s) detected. Review logs for details.
          </p>
        </div>
      )}
    </div>
  );
};

export default SecurityMonitoringInterface;

