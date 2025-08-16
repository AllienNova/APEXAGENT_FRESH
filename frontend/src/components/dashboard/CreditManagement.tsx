import React, { useState, useEffect } from 'react';
import { CreditCard, DollarSign, TrendingUp, Users, AlertCircle, CheckCircle } from 'lucide-react';

interface CreditBalance {
  current: number;
  monthly: number;
  used: number;
  percentage: number;
}

interface UserTier {
  name: string;
  price: number;
  ownApiPrice: number;
  credits: number;
}

interface ApiKeyStatus {
  service: string;
  hasKey: boolean;
  status: 'active' | 'inactive' | 'error';
}

const CreditManagement: React.FC = () => {
  const [creditBalance, setCreditBalance] = useState<CreditBalance>({
    current: 3247,
    monthly: 5000,
    used: 1753,
    percentage: 65
  });

  const [userTier] = useState<UserTier>({
    name: 'Pro',
    price: 149.99,
    ownApiPrice: 99.99,
    credits: 5000
  });

  const [apiKeys] = useState<ApiKeyStatus[]>([
    { service: 'OpenAI', hasKey: true, status: 'active' },
    { service: 'Anthropic', hasKey: false, status: 'inactive' },
    { service: 'Midjourney', hasKey: true, status: 'active' },
    { service: 'Runway', hasKey: false, status: 'inactive' },
    { service: 'Google AI', hasKey: false, status: 'inactive' }
  ]);

  const [creditPackages] = useState([
    { credits: 1000, price: 10, popular: false },
    { credits: 5000, price: 45, popular: true },
    { credits: 10000, price: 85, popular: false },
    { credits: 25000, price: 200, popular: false }
  ]);

  const calculateSavings = () => {
    const userKeysCount = apiKeys.filter(key => key.hasKey).length;
    const totalKeys = apiKeys.length;
    const savingsPercentage = (userKeysCount / totalKeys) * 100;
    return Math.round(savingsPercentage);
  };

  const getCreditCostForService = (service: string, hasKey: boolean) => {
    if (hasKey) return 0;
    
    const costs: { [key: string]: number } = {
      'OpenAI': 10,
      'Anthropic': 15,
      'Midjourney': 20,
      'Runway': 80,
      'Google AI': 12
    };
    
    return costs[service] || 10;
  };

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Credit Management</h1>
            <p className="text-gray-600 mt-1">Manage your credits and API key settings</p>
          </div>
          <div className="text-right">
            <div className="text-sm text-gray-500">Current Plan</div>
            <div className="text-xl font-bold text-indigo-600">{userTier.name}</div>
            <div className="text-sm text-gray-500">
              ${userTier.price}/month (${userTier.ownApiPrice} with own keys)
            </div>
          </div>
        </div>
      </div>

      {/* Credit Balance Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center">
            <CreditCard className="h-8 w-8 text-indigo-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Current Balance</p>
              <p className="text-2xl font-bold text-gray-900">{creditBalance.current.toLocaleString()}</p>
            </div>
          </div>
          <div className="mt-4">
            <div className="flex justify-between text-sm text-gray-500">
              <span>Used this month</span>
              <span>{creditBalance.used.toLocaleString()} / {creditBalance.monthly.toLocaleString()}</span>
            </div>
            <div className="mt-2 bg-gray-200 rounded-full h-2">
              <div 
                className="bg-indigo-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${creditBalance.percentage}%` }}
              ></div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center">
            <TrendingUp className="h-8 w-8 text-green-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Estimated Savings</p>
              <p className="text-2xl font-bold text-gray-900">{calculateSavings()}%</p>
            </div>
          </div>
          <p className="text-sm text-gray-500 mt-2">
            Based on your API key configuration
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center">
            <DollarSign className="h-8 w-8 text-blue-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Monthly Allocation</p>
              <p className="text-2xl font-bold text-gray-900">{userTier.credits.toLocaleString()}</p>
            </div>
          </div>
          <p className="text-sm text-gray-500 mt-2">
            Resets on billing cycle
          </p>
        </div>
      </div>

      {/* API Key Status */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">API Key Status</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {apiKeys.map((key) => (
            <div key={key.service} className="border rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  {key.hasKey ? (
                    <CheckCircle className="h-5 w-5 text-green-500" />
                  ) : (
                    <AlertCircle className="h-5 w-5 text-red-500" />
                  )}
                  <span className="ml-2 font-medium">{key.service}</span>
                </div>
                <span className={`px-2 py-1 text-xs rounded-full ${
                  key.hasKey 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-red-100 text-red-800'
                }`}>
                  {key.hasKey ? 'Own Key' : 'System Key'}
                </span>
              </div>
              <div className="mt-2 text-sm text-gray-600">
                Credit cost: {getCreditCostForService(key.service, key.hasKey)} per 1K tokens
              </div>
              {!key.hasKey && (
                <button className="mt-2 text-sm text-indigo-600 hover:text-indigo-800">
                  Add your API key
                </button>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Purchase Additional Credits */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Purchase Additional Credits</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {creditPackages.map((pkg) => (
            <div key={pkg.credits} className={`border rounded-lg p-4 relative ${
              pkg.popular ? 'border-indigo-500 bg-indigo-50' : 'border-gray-200'
            }`}>
              {pkg.popular && (
                <div className="absolute -top-2 left-1/2 transform -translate-x-1/2">
                  <span className="bg-indigo-600 text-white px-3 py-1 text-xs rounded-full">
                    Popular
                  </span>
                </div>
              )}
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">
                  {pkg.credits.toLocaleString()}
                </div>
                <div className="text-sm text-gray-500">credits</div>
                <div className="text-xl font-semibold text-gray-900 mt-2">
                  ${pkg.price}
                </div>
                <div className="text-sm text-gray-500">
                  ${(pkg.price / pkg.credits * 1000).toFixed(2)} per 1K credits
                </div>
                <button className={`w-full mt-4 py-2 px-4 rounded-md text-sm font-medium ${
                  pkg.popular
                    ? 'bg-indigo-600 text-white hover:bg-indigo-700'
                    : 'bg-gray-100 text-gray-900 hover:bg-gray-200'
                }`}>
                  Purchase
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Usage Analytics */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Usage Analytics</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 className="text-sm font-medium text-gray-700 mb-3">Credit Usage by Service</h3>
            <div className="space-y-3">
              {apiKeys.map((key) => {
                const usage = Math.floor(Math.random() * 500) + 50;
                const percentage = (usage / creditBalance.used) * 100;
                return (
                  <div key={key.service}>
                    <div className="flex justify-between text-sm">
                      <span>{key.service}</span>
                      <span>{usage} credits</span>
                    </div>
                    <div className="mt-1 bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-indigo-600 h-2 rounded-full"
                        style={{ width: `${Math.min(percentage, 100)}%` }}
                      ></div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
          <div>
            <h3 className="text-sm font-medium text-gray-700 mb-3">Monthly Trend</h3>
            <div className="text-sm text-gray-600">
              <p>• Average daily usage: {Math.floor(creditBalance.used / 30)} credits</p>
              <p>• Projected monthly usage: {Math.floor(creditBalance.used * 1.2).toLocaleString()} credits</p>
              <p>• Estimated overage: {Math.max(0, Math.floor(creditBalance.used * 1.2) - creditBalance.monthly).toLocaleString()} credits</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CreditManagement;

