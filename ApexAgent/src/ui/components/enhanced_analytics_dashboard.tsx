// Enhanced Analytics Dashboard Component
import React, { useState, useEffect } from 'react';
import { BarChart3, TrendingUp, Users, Clock, Zap, Award, Filter, Download, Calendar, ChevronDown, Search, RefreshCw } from 'lucide-react';

// Mock data for demonstration
const performanceData = {
  responseTime: [
    { date: '2025-05-20', value: 1.2 },
    { date: '2025-05-21', value: 1.4 },
    { date: '2025-05-22', value: 1.1 },
    { date: '2025-05-23', value: 0.9 },
    { date: '2025-05-24', value: 1.0 },
    { date: '2025-05-25', value: 0.8 },
    { date: '2025-05-26', value: 0.7 },
  ],
  throughput: [
    { date: '2025-05-20', value: 245 },
    { date: '2025-05-21', value: 312 },
    { date: '2025-05-22', value: 287 },
    { date: '2025-05-23', value: 356 },
    { date: '2025-05-24', value: 290 },
    { date: '2025-05-25', value: 402 },
    { date: '2025-05-26', value: 378 },
  ],
  qualityScore: [
    { date: '2025-05-20', value: 92 },
    { date: '2025-05-21', value: 94 },
    { date: '2025-05-22', value: 91 },
    { date: '2025-05-23', value: 95 },
    { date: '2025-05-24', value: 93 },
    { date: '2025-05-25', value: 96 },
    { date: '2025-05-26', value: 97 },
  ],
  resourceEfficiency: [
    { date: '2025-05-20', value: 78 },
    { date: '2025-05-21', value: 82 },
    { date: '2025-05-22', value: 80 },
    { date: '2025-05-23', value: 85 },
    { date: '2025-05-24', value: 83 },
    { date: '2025-05-25', value: 88 },
    { date: '2025-05-26', value: 90 },
  ]
};

const usageData = {
  featureUsage: [
    { name: 'Chat', usage: 42 },
    { name: 'File Management', usage: 18 },
    { name: 'Agent Orchestration', usage: 15 },
    { name: 'Memory Management', usage: 12 },
    { name: 'Dr. T Assistance', usage: 8 },
    { name: 'Analytics', usage: 5 },
  ],
  timeSaved: {
    today: 2.5,
    week: 14.3,
    month: 58.7,
    total: 247.2
  },
  userSatisfaction: 92,
  errorRate: 0.8
};

const AnalyticsInterface = () => {
  const [activeTab, setActiveTab] = useState('performance');
  const [timeRange, setTimeRange] = useState('week');
  
  // Simple line chart component
  const LineChart = ({ data, height = 100, color = '#3B82F6' }) => {
    const max = Math.max(...data.map(d => d.value)) * 1.1;
    const min = Math.min(...data.map(d => d.value)) * 0.9;
    const range = max - min;
    
    const points = data.map((d, i) => {
      const x = (i / (data.length - 1)) * 100;
      const y = 100 - ((d.value - min) / range) * 100;
      return `${x},${y}`;
    }).join(' ');
    
    return (
      <svg width="100%" height={height} className="overflow-visible">
        <polyline
          points={points}
          fill="none"
          stroke={color}
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        {data.map((d, i) => (
          <circle
            key={i}
            cx={`${(i / (data.length - 1)) * 100}%`}
            cy={`${100 - ((d.value - min) / range) * 100}%`}
            r="3"
            fill="white"
            stroke={color}
            strokeWidth="2"
          />
        ))}
      </svg>
    );
  };
  
  // Bar chart component
  const BarChart = ({ data, height = 150, color = '#3B82F6' }) => {
    const max = Math.max(...data.map(d => d.usage));
    
    return (
      <div className="flex items-end h-full space-x-2">
        {data.map((item, i) => (
          <div key={i} className="flex flex-col items-center flex-1">
            <div 
              className="w-full rounded-t-sm" 
              style={{ 
                height: `${(item.usage / max) * height}px`,
                backgroundColor: color
              }}
            />
            <span className="text-xs mt-1 text-gray-600 dark:text-gray-400 truncate w-full text-center">
              {item.name}
            </span>
          </div>
        ))}
      </div>
    );
  };
  
  // Circular progress component
  const CircularProgress = ({ value, size = 120, strokeWidth = 8, color = '#3B82F6' }) => {
    const radius = (size - strokeWidth) / 2;
    const circumference = radius * 2 * Math.PI;
    const offset = circumference - (value / 100) * circumference;
    
    return (
      <svg width={size} height={size} className="transform -rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="#E5E7EB"
          strokeWidth={strokeWidth}
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
        />
        <text
          x="50%"
          y="50%"
          dy=".3em"
          textAnchor="middle"
          fill="currentColor"
          className="text-lg font-bold transform rotate-90"
        >
          {value}%
        </text>
      </svg>
    );
  };

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold">Analytics Dashboard</h2>
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg p-1">
            <button 
              className={`px-3 py-1.5 text-sm rounded ${timeRange === 'day' ? 'bg-blue-500 text-white' : 'text-gray-600 dark:text-gray-300'}`}
              onClick={() => setTimeRange('day')}
            >
              Day
            </button>
            <button 
              className={`px-3 py-1.5 text-sm rounded ${timeRange === 'week' ? 'bg-blue-500 text-white' : 'text-gray-600 dark:text-gray-300'}`}
              onClick={() => setTimeRange('week')}
            >
              Week
            </button>
            <button 
              className={`px-3 py-1.5 text-sm rounded ${timeRange === 'month' ? 'bg-blue-500 text-white' : 'text-gray-600 dark:text-gray-300'}`}
              onClick={() => setTimeRange('month')}
            >
              Month
            </button>
            <button 
              className={`px-3 py-1.5 text-sm rounded ${timeRange === 'year' ? 'bg-blue-500 text-white' : 'text-gray-600 dark:text-gray-300'}`}
              onClick={() => setTimeRange('year')}
            >
              Year
            </button>
          </div>
          
          <button className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg">
            <Calendar className="w-5 h-5" />
          </button>
          
          <div className="relative">
            <button className="flex items-center space-x-2 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg px-3 py-2 text-sm">
              <Filter className="w-4 h-4" />
              <span>Filters</span>
              <ChevronDown className="w-4 h-4" />
            </button>
          </div>
          
          <button className="flex items-center space-x-2 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg px-3 py-2 text-sm">
            <Download className="w-4 h-4" />
            <span>Export</span>
          </button>
          
          <button className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg">
            <RefreshCw className="w-5 h-5" />
          </button>
        </div>
      </div>
      
      <div className="flex border-b border-gray-200 dark:border-gray-700 mb-6">
        <button 
          className={`px-4 py-2 font-medium text-sm ${activeTab === 'performance' ? 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-500' : 'text-gray-600 dark:text-gray-400'}`}
          onClick={() => setActiveTab('performance')}
        >
          Performance
        </button>
        <button 
          className={`px-4 py-2 font-medium text-sm ${activeTab === 'usage' ? 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-500' : 'text-gray-600 dark:text-gray-400'}`}
          onClick={() => setActiveTab('usage')}
        >
          Usage Analytics
        </button>
        <button 
          className={`px-4 py-2 font-medium text-sm ${activeTab === 'quality' ? 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-500' : 'text-gray-600 dark:text-gray-400'}`}
          onClick={() => setActiveTab('quality')}
        >
          Quality Metrics
        </button>
        <button 
          className={`px-4 py-2 font-medium text-sm ${activeTab === 'cost' ? 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-500' : 'text-gray-600 dark:text-gray-400'}`}
          onClick={() => setActiveTab('cost')}
        >
          Cost Optimization
        </button>
      </div>
      
      {activeTab === 'performance' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-medium text-sm">Response Time</h3>
                <Clock className="w-5 h-5 text-blue-500" />
              </div>
              <p className="text-2xl font-bold mb-1">{performanceData.responseTime[performanceData.responseTime.length - 1].value}s</p>
              <div className="flex items-center text-xs text-green-600">
                <TrendingUp className="w-3 h-3 mr-1" />
                <span>12% faster than last week</span>
              </div>
              <div className="mt-3 h-12">
                <LineChart data={performanceData.responseTime} height={40} color="#3B82F6" />
              </div>
            </div>
            
            <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-medium text-sm">Throughput</h3>
                <Zap className="w-5 h-5 text-purple-500" />
              </div>
              <p className="text-2xl font-bold mb-1">{performanceData.throughput[performanceData.throughput.length - 1].value}/hr</p>
              <div className="flex items-center text-xs text-green-600">
                <TrendingUp className="w-3 h-3 mr-1" />
                <span>8% higher than last week</span>
              </div>
              <div className="mt-3 h-12">
                <LineChart data={performanceData.throughput} height={40} color="#8B5CF6" />
              </div>
            </div>
            
            <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-medium text-sm">Quality Score</h3>
                <Award className="w-5 h-5 text-yellow-500" />
              </div>
              <p className="text-2xl font-bold mb-1">{performanceData.qualityScore[performanceData.qualityScore.length - 1].value}%</p>
              <div className="flex items-center text-xs text-green-600">
                <TrendingUp className="w-3 h-3 mr-1" />
                <span>3% improvement</span>
              </div>
              <div className="mt-3 h-12">
                <LineChart data={performanceData.qualityScore} height={40} color="#EAB308" />
              </div>
            </div>
            
            <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-medium text-sm">Resource Efficiency</h3>
                <BarChart3 className="w-5 h-5 text-green-500" />
              </div>
              <p className="text-2xl font-bold mb-1">{performanceData.resourceEfficiency[performanceData.resourceEfficiency.length - 1].value}%</p>
              <div className="flex items-center text-xs text-green-600">
                <TrendingUp className="w-3 h-3 mr-1" />
                <span>5% improvement</span>
              </div>
              <div className="mt-3 h-12">
                <LineChart data={performanceData.resourceEfficiency} height={40} color="#22C55E" />
              </div>
            </div>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
              <div className="p-4 border-b border-gray-200 dark:border-gray-700">
                <div className="flex items-center justify-between">
                  <h3 className="font-semibold">Response Time Trend</h3>
                  <div className="flex items-center space-x-2">
                    <button className="text-xs text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200">
                      By Agent
                    </button>
                    <button className="text-xs text-blue-600 dark:text-blue-400 hover:underline">
                      By Operation
                    </button>
                  </div>
                </div>
              </div>
              <div className="p-4">
                <div className="h-64">
                  <LineChart data={performanceData.responseTime} height={250} color="#3B82F6" />
                </div>
                <div className="flex justify-between mt-2 text-xs text-gray-500">
                  {performanceData.responseTime.map((d, i) => (
                    <span key={i}>{d.date.split('-')[2]}</span>
                  ))}
                </div>
              </div>
            </div>
            
            <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
              <div className="p-4 border-b border-gray-200 dark:border-gray-700">
                <div className="flex items-center justify-between">
                  <h3 className="font-semibold">Throughput Analysis</h3>
                  <div className="flex items-center space-x-2">
                    <button className="text-xs text-blue-600 dark:text-blue-400 hover:underline">
                      By Time
                    </button>
                    <button className="text-xs text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200">
                      By Feature
                    </button>
                  </div>
                </div>
              </div>
              <div className="p-4">
                <div className="h-64">
                  <LineChart data={performanceData.throughput} height={250} color="#8B5CF6" />
                </div>
                <div className="flex justify-between mt-2 text-xs text-gray-500">
                  {performanceData.throughput.map((d, i) => (
                    <span key={i}>{d.date.split('-')[2]}</span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
      
      {activeTab === 'usage' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-medium text-sm">Time Saved Today</h3>
                <Clock className="w-5 h-5 text-blue-500" />
              </div>
              <p className="text-2xl font-bold mb-1">{usageData.timeSaved.today} hours</p>
              <div className="flex items-center text-xs text-green-600">
                <TrendingUp className="w-3 h-3 mr-1" />
                <span>15% increase from yesterday</span>
              </div>
            </div>
            
            <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-medium text-sm">Weekly Time Saved</h3>
                <Clock className="w-5 h-5 text-purple-500" />
              </div>
              <p className="text-2xl font-bold mb-1">{usageData.timeSaved.week} hours</p>
              <div className="flex items-center text-xs text-green-600">
                <TrendingUp className="w-3 h-3 mr-1" />
                <span>10% increase from last week</span>
              </div>
            </div>
            
            <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-medium text-sm">User Satisfaction</h3>
                <Users className="w-5 h-5 text-green-500" />
              </div>
              <p className="text-2xl font-bold mb-1">{usageData.userSatisfaction}%</p>
              <div className="flex items-center text-xs text-green-600">
                <TrendingUp className="w-3 h-3 mr-1" />
                <span>5% increase from last month</span>
              </div>
            </div>
            
            <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-medium text-sm">Total Time Saved</h3>
                <Clock className="w-5 h-5 text-yellow-500" />
              </div>
              <p className="text-2xl font-bold mb-1">{usageData.timeSaved.total} hours</p>
              <div className="flex items-center text-xs text-gray-500">
                <span>Since installation</span>
              </div>
            </div>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
              <div className="p-4 border-b border-gray-200 dark:border-gray-700">
                <h3 className="font-semibold">Feature Usage Distribution</h3>
              </div>
              <div className="p-4">
                <div className="h-64">
                  <BarChart data={usageData.featureUsage} height={250} color="#3B82F6" />
                </div>
              </div>
            </div>
            
            <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
              <div className="p-4 border-b border-gray-200 dark:border-gray-700">
                <h3 className="font-semibold">User Satisfaction Score</h3>
              </div>
              <div className="p-4 flex flex-col items-center justify-center h-64">
                <CircularProgress value={usageData.userSatisfaction} size={180} color="#22C55E" />
                <div className="mt-4 text-center">
                  <p className="text-sm text-gray-600 dark:text-gray-400">Based on user feedback and interaction patterns</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
      
      {activeTab === 'quality' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-medium text-sm">Output Quality</h3>
                <Award className="w-5 h-5 text-yellow-500" />
              </div>
              <p className="text-2xl font-bold mb-1">{performanceData.qualityScore[performanceData.qualityScore.length - 1].value}%</p>
              <div className="flex items-center text-xs text-green-600">
                <TrendingUp className="w-3 h-3 mr-1" />
                <span>3% improvement</span>
              </div>
            </div>
            
            <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-medium text-sm">Error Rate</h3>
                <BarChart3 className="w-5 h-5 text-red-500" />
              </div>
              <p className="text-2xl font-bold mb-1">{usageData.errorRate}%</p>
              <div className="flex items-center text-xs text-green-600">
                <TrendingUp className="w-3 h-3 mr-1 transform rotate-180" />
                <span>0.2% decrease</span>
              </div>
            </div>
            
            <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-medium text-sm">Task Completion</h3>
                <Zap className="w-5 h-5 text-green-500" />
              </div>
              <p className="text-2xl font-bold mb-1">98.2%</p>
              <div className="flex items-center text-xs text-green-600">
                <TrendingUp className="w-3 h-3 mr-1" />
                <span>1.5% improvement</span>
              </div>
            </div>
            
            <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-medium text-sm">Factual Accuracy</h3>
                <Award className="w-5 h-5 text-blue-500" />
              </div>
              <p className="text-2xl font-bold mb-1">96.7%</p>
              <div className="flex items-center text-xs text-green-600">
                <TrendingUp className="w-3 h-3 mr-1" />
                <span>2.1% improvement</span>
              </div>
            </div>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
              <div className="p-4 border-b border-gray-200 dark:border-gray-700">
                <h3 className="font-semibold">Quality Score Trend</h3>
              </div>
              <div className="p-4">
                <div className="h-64">
                  <LineChart data={performanceData.qualityScore} height={250} color="#EAB308" />
                </div>
                <div className="flex justify-between mt-2 text-xs text-gray-500">
                  {performanceData.qualityScore.map((d, i) => (
                    <span key={i}>{d.date.split('-')[2]}</span>
                  ))}
                </div>
              </div>
            </div>
            
            <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
              <div className="p-4 border-b border-gray-200 dark:border-gray-700">
                <h3 className="font-semibold">Error Analysis</h3>
              </div>
              <div className="p-4">
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-sm">API Connection Errors</span>
                    <span className="text-sm font-medium">0.3%</span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div className="bg-red-500 h-2 rounded-full" style={{ width: '30%' }}></div>
                  </div>
                  
                  <div className="flex justify-between items-center">
                    <span className="text-sm">Data Processing Errors</span>
                    <span className="text-sm font-medium">0.2%</span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div className="bg-red-500 h-2 rounded-full" style={{ width: '20%' }}></div>
                  </div>
                  
                  <div className="flex justify-between items-center">
                    <span className="text-sm">User Input Errors</span>
                    <span className="text-sm font-medium">0.2%</span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div className="bg-red-500 h-2 rounded-full" style={{ width: '20%' }}></div>
                  </div>
                  
                  <div className="flex justify-between items-center">
                    <span className="text-sm">Agent Coordination Errors</span>
                    <span className="text-sm font-medium">0.1%</span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div className="bg-red-500 h-2 rounded-full" style={{ width: '10%' }}></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
      
      {activeTab === 'cost' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-medium text-sm">API Cost</h3>
                <BarChart3 className="w-5 h-5 text-blue-500" />
              </div>
              <p className="text-2xl font-bold mb-1">$12.47</p>
              <div className="flex items-center text-xs text-green-600">
                <TrendingUp className="w-3 h-3 mr-1 transform rotate-180" />
                <span>8% decrease from last week</span>
              </div>
            </div>
            
            <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-medium text-sm">Cost per Task</h3>
                <BarChart3 className="w-5 h-5 text-green-500" />
              </div>
              <p className="text-2xl font-bold mb-1">$0.023</p>
              <div className="flex items-center text-xs text-green-600">
                <TrendingUp className="w-3 h-3 mr-1 transform rotate-180" />
                <span>12% decrease</span>
              </div>
            </div>
            
            <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-medium text-sm">Resource Efficiency</h3>
                <Zap className="w-5 h-5 text-yellow-500" />
              </div>
              <p className="text-2xl font-bold mb-1">{performanceData.resourceEfficiency[performanceData.resourceEfficiency.length - 1].value}%</p>
              <div className="flex items-center text-xs text-green-600">
                <TrendingUp className="w-3 h-3 mr-1" />
                <span>5% improvement</span>
              </div>
            </div>
            
            <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-medium text-sm">Projected Monthly</h3>
                <BarChart3 className="w-5 h-5 text-purple-500" />
              </div>
              <p className="text-2xl font-bold mb-1">$87.32</p>
              <div className="flex items-center text-xs text-green-600">
                <TrendingUp className="w-3 h-3 mr-1 transform rotate-180" />
                <span>Under budget by 12%</span>
              </div>
            </div>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
              <div className="p-4 border-b border-gray-200 dark:border-gray-700">
                <h3 className="font-semibold">Cost Breakdown</h3>
              </div>
              <div className="p-4">
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-sm">LLM API Calls</span>
                    <span className="text-sm font-medium">$8.23</span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div className="bg-blue-500 h-2 rounded-full" style={{ width: '65%' }}></div>
                  </div>
                  
                  <div className="flex justify-between items-center">
                    <span className="text-sm">Vector Database</span>
                    <span className="text-sm font-medium">$2.15</span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div className="bg-purple-500 h-2 rounded-full" style={{ width: '17%' }}></div>
                  </div>
                  
                  <div className="flex justify-between items-center">
                    <span className="text-sm">Image Generation</span>
                    <span className="text-sm font-medium">$1.42</span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div className="bg-green-500 h-2 rounded-full" style={{ width: '11%' }}></div>
                  </div>
                  
                  <div className="flex justify-between items-center">
                    <span className="text-sm">Other Services</span>
                    <span className="text-sm font-medium">$0.67</span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div className="bg-yellow-500 h-2 rounded-full" style={{ width: '7%' }}></div>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
              <div className="p-4 border-b border-gray-200 dark:border-gray-700">
                <h3 className="font-semibold">Optimization Recommendations</h3>
              </div>
              <div className="p-4">
                <div className="space-y-4">
                  <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-3">
                    <div className="flex items-start space-x-3">
                      <div className="flex-shrink-0 mt-0.5">
                        <Zap className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                      </div>
                      <div>
                        <h4 className="text-sm font-medium text-blue-900 dark:text-blue-100">Optimize LLM Prompt Length</h4>
                        <p className="text-xs text-blue-700 dark:text-blue-300 mt-1">
                          Reducing average prompt length by 15% could save approximately $1.23/week
                        </p>
                      </div>
                    </div>
                  </div>
                  
                  <div className="bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-lg p-3">
                    <div className="flex items-start space-x-3">
                      <div className="flex-shrink-0 mt-0.5">
                        <Zap className="w-5 h-5 text-purple-600 dark:text-purple-400" />
                      </div>
                      <div>
                        <h4 className="text-sm font-medium text-purple-900 dark:text-purple-100">Implement Vector Cache</h4>
                        <p className="text-xs text-purple-700 dark:text-purple-300 mt-1">
                          Caching frequent vector searches could reduce database costs by up to 30%
                        </p>
                      </div>
                    </div>
                  </div>
                  
                  <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-3">
                    <div className="flex items-start space-x-3">
                      <div className="flex-shrink-0 mt-0.5">
                        <Zap className="w-5 h-5 text-green-600 dark:text-green-400" />
                      </div>
                      <div>
                        <h4 className="text-sm font-medium text-green-900 dark:text-green-100">Batch Processing</h4>
                        <p className="text-xs text-green-700 dark:text-green-300 mt-1">
                          Implementing batch processing for similar tasks could improve efficiency by 25%
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AnalyticsInterface;
