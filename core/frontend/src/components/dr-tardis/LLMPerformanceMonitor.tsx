import React, { useState } from 'react';
import { Activity, Cpu, HardDrive, RefreshCw } from 'lucide-react';

interface LLMModel {
  id: string;
  name: string;
  provider: string;
  icon: string;
  status: 'Active' | 'Inactive' | 'Error';
  metrics: {
    responseTime: string;
    successRate: string;
    tokensUsed: string;
  };
}

const LLMPerformanceMonitor: React.FC = () => {
  // Sample data - would be fetched from API in production
  const [models, setModels] = useState<LLMModel[]>([
    {
      id: '1',
      name: 'GPT-4',
      provider: 'OpenAI',
      icon: 'openai',
      status: 'Active',
      metrics: {
        responseTime: '1.2s',
        successRate: '98.5%',
        tokensUsed: '1.2M / 5M'
      }
    },
    {
      id: '2',
      name: 'Gemini Pro',
      provider: 'Google',
      icon: 'google',
      status: 'Active',
      metrics: {
        responseTime: '0.9s',
        successRate: '97.2%',
        tokensUsed: '0.8M / 2M'
      }
    },
    {
      id: '3',
      name: 'Claude 3',
      provider: 'Anthropic',
      icon: 'anthropic',
      status: 'Active',
      metrics: {
        responseTime: '1.1s',
        successRate: '99.1%',
        tokensUsed: '1.5M / 2M'
      }
    }
  ]);

  const getProviderIcon = (icon: string) => {
    switch (icon) {
      case 'openai':
        return <div className="h-8 w-8 rounded-full bg-blue-100 flex items-center justify-center mr-2">
          <i className="fab fa-openai text-blue-600 text-sm"></i>
        </div>;
      case 'google':
        return <div className="h-8 w-8 rounded-full bg-purple-100 flex items-center justify-center mr-2">
          <i className="fab fa-google text-purple-600 text-sm"></i>
        </div>;
      case 'anthropic':
        return <div className="h-8 w-8 rounded-full bg-green-100 flex items-center justify-center mr-2">
          <i className="fas fa-database text-green-600 text-sm"></i>
        </div>;
      default:
        return <div className="h-8 w-8 rounded-full bg-gray-100 flex items-center justify-center mr-2">
          <Activity className="h-4 w-4 text-gray-600" />
        </div>;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'Active':
        return <span className="text-xs px-2 py-1 rounded-full bg-green-100 text-green-800">
          Active
        </span>;
      case 'Inactive':
        return <span className="text-xs px-2 py-1 rounded-full bg-gray-100 text-gray-800">
          Inactive
        </span>;
      case 'Error':
        return <span className="text-xs px-2 py-1 rounded-full bg-red-100 text-red-800">
          Error
        </span>;
      default:
        return <span className="text-xs px-2 py-1 rounded-full bg-gray-100 text-gray-800">
          Unknown
        </span>;
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold">LLM Performance</h2>
        <button className="text-sm text-indigo-600 hover:text-indigo-800 flex items-center">
          <RefreshCw className="h-4 w-4 mr-1" />
          Refresh
        </button>
      </div>
      
      <div className="space-y-4">
        {models.map((model) => (
          <div key={model.id} className="p-3 bg-white border border-gray-200 rounded-md">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center">
                {getProviderIcon(model.icon)}
                <span className="font-medium">{model.name}</span>
              </div>
              {getStatusBadge(model.status)}
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-xs">
                <span className="text-gray-500 flex items-center">
                  <Activity className="h-3 w-3 mr-1" />
                  Avg. Response Time
                </span>
                <span>{model.metrics.responseTime}</span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-gray-500 flex items-center">
                  <Cpu className="h-3 w-3 mr-1" />
                  Success Rate
                </span>
                <span>{model.metrics.successRate}</span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-gray-500 flex items-center">
                  <HardDrive className="h-3 w-3 mr-1" />
                  Tokens Used
                </span>
                <span>{model.metrics.tokensUsed}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
      
      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-500">Last updated: 2 minutes ago</span>
          <button className="text-xs text-indigo-600 hover:text-indigo-800">
            View detailed metrics
          </button>
        </div>
      </div>
    </div>
  );
};

export default LLMPerformanceMonitor;
