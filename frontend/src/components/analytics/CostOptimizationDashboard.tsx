import React, { useState, useEffect } from 'react';
import { 
  DollarSign, 
  TrendingUp, 
  TrendingDown,
  PieChart,
  BarChart3,
  LineChart,
  Zap,
  Target,
  Award,
  Calculator,
  Settings,
  Download,
  RefreshCw,
  Calendar,
  Filter,
  ArrowUpRight,
  ArrowDownRight,
  Percent,
  Clock,
  Users,
  Activity,
  CheckCircle,
  AlertTriangle,
  Info,
  Lightbulb,
  Star,
  ThumbsUp
} from 'lucide-react';

// Cost Optimization and Analytics Interface
export const CostOptimizationDashboard = () => {
  const [timeRange, setTimeRange] = useState('30d');
  const [selectedProvider, setSelectedProvider] = useState('all');
  const [viewMode, setViewMode] = useState('overview');

  const [costMetrics, setCostMetrics] = useState({
    currentMonthSpend: 12450,
    previousMonthSpend: 78900,
    totalSavings: 66450,
    savingsPercentage: 84,
    projectedAnnualSavings: 797400,
    costPerUser: 9.98,
    previousCostPerUser: 63.25,
    totalUsers: 1247,
    activeUsers: 892
  });

  const [providerData, setProviderData] = useState([
    {
      name: 'Together AI',
      usage: 78,
      cost: 1245,
      previousCost: 15600,
      savings: 92,
      requests: 156000,
      avgCostPerRequest: 0.008,
      status: 'optimal',
      trend: 'up'
    },
    {
      name: 'OpenAI GPT-4',
      usage: 15,
      cost: 2890,
      previousCost: 2890,
      savings: 0,
      requests: 23400,
      avgCostPerRequest: 0.123,
      status: 'premium',
      trend: 'stable'
    },
    {
      name: 'Anthropic Claude',
      usage: 5,
      cost: 567,
      previousCost: 567,
      savings: 0,
      requests: 7800,
      avgCostPerRequest: 0.073,
      status: 'premium',
      trend: 'down'
    },
    {
      name: 'Google Gemini',
      usage: 2,
      cost: 234,
      previousCost: 234,
      savings: 0,
      requests: 3120,
      avgCostPerRequest: 0.075,
      status: 'premium',
      trend: 'stable'
    }
  ]);

  const [costTrends, setCostTrends] = useState([
    { month: 'Jan', traditional: 78900, optimized: 12450, savings: 66450 },
    { month: 'Feb', traditional: 82100, optimized: 13200, savings: 68900 },
    { month: 'Mar', traditional: 79800, optimized: 12800, savings: 67000 },
    { month: 'Apr', traditional: 85200, optimized: 13600, savings: 71600 },
    { month: 'May', traditional: 88500, optimized: 14100, savings: 74400 },
    { month: 'Jun', traditional: 91200, optimized: 14500, savings: 76700 }
  ]);

  const [optimizationRecommendations, setOptimizationRecommendations] = useState([
    {
      id: 1,
      title: 'Increase Together AI Usage',
      description: 'Migrate 10% more requests from OpenAI to Together AI',
      potentialSavings: 2340,
      effort: 'low',
      impact: 'high',
      timeframe: '1 week'
    },
    {
      id: 2,
      title: 'Implement Request Caching',
      description: 'Cache frequently requested AI responses to reduce API calls',
      potentialSavings: 1560,
      effort: 'medium',
      impact: 'medium',
      timeframe: '2 weeks'
    },
    {
      id: 3,
      title: 'Optimize Model Selection',
      description: 'Use smaller models for simple tasks, larger for complex ones',
      potentialSavings: 890,
      effort: 'high',
      impact: 'medium',
      timeframe: '1 month'
    },
    {
      id: 4,
      title: 'Batch Processing',
      description: 'Group similar requests to reduce overhead costs',
      potentialSavings: 670,
      effort: 'medium',
      impact: 'low',
      timeframe: '3 weeks'
    }
  ]);

  const getStatusColor = (status) => {
    switch (status) {
      case 'optimal': return 'text-green-700 bg-green-100';
      case 'premium': return 'text-blue-700 bg-blue-100';
      case 'warning': return 'text-yellow-700 bg-yellow-100';
      case 'expensive': return 'text-red-700 bg-red-100';
      default: return 'text-gray-700 bg-gray-100';
    }
  };

  const getTrendIcon = (trend) => {
    switch (trend) {
      case 'up': return <TrendingUp className="h-4 w-4 text-green-500" />;
      case 'down': return <TrendingDown className="h-4 w-4 text-red-500" />;
      case 'stable': return <ArrowUpRight className="h-4 w-4 text-gray-500" />;
      default: return <ArrowUpRight className="h-4 w-4 text-gray-500" />;
    }
  };

  const getEffortColor = (effort) => {
    switch (effort) {
      case 'low': return 'text-green-700 bg-green-100';
      case 'medium': return 'text-yellow-700 bg-yellow-100';
      case 'high': return 'text-red-700 bg-red-100';
      default: return 'text-gray-700 bg-gray-100';
    }
  };

  const getImpactColor = (impact) => {
    switch (impact) {
      case 'high': return 'text-green-700 bg-green-100';
      case 'medium': return 'text-yellow-700 bg-yellow-100';
      case 'low': return 'text-red-700 bg-red-100';
      default: return 'text-gray-700 bg-gray-100';
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  const calculateROI = () => {
    return ((costMetrics.totalSavings / costMetrics.previousMonthSpend) * 100).toFixed(1);
  };

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-8">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Cost Optimization Dashboard</h1>
            <p className="text-gray-600 mt-1">AI cost analytics and optimization insights</p>
          </div>
          <div className="flex items-center space-x-4">
            <div className="text-right">
              <p className="text-sm font-medium text-gray-900">
                Total Savings: <span className="text-green-600 font-bold">{formatCurrency(costMetrics.totalSavings)}</span>
              </p>
              <p className="text-xs text-gray-500">This month vs. traditional pricing</p>
            </div>
            <button className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition-colors flex items-center space-x-2">
              <Download className="h-4 w-4" />
              <span>Export Report</span>
            </button>
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Monthly Spend</p>
              <p className="text-3xl font-bold text-gray-900">{formatCurrency(costMetrics.currentMonthSpend)}</p>
            </div>
            <DollarSign className="h-8 w-8 text-green-500" />
          </div>
          <div className="mt-4 flex items-center text-sm">
            <TrendingDown className="h-4 w-4 text-green-500 mr-1" />
            <span className="text-green-600">
              -{costMetrics.savingsPercentage}% from last month
            </span>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Cost Savings</p>
              <p className="text-3xl font-bold text-green-600">{costMetrics.savingsPercentage}%</p>
            </div>
            <Percent className="h-8 w-8 text-green-500" />
          </div>
          <div className="mt-4 flex items-center text-sm">
            <Award className="h-4 w-4 text-green-500 mr-1" />
            <span className="text-green-600">
              {formatCurrency(costMetrics.totalSavings)} saved
            </span>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Cost per User</p>
              <p className="text-3xl font-bold text-gray-900">${costMetrics.costPerUser}</p>
            </div>
            <Users className="h-8 w-8 text-blue-500" />
          </div>
          <div className="mt-4 flex items-center text-sm">
            <TrendingDown className="h-4 w-4 text-green-500 mr-1" />
            <span className="text-green-600">
              Was ${costMetrics.previousCostPerUser}
            </span>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Annual Projection</p>
              <p className="text-3xl font-bold text-green-600">{formatCurrency(costMetrics.projectedAnnualSavings)}</p>
            </div>
            <Target className="h-8 w-8 text-green-500" />
          </div>
          <div className="mt-4 flex items-center text-sm">
            <Calculator className="h-4 w-4 text-green-500 mr-1" />
            <span className="text-green-600">
              Projected savings
            </span>
          </div>
        </div>
      </div>

      {/* Cost Trends Chart */}
      <div className="bg-white rounded-lg shadow-sm border">
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">Cost Trends Analysis</h2>
            <div className="flex items-center space-x-2">
              <select 
                value={timeRange}
                onChange={(e) => setTimeRange(e.target.value)}
                className="border border-gray-300 rounded-md px-3 py-1 text-sm"
              >
                <option value="7d">Last 7 Days</option>
                <option value="30d">Last 30 Days</option>
                <option value="90d">Last 3 Months</option>
                <option value="1y">Last Year</option>
              </select>
            </div>
          </div>
        </div>
        <div className="p-6">
          <div className="h-64 flex items-end justify-between space-x-2">
            {costTrends.map((data, index) => (
              <div key={index} className="flex-1 flex flex-col items-center">
                <div className="w-full flex flex-col space-y-1">
                  <div 
                    className="bg-red-400 rounded-t"
                    style={{ height: `${(data.traditional / 100000) * 200}px` }}
                    title={`Traditional: ${formatCurrency(data.traditional)}`}
                  ></div>
                  <div 
                    className="bg-green-500 rounded"
                    style={{ height: `${(data.optimized / 100000) * 200}px` }}
                    title={`Optimized: ${formatCurrency(data.optimized)}`}
                  ></div>
                </div>
                <span className="text-xs text-gray-600 mt-2">{data.month}</span>
              </div>
            ))}
          </div>
          <div className="flex items-center justify-center space-x-6 mt-4">
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-red-400 rounded"></div>
              <span className="text-sm text-gray-600">Traditional Pricing</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-green-500 rounded"></div>
              <span className="text-sm text-gray-600">Optimized Pricing</span>
            </div>
          </div>
        </div>
      </div>

      {/* Provider Breakdown */}
      <div className="bg-white rounded-lg shadow-sm border">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">AI Provider Cost Breakdown</h2>
        </div>
        <div className="p-6">
          <div className="space-y-4">
            {providerData.map((provider) => (
              <div key={provider.name} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center space-x-3">
                    <Zap className="h-6 w-6 text-indigo-500" />
                    <div>
                      <h4 className="font-medium text-gray-900">{provider.name}</h4>
                      <p className="text-sm text-gray-600">{provider.requests.toLocaleString()} requests</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(provider.status)}`}>
                      {provider.status}
                    </span>
                    {getTrendIcon(provider.trend)}
                  </div>
                </div>
                
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div>
                    <label className="text-xs text-gray-600">Usage</label>
                    <div className="flex items-center space-x-2">
                      <div className="flex-1 bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-indigo-600 h-2 rounded-full" 
                          style={{ width: `${provider.usage}%` }}
                        ></div>
                      </div>
                      <span className="text-sm font-medium">{provider.usage}%</span>
                    </div>
                  </div>
                  
                  <div>
                    <label className="text-xs text-gray-600">Current Cost</label>
                    <p className="text-lg font-bold text-gray-900">{formatCurrency(provider.cost)}</p>
                  </div>
                  
                  <div>
                    <label className="text-xs text-gray-600">Savings</label>
                    <p className={`text-lg font-bold ${provider.savings > 0 ? 'text-green-600' : 'text-gray-600'}`}>
                      {provider.savings > 0 ? `${provider.savings}%` : 'Premium'}
                    </p>
                  </div>
                  
                  <div>
                    <label className="text-xs text-gray-600">Cost per Request</label>
                    <p className="text-lg font-bold text-gray-900">${provider.avgCostPerRequest}</p>
                  </div>
                </div>
                
                {provider.savings > 0 && (
                  <div className="mt-3 p-3 bg-green-50 rounded-lg">
                    <div className="flex items-center space-x-2">
                      <CheckCircle className="h-4 w-4 text-green-500" />
                      <span className="text-sm text-green-700">
                        Saving {formatCurrency(provider.previousCost - provider.cost)} per month with this provider
                      </span>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Optimization Recommendations */}
      <div className="bg-white rounded-lg shadow-sm border">
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">Optimization Recommendations</h2>
            <div className="flex items-center space-x-2">
              <Lightbulb className="h-5 w-5 text-yellow-500" />
              <span className="text-sm text-gray-600">AI-powered insights</span>
            </div>
          </div>
        </div>
        <div className="p-6">
          <div className="space-y-4">
            {optimizationRecommendations.map((rec) => (
              <div key={rec.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <h4 className="font-medium text-gray-900">{rec.title}</h4>
                      <span className="text-green-600 font-bold">+{formatCurrency(rec.potentialSavings)}</span>
                    </div>
                    <p className="text-sm text-gray-600 mb-3">{rec.description}</p>
                    <div className="flex items-center space-x-4">
                      <div className="flex items-center space-x-1">
                        <span className="text-xs text-gray-500">Effort:</span>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getEffortColor(rec.effort)}`}>
                          {rec.effort}
                        </span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <span className="text-xs text-gray-500">Impact:</span>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getImpactColor(rec.impact)}`}>
                          {rec.impact}
                        </span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <Clock className="h-3 w-3 text-gray-500" />
                        <span className="text-xs text-gray-500">{rec.timeframe}</span>
                      </div>
                    </div>
                  </div>
                  <div className="flex space-x-2 ml-4">
                    <button className="bg-indigo-600 text-white px-3 py-1 rounded-md hover:bg-indigo-700 transition-colors text-sm">
                      Implement
                    </button>
                    <button className="bg-gray-200 text-gray-700 px-3 py-1 rounded-md hover:bg-gray-300 transition-colors text-sm">
                      Learn More
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ROI Summary */}
      <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg border border-green-200 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Return on Investment Summary</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <p className="text-sm text-gray-600">Monthly ROI</p>
                <p className="text-2xl font-bold text-green-600">{calculateROI()}%</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Payback Period</p>
                <p className="text-2xl font-bold text-green-600">Immediate</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Annual Savings</p>
                <p className="text-2xl font-bold text-green-600">{formatCurrency(costMetrics.projectedAnnualSavings)}</p>
              </div>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Star className="h-8 w-8 text-yellow-500" />
            <div className="text-right">
              <p className="text-sm font-medium text-gray-900">Optimization Score</p>
              <p className="text-2xl font-bold text-green-600">A+</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CostOptimizationDashboard;

