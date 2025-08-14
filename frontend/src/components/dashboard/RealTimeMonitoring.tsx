import React, { useState } from 'react';
import { LineChart, BarChart } from 'lucide-react';

interface MonitoringProps {
  className?: string;
}

const RealTimeMonitoring: React.FC<MonitoringProps> = ({ className }) => {
  // Sample data - would be fetched from API in production
  const [monitoringData, setMonitoringData] = useState({
    responseTime: {
      labels: ['1h ago', '45m ago', '30m ago', '15m ago', 'Now'],
      values: [1.8, 1.5, 1.3, 1.4, 1.2],
      target: 2.0 // Target is under 2 seconds
    },
    errorRate: {
      labels: ['1h ago', '45m ago', '30m ago', '15m ago', 'Now'],
      values: [2.1, 1.8, 1.5, 1.2, 0.8],
      target: 1.0 // Target is under 1%
    }
  });

  // This would be replaced with actual chart rendering using Chart.js or similar
  const renderChartPlaceholder = (title: string, icon: React.ReactNode, data: any) => (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="text-md font-medium mb-4 flex items-center">
        {icon}
        <span className="ml-2">{title}</span>
      </h3>
      <div className="h-64 bg-gray-100 rounded-lg flex flex-col items-center justify-center p-4">
        <div className="text-center mb-4">
          <div className="text-5xl text-indigo-300 mb-2">{icon}</div>
          <p className="text-gray-500">{title} Chart</p>
        </div>
        
        {/* Simple data visualization */}
        <div className="w-full mt-4">
          <div className="flex justify-between mb-2">
            <span className="text-sm font-medium">Current: {data.values[data.values.length - 1]}</span>
            <span className="text-sm font-medium">Target: {data.target}</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2.5 mb-4">
            <div 
              className={`h-2.5 rounded-full ${
                title.includes('Response') ? 'bg-blue-600' : 'bg-red-600'
              }`} 
              style={{
                width: `${(data.values[data.values.length - 1] / data.target) * 100}%`,
                maxWidth: '100%'
              }}
            ></div>
          </div>
          
          {/* Simple bar representation of data */}
          <div className="flex items-end justify-between h-20 mt-4">
            {data.values.map((value: number, index: number) => (
              <div key={index} className="flex flex-col items-center">
                <div 
                  className={`w-8 ${
                    title.includes('Response') ? 'bg-blue-500' : 'bg-red-500'
                  } rounded-t`}
                  style={{ 
                    height: `${(value / Math.max(...data.values)) * 100}%`,
                  }}
                ></div>
                <span className="text-xs mt-1">{data.labels[index]}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className={`mb-8 ${className}`}>
      <h2 className="text-lg font-semibold mb-4">Real-time System Monitoring</h2>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {renderChartPlaceholder(
          "Response Time (ms)", 
          <LineChart className="h-5 w-5 text-indigo-600" />, 
          monitoringData.responseTime
        )}
        {renderChartPlaceholder(
          "Error Rate (%)", 
          <BarChart className="h-5 w-5 text-indigo-600" />, 
          monitoringData.errorRate
        )}
      </div>
    </div>
  );
};

export default RealTimeMonitoring;
