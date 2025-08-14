import React, { useState, useEffect } from 'react';
import { LLMApi } from '../api/apiService';

interface MultiLLMOrchestratorProps {
  onConfigChange?: (config: OrchestrationConfig) => void;
}

interface LLMModel {
  id: string;
  name: string;
  provider: string;
  capabilities: {
    reasoning: number;
    creativity: number;
    knowledge: number;
    coding: number;
    math: number;
  };
  enabled: boolean;
  latency: number;
  costPerToken: number;
}

interface OrchestrationConfig {
  strategy: 'auto' | 'sequential' | 'parallel' | 'voting';
  taskRouting: {
    simple: string[];
    medium: string[];
    complex: string[];
  };
  specializedCapabilities: {
    reasoning: string[];
    creativity: string[];
    knowledge: string[];
    coding: string[];
    math: string[];
  };
  votingThreshold: number;
  parallelLimit: number;
}

interface ModelUsage {
  modelId: string;
  name: string;
  usagePercentage: number;
  averageLatency: number;
  successRate: number;
}

const MultiLLMOrchestrator: React.FC<MultiLLMOrchestratorProps> = ({
  onConfigChange
}) => {
  const [models, setModels] = useState<LLMModel[]>([]);
  const [config, setConfig] = useState<OrchestrationConfig>({
    strategy: 'auto',
    taskRouting: {
      simple: [],
      medium: [],
      complex: []
    },
    specializedCapabilities: {
      reasoning: [],
      creativity: [],
      knowledge: [],
      coding: [],
      math: []
    },
    votingThreshold: 0.6,
    parallelLimit: 3
  });
  const [usageStats, setUsageStats] = useState<ModelUsage[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'models' | 'routing' | 'analytics'>('models');

  // Fetch models and configuration when component mounts
  useEffect(() => {
    fetchModels();
    fetchOrchestrationConfig();
    fetchAnalytics();
  }, []);

  const fetchModels = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await LLMApi.getModels();
      
      if (response.data) {
        setModels(response.data);
      }
    } catch (err: any) {
      console.error('Failed to fetch models:', err);
      setError(err.message || 'Failed to load models');
    } finally {
      setIsLoading(false);
    }
  };

  const fetchOrchestrationConfig = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await LLMApi.getOrchestrationConfig();
      
      if (response.data) {
        setConfig(response.data);
      }
    } catch (err: any) {
      console.error('Failed to fetch orchestration config:', err);
      setError(err.message || 'Failed to load orchestration configuration');
    } finally {
      setIsLoading(false);
    }
  };

  const fetchAnalytics = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await LLMApi.getAnalytics('week');
      
      if (response.data && response.data.modelUsage) {
        setUsageStats(response.data.modelUsage);
      }
    } catch (err: any) {
      console.error('Failed to fetch analytics:', err);
      setError(err.message || 'Failed to load analytics data');
    } finally {
      setIsLoading(false);
    }
  };

  const handleModelToggle = async (modelId: string) => {
    const updatedModels = models.map(model => 
      model.id === modelId ? { ...model, enabled: !model.enabled } : model
    );
    
    setModels(updatedModels);
    
    // Update task routing based on enabled models
    const enabledModelIds = updatedModels
      .filter(model => model.enabled)
      .map(model => model.id);
    
    // Update config with enabled models only
    const updatedConfig = {
      ...config,
      taskRouting: {
        simple: config.taskRouting.simple.filter(id => enabledModelIds.includes(id)),
        medium: config.taskRouting.medium.filter(id => enabledModelIds.includes(id)),
        complex: config.taskRouting.complex.filter(id => enabledModelIds.includes(id))
      },
      specializedCapabilities: {
        reasoning: config.specializedCapabilities.reasoning.filter(id => enabledModelIds.includes(id)),
        creativity: config.specializedCapabilities.creativity.filter(id => enabledModelIds.includes(id)),
        knowledge: config.specializedCapabilities.knowledge.filter(id => enabledModelIds.includes(id)),
        coding: config.specializedCapabilities.coding.filter(id => enabledModelIds.includes(id)),
        math: config.specializedCapabilities.math.filter(id => enabledModelIds.includes(id))
      }
    };
    
    setConfig(updatedConfig);
    
    if (onConfigChange) {
      onConfigChange(updatedConfig);
    }
    
    try {
      await LLMApi.updateOrchestrationConfig(updatedConfig);
    } catch (err: any) {
      console.error('Failed to update orchestration config:', err);
      // Revert changes on error
      fetchOrchestrationConfig();
    }
  };

  const handleStrategyChange = async (strategy: 'auto' | 'sequential' | 'parallel' | 'voting') => {
    const updatedConfig = {
      ...config,
      strategy
    };
    
    setConfig(updatedConfig);
    
    if (onConfigChange) {
      onConfigChange(updatedConfig);
    }
    
    try {
      await LLMApi.updateOrchestrationConfig(updatedConfig);
    } catch (err: any) {
      console.error('Failed to update orchestration config:', err);
      // Revert changes on error
      fetchOrchestrationConfig();
    }
  };

  const handleTaskRoutingChange = async (
    complexity: 'simple' | 'medium' | 'complex',
    modelIds: string[]
  ) => {
    const updatedConfig = {
      ...config,
      taskRouting: {
        ...config.taskRouting,
        [complexity]: modelIds
      }
    };
    
    setConfig(updatedConfig);
    
    if (onConfigChange) {
      onConfigChange(updatedConfig);
    }
    
    try {
      await LLMApi.updateOrchestrationConfig(updatedConfig);
    } catch (err: any) {
      console.error('Failed to update orchestration config:', err);
      // Revert changes on error
      fetchOrchestrationConfig();
    }
  };

  const handleCapabilityAssignment = async (
    capability: 'reasoning' | 'creativity' | 'knowledge' | 'coding' | 'math',
    modelIds: string[]
  ) => {
    const updatedConfig = {
      ...config,
      specializedCapabilities: {
        ...config.specializedCapabilities,
        [capability]: modelIds
      }
    };
    
    setConfig(updatedConfig);
    
    if (onConfigChange) {
      onConfigChange(updatedConfig);
    }
    
    try {
      await LLMApi.updateOrchestrationConfig(updatedConfig);
    } catch (err: any) {
      console.error('Failed to update orchestration config:', err);
      // Revert changes on error
      fetchOrchestrationConfig();
    }
  };

  const renderModelsTab = () => (
    <div className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {models.map(model => (
          <div 
            key={model.id} 
            className={`border rounded-lg p-4 ${
              model.enabled ? 'border-primary' : 'border-border'
            }`}
          >
            <div className="flex items-center justify-between mb-3">
              <div>
                <h3 className="font-medium">{model.name}</h3>
                <div className="text-xs text-muted-foreground">{model.provider}</div>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input 
                  type="checkbox" 
                  className="sr-only peer"
                  checked={model.enabled}
                  onChange={() => handleModelToggle(model.id)}
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary/20 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
              </label>
            </div>
            
            <div className="space-y-2 mb-3">
              <div className="flex items-center justify-between text-xs">
                <span>Reasoning</span>
                <span>{model.capabilities.reasoning}/10</span>
              </div>
              <div className="h-1.5 bg-muted rounded-full overflow-hidden">
                <div 
                  className="h-full bg-blue-500 rounded-full" 
                  style={{width: `${model.capabilities.reasoning * 10}%`}}
                ></div>
              </div>
              
              <div className="flex items-center justify-between text-xs">
                <span>Creativity</span>
                <span>{model.capabilities.creativity}/10</span>
              </div>
              <div className="h-1.5 bg-muted rounded-full overflow-hidden">
                <div 
                  className="h-full bg-purple-500 rounded-full" 
                  style={{width: `${model.capabilities.creativity * 10}%`}}
                ></div>
              </div>
              
              <div className="flex items-center justify-between text-xs">
                <span>Knowledge</span>
                <span>{model.capabilities.knowledge}/10</span>
              </div>
              <div className="h-1.5 bg-muted rounded-full overflow-hidden">
                <div 
                  className="h-full bg-green-500 rounded-full" 
                  style={{width: `${model.capabilities.knowledge * 10}%`}}
                ></div>
              </div>
              
              <div className="flex items-center justify-between text-xs">
                <span>Coding</span>
                <span>{model.capabilities.coding}/10</span>
              </div>
              <div className="h-1.5 bg-muted rounded-full overflow-hidden">
                <div 
                  className="h-full bg-amber-500 rounded-full" 
                  style={{width: `${model.capabilities.coding * 10}%`}}
                ></div>
              </div>
              
              <div className="flex items-center justify-between text-xs">
                <span>Math</span>
                <span>{model.capabilities.math}/10</span>
              </div>
              <div className="h-1.5 bg-muted rounded-full overflow-hidden">
                <div 
                  className="h-full bg-red-500 rounded-full" 
                  style={{width: `${model.capabilities.math * 10}%`}}
                ></div>
              </div>
            </div>
            
            <div className="flex items-center justify-between text-xs text-muted-foreground">
              <div>Latency: {model.latency}ms</div>
              <div>Cost: ${model.costPerToken.toFixed(6)}/token</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderRoutingTab = () => (
    <div className="space-y-6">
      <div>
        <h3 className="font-medium mb-2">Orchestration Strategy</h3>
        <div className="flex flex-wrap gap-2">
          <button 
            className={`px-3 py-1.5 rounded-md text-sm ${
              config.strategy === 'auto' ? 'bg-primary text-primary-foreground' : 'bg-accent/50 hover:bg-accent'
            }`}
            onClick={() => handleStrategyChange('auto')}
          >
            Auto
          </button>
          <button 
            className={`px-3 py-1.5 rounded-md text-sm ${
              config.strategy === 'sequential' ? 'bg-primary text-primary-foreground' : 'bg-accent/50 hover:bg-accent'
            }`}
            onClick={() => handleStrategyChange('sequential')}
          >
            Sequential
          </button>
          <button 
            className={`px-3 py-1.5 rounded-md text-sm ${
              config.strategy === 'parallel' ? 'bg-primary text-primary-foreground' : 'bg-accent/50 hover:bg-accent'
            }`}
            onClick={() => handleStrategyChange('parallel')}
          >
            Parallel
          </button>
          <button 
            className={`px-3 py-1.5 rounded-md text-sm ${
              config.strategy === 'voting' ? 'bg-primary text-primary-foreground' : 'bg-accent/50 hover:bg-accent'
            }`}
            onClick={() => handleStrategyChange('voting')}
          >
            Voting
          </button>
        </div>
        <div className="mt-2 text-xs text-muted-foreground">
          {config.strategy === 'auto' && 'Automatically select the best strategy based on task complexity'}
          {config.strategy === 'sequential' && 'Process tasks through models in sequence, using results from previous models'}
          {config.strategy === 'parallel' && 'Process tasks through multiple models simultaneously and combine results'}
          {config.strategy === 'voting' && 'Use multiple models and select the most common or highest confidence answer'}
        </div>
      </div>
      
      <div>
        <h3 className="font-medium mb-2">Task Complexity Routing</h3>
        <div className="space-y-4">
          <div>
            <div className="flex items-center mb-1">
              <div className="w-20 text-sm">Simple</div>
              <div className="flex-1 flex flex-wrap gap-1">
                {models.filter(model => model.enabled).map(model => (
                  <label 
                    key={model.id}
                    className={`px-2 py-1 text-xs rounded-full flex items-center gap-1 cursor-pointer ${
                      config.taskRouting.simple.includes(model.id) 
                        ? 'bg-primary/20 text-primary' 
                        : 'bg-accent/30 hover:bg-accent/50'
                    }`}
                  >
                    <input 
                      type="checkbox"
                      className="sr-only"
                      checked={config.taskRouting.simple.includes(model.id)}
                      onChange={() => {
                        const newModelIds = config.taskRouting.simple.includes(model.id)
                          ? config.taskRouting.simple.filter(id => id !== model.id)
                          : [...config.taskRouting.simple, model.id];
                        handleTaskRoutingChange('simple', newModelIds);
                      }}
                    />
                    {model.name}
                  </label>
                ))}
              </div>
            </div>
            <div className="text-xs text-muted-foreground ml-20">
              Simple tasks like answering questions, summarizing text, or basic formatting
            </div>
          </div>
          
          <div>
            <div className="flex items-center mb-1">
              <div className="w-20 text-sm">Medium</div>
              <div className="flex-1 flex flex-wrap gap-1">
                {models.filter(model => model.enabled).map(model => (
                  <label 
                    key={model.id}
                    className={`px-2 py-1 text-xs rounded-full flex items-center gap-1 cursor-pointer ${
                      config.taskRouting.medium.includes(model.id) 
                        ? 'bg-primary/20 text-primary' 
                        : 'bg-accent/30 hover:bg-accent/50'
                    }`}
                  >
                    <input 
                      type="checkbox"
                      className="sr-only"
                      checked={config.taskRouting.medium.includes(model.id)}
                      onChange={() => {
                        const newModelIds = config.taskRouting.medium.includes(model.id)
                          ? config.taskRouting.medium.filter(id => id !== model.id)
                          : [...config.taskRouting.medium, model.id];
                        handleTaskRoutingChange('medium', newModelIds);
                      }}
                    />
                    {model.name}
                  </label>
                ))}
              </div>
            </div>
            <div className="text-xs text-muted-foreground ml-20">
              Medium complexity tasks like content creation, data analysis, or basic coding
            </div>
          </div>
          
          <div>
            <div className="flex items-center mb-1">
              <div className="w-20 text-sm">Complex</div>
              <div className="flex-1 flex flex-wrap gap-1">
                {models.filter(model => model.enabled).map(model => (
                  <label 
                    key={model.id}
                    className={`px-2 py-1 text-xs rounded-full flex items-center gap-1 cursor-pointer ${
                      config.taskRouting.complex.includes(model.id) 
                        ? 'bg-primary/20 text-primary' 
                        : 'bg-accent/30 hover:bg-accent/50'
                    }`}
                  >
                    <input 
                      type="checkbox"
                      className="sr-only"
                      checked={config.taskRouting.complex.includes(model.id)}
                      onChange={() => {
                        const newModelIds = config.taskRouting.complex.includes(model.id)
                          ? config.taskRouting.complex.filter(id => id !== model.id)
                          : [...config.taskRouting.complex, model.id];
                        handleTaskRoutingChange('complex', newModelIds);
                      }}
                    />
                    {model.name}
                  </label>
                ))}
              </div>
            </div>
            <div className="text-xs text-muted-foreground ml-20">
              Complex tasks like advanced reasoning, multi-step problem solving, or complex coding
            </div>
          </div>
        </div>
      </div>
      
      <div>
        <h3 className="font-medium mb-2">Specialized Capability Assignment</h3>
        <div className="space-y-4">
          <div>
            <div className="flex items-center mb-1">
              <div className="w-20 text-sm">Reasoning</div>
              <div className="flex-1 flex flex-wrap gap-1">
                {models.filter(model => model.enabled).map(model => (
                  <label 
                    key={model.id}
                    className={`px-2 py-1 text-xs rounded-full flex items-center gap-1 cursor-pointer ${
                      config.specializedCapabilities.reasoning.includes(model.id) 
                        ? 'bg-blue-100 text-blue-800' 
                        : 'bg-accent/30 hover:bg-accent/50'
                    }`}
                  >
                    <input 
                      type="checkbox"
                      className="sr-only"
                      checked={config.specializedCapabilities.reasoning.includes(model.id)}
                      onChange={() => {
                        const newModelIds = config.specializedCapabilities.reasoning.includes(model.id)
                          ? config.specializedCapabilities.reasoning.filter(id => id !== model.id)
                          : [...config.specializedCapabilities.reasoning, model.id];
                        handleCapabilityAssignment('reasoning', newModelIds);
                      }}
                    />
                    {model.name}
                  </label>
                ))}
              </div>
            </div>
          </div>
          
          <div>
            <div className="flex items-center mb-1">
              <div className="w-20 text-sm">Creativity</div>
              <div className="flex-1 flex flex-wrap gap-1">
                {models.filter(model => model.enabled).map(model => (
                  <label 
                    key={model.id}
                    className={`px-2 py-1 text-xs rounded-full flex items-center gap-1 cursor-pointer ${
                      config.specializedCapabilities.creativity.includes(model.id) 
                        ? 'bg-purple-100 text-purple-800' 
                        : 'bg-accent/30 hover:bg-accent/50'
                    }`}
                  >
                    <input 
                      type="checkbox"
                      className="sr-only"
                      checked={config.specializedCapabilities.creativity.includes(model.id)}
                      onChange={() => {
                        const newModelIds = config.specializedCapabilities.creativity.includes(model.id)
                          ? config.specializedCapabilities.creativity.filter(id => id !== model.id)
                          : [...config.specializedCapabilities.creativity, model.id];
                        handleCapabilityAssignment('creativity', newModelIds);
                      }}
                    />
                    {model.name}
                  </label>
                ))}
              </div>
            </div>
          </div>
          
          <div>
            <div className="flex items-center mb-1">
              <div className="w-20 text-sm">Knowledge</div>
              <div className="flex-1 flex flex-wrap gap-1">
                {models.filter(model => model.enabled).map(model => (
                  <label 
                    key={model.id}
                    className={`px-2 py-1 text-xs rounded-full flex items-center gap-1 cursor-pointer ${
                      config.specializedCapabilities.knowledge.includes(model.id) 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-accent/30 hover:bg-accent/50'
                    }`}
                  >
                    <input 
                      type="checkbox"
                      className="sr-only"
                      checked={config.specializedCapabilities.knowledge.includes(model.id)}
                      onChange={() => {
                        const newModelIds = config.specializedCapabilities.knowledge.includes(model.id)
                          ? config.specializedCapabilities.knowledge.filter(id => id !== model.id)
                          : [...config.specializedCapabilities.knowledge, model.id];
                        handleCapabilityAssignment('knowledge', newModelIds);
                      }}
                    />
                    {model.name}
                  </label>
                ))}
              </div>
            </div>
          </div>
          
          <div>
            <div className="flex items-center mb-1">
              <div className="w-20 text-sm">Coding</div>
              <div className="flex-1 flex flex-wrap gap-1">
                {models.filter(model => model.enabled).map(model => (
                  <label 
                    key={model.id}
                    className={`px-2 py-1 text-xs rounded-full flex items-center gap-1 cursor-pointer ${
                      config.specializedCapabilities.coding.includes(model.id) 
                        ? 'bg-amber-100 text-amber-800' 
                        : 'bg-accent/30 hover:bg-accent/50'
                    }`}
                  >
                    <input 
                      type="checkbox"
                      className="sr-only"
                      checked={config.specializedCapabilities.coding.includes(model.id)}
                      onChange={() => {
                        const newModelIds = config.specializedCapabilities.coding.includes(model.id)
                          ? config.specializedCapabilities.coding.filter(id => id !== model.id)
                          : [...config.specializedCapabilities.coding, model.id];
                        handleCapabilityAssignment('coding', newModelIds);
                      }}
                    />
                    {model.name}
                  </label>
                ))}
              </div>
            </div>
          </div>
          
          <div>
            <div className="flex items-center mb-1">
              <div className="w-20 text-sm">Math</div>
              <div className="flex-1 flex flex-wrap gap-1">
                {models.filter(model => model.enabled).map(model => (
                  <label 
                    key={model.id}
                    className={`px-2 py-1 text-xs rounded-full flex items-center gap-1 cursor-pointer ${
                      config.specializedCapabilities.math.includes(model.id) 
                        ? 'bg-red-100 text-red-800' 
                        : 'bg-accent/30 hover:bg-accent/50'
                    }`}
                  >
                    <input 
                      type="checkbox"
                      className="sr-only"
                      checked={config.specializedCapabilities.math.includes(model.id)}
                      onChange={() => {
                        const newModelIds = config.specializedCapabilities.math.includes(model.id)
                          ? config.specializedCapabilities.math.filter(id => id !== model.id)
                          : [...config.specializedCapabilities.math, model.id];
                        handleCapabilityAssignment('math', newModelIds);
                      }}
                    />
                    {model.name}
                  </label>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderAnalyticsTab = () => (
    <div className="space-y-6">
      <div>
        <h3 className="font-medium mb-3">Model Usage Distribution</h3>
        <div className="h-64 bg-card border border-border rounded-lg p-4">
          <div className="h-full flex items-end justify-around">
            {usageStats.map(stat => (
              <div key={stat.modelId} className="flex flex-col items-center">
                <div 
                  className="w-16 bg-primary rounded-t-md" 
                  style={{height: `${stat.usagePercentage * 200}px`}}
                ></div>
                <div className="mt-2 text-xs font-medium truncate w-20 text-center">{stat.name}</div>
                <div className="text-xs text-muted-foreground">{(stat.usagePercentage * 100).toFixed(1)}%</div>
              </div>
            ))}
          </div>
        </div>
      </div>
      
      <div>
        <h3 className="font-medium mb-3">Performance Metrics</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border">
                <th className="text-left py-2 px-2">Model</th>
                <th className="text-left py-2 px-2">Usage</th>
                <th className="text-left py-2 px-2">Avg. Latency</th>
                <th className="text-left py-2 px-2">Success Rate</th>
              </tr>
            </thead>
            <tbody>
              {usageStats.map(stat => (
                <tr key={stat.modelId} className="border-b border-border">
                  <td className="py-2 px-2">{stat.name}</td>
                  <td className="py-2 px-2">{(stat.usagePercentage * 100).toFixed(1)}%</td>
                  <td className="py-2 px-2">{stat.averageLatency}ms</td>
                  <td className="py-2 px-2">{(stat.successRate * 100).toFixed(1)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
      
      <div>
        <h3 className="font-medium mb-3">Performance Improvement</h3>
        <div className="bg-card border border-border rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <div className="text-sm">Multi-LLM vs. Single Model</div>
            <div className="text-sm font-medium text-green-500">+24% accuracy</div>
          </div>
          <div className="h-2 bg-muted rounded-full overflow-hidden mb-4">
            <div className="h-full bg-green-500 rounded-full" style={{width: '24%'}}></div>
          </div>
          
          <div className="flex items-center justify-between mb-2">
            <div className="text-sm">Response Quality</div>
            <div className="text-sm font-medium text-green-500">+18% improvement</div>
          </div>
          <div className="h-2 bg-muted rounded-full overflow-hidden mb-4">
            <div className="h-full bg-green-500 rounded-full" style={{width: '18%'}}></div>
          </div>
          
          <div className="flex items-center justify-between mb-2">
            <div className="text-sm">Task Completion Rate</div>
            <div className="text-sm font-medium text-green-500">+32% improvement</div>
          </div>
          <div className="h-2 bg-muted rounded-full overflow-hidden">
            <div className="h-full bg-green-500 rounded-full" style={{width: '32%'}}></div>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="h-full flex flex-col">
      <div className="border-b border-border p-3 flex items-center justify-between">
        <h2 className="font-semibold">Multi-LLM Orchestration</h2>
        <div className="flex items-center space-x-2">
          <button 
            className="p-1 rounded-md hover:bg-accent text-muted-foreground" 
            title="Refresh"
            onClick={() => {
              fetchModels();
              fetchOrchestrationConfig();
              fetchAnalytics();
            }}
          >
            🔄
          </button>
          <button className="p-1 rounded-md hover:bg-accent text-muted-foreground" title="Settings">
            ⚙️
          </button>
        </div>
      </div>
      
      <div className="border-b border-border p-2 flex items-center space-x-4">
        <button 
          className={`px-3 py-1.5 rounded-md text-sm ${activeTab === 'models' ? 'bg-primary text-primary-foreground' : 'hover:bg-accent'}`}
          onClick={() => setActiveTab('models')}
        >
          Models
        </button>
        <button 
          className={`px-3 py-1.5 rounded-md text-sm ${activeTab === 'routing' ? 'bg-primary text-primary-foreground' : 'hover:bg-accent'}`}
          onClick={() => setActiveTab('routing')}
        >
          Task Routing
        </button>
        <button 
          className={`px-3 py-1.5 rounded-md text-sm ${activeTab === 'analytics' ? 'bg-primary text-primary-foreground' : 'hover:bg-accent'}`}
          onClick={() => setActiveTab('analytics')}
        >
          Analytics
        </button>
      </div>
      
      <div className="flex-1 overflow-auto p-4">
        {isLoading ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-muted-foreground">Loading...</div>
          </div>
        ) : error ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-red-500">{error}</div>
          </div>
        ) : (
          <>
            {activeTab === 'models' && renderModelsTab()}
            {activeTab === 'routing' && renderRoutingTab()}
            {activeTab === 'analytics' && renderAnalyticsTab()}
          </>
        )}
      </div>
      
      <div className="border-t border-border p-2 flex items-center justify-between text-xs text-muted-foreground">
        <div>
          {models.filter(m => m.enabled).length} of {models.length} models enabled
        </div>
        <div>
          Strategy: {config.strategy.charAt(0).toUpperCase() + config.strategy.slice(1)}
        </div>
      </div>
    </div>
  );
};

export default MultiLLMOrchestrator;
