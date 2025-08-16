import React, { useState } from 'react';
import { DollarSign, Users, TrendingUp, Settings, CreditCard, Key } from 'lucide-react';

interface BillingData {
  currentPlan: {
    name: string;
    price: number;
    ownApiPrice: number;
    credits: number;
    users: number;
  };
  usage: {
    credits: number;
    percentage: number;
  };
  revenue: {
    monthly: number;
    annual: number;
    growth: number;
  };
  users: {
    total: number;
    basic: number;
    pro: number;
    expert: number;
    enterprise: number;
  };
}

const BillingSubscriptionsTab: React.FC = () => {
  const [billingData] = useState<BillingData>({
    currentPlan: {
      name: 'Pro',
      price: 149.99,
      ownApiPrice: 99.99,
      credits: 5000,
      users: 12547
    },
    usage: {
      credits: 3247,
      percentage: 65
    },
    revenue: {
      monthly: 1407905,
      annual: 16894860,
      growth: 23.5
    },
    users: {
      total: 12547,
      basic: 3764, // 30%
      pro: 6274,  // 50%
      expert: 1882, // 15%
      enterprise: 627 // 5%
    }
  });

  const [pricingTiers] = useState([
    {
      name: 'Basic',
      price: 59.99,
      ownApiPrice: 29.99,
      credits: 2000,
      features: ['Up to 2 standard LLMs', 'Document creation & editing', 'Email support'],
      users: billingData.users.basic,
      revenue: billingData.users.basic * 59.99 * 0.7 + billingData.users.basic * 29.99 * 0.3
    },
    {
      name: 'Pro',
      price: 149.99,
      ownApiPrice: 99.99,
      credits: 5000,
      features: ['3 standard + 2 advanced LLMs', 'Priority support', 'Advanced customization'],
      users: billingData.users.pro,
      revenue: billingData.users.pro * 149.99 * 0.7 + billingData.users.pro * 99.99 * 0.3,
      popular: true
    },
    {
      name: 'Expert',
      price: 249.99,
      ownApiPrice: 149.99,
      credits: 15000,
      features: ['All LLMs', '24/7 dedicated support', 'Custom integrations'],
      users: billingData.users.expert,
      revenue: billingData.users.expert * 249.99 * 0.7 + billingData.users.expert * 149.99 * 0.3
    },
    {
      name: 'Enterprise',
      price: 500,
      ownApiPrice: 500,
      credits: 50000,
      features: ['Custom deployment', 'Dedicated account manager', 'SLA guarantees'],
      users: billingData.users.enterprise,
      revenue: billingData.users.enterprise * 500
    }
  ]);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat('en-US').format(num);
  };

  return (
    <div className="space-y-6">
      {/* Revenue Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center">
            <DollarSign className="h-8 w-8 text-green-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Monthly Revenue</p>
              <p className="text-2xl font-bold text-gray-900">
                {formatCurrency(billingData.revenue.monthly)}
              </p>
            </div>
          </div>
          <div className="mt-4">
            <div className="flex items-center text-sm">
              <TrendingUp className="h-4 w-4 text-green-500 mr-1" />
              <span className="text-green-600 font-medium">+{billingData.revenue.growth}%</span>
              <span className="text-gray-500 ml-1">from last month</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center">
            <TrendingUp className="h-8 w-8 text-blue-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Annual Revenue</p>
              <p className="text-2xl font-bold text-gray-900">
                {formatCurrency(billingData.revenue.annual)}
              </p>
            </div>
          </div>
          <div className="mt-4">
            <div className="text-sm text-gray-500">
              Projected based on current growth
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center">
            <Users className="h-8 w-8 text-purple-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Total Users</p>
              <p className="text-2xl font-bold text-gray-900">
                {formatNumber(billingData.users.total)}
              </p>
            </div>
          </div>
          <div className="mt-4">
            <div className="text-sm text-gray-500">
              Across all subscription tiers
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center">
            <CreditCard className="h-8 w-8 text-indigo-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Avg Revenue/User</p>
              <p className="text-2xl font-bold text-gray-900">
                {formatCurrency(billingData.revenue.monthly / billingData.users.total)}
              </p>
            </div>
          </div>
          <div className="mt-4">
            <div className="text-sm text-gray-500">
              Monthly average per user
            </div>
          </div>
        </div>
      </div>

      {/* Subscription Tiers */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-6">Subscription Tiers</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {pricingTiers.map((tier) => (
            <div key={tier.name} className={`border rounded-lg p-6 relative ${
              tier.popular ? 'border-indigo-500 bg-indigo-50' : 'border-gray-200'
            }`}>
              {tier.popular && (
                <div className="absolute -top-2 left-1/2 transform -translate-x-1/2">
                  <span className="bg-indigo-600 text-white px-3 py-1 text-xs rounded-full">
                    Most Popular
                  </span>
                </div>
              )}
              
              <div className="text-center">
                <h3 className="text-lg font-semibold text-gray-900">{tier.name}</h3>
                <div className="mt-2">
                  <span className="text-3xl font-bold text-gray-900">
                    {formatCurrency(tier.price)}
                  </span>
                  <span className="text-gray-500">/month</span>
                </div>
                <div className="text-sm text-gray-500 mt-1">
                  {formatCurrency(tier.ownApiPrice)}/month with own API
                </div>
              </div>

              <div className="mt-4 space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Users:</span>
                  <span className="font-medium">{formatNumber(tier.users)}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Credits:</span>
                  <span className="font-medium">{formatNumber(tier.credits)}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Revenue:</span>
                  <span className="font-medium">{formatCurrency(tier.revenue)}</span>
                </div>
              </div>

              <div className="mt-4">
                <div className="text-xs text-gray-500 mb-2">Features:</div>
                <ul className="text-xs text-gray-600 space-y-1">
                  {tier.features.map((feature, index) => (
                    <li key={index}>• {feature}</li>
                  ))}
                </ul>
              </div>

              <div className="mt-4 pt-4 border-t border-gray-200">
                <button className="w-full text-sm text-indigo-600 hover:text-indigo-800">
                  Manage Tier
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Revenue Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Revenue by Tier</h3>
          <div className="space-y-4">
            {pricingTiers.map((tier) => {
              const percentage = (tier.revenue / billingData.revenue.monthly) * 100;
              return (
                <div key={tier.name}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="font-medium">{tier.name}</span>
                    <span>{formatCurrency(tier.revenue)} ({percentage.toFixed(1)}%)</span>
                  </div>
                  <div className="bg-gray-200 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full ${
                        tier.popular ? 'bg-indigo-600' : 'bg-gray-400'
                      }`}
                      style={{ width: `${percentage}%` }}
                    ></div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">User Distribution</h3>
          <div className="space-y-4">
            {pricingTiers.map((tier) => {
              const percentage = (tier.users / billingData.users.total) * 100;
              return (
                <div key={tier.name}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="font-medium">{tier.name}</span>
                    <span>{formatNumber(tier.users)} ({percentage.toFixed(1)}%)</span>
                  </div>
                  <div className="bg-gray-200 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full ${
                        tier.popular ? 'bg-indigo-600' : 'bg-gray-400'
                      }`}
                      style={{ width: `${percentage}%` }}
                    ></div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Billing Settings */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-gray-900">Billing Settings</h3>
          <button className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700 flex items-center">
            <Settings className="h-4 w-4 mr-2" />
            Configure
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className="border rounded-lg p-4">
            <h4 className="font-medium text-gray-900 mb-2">Payment Processing</h4>
            <p className="text-sm text-gray-600 mb-3">
              Stripe integration for secure payment processing
            </p>
            <div className="text-sm">
              <div className="flex justify-between">
                <span>Processing Fee:</span>
                <span>2.9% + $0.30</span>
              </div>
              <div className="flex justify-between">
                <span>Monthly Volume:</span>
                <span>{formatCurrency(billingData.revenue.monthly)}</span>
              </div>
            </div>
          </div>

          <div className="border rounded-lg p-4">
            <h4 className="font-medium text-gray-900 mb-2">Credit System</h4>
            <p className="text-sm text-gray-600 mb-3">
              Manage credit pricing and packages
            </p>
            <div className="text-sm">
              <div className="flex justify-between">
                <span>Base Rate:</span>
                <span>$0.01 per credit</span>
              </div>
              <div className="flex justify-between">
                <span>Bulk Discount:</span>
                <span>Up to 20%</span>
              </div>
            </div>
          </div>

          <div className="border rounded-lg p-4">
            <h4 className="font-medium text-gray-900 mb-2">Enterprise Billing</h4>
            <p className="text-sm text-gray-600 mb-3">
              Custom billing for enterprise clients
            </p>
            <div className="text-sm">
              <div className="flex justify-between">
                <span>Custom Contracts:</span>
                <span>{billingData.users.enterprise}</span>
              </div>
              <div className="flex justify-between">
                <span>Avg Contract:</span>
                <span>{formatCurrency(500)}/month</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Transactions */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Transactions</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  User
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Plan
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Amount
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {[
                { user: 'john.doe@company.com', plan: 'Pro', amount: 149.99, date: '2024-06-08', status: 'Paid' },
                { user: 'jane.smith@startup.io', plan: 'Expert', amount: 249.99, date: '2024-06-08', status: 'Paid' },
                { user: 'enterprise@bigcorp.com', plan: 'Enterprise', amount: 2500.00, date: '2024-06-07', status: 'Paid' },
                { user: 'freelancer@gmail.com', plan: 'Basic', amount: 59.99, date: '2024-06-07', status: 'Paid' },
                { user: 'team@agency.com', plan: 'Pro', amount: 99.99, date: '2024-06-07', status: 'Paid' }
              ].map((transaction, index) => (
                <tr key={index}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {transaction.user}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {transaction.plan}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {formatCurrency(transaction.amount)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {transaction.date}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                      {transaction.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default BillingSubscriptionsTab;

