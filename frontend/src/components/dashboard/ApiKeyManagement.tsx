import React, { useState } from 'react';
import { Key, Shield, AlertTriangle, CheckCircle, Plus, RotateCcw, Trash2 } from 'lucide-react';

interface ApiKey {
  id: string;
  service: string;
  name: string;
  status: 'active' | 'inactive' | 'expired' | 'error';
  lastUsed: string;
  usageCount: number;
  expiresAt?: string;
  isUserProvided: boolean;
}

interface ServiceConfig {
  name: string;
  description: string;
  category: 'text' | 'image' | 'video' | 'audio';
  creditCost: number;
  required: boolean;
}

const ApiKeyManagement: React.FC = () => {
  const [apiKeys, setApiKeys] = useState<ApiKey[]>([
    {
      id: '1',
      service: 'openai',
      name: 'OpenAI GPT-4',
      status: 'active',
      lastUsed: '2 hours ago',
      usageCount: 1247,
      expiresAt: '2024-12-31',
      isUserProvided: true
    },
    {
      id: '2',
      service: 'anthropic',
      name: 'Anthropic Claude',
      status: 'inactive',
      lastUsed: 'Never',
      usageCount: 0,
      isUserProvided: false
    },
    {
      id: '3',
      service: 'midjourney',
      name: 'Midjourney Pro',
      status: 'active',
      lastUsed: '1 day ago',
      usageCount: 89,
      expiresAt: '2024-11-15',
      isUserProvided: true
    },
    {
      id: '4',
      service: 'runway',
      name: 'Runway ML',
      status: 'inactive',
      lastUsed: 'Never',
      usageCount: 0,
      isUserProvided: false
    },
    {
      id: '5',
      service: 'google',
      name: 'Google AI',
      status: 'error',
      lastUsed: '3 days ago',
      usageCount: 156,
      isUserProvided: false
    }
  ]);

  const [services] = useState<ServiceConfig[]>([
    {
      name: 'OpenAI',
      description: 'GPT-4, GPT-3.5, DALL-E 3',
      category: 'text',
      creditCost: 10,
      required: true
    },
    {
      name: 'Anthropic',
      description: 'Claude 3 Opus, Sonnet, Haiku',
      category: 'text',
      creditCost: 15,
      required: true
    },
    {
      name: 'Midjourney',
      description: 'Image generation and editing',
      category: 'image',
      creditCost: 20,
      required: false
    },
    {
      name: 'Runway',
      description: 'Video generation and editing',
      category: 'video',
      creditCost: 80,
      required: false
    },
    {
      name: 'Google AI',
      description: 'Gemini Pro, Imagen 2',
      category: 'text',
      creditCost: 12,
      required: false
    },
    {
      name: 'Stability AI',
      description: 'Stable Diffusion, Video',
      category: 'image',
      creditCost: 15,
      required: false
    }
  ]);

  const [showAddModal, setShowAddModal] = useState(false);
  const [selectedService, setSelectedService] = useState('');

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'inactive':
        return <AlertTriangle className="h-5 w-5 text-yellow-500" />;
      case 'error':
        return <AlertTriangle className="h-5 w-5 text-red-500" />;
      case 'expired':
        return <AlertTriangle className="h-5 w-5 text-orange-500" />;
      default:
        return <AlertTriangle className="h-5 w-5 text-gray-500" />;
    }
  };

  const getStatusBadge = (status: string) => {
    const baseClasses = "px-2 py-1 text-xs rounded-full font-medium";
    switch (status) {
      case 'active':
        return `${baseClasses} bg-green-100 text-green-800`;
      case 'inactive':
        return `${baseClasses} bg-yellow-100 text-yellow-800`;
      case 'error':
        return `${baseClasses} bg-red-100 text-red-800`;
      case 'expired':
        return `${baseClasses} bg-orange-100 text-orange-800`;
      default:
        return `${baseClasses} bg-gray-100 text-gray-800`;
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'text':
        return '📝';
      case 'image':
        return '🎨';
      case 'video':
        return '🎬';
      case 'audio':
        return '🎵';
      default:
        return '⚙️';
    }
  };

  const handleAddApiKey = (service: string, apiKey: string) => {
    // In a real implementation, this would validate and store the API key
    const newKey: ApiKey = {
      id: Date.now().toString(),
      service: service.toLowerCase(),
      name: service,
      status: 'active',
      lastUsed: 'Never',
      usageCount: 0,
      isUserProvided: true
    };
    
    setApiKeys([...apiKeys, newKey]);
    setShowAddModal(false);
    setSelectedService('');
  };

  const handleRemoveApiKey = (id: string) => {
    setApiKeys(apiKeys.filter(key => key.id !== id));
  };

  const handleRotateApiKey = (id: string) => {
    setApiKeys(apiKeys.map(key => 
      key.id === id 
        ? { ...key, status: 'active' as const, lastUsed: 'Just now' }
        : key
    ));
  };

  const userProvidedKeys = apiKeys.filter(key => key.isUserProvided);
  const systemKeys = apiKeys.filter(key => !key.isUserProvided);

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">API Key Management</h1>
            <p className="text-gray-600 mt-1">Manage your API keys for different AI services</p>
          </div>
          <button
            onClick={() => setShowAddModal(true)}
            className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700 flex items-center"
          >
            <Plus className="h-4 w-4 mr-2" />
            Add API Key
          </button>
        </div>
      </div>

      {/* Cost Savings Overview */}
      <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg border p-6">
        <div className="flex items-center">
          <Shield className="h-8 w-8 text-green-600" />
          <div className="ml-4">
            <h2 className="text-lg font-semibold text-gray-900">Cost Optimization</h2>
            <p className="text-gray-600">
              You have {userProvidedKeys.length} of {services.length} services configured with your own API keys.
              This saves you approximately {Math.round((userProvidedKeys.length / services.length) * 100)}% on credit consumption.
            </p>
          </div>
        </div>
      </div>

      {/* Your API Keys */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Your API Keys</h2>
        {userProvidedKeys.length > 0 ? (
          <div className="space-y-4">
            {userProvidedKeys.map((key) => (
              <div key={key.id} className="border rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    {getStatusIcon(key.status)}
                    <div className="ml-3">
                      <h3 className="font-medium text-gray-900">{key.name}</h3>
                      <p className="text-sm text-gray-500">
                        Last used: {key.lastUsed} • {key.usageCount.toLocaleString()} operations
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3">
                    <span className={getStatusBadge(key.status)}>
                      {key.status}
                    </span>
                    <button
                      onClick={() => handleRotateApiKey(key.id)}
                      className="text-gray-400 hover:text-gray-600"
                      title="Rotate API Key"
                    >
                      <RotateCcw className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => handleRemoveApiKey(key.id)}
                      className="text-red-400 hover:text-red-600"
                      title="Remove API Key"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </div>
                {key.expiresAt && (
                  <div className="mt-2 text-sm text-gray-500">
                    Expires: {key.expiresAt}
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            <Key className="h-12 w-12 mx-auto mb-4 text-gray-300" />
            <p>No API keys configured yet.</p>
            <p className="text-sm">Add your own API keys to reduce credit consumption.</p>
          </div>
        )}
      </div>

      {/* Available Services */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Available Services</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {services.map((service) => {
            const hasUserKey = userProvidedKeys.some(key => 
              key.service.toLowerCase() === service.name.toLowerCase()
            );
            const systemKey = systemKeys.find(key => 
              key.service.toLowerCase() === service.name.toLowerCase()
            );
            
            return (
              <div key={service.name} className="border rounded-lg p-4">
                <div className="flex items-start justify-between">
                  <div className="flex items-center">
                    <span className="text-2xl mr-3">{getCategoryIcon(service.category)}</span>
                    <div>
                      <h3 className="font-medium text-gray-900">{service.name}</h3>
                      <p className="text-sm text-gray-500">{service.description}</p>
                    </div>
                  </div>
                  {service.required && (
                    <span className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full">
                      Required
                    </span>
                  )}
                </div>
                
                <div className="mt-3 flex items-center justify-between">
                  <div className="text-sm">
                    <span className="text-gray-500">Credit cost: </span>
                    <span className="font-medium">
                      {hasUserKey ? '0' : service.creditCost} credits
                    </span>
                  </div>
                  <div className="flex items-center">
                    {hasUserKey ? (
                      <span className="text-green-600 text-sm font-medium">Your Key</span>
                    ) : systemKey ? (
                      <span className="text-blue-600 text-sm font-medium">System Key</span>
                    ) : (
                      <span className="text-gray-400 text-sm">Not Available</span>
                    )}
                  </div>
                </div>
                
                {!hasUserKey && (
                  <button
                    onClick={() => {
                      setSelectedService(service.name);
                      setShowAddModal(true);
                    }}
                    className="mt-3 w-full text-sm text-indigo-600 hover:text-indigo-800 border border-indigo-200 rounded-md py-2"
                  >
                    Add Your API Key
                  </button>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* System Fallback Keys */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">System Fallback Keys</h2>
        <p className="text-gray-600 mb-4">
          These are system-provided API keys that will be used when you don't have your own keys configured.
          Operations using these keys will consume credits from your allocation.
        </p>
        <div className="space-y-3">
          {systemKeys.map((key) => (
            <div key={key.id} className="flex items-center justify-between border rounded-lg p-3">
              <div className="flex items-center">
                {getStatusIcon(key.status)}
                <div className="ml-3">
                  <span className="font-medium text-gray-900">{key.name}</span>
                  <span className="ml-2 text-sm text-gray-500">
                    ({key.usageCount.toLocaleString()} operations)
                  </span>
                </div>
              </div>
              <span className={getStatusBadge(key.status)}>
                {key.status}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Add API Key Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Add API Key {selectedService && `for ${selectedService}`}
            </h3>
            
            {!selectedService && (
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select Service
                </label>
                <select
                  value={selectedService}
                  onChange={(e) => setSelectedService(e.target.value)}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                >
                  <option value="">Choose a service...</option>
                  {services.map((service) => (
                    <option key={service.name} value={service.name}>
                      {service.name}
                    </option>
                  ))}
                </select>
              </div>
            )}
            
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                API Key
              </label>
              <input
                type="password"
                placeholder="Enter your API key..."
                className="w-full border border-gray-300 rounded-md px-3 py-2"
              />
            </div>
            
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => {
                  setShowAddModal(false);
                  setSelectedService('');
                }}
                className="px-4 py-2 text-gray-600 hover:text-gray-800"
              >
                Cancel
              </button>
              <button
                onClick={() => handleAddApiKey(selectedService, 'dummy-key')}
                disabled={!selectedService}
                className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50"
              >
                Add Key
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ApiKeyManagement;

