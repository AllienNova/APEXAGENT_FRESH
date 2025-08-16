import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Brain, 
  Zap, 
  Target, 
  CheckCircle, 
  AlertTriangle, 
  TrendingUp,
  Settings,
  Play,
  Pause,
  RotateCcw,
  BarChart3,
  Users,
  Clock,
  Star
} from 'lucide-react';

// Agent types enum
const AgentType = {
  PLANNER: 'planner',
  EXECUTION: 'execution',
  VERIFICATION: 'verification',
  SECURITY: 'security',
  OPTIMIZATION: 'optimization',
  LEARNING: 'learning',
  COORDINATOR: 'coordinator'
};

// Prompt patterns enum
const PromptPattern = {
  CHAIN_OF_THOUGHT: 'chain_of_thought',
  TREE_OF_THOUGHTS: 'tree_of_thoughts',
  SELF_CORRECTION: 'self_correction',
  MULTI_PERSPECTIVE: 'multi_perspective',
  CONSTRAINT_BASED: 'constraint_based',
  SCENARIO_PLANNING: 'scenario_planning'
};

// Task complexity enum
const TaskComplexity = {
  SIMPLE: 'simple',
  MEDIUM: 'medium',
  COMPLEX: 'complex',
  EXPERT: 'expert'
};

const EnhancedPromptInterface = () => {
  const [activeAgent, setActiveAgent] = useState(AgentType.PLANNER);
  const [promptMetrics, setPromptMetrics] = useState({});
  const [systemStatus, setSystemStatus] = useState('active');
  const [performanceData, setPerformanceData] = useState({
    totalPrompts: 0,
    avgResponseQuality: 0,
    avgResponseTime: 0,
    avgUserSatisfaction: 0,
    avgSuccessRate: 0
  });

  // Agent configuration data
  const agentConfigs = {
    [AgentType.PLANNER]: {
      name: 'Strategic Planner',
      icon: Target,
      color: 'bg-blue-500',
      description: 'Advanced strategic planning with cognitive frameworks',
      patterns: [
        PromptPattern.CHAIN_OF_THOUGHT,
        PromptPattern.SCENARIO_PLANNING,
        PromptPattern.CONSTRAINT_BASED,
        PromptPattern.MULTI_PERSPECTIVE
      ],
      qualityChecks: 7,
      examples: 1,
      avgQuality: 92
    },
    [AgentType.EXECUTION]: {
      name: 'Task Executor',
      icon: Zap,
      color: 'bg-green-500',
      description: 'Systematic task execution with tool optimization',
      patterns: [
        PromptPattern.CHAIN_OF_THOUGHT,
        PromptPattern.SELF_CORRECTION,
        PromptPattern.CONSTRAINT_BASED
      ],
      qualityChecks: 7,
      examples: 1,
      avgQuality: 89
    },
    [AgentType.VERIFICATION]: {
      name: 'Quality Verifier',
      icon: CheckCircle,
      color: 'bg-purple-500',
      description: 'Comprehensive quality assurance and validation',
      patterns: [
        PromptPattern.MULTI_PERSPECTIVE,
        PromptPattern.SELF_CORRECTION,
        PromptPattern.CHAIN_OF_THOUGHT
      ],
      qualityChecks: 7,
      examples: 1,
      avgQuality: 94
    },
    [AgentType.SECURITY]: {
      name: 'Security Analyst',
      icon: AlertTriangle,
      color: 'bg-red-500',
      description: 'Advanced threat assessment and risk mitigation',
      patterns: [
        PromptPattern.SCENARIO_PLANNING,
        PromptPattern.MULTI_PERSPECTIVE,
        PromptPattern.CONSTRAINT_BASED
      ],
      qualityChecks: 7,
      examples: 1,
      avgQuality: 91
    },
    [AgentType.OPTIMIZATION]: {
      name: 'Performance Optimizer',
      icon: TrendingUp,
      color: 'bg-orange-500',
      description: 'System efficiency and continuous improvement',
      patterns: [
        PromptPattern.CONSTRAINT_BASED,
        PromptPattern.MULTI_PERSPECTIVE,
        PromptPattern.CHAIN_OF_THOUGHT
      ],
      qualityChecks: 7,
      examples: 1,
      avgQuality: 88
    },
    [AgentType.LEARNING]: {
      name: 'Learning Specialist',
      icon: Brain,
      color: 'bg-indigo-500',
      description: 'Adaptive learning and knowledge synthesis',
      patterns: [
        PromptPattern.CHAIN_OF_THOUGHT,
        PromptPattern.MULTI_PERSPECTIVE,
        PromptPattern.SELF_CORRECTION
      ],
      qualityChecks: 7,
      examples: 1,
      avgQuality: 90
    },
    [AgentType.COORDINATOR]: {
      name: 'System Coordinator',
      icon: Users,
      color: 'bg-teal-500',
      description: 'Multi-agent orchestration and workflow management',
      patterns: [
        PromptPattern.MULTI_PERSPECTIVE,
        PromptPattern.CHAIN_OF_THOUGHT,
        PromptPattern.SELF_CORRECTION
      ],
      qualityChecks: 7,
      examples: 1,
      avgQuality: 93
    }
  };

  // Pattern descriptions
  const patternDescriptions = {
    [PromptPattern.CHAIN_OF_THOUGHT]: 'Step-by-step reasoning with explicit logic',
    [PromptPattern.TREE_OF_THOUGHTS]: 'Multiple reasoning paths exploration',
    [PromptPattern.SELF_CORRECTION]: 'Built-in error checking and validation',
    [PromptPattern.MULTI_PERSPECTIVE]: 'Multiple viewpoint analysis',
    [PromptPattern.CONSTRAINT_BASED]: 'Solution design within constraints',
    [PromptPattern.SCENARIO_PLANNING]: 'Multiple scenario consideration'
  };

  // Simulate real-time performance updates
  useEffect(() => {
    const interval = setInterval(() => {
      setPerformanceData(prev => ({
        totalPrompts: prev.totalPrompts + Math.floor(Math.random() * 3),
        avgResponseQuality: Math.min(100, prev.avgResponseQuality + (Math.random() - 0.5) * 2),
        avgResponseTime: Math.max(0.5, prev.avgResponseTime + (Math.random() - 0.5) * 0.2),
        avgUserSatisfaction: Math.min(100, prev.avgUserSatisfaction + (Math.random() - 0.5) * 1.5),
        avgSuccessRate: Math.min(100, prev.avgSuccessRate + (Math.random() - 0.5) * 1)
      }));
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  // Initialize performance data
  useEffect(() => {
    setPerformanceData({
      totalPrompts: 247,
      avgResponseQuality: 91.2,
      avgResponseTime: 1.38,
      avgUserSatisfaction: 94.7,
      avgSuccessRate: 96.8
    });
  }, []);

  const handleAgentSelect = useCallback((agentType) => {
    setActiveAgent(agentType);
  }, []);

  const handleSystemToggle = useCallback(() => {
    setSystemStatus(prev => prev === 'active' ? 'paused' : 'active');
  }, []);

  const handleSystemReset = useCallback(() => {
    setPerformanceData({
      totalPrompts: 0,
      avgResponseQuality: 85,
      avgResponseTime: 2.0,
      avgUserSatisfaction: 85,
      avgSuccessRate: 90
    });
  }, []);

  const getQualityColor = (quality) => {
    if (quality >= 95) return 'text-green-600';
    if (quality >= 90) return 'text-blue-600';
    if (quality >= 85) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getQualityBadgeColor = (quality) => {
    if (quality >= 95) return 'bg-green-100 text-green-800';
    if (quality >= 90) return 'bg-blue-100 text-blue-800';
    if (quality >= 85) return 'bg-yellow-100 text-yellow-800';
    return 'bg-red-100 text-red-800';
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
              <Brain className="h-8 w-8 text-blue-600" />
              Enhanced Prompt Engineering System
            </h1>
            <p className="text-gray-600 mt-2">
              Advanced cognitive architectures and optimization patterns for superhuman AI performance
            </p>
          </div>
          
          <div className="flex items-center gap-3">
            <Badge 
              variant={systemStatus === 'active' ? 'default' : 'secondary'}
              className="px-3 py-1"
            >
              {systemStatus === 'active' ? 'Active' : 'Paused'}
            </Badge>
            
            <Button
              variant="outline"
              size="sm"
              onClick={handleSystemToggle}
              className="flex items-center gap-2"
            >
              {systemStatus === 'active' ? (
                <>
                  <Pause className="h-4 w-4" />
                  Pause
                </>
              ) : (
                <>
                  <Play className="h-4 w-4" />
                  Resume
                </>
              )}
            </Button>
            
            <Button
              variant="outline"
              size="sm"
              onClick={handleSystemReset}
              className="flex items-center gap-2"
            >
              <RotateCcw className="h-4 w-4" />
              Reset
            </Button>
          </div>
        </div>

        {/* Performance Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Total Prompts</p>
                  <p className="text-2xl font-bold text-gray-900">{performanceData.totalPrompts}</p>
                </div>
                <BarChart3 className="h-8 w-8 text-blue-600" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Avg Quality</p>
                  <p className={`text-2xl font-bold ${getQualityColor(performanceData.avgResponseQuality)}`}>
                    {performanceData.avgResponseQuality.toFixed(1)}%
                  </p>
                </div>
                <Star className="h-8 w-8 text-yellow-600" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Response Time</p>
                  <p className="text-2xl font-bold text-gray-900">{performanceData.avgResponseTime.toFixed(2)}s</p>
                </div>
                <Clock className="h-8 w-8 text-green-600" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Success Rate</p>
                  <p className="text-2xl font-bold text-green-600">{performanceData.avgSuccessRate.toFixed(1)}%</p>
                </div>
                <CheckCircle className="h-8 w-8 text-green-600" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Main Content */}
        <Tabs defaultValue="agents" className="space-y-6">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="agents">Agent Management</TabsTrigger>
            <TabsTrigger value="patterns">Optimization Patterns</TabsTrigger>
            <TabsTrigger value="analytics">Performance Analytics</TabsTrigger>
          </TabsList>

          {/* Agent Management Tab */}
          <TabsContent value="agents" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              
              {/* Agent List */}
              <div className="lg:col-span-1">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Users className="h-5 w-5" />
                      AI Agents
                    </CardTitle>
                    <CardDescription>
                      Select an agent to view detailed configuration
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {Object.entries(agentConfigs).map(([type, config]) => {
                      const IconComponent = config.icon;
                      const isActive = activeAgent === type;
                      
                      return (
                        <div
                          key={type}
                          className={`p-3 rounded-lg border cursor-pointer transition-all ${
                            isActive 
                              ? 'border-blue-500 bg-blue-50' 
                              : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                          }`}
                          onClick={() => handleAgentSelect(type)}
                        >
                          <div className="flex items-center gap-3">
                            <div className={`p-2 rounded-lg ${config.color} text-white`}>
                              <IconComponent className="h-4 w-4" />
                            </div>
                            <div className="flex-1">
                              <p className="font-medium text-gray-900">{config.name}</p>
                              <div className="flex items-center gap-2 mt-1">
                                <Badge className={getQualityBadgeColor(config.avgQuality)}>
                                  {config.avgQuality}%
                                </Badge>
                                <span className="text-xs text-gray-500">
                                  {config.patterns.length} patterns
                                </span>
                              </div>
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </CardContent>
                </Card>
              </div>

              {/* Agent Details */}
              <div className="lg:col-span-2">
                <Card>
                  <CardHeader>
                    <div className="flex items-center gap-3">
                      <div className={`p-3 rounded-lg ${agentConfigs[activeAgent].color} text-white`}>
                        {React.createElement(agentConfigs[activeAgent].icon, { className: "h-6 w-6" })}
                      </div>
                      <div>
                        <CardTitle>{agentConfigs[activeAgent].name}</CardTitle>
                        <CardDescription>{agentConfigs[activeAgent].description}</CardDescription>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    
                    {/* Performance Metrics */}
                    <div>
                      <h4 className="font-medium text-gray-900 mb-3">Performance Metrics</h4>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <p className="text-sm text-gray-600">Average Quality</p>
                          <div className="flex items-center gap-2 mt-1">
                            <Progress value={agentConfigs[activeAgent].avgQuality} className="flex-1" />
                            <span className={`text-sm font-medium ${getQualityColor(agentConfigs[activeAgent].avgQuality)}`}>
                              {agentConfigs[activeAgent].avgQuality}%
                            </span>
                          </div>
                        </div>
                        <div>
                          <p className="text-sm text-gray-600">Quality Checks</p>
                          <p className="text-lg font-semibold text-gray-900 mt-1">
                            {agentConfigs[activeAgent].qualityChecks} checks
                          </p>
                        </div>
                      </div>
                    </div>

                    {/* Optimization Patterns */}
                    <div>
                      <h4 className="font-medium text-gray-900 mb-3">Optimization Patterns</h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        {agentConfigs[activeAgent].patterns.map((pattern) => (
                          <div key={pattern} className="p-3 border rounded-lg bg-gray-50">
                            <p className="font-medium text-gray-900 text-sm">
                              {pattern.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                            </p>
                            <p className="text-xs text-gray-600 mt-1">
                              {patternDescriptions[pattern]}
                            </p>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Configuration Actions */}
                    <div className="flex gap-3 pt-4 border-t">
                      <Button variant="outline" size="sm" className="flex items-center gap-2">
                        <Settings className="h-4 w-4" />
                        Configure
                      </Button>
                      <Button variant="outline" size="sm" className="flex items-center gap-2">
                        <Play className="h-4 w-4" />
                        Test Prompt
                      </Button>
                      <Button variant="outline" size="sm" className="flex items-center gap-2">
                        <BarChart3 className="h-4 w-4" />
                        View Analytics
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          </TabsContent>

          {/* Optimization Patterns Tab */}
          <TabsContent value="patterns" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {Object.entries(patternDescriptions).map(([pattern, description]) => (
                <Card key={pattern}>
                  <CardHeader>
                    <CardTitle className="text-lg">
                      {pattern.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-gray-600 text-sm mb-4">{description}</p>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Usage</span>
                        <span className="font-medium">
                          {Object.values(agentConfigs).filter(config => 
                            config.patterns.includes(pattern)
                          ).length} agents
                        </span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Effectiveness</span>
                        <span className="font-medium text-green-600">High</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          {/* Performance Analytics Tab */}
          <TabsContent value="analytics" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              
              {/* System Performance */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <TrendingUp className="h-5 w-5" />
                    System Performance
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <div className="flex justify-between text-sm mb-2">
                      <span>Response Quality</span>
                      <span className="font-medium">{performanceData.avgResponseQuality.toFixed(1)}%</span>
                    </div>
                    <Progress value={performanceData.avgResponseQuality} />
                  </div>
                  
                  <div>
                    <div className="flex justify-between text-sm mb-2">
                      <span>User Satisfaction</span>
                      <span className="font-medium">{performanceData.avgUserSatisfaction.toFixed(1)}%</span>
                    </div>
                    <Progress value={performanceData.avgUserSatisfaction} />
                  </div>
                  
                  <div>
                    <div className="flex justify-between text-sm mb-2">
                      <span>Success Rate</span>
                      <span className="font-medium">{performanceData.avgSuccessRate.toFixed(1)}%</span>
                    </div>
                    <Progress value={performanceData.avgSuccessRate} />
                  </div>
                </CardContent>
              </Card>

              {/* Agent Performance Comparison */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <BarChart3 className="h-5 w-5" />
                    Agent Performance
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {Object.entries(agentConfigs)
                      .sort(([,a], [,b]) => b.avgQuality - a.avgQuality)
                      .map(([type, config]) => (
                        <div key={type} className="flex items-center gap-3">
                          <div className={`p-1.5 rounded ${config.color} text-white`}>
                            {React.createElement(config.icon, { className: "h-3 w-3" })}
                          </div>
                          <div className="flex-1">
                            <div className="flex justify-between text-sm mb-1">
                              <span className="font-medium">{config.name}</span>
                              <span className={getQualityColor(config.avgQuality)}>
                                {config.avgQuality}%
                              </span>
                            </div>
                            <Progress value={config.avgQuality} className="h-2" />
                          </div>
                        </div>
                      ))}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* System Status Alert */}
            <Alert>
              <CheckCircle className="h-4 w-4" />
              <AlertDescription>
                Enhanced Prompt Engineering System is operating at optimal performance. 
                All 7 agents are active with advanced cognitive architectures and optimization patterns enabled.
                Average system performance: {((performanceData.avgResponseQuality + performanceData.avgSuccessRate) / 2).toFixed(1)}%
              </AlertDescription>
            </Alert>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default EnhancedPromptInterface;

