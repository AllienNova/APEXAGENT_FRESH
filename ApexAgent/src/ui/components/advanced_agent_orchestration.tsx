// Advanced Agent Orchestration Component
import React, { useState, useEffect } from 'react';
import { Bot, Settings, Play, Pause, Zap, Activity, Users, Clock, HardDrive, Wifi, Shield, ChevronDown, Search, Plus, Filter, MoreHorizontal, ArrowRight, ArrowLeft, Trash2, Edit, Save, RefreshCw, AlertTriangle, CheckCircle, XCircle, Sliders, Cpu, Database, Code, FileText, MessageCircle } from 'lucide-react';

// Mock data for demonstration
const agentTypes = [
  { id: 'planner', name: 'Planner Agent', description: 'Advanced reasoning and task decomposition', icon: 'Cpu', color: 'blue' },
  { id: 'execution', name: 'Execution Agent', description: '100+ tool integrations and task execution', icon: 'Zap', color: 'purple' },
  { id: 'verification', name: 'Verification Agent', description: 'Quality control and validation', icon: 'CheckCircle', color: 'green' },
  { id: 'security', name: 'Security Agent', description: 'Real-time threat monitoring and compliance', icon: 'Shield', color: 'red' },
  { id: 'optimization', name: 'Optimization Agent', description: 'Performance tuning and resource management', icon: 'Sliders', color: 'yellow' },
  { id: 'learning', name: 'Learning Agent', description: 'Federated learning and personalization', icon: 'Database', color: 'teal' },
  { id: 'research', name: 'Research Agent', description: 'Information gathering and analysis', icon: 'Search', color: 'indigo' },
  { id: 'code', name: 'Code Generator', description: 'Code generation and optimization', icon: 'Code', color: 'gray' },
  { id: 'content', name: 'Content Writer', description: 'Content creation and editing', icon: 'FileText', color: 'pink' },
  { id: 'conversation', name: 'Conversation Agent', description: 'Natural language interaction', icon: 'MessageCircle', color: 'orange' }
];

const agentInstances = [
  { id: 1, typeId: 'planner', name: 'Task Planner', status: 'active', cpu: 35, memory: 1.2, tasks: 2, priority: 'high' },
  { id: 2, typeId: 'execution', name: 'Tool Executor', status: 'active', cpu: 65, memory: 1.8, tasks: 3, priority: 'high' },
  { id: 3, typeId: 'verification', name: 'Quality Control', status: 'active', cpu: 25, memory: 0.8, tasks: 2, priority: 'medium' },
  { id: 4, typeId: 'research', name: 'Research Assistant', status: 'active', cpu: 45, memory: 1.5, tasks: 1, priority: 'medium' },
  { id: 5, typeId: 'code', name: 'Code Generator', status: 'idle', cpu: 5, memory: 0.3, tasks: 0, priority: 'low' },
  { id: 6, typeId: 'content', name: 'Content Writer', status: 'paused', cpu: 10, memory: 0.5, tasks: 1, priority: 'low' },
  { id: 7, typeId: 'security', name: 'Security Monitor', status: 'active', cpu: 20, memory: 0.7, tasks: 1, priority: 'high' }
];

const agentRelationships = [
  { source: 1, target: 2, type: 'delegates' },
  { source: 1, target: 3, type: 'validates' },
  { source: 2, target: 4, type: 'requests' },
  { source: 2, target: 5, type: 'delegates' },
  { source: 3, target: 6, type: 'requests' },
  { source: 7, target: 1, type: 'monitors' },
  { source: 7, target: 2, type: 'monitors' }
];

const agentTasks = [
  { id: 1, agentId: 1, name: 'Plan market analysis', status: 'in_progress', progress: 65, startTime: '10:23 AM', estimatedCompletion: '10:45 AM' },
  { id: 2, agentId: 1, name: 'Decompose report generation', status: 'queued', progress: 0, startTime: '-', estimatedCompletion: '11:15 AM' },
  { id: 3, agentId: 2, name: 'Execute data collection', status: 'in_progress', progress: 78, startTime: '10:25 AM', estimatedCompletion: '10:40 AM' },
  { id: 4, agentId: 2, name: 'Process market trends', status: 'in_progress', progress: 45, startTime: '10:30 AM', estimatedCompletion: '10:50 AM' },
  { id: 5, agentId: 2, name: 'Generate visualizations', status: 'queued', progress: 0, startTime: '-', estimatedCompletion: '11:05 AM' },
  { id: 6, agentId: 3, name: 'Validate data accuracy', status: 'in_progress', progress: 50, startTime: '10:28 AM', estimatedCompletion: '10:42 AM' },
  { id: 7, agentId: 3, name: 'Quality check report', status: 'queued', progress: 0, startTime: '-', estimatedCompletion: '11:20 AM' },
  { id: 8, agentId: 4, name: 'Research competitor data', status: 'in_progress', progress: 80, startTime: '10:26 AM', estimatedCompletion: '10:38 AM' },
  { id: 9, agentId: 6, name: 'Draft executive summary', status: 'paused', progress: 30, startTime: '10:29 AM', estimatedCompletion: 'On Hold' },
  { id: 10, agentId: 7, name: 'Monitor data access', status: 'in_progress', progress: 100, startTime: '10:20 AM', estimatedCompletion: 'Continuous' }
];

const AdvancedAgentOrchestration = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [showNewAgentModal, setShowNewAgentModal] = useState(false);
  const [filterStatus, setFilterStatus] = useState('all');
  
  const getAgentTypeById = (typeId) => {
    return agentTypes.find(type => type.id === typeId);
  };
  
  const getAgentIcon = (typeId) => {
    const type = getAgentTypeById(typeId);
    switch(type?.icon) {
      case 'Cpu': return <Cpu />;
      case 'Zap': return <Zap />;
      case 'CheckCircle': return <CheckCircle />;
      case 'Shield': return <Shield />;
      case 'Sliders': return <Sliders />;
      case 'Database': return <Database />;
      case 'Search': return <Search />;
      case 'Code': return <Code />;
      case 'FileText': return <FileText />;
      case 'MessageCircle': return <MessageCircle />;
      default: return <Bot />;
    }
  };
  
  const getAgentColorClass = (typeId) => {
    const type = getAgentTypeById(typeId);
    switch(type?.color) {
      case 'blue': return 'text-blue-500';
      case 'purple': return 'text-purple-500';
      case 'green': return 'text-green-500';
      case 'red': return 'text-red-500';
      case 'yellow': return 'text-yellow-500';
      case 'teal': return 'text-teal-500';
      case 'indigo': return 'text-indigo-500';
      case 'gray': return 'text-gray-500';
      case 'pink': return 'text-pink-500';
      case 'orange': return 'text-orange-500';
      default: return 'text-blue-500';
    }
  };
  
  const getStatusColorClass = (status) => {
    switch(status) {
      case 'active': return 'bg-green-500';
      case 'idle': return 'bg-gray-400';
      case 'paused': return 'bg-yellow-500';
      case 'error': return 'bg-red-500';
      default: return 'bg-gray-400';
    }
  };
  
  const getTaskStatusColorClass = (status) => {
    switch(status) {
      case 'completed': return 'bg-green-500';
      case 'in_progress': return 'bg-blue-500';
      case 'queued': return 'bg-yellow-500';
      case 'paused': return 'bg-gray-400';
      case 'failed': return 'bg-red-500';
      default: return 'bg-gray-400';
    }
  };
  
  const filteredAgents = filterStatus === 'all' 
    ? agentInstances 
    : agentInstances.filter(agent => agent.status === filterStatus);
  
  const AgentDashboard = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-4">
          <h2 className="text-xl font-semibold">Agent Orchestration</h2>
          <div className="flex items-center space-x-2 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg p-1">
            <button 
              className={`px-3 py-1.5 text-xs rounded ${filterStatus === 'all' ? 'bg-blue-500 text-white' : 'text-gray-600 dark:text-gray-300'}`}
              onClick={() => setFilterStatus('all')}
            >
              All
            </button>
            <button 
              className={`px-3 py-1.5 text-xs rounded ${filterStatus === 'active' ? 'bg-blue-500 text-white' : 'text-gray-600 dark:text-gray-300'}`}
              onClick={() => setFilterStatus('active')}
            >
              Active
            </button>
            <button 
              className={`px-3 py-1.5 text-xs rounded ${filterStatus === 'idle' ? 'bg-blue-500 text-white' : 'text-gray-600 dark:text-gray-300'}`}
              onClick={() => setFilterStatus('idle')}
            >
              Idle
            </button>
            <button 
              className={`px-3 py-1.5 text-xs rounded ${filterStatus === 'paused' ? 'bg-blue-500 text-white' : 'text-gray-600 dark:text-gray-300'}`}
              onClick={() => setFilterStatus('paused')}
            >
              Paused
            </button>
          </div>
        </div>
        <div className="flex items-center space-x-3">
          <div className="relative">
            <input 
              type="text" 
              placeholder="Search agents..."
              className="px-3 py-2 pr-8 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <Search className="w-4 h-4 absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
          </div>
          <button 
            className="px-3 py-2 text-sm bg-blue-500 text-white rounded-lg hover:bg-blue-600 flex items-center space-x-2"
            onClick={() => setShowNewAgentModal(true)}
          >
            <Plus className="w-4 h-4" />
            <span>New Agent</span>
          </button>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredAgents.map(agent => (
          <div 
            key={agent.id} 
            className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 p-4 hover:shadow-md transition-shadow cursor-pointer"
            onClick={() => setSelectedAgent(agent)}
          >
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-3">
                <div className={`w-10 h-10 rounded-lg bg-${getAgentTypeById(agent.typeId)?.color}-100 dark:bg-${getAgentTypeById(agent.typeId)?.color}-900/20 flex items-center justify-center ${getAgentColorClass(agent.typeId)}`}>
                  {getAgentIcon(agent.typeId)}
                </div>
                <div>
                  <h3 className="font-medium">{agent.name}</h3>
                  <div className="flex items-center space-x-2 text-xs text-gray-500 dark:text-gray-400">
                    <div className={`w-2 h-2 rounded-full ${getStatusColorClass(agent.status)}`}></div>
                    <span className="capitalize">{agent.status}</span>
                  </div>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                {agent.status === 'active' ? (
                  <button className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800">
                    <Pause className="w-4 h-4" />
                  </button>
                ) : (
                  <button className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800">
                    <Play className="w-4 h-4" />
                  </button>
                )}
                <button className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800">
                  <MoreHorizontal className="w-4 h-4" />
                </button>
              </div>
            </div>
            
            <div className="space-y-3">
              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-gray-500">CPU Usage</span>
                  <span>{agent.cpu}%</span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1.5">
                  <div className={`h-1.5 rounded-full ${agent.cpu > 70 ? 'bg-red-500' : agent.cpu > 40 ? 'bg-yellow-500' : 'bg-green-500'}`} style={{width: `${agent.cpu}%`}}></div>
                </div>
              </div>
              
              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-gray-500">Memory</span>
                  <span>{agent.memory} GB</span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1.5">
                  <div className="h-1.5 rounded-full bg-blue-500" style={{width: `${(agent.memory / 4) * 100}%`}}></div>
                </div>
              </div>
              
              <div className="flex justify-between text-xs text-gray-500">
                <span>Tasks: {agent.tasks}</span>
                <span>Priority: <span className={`${agent.priority === 'high' ? 'text-red-500' : agent.priority === 'medium' ? 'text-yellow-500' : 'text-green-500'}`}>{agent.priority}</span></span>
              </div>
            </div>
          </div>
        ))}
      </div>
      
      {/* Agent Tasks */}
      <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold">Active Agent Tasks</h3>
            <button className="text-xs text-blue-600 dark:text-blue-400 hover:underline">View All</button>
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 dark:bg-gray-800 text-xs text-gray-700 dark:text-gray-300">
              <tr>
                <th className="px-4 py-2 text-left">Task</th>
                <th className="px-4 py-2 text-left">Agent</th>
                <th className="px-4 py-2 text-left">Status</th>
                <th className="px-4 py-2 text-left">Progress</th>
                <th className="px-4 py-2 text-left">Started</th>
                <th className="px-4 py-2 text-left">Est. Completion</th>
                <th className="px-4 py-2 text-left">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
              {agentTasks.filter(task => task.status === 'in_progress').map(task => {
                const agent = agentInstances.find(a => a.id === task.agentId);
                return (
                  <tr key={task.id} className="text-sm">
                    <td className="px-4 py-3">{task.name}</td>
                    <td className="px-4 py-3">
                      <div className="flex items-center space-x-2">
                        <div className={`w-2 h-2 rounded-full ${getStatusColorClass(agent.status)}`}></div>
                        <span>{agent.name}</span>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center space-x-2">
                        <div className={`w-2 h-2 rounded-full ${getTaskStatusColorClass(task.status)}`}></div>
                        <span className="capitalize">{task.status.replace('_', ' ')}</span>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center space-x-2">
                        <div className="w-24 bg-gray-200 dark:bg-gray-700 rounded-full h-1.5">
                          <div className={`h-1.5 rounded-full ${task.status === 'in_progress' ? 'bg-blue-500' : task.status === 'completed' ? 'bg-green-500' : task.status === 'paused' ? 'bg-yellow-500' : 'bg-gray-400'}`} style={{width: `${task.progress}%`}}></div>
                        </div>
                        <span className="text-xs text-gray-500">{task.progress}%</span>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-gray-500">{task.startTime}</td>
                    <td className="px-4 py-3 text-gray-500">{task.estimatedCompletion}</td>
                    <td className="px-4 py-3">
                      <div className="flex items-center space-x-2">
                        <button className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800">
                          <Pause className="w-4 h-4" />
                        </button>
                        <button className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800">
                          <MoreHorizontal className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
  
  const AgentOrchestrationView = () => {
    // This would be a more sophisticated visualization in a real implementation
    // Here we're creating a simplified version for demonstration
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold">Agent Orchestration Visualization</h2>
          <div className="flex items-center space-x-3">
            <button className="px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 flex items-center space-x-2">
              <RefreshCw className="w-4 h-4" />
              <span>Refresh</span>
            </button>
            <button className="px-3 py-2 text-sm bg-blue-500 text-white rounded-lg hover:bg-blue-600 flex items-center space-x-2">
              <Settings className="w-4 h-4" />
              <span>Configure</span>
            </button>
          </div>
        </div>
        
        <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
          <div className="flex flex-col items-center">
            <div className="relative w-full h-[400px] bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
              {/* This is a simplified visualization - in a real implementation, this would be a proper graph visualization */}
              <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
                <div className="w-16 h-16 rounded-full bg-blue-100 dark:bg-blue-900/20 flex items-center justify-center text-blue-500 border-2 border-blue-500">
                  <Cpu className="w-8 h-8" />
                </div>
                <div className="text-center mt-2 font-medium text-sm">Planner</div>
              </div>
              
              <div className="absolute top-1/4 left-1/4">
                <div className="w-14 h-14 rounded-full bg-purple-100 dark:bg-purple-900/20 flex items-center justify-center text-purple-500 border-2 border-purple-500">
                  <Zap className="w-7 h-7" />
                </div>
                <div className="text-center mt-2 font-medium text-sm">Execution</div>
              </div>
              
              <div className="absolute top-1/4 right-1/4">
                <div className="w-14 h-14 rounded-full bg-green-100 dark:bg-green-900/20 flex items-center justify-center text-green-500 border-2 border-green-500">
                  <CheckCircle className="w-7 h-7" />
                </div>
                <div className="text-center mt-2 font-medium text-sm">Verification</div>
              </div>
              
              <div className="absolute bottom-1/4 left-1/4">
                <div className="w-14 h-14 rounded-full bg-indigo-100 dark:bg-indigo-900/20 flex items-center justify-center text-indigo-500 border-2 border-indigo-500">
                  <Search className="w-7 h-7" />
                </div>
                <div className="text-center mt-2 font-medium text-sm">Research</div>
              </div>
              
              <div className="absolute bottom-1/4 right-1/4">
                <div className="w-14 h-14 rounded-full bg-gray-100 dark:bg-gray-700 flex items-center justify-center text-gray-500 border-2 border-gray-500">
                  <Code className="w-7 h-7" />
                </div>
                <div className="text-center mt-2 font-medium text-sm">Code</div>
              </div>
              
              <div className="absolute top-10 right-10">
                <div className="w-14 h-14 rounded-full bg-red-100 dark:bg-red-900/20 flex items-center justify-center text-red-500 border-2 border-red-500">
                  <Shield className="w-7 h-7" />
                </div>
                <div className="text-center mt-2 font-medium text-sm">Security</div>
              </div>
              
              <div className="absolute bottom-10 left-10">
                <div className="w-14 h-14 rounded-full bg-pink-100 dark:bg-pink-900/20 flex items-center justify-center text-pink-500 border-2 border-pink-500">
                  <FileText className="w-7 h-7" />
                </div>
                <div className="text-center mt-2 font-medium text-sm">Content</div>
              </div>
              
              {/* Connection lines would be SVG paths in a real implementation */}
              <svg className="absolute inset-0 w-full h-full pointer-events-none" style={{ zIndex: 0 }}>
                <path d="M 200,200 L 150,100" stroke="#3B82F6" strokeWidth="2" fill="none" strokeDasharray="5,5" />
                <path d="M 200,200 L 350,100" stroke="#3B82F6" strokeWidth="2" fill="none" strokeDasharray="5,5" />
                <path d="M 200,200 L 150,300" stroke="#3B82F6" strokeWidth="2" fill="none" strokeDasharray="5,5" />
                <path d="M 200,200 L 350,300" stroke="#3B82F6" strokeWidth="2" fill="none" strokeDasharray="5,5" />
                <path d="M 150,100 L 150,300" stroke="#8B5CF6" strokeWidth="2" fill="none" />
                <path d="M 150,100 L 350,300" stroke="#8B5CF6" strokeWidth="2" fill="none" />
                <path d="M 350,100 L 100,350" stroke="#10B981" strokeWidth="2" fill="none" />
                <path d="M 350,10 L 200,200" stroke="#EF4444" strokeWidth="2" fill="none" />
                <path d="M 350,10 L 150,100" stroke="#EF4444" strokeWidth="2" fill="none" />
              </svg>
            </div>
            
            <div className="mt-6 flex items-center space-x-6">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-0.5 bg-blue-500"></div>
                <span className="text-xs text-gray-500">Planning</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-0.5 bg-purple-500"></div>
                <span className="text-xs text-gray-500">Execution</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-0.5 bg-green-500"></div>
                <span className="text-xs text-gray-500">Verification</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-0.5 bg-red-500"></div>
                <span className="text-xs text-gray-500">Security</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-0.5 bg-gray-500 stroke-dasharray-2"></div>
                <span className="text-xs text-gray-500">Optional</span>
              </div>
            </div>
          </div>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
            <div className="p-4 border-b border-gray-200 dark:border-gray-700">
              <h3 className="font-semibold">Agent Relationships</h3>
            </div>
            <div className="p-4">
              <div className="space-y-3">
                {agentRelationships.map((rel, index) => {
                  const source = agentInstances.find(a => a.id === rel.source);
                  const target = agentInstances.find(a => a.id === rel.target);
                  return (
                    <div key={index} className="flex items-center space-x-3">
                      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-100 dark:bg-gray-800 flex items-center justify-center">
                        <span className="text-xs font-medium">{source.id}</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className="text-sm">{source.name}</span>
                        <ArrowRight className="w-4 h-4 text-gray-400" />
                        <span className="text-xs px-2 py-1 bg-gray-100 dark:bg-gray-800 rounded-full">{rel.type}</span>
                        <ArrowRight className="w-4 h-4 text-gray-400" />
                        <span className="text-sm">{target.name}</span>
                      </div>
                      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-100 dark:bg-gray-800 flex items-center justify-center">
                        <span className="text-xs font-medium">{target.id}</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
          
          <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
            <div className="p-4 border-b border-gray-200 dark:border-gray-700">
              <h3 className="font-semibold">Orchestration Settings</h3>
            </div>
            <div className="p-4">
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Task Routing Strategy</label>
                  <select className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800">
                    <option>Automatic (AI-driven)</option>
                    <option>Round Robin</option>
                    <option>Priority-based</option>
                    <option>Capability-based</option>
                    <option>Load-balanced</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium mb-1">Conflict Resolution</label>
                  <select className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800">
                    <option>Consensus-based</option>
                    <option>Priority Override</option>
                    <option>Human Intervention</option>
                    <option>Majority Vote</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium mb-1">Resource Allocation</label>
                  <select className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800">
                    <option>Dynamic (Adaptive)</option>
                    <option>Fixed Allocation</option>
                    <option>Priority-based</option>
                    <option>Equal Distribution</option>
                  </select>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-sm">Enable Self-Healing</span>
                  <div className="relative inline-block w-10 mr-2 align-middle select-none">
                    <input type="checkbox" name="toggle" id="toggle" className="toggle-checkbox absolute block w-6 h-6 rounded-full bg-white border-4 border-gray-300 appearance-none cursor-pointer" defaultChecked />
                    <label htmlFor="toggle" className="toggle-label block overflow-hidden h-6 rounded-full bg-gray-300 cursor-pointer"></label>
                  </div>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-sm">Autonomous Mode</span>
                  <div className="relative inline-block w-10 mr-2 align-middle select-none">
                    <input type="checkbox" name="toggle2" id="toggle2" className="toggle-checkbox absolute block w-6 h-6 rounded-full bg-white border-4 border-gray-300 appearance-none cursor-pointer" defaultChecked />
                    <label htmlFor="toggle2" className="toggle-label block overflow-hidden h-6 rounded-full bg-gray-300 cursor-pointer"></label>
                  </div>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-sm">Human Oversight</span>
                  <div className="relative inline-block w-10 mr-2 align-middle select-none">
                    <input type="checkbox" name="toggle3" id="toggle3" className="toggle-checkbox absolute block w-6 h-6 rounded-full bg-white border-4 border-gray-300 appearance-none cursor-pointer" defaultChecked />
                    <label htmlFor="toggle3" className="toggle-label block overflow-hidden h-6 rounded-full bg-gray-300 cursor-pointer"></label>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };
  
  const AgentConfiguration = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold">Agent Configuration</h2>
        <div className="flex items-center space-x-3">
          <button className="px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 flex items-center space-x-2">
            <RefreshCw className="w-4 h-4" />
            <span>Reset Defaults</span>
          </button>
          <button className="px-3 py-2 text-sm bg-blue-500 text-white rounded-lg hover:bg-blue-600 flex items-center space-x-2">
            <Save className="w-4 h-4" />
            <span>Save Configuration</span>
          </button>
        </div>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
            <div className="p-4 border-b border-gray-200 dark:border-gray-700">
              <h3 className="font-semibold">Agent Types</h3>
            </div>
            <div className="p-4">
              <div className="space-y-3">
                {agentTypes.map(type => (
                  <div key={type.id} className="flex items-center space-x-3 p-2 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer">
                    <div className={`w-8 h-8 rounded-lg bg-${type.color}-100 dark:bg-${type.color}-900/20 flex items-center justify-center ${getAgentColorClass(type.id)}`}>
                      {getAgentIcon(type.id)}
                    </div>
                    <div>
                      <h4 className="text-sm font-medium">{type.name}</h4>
                      <p className="text-xs text-gray-500">{type.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
        
        <div className="lg:col-span-2">
          <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
            <div className="p-4 border-b border-gray-200 dark:border-gray-700">
              <h3 className="font-semibold">Global Agent Settings</h3>
            </div>
            <div className="p-4">
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Default Resource Allocation</label>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs text-gray-500 mb-1">CPU Limit</label>
                      <select className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800">
                        <option>Adaptive</option>
                        <option>25%</option>
                        <option>50%</option>
                        <option>75%</option>
                        <option>100%</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-xs text-gray-500 mb-1">Memory Limit</label>
                      <select className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800">
                        <option>Adaptive</option>
                        <option>1 GB</option>
                        <option>2 GB</option>
                        <option>4 GB</option>
                        <option>8 GB</option>
                      </select>
                    </div>
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium mb-1">Agent Communication</label>
                  <select className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800">
                    <option>Direct (Point-to-Point)</option>
                    <option>Broker-based</option>
                    <option>Publish-Subscribe</option>
                    <option>Hybrid</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium mb-1">Agent Lifecycle Management</label>
                  <select className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800">
                    <option>Dynamic (On-demand)</option>
                    <option>Static (Pre-allocated)</option>
                    <option>Hybrid</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium mb-1">Default Priority</label>
                  <select className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800">
                    <option>Medium</option>
                    <option>High</option>
                    <option>Low</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium mb-1">Monitoring Frequency</label>
                  <select className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800">
                    <option>Real-time</option>
                    <option>Every 5 seconds</option>
                    <option>Every 15 seconds</option>
                    <option>Every 30 seconds</option>
                    <option>Every minute</option>
                  </select>
                </div>
                
                <div className="pt-2">
                  <h4 className="text-sm font-medium mb-3">Advanced Settings</h4>
                  
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Auto-scaling</span>
                      <div className="relative inline-block w-10 mr-2 align-middle select-none">
                        <input type="checkbox" name="toggle4" id="toggle4" className="toggle-checkbox absolute block w-6 h-6 rounded-full bg-white border-4 border-gray-300 appearance-none cursor-pointer" defaultChecked />
                        <label htmlFor="toggle4" className="toggle-label block overflow-hidden h-6 rounded-full bg-gray-300 cursor-pointer"></label>
                      </div>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Fault Tolerance</span>
                      <div className="relative inline-block w-10 mr-2 align-middle select-none">
                        <input type="checkbox" name="toggle5" id="toggle5" className="toggle-checkbox absolute block w-6 h-6 rounded-full bg-white border-4 border-gray-300 appearance-none cursor-pointer" defaultChecked />
                        <label htmlFor="toggle5" className="toggle-label block overflow-hidden h-6 rounded-full bg-gray-300 cursor-pointer"></label>
                      </div>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Performance Optimization</span>
                      <div className="relative inline-block w-10 mr-2 align-middle select-none">
                        <input type="checkbox" name="toggle6" id="toggle6" className="toggle-checkbox absolute block w-6 h-6 rounded-full bg-white border-4 border-gray-300 appearance-none cursor-pointer" defaultChecked />
                        <label htmlFor="toggle6" className="toggle-label block overflow-hidden h-6 rounded-full bg-gray-300 cursor-pointer"></label>
                      </div>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Continuous Learning</span>
                      <div className="relative inline-block w-10 mr-2 align-middle select-none">
                        <input type="checkbox" name="toggle7" id="toggle7" className="toggle-checkbox absolute block w-6 h-6 rounded-full bg-white border-4 border-gray-300 appearance-none cursor-pointer" defaultChecked />
                        <label htmlFor="toggle7" className="toggle-label block overflow-hidden h-6 rounded-full bg-gray-300 cursor-pointer"></label>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
  
  const AgentTraining = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold">Agent Training & Specialization</h2>
        <button className="px-3 py-2 text-sm bg-blue-500 text-white rounded-lg hover:bg-blue-600 flex items-center space-x-2">
          <Zap className="w-4 h-4" />
          <span>Start Training Session</span>
        </button>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
            <div className="p-4 border-b border-gray-200 dark:border-gray-700">
              <h3 className="font-semibold">Training Metrics</h3>
            </div>
            <div className="p-4">
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span>Overall Performance</span>
                    <span className="font-medium">92%</span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div className="h-2 rounded-full bg-green-500" style={{width: '92%'}}></div>
                  </div>
                </div>
                
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span>Task Accuracy</span>
                    <span className="font-medium">88%</span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div className="h-2 rounded-full bg-blue-500" style={{width: '88%'}}></div>
                  </div>
                </div>
                
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span>Adaptation Rate</span>
                    <span className="font-medium">76%</span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div className="h-2 rounded-full bg-yellow-500" style={{width: '76%'}}></div>
                  </div>
                </div>
                
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span>Learning Efficiency</span>
                    <span className="font-medium">94%</span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div className="h-2 rounded-full bg-purple-500" style={{width: '94%'}}></div>
                  </div>
                </div>
              </div>
              
              <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                <h4 className="text-sm font-medium mb-3">Training History</h4>
                <div className="space-y-2">
                  <div className="flex justify-between text-xs">
                    <span>Last Training Session</span>
                    <span>2 days ago</span>
                  </div>
                  <div className="flex justify-between text-xs">
                    <span>Total Training Hours</span>
                    <span>127.5</span>
                  </div>
                  <div className="flex justify-between text-xs">
                    <span>Training Iterations</span>
                    <span>42</span>
                  </div>
                  <div className="flex justify-between text-xs">
                    <span>Performance Improvement</span>
                    <span className="text-green-500">+12%</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div className="lg:col-span-2">
          <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
            <div className="p-4 border-b border-gray-200 dark:border-gray-700">
              <h3 className="font-semibold">Agent Specialization</h3>
            </div>
            <div className="p-4">
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                    <div className="flex items-center space-x-3 mb-3">
                      <div className="w-8 h-8 rounded-lg bg-blue-100 dark:bg-blue-900/20 flex items-center justify-center text-blue-500">
                        <Cpu className="w-5 h-5" />
                      </div>
                      <div>
                        <h4 className="font-medium">Planner Agent</h4>
                        <div className="flex items-center space-x-1 text-xs text-gray-500">
                          <span>Specialization:</span>
                          <span className="font-medium">Advanced</span>
                        </div>
                      </div>
                    </div>
                    
                    <div className="space-y-2">
                      <div>
                        <div className="flex justify-between text-xs mb-1">
                          <span>Task Decomposition</span>
                          <span>95%</span>
                        </div>
                        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1.5">
                          <div className="h-1.5 rounded-full bg-blue-500" style={{width: '95%'}}></div>
                        </div>
                      </div>
                      
                      <div>
                        <div className="flex justify-between text-xs mb-1">
                          <span>Strategic Planning</span>
                          <span>92%</span>
                        </div>
                        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1.5">
                          <div className="h-1.5 rounded-full bg-blue-500" style={{width: '92%'}}></div>
                        </div>
                      </div>
                      
                      <div>
                        <div className="flex justify-between text-xs mb-1">
                          <span>Resource Allocation</span>
                          <span>88%</span>
                        </div>
                        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1.5">
                          <div className="h-1.5 rounded-full bg-blue-500" style={{width: '88%'}}></div>
                        </div>
                      </div>
                    </div>
                    
                    <div className="mt-3 flex items-center space-x-2">
                      <button className="px-2 py-1 text-xs bg-blue-500 text-white rounded hover:bg-blue-600">
                        Train
                      </button>
                      <button className="px-2 py-1 text-xs border border-gray-300 dark:border-gray-600 rounded hover:bg-gray-50 dark:hover:bg-gray-800">
                        Configure
                      </button>
                    </div>
                  </div>
                  
                  <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                    <div className="flex items-center space-x-3 mb-3">
                      <div className="w-8 h-8 rounded-lg bg-purple-100 dark:bg-purple-900/20 flex items-center justify-center text-purple-500">
                        <Zap className="w-5 h-5" />
                      </div>
                      <div>
                        <h4 className="font-medium">Execution Agent</h4>
                        <div className="flex items-center space-x-1 text-xs text-gray-500">
                          <span>Specialization:</span>
                          <span className="font-medium">Expert</span>
                        </div>
                      </div>
                    </div>
                    
                    <div className="space-y-2">
                      <div>
                        <div className="flex justify-between text-xs mb-1">
                          <span>Tool Integration</span>
                          <span>98%</span>
                        </div>
                        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1.5">
                          <div className="h-1.5 rounded-full bg-purple-500" style={{width: '98%'}}></div>
                        </div>
                      </div>
                      
                      <div>
                        <div className="flex justify-between text-xs mb-1">
                          <span>Task Execution</span>
                          <span>96%</span>
                        </div>
                        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1.5">
                          <div className="h-1.5 rounded-full bg-purple-500" style={{width: '96%'}}></div>
                        </div>
                      </div>
                      
                      <div>
                        <div className="flex justify-between text-xs mb-1">
                          <span>Error Handling</span>
                          <span>90%</span>
                        </div>
                        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1.5">
                          <div className="h-1.5 rounded-full bg-purple-500" style={{width: '90%'}}></div>
                        </div>
                      </div>
                    </div>
                    
                    <div className="mt-3 flex items-center space-x-2">
                      <button className="px-2 py-1 text-xs bg-purple-500 text-white rounded hover:bg-purple-600">
                        Train
                      </button>
                      <button className="px-2 py-1 text-xs border border-gray-300 dark:border-gray-600 rounded hover:bg-gray-50 dark:hover:bg-gray-800">
                        Configure
                      </button>
                    </div>
                  </div>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                    <div className="flex items-center space-x-3 mb-3">
                      <div className="w-8 h-8 rounded-lg bg-green-100 dark:bg-green-900/20 flex items-center justify-center text-green-500">
                        <CheckCircle className="w-5 h-5" />
                      </div>
                      <div>
                        <h4 className="font-medium">Verification Agent</h4>
                        <div className="flex items-center space-x-1 text-xs text-gray-500">
                          <span>Specialization:</span>
                          <span className="font-medium">Intermediate</span>
                        </div>
                      </div>
                    </div>
                    
                    <div className="space-y-2">
                      <div>
                        <div className="flex justify-between text-xs mb-1">
                          <span>Quality Control</span>
                          <span>85%</span>
                        </div>
                        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1.5">
                          <div className="h-1.5 rounded-full bg-green-500" style={{width: '85%'}}></div>
                        </div>
                      </div>
                      
                      <div>
                        <div className="flex justify-between text-xs mb-1">
                          <span>Validation</span>
                          <span>82%</span>
                        </div>
                        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1.5">
                          <div className="h-1.5 rounded-full bg-green-500" style={{width: '82%'}}></div>
                        </div>
                      </div>
                      
                      <div>
                        <div className="flex justify-between text-xs mb-1">
                          <span>Error Detection</span>
                          <span>88%</span>
                        </div>
                        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1.5">
                          <div className="h-1.5 rounded-full bg-green-500" style={{width: '88%'}}></div>
                        </div>
                      </div>
                    </div>
                    
                    <div className="mt-3 flex items-center space-x-2">
                      <button className="px-2 py-1 text-xs bg-green-500 text-white rounded hover:bg-green-600">
                        Train
                      </button>
                      <button className="px-2 py-1 text-xs border border-gray-300 dark:border-gray-600 rounded hover:bg-gray-50 dark:hover:bg-gray-800">
                        Configure
                      </button>
                    </div>
                  </div>
                  
                  <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                    <div className="flex items-center space-x-3 mb-3">
                      <div className="w-8 h-8 rounded-lg bg-red-100 dark:bg-red-900/20 flex items-center justify-center text-red-500">
                        <Shield className="w-5 h-5" />
                      </div>
                      <div>
                        <h4 className="font-medium">Security Agent</h4>
                        <div className="flex items-center space-x-1 text-xs text-gray-500">
                          <span>Specialization:</span>
                          <span className="font-medium">Advanced</span>
                        </div>
                      </div>
                    </div>
                    
                    <div className="space-y-2">
                      <div>
                        <div className="flex justify-between text-xs mb-1">
                          <span>Threat Detection</span>
                          <span>94%</span>
                        </div>
                        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1.5">
                          <div className="h-1.5 rounded-full bg-red-500" style={{width: '94%'}}></div>
                        </div>
                      </div>
                      
                      <div>
                        <div className="flex justify-between text-xs mb-1">
                          <span>Compliance Monitoring</span>
                          <span>91%</span>
                        </div>
                        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1.5">
                          <div className="h-1.5 rounded-full bg-red-500" style={{width: '91%'}}></div>
                        </div>
                      </div>
                      
                      <div>
                        <div className="flex justify-between text-xs mb-1">
                          <span>Access Control</span>
                          <span>96%</span>
                        </div>
                        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1.5">
                          <div className="h-1.5 rounded-full bg-red-500" style={{width: '96%'}}></div>
                        </div>
                      </div>
                    </div>
                    
                    <div className="mt-3 flex items-center space-x-2">
                      <button className="px-2 py-1 text-xs bg-red-500 text-white rounded hover:bg-red-600">
                        Train
                      </button>
                      <button className="px-2 py-1 text-xs border border-gray-300 dark:border-gray-600 rounded hover:bg-gray-50 dark:hover:bg-gray-800">
                        Configure
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
  
  // Modal for creating a new agent
  const NewAgentModal = () => (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-900 rounded-lg w-full max-w-md p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">Create New Agent</h3>
          <button 
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            onClick={() => setShowNewAgentModal(false)}
          >
            <XCircle className="w-5 h-5" />
          </button>
        </div>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Agent Name</label>
            <input 
              type="text" 
              placeholder="Enter agent name"
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">Agent Type</label>
            <select className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800">
              {agentTypes.map(type => (
                <option key={type.id} value={type.id}>{type.name}</option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">Priority</label>
            <select className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800">
              <option value="high">High</option>
              <option value="medium" selected>Medium</option>
              <option value="low">Low</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">Resource Allocation</label>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs text-gray-500 mb-1">CPU Limit</label>
                <select className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800">
                  <option>Adaptive</option>
                  <option>25%</option>
                  <option>50%</option>
                  <option>75%</option>
                  <option>100%</option>
                </select>
              </div>
              <div>
                <label className="block text-xs text-gray-500 mb-1">Memory Limit</label>
                <select className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800">
                  <option>Adaptive</option>
                  <option>1 GB</option>
                  <option>2 GB</option>
                  <option>4 GB</option>
                  <option>8 GB</option>
                </select>
              </div>
            </div>
          </div>
          
          <div className="flex items-center space-x-2 pt-2">
            <input type="checkbox" id="autostart" className="rounded border-gray-300 text-blue-600 focus:ring-blue-500" />
            <label htmlFor="autostart" className="text-sm">Auto-start agent</label>
          </div>
          
          <div className="flex items-center space-x-2">
            <input type="checkbox" id="training" className="rounded border-gray-300 text-blue-600 focus:ring-blue-500" />
            <label htmlFor="training" className="text-sm">Run initial training</label>
          </div>
        </div>
        
        <div className="flex items-center justify-end space-x-3 mt-6">
          <button 
            className="px-4 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800"
            onClick={() => setShowNewAgentModal(false)}
          >
            Cancel
          </button>
          <button 
            className="px-4 py-2 text-sm bg-blue-500 text-white rounded-lg hover:bg-blue-600"
            onClick={() => setShowNewAgentModal(false)}
          >
            Create Agent
          </button>
        </div>
      </div>
    </div>
  );
  
  // Agent detail view when an agent is selected
  const AgentDetailView = () => {
    const agent = selectedAgent;
    const agentType = getAgentTypeById(agent.typeId);
    const agentTasks = agentTasks.filter(task => task.agentId === agent.id);
    
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white dark:bg-gray-900 rounded-lg w-full max-w-4xl p-6 max-h-[90vh] overflow-y-auto">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-3">
              <div className={`w-10 h-10 rounded-lg bg-${agentType.color}-100 dark:bg-${agentType.color}-900/20 flex items-center justify-center ${getAgentColorClass(agent.typeId)}`}>
                {getAgentIcon(agent.typeId)}
              </div>
              <div>
                <h2 className="text-xl font-semibold">{agent.name}</h2>
                <div className="flex items-center space-x-2 text-sm text-gray-500 dark:text-gray-400">
                  <div className={`w-2 h-2 rounded-full ${getStatusColorClass(agent.status)}`}></div>
                  <span className="capitalize">{agent.status}</span>
                  <span>•</span>
                  <span>{agentType.name}</span>
                </div>
              </div>
            </div>
            <button 
              className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              onClick={() => setSelectedAgent(null)}
            >
              <XCircle className="w-6 h-6" />
            </button>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
              <h3 className="font-medium text-sm mb-3">Resource Usage</h3>
              <div className="space-y-3">
                <div>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-gray-500">CPU Usage</span>
                    <span>{agent.cpu}%</span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1.5">
                    <div className={`h-1.5 rounded-full ${agent.cpu > 70 ? 'bg-red-500' : agent.cpu > 40 ? 'bg-yellow-500' : 'bg-green-500'}`} style={{width: `${agent.cpu}%`}}></div>
                  </div>
                </div>
                
                <div>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-gray-500">Memory</span>
                    <span>{agent.memory} GB</span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1.5">
                    <div className="h-1.5 rounded-full bg-blue-500" style={{width: `${(agent.memory / 4) * 100}%`}}></div>
                  </div>
                </div>
                
                <div>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-gray-500">Network I/O</span>
                    <span>2.3 MB/s</span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1.5">
                    <div className="h-1.5 rounded-full bg-purple-500" style={{width: '45%'}}></div>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
              <h3 className="font-medium text-sm mb-3">Performance</h3>
              <div className="space-y-3">
                <div>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-gray-500">Task Success Rate</span>
                    <span>94%</span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1.5">
                    <div className="h-1.5 rounded-full bg-green-500" style={{width: '94%'}}></div>
                  </div>
                </div>
                
                <div>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-gray-500">Avg. Response Time</span>
                    <span>1.2s</span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1.5">
                    <div className="h-1.5 rounded-full bg-blue-500" style={{width: '85%'}}></div>
                  </div>
                </div>
                
                <div>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-gray-500">Error Rate</span>
                    <span>0.8%</span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1.5">
                    <div className="h-1.5 rounded-full bg-red-500" style={{width: '8%'}}></div>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
              <h3 className="font-medium text-sm mb-3">Configuration</h3>
              <div className="space-y-2 text-xs">
                <div className="flex justify-between">
                  <span className="text-gray-500">Priority</span>
                  <span className={`${agent.priority === 'high' ? 'text-red-500' : agent.priority === 'medium' ? 'text-yellow-500' : 'text-green-500'} font-medium capitalize`}>{agent.priority}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Auto-scaling</span>
                  <span className="font-medium">Enabled</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Fault Tolerance</span>
                  <span className="font-medium">Enabled</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Learning Rate</span>
                  <span className="font-medium">0.05</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Specialization</span>
                  <span className="font-medium">Advanced</span>
                </div>
              </div>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
              <div className="p-4 border-b border-gray-200 dark:border-gray-700">
                <h3 className="font-medium">Current Tasks</h3>
              </div>
              <div className="p-4">
                {agentTasks.length > 0 ? (
                  <div className="space-y-3">
                    {agentTasks.map(task => (
                      <div key={task.id} className="border border-gray-200 dark:border-gray-700 rounded-lg p-3">
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center space-x-2">
                            <div className={`w-2 h-2 rounded-full ${getTaskStatusColorClass(task.status)}`}></div>
                            <h4 className="font-medium text-sm">{task.name}</h4>
                          </div>
                          <div className="flex items-center space-x-1">
                            <button className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700">
                              <Pause className="w-4 h-4" />
                            </button>
                            <button className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700">
                              <MoreHorizontal className="w-4 h-4" />
                            </button>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2 mb-2">
                          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1.5">
                            <div className={`h-1.5 rounded-full ${task.status === 'in_progress' ? 'bg-blue-500' : task.status === 'completed' ? 'bg-green-500' : task.status === 'paused' ? 'bg-yellow-500' : 'bg-gray-400'}`} style={{width: `${task.progress}%`}}></div>
                          </div>
                          <span className="text-xs text-gray-500">{task.progress}%</span>
                        </div>
                        <div className="flex justify-between text-xs text-gray-500">
                          <span>Started: {task.startTime}</span>
                          <span>Est. Completion: {task.estimatedCompletion}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-4 text-gray-500">
                    <p>No active tasks</p>
                  </div>
                )}
              </div>
            </div>
            
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
              <div className="p-4 border-b border-gray-200 dark:border-gray-700">
                <h3 className="font-medium">Agent Relationships</h3>
              </div>
              <div className="p-4">
                <div className="space-y-3">
                  {agentRelationships
                    .filter(rel => rel.source === agent.id || rel.target === agent.id)
                    .map((rel, index) => {
                      const isSource = rel.source === agent.id;
                      const otherAgent = agentInstances.find(a => a.id === (isSource ? rel.target : rel.source));
                      return (
                        <div key={index} className="flex items-center space-x-3">
                          {isSource ? (
                            <>
                              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-100 dark:bg-gray-700 flex items-center justify-center">
                                <span className="text-xs font-medium">{agent.id}</span>
                              </div>
                              <div className="flex items-center space-x-2">
                                <span className="text-sm">{agent.name}</span>
                                <ArrowRight className="w-4 h-4 text-gray-400" />
                                <span className="text-xs px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded-full">{rel.type}</span>
                                <ArrowRight className="w-4 h-4 text-gray-400" />
                                <span className="text-sm">{otherAgent.name}</span>
                              </div>
                              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-100 dark:bg-gray-700 flex items-center justify-center">
                                <span className="text-xs font-medium">{otherAgent.id}</span>
                              </div>
                            </>
                          ) : (
                            <>
                              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-100 dark:bg-gray-700 flex items-center justify-center">
                                <span className="text-xs font-medium">{otherAgent.id}</span>
                              </div>
                              <div className="flex items-center space-x-2">
                                <span className="text-sm">{otherAgent.name}</span>
                                <ArrowRight className="w-4 h-4 text-gray-400" />
                                <span className="text-xs px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded-full">{rel.type}</span>
                                <ArrowRight className="w-4 h-4 text-gray-400" />
                                <span className="text-sm">{agent.name}</span>
                              </div>
                              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-100 dark:bg-gray-700 flex items-center justify-center">
                                <span className="text-xs font-medium">{agent.id}</span>
                              </div>
                            </>
                          )}
                        </div>
                      );
                    })}
                </div>
              </div>
            </div>
          </div>
          
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              {agent.status === 'active' ? (
                <button className="px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 flex items-center space-x-2">
                  <Pause className="w-4 h-4" />
                  <span>Pause Agent</span>
                </button>
              ) : (
                <button className="px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 flex items-center space-x-2">
                  <Play className="w-4 h-4" />
                  <span>Start Agent</span>
                </button>
              )}
              <button className="px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 flex items-center space-x-2">
                <RefreshCw className="w-4 h-4" />
                <span>Restart</span>
              </button>
              <button className="px-3 py-2 text-sm border border-red-300 dark:border-red-800 text-red-600 dark:text-red-400 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20 flex items-center space-x-2">
                <Trash2 className="w-4 h-4" />
                <span>Delete</span>
              </button>
            </div>
            <div>
              <button className="px-3 py-2 text-sm bg-blue-500 text-white rounded-lg hover:bg-blue-600 flex items-center space-x-2">
                <Edit className="w-4 h-4" />
                <span>Edit Configuration</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  };
  
  return (
    <div className="h-full">
      <div className="flex border-b border-gray-200 dark:border-gray-700 mb-6">
        <button 
          className={`px-4 py-2 font-medium text-sm ${activeTab === 'dashboard' ? 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-500' : 'text-gray-600 dark:text-gray-400'}`}
          onClick={() => setActiveTab('dashboard')}
        >
          Dashboard
        </button>
        <button 
          className={`px-4 py-2 font-medium text-sm ${activeTab === 'orchestration' ? 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-500' : 'text-gray-600 dark:text-gray-400'}`}
          onClick={() => setActiveTab('orchestration')}
        >
          Orchestration
        </button>
        <button 
          className={`px-4 py-2 font-medium text-sm ${activeTab === 'configuration' ? 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-500' : 'text-gray-600 dark:text-gray-400'}`}
          onClick={() => setActiveTab('configuration')}
        >
          Configuration
        </button>
        <button 
          className={`px-4 py-2 font-medium text-sm ${activeTab === 'training' ? 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-500' : 'text-gray-600 dark:text-gray-400'}`}
          onClick={() => setActiveTab('training')}
        >
          Training
        </button>
      </div>
      
      {activeTab === 'dashboard' && <AgentDashboard />}
      {activeTab === 'orchestration' && <AgentOrchestrationView />}
      {activeTab === 'configuration' && <AgentConfiguration />}
      {activeTab === 'training' && <AgentTraining />}
      
      {showNewAgentModal && <NewAgentModal />}
      {selectedAgent && <AgentDetailView />}
    </div>
  );
};

export default AdvancedAgentOrchestration;
