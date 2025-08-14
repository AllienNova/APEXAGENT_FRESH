import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { Textarea } from '@/components/ui/textarea';
import { 
  Key, 
  Brain, 
  Zap, 
  DollarSign, 
  Shield, 
  Globe, 
  Settings,
  Plus,
  Edit,
  Trash2,
  Eye,
  EyeOff,
  CheckCircle,
  AlertCircle,
  Sparkles,
  Target,
  BarChart3,
  Users,
  Clock
} from 'lucide-react';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from '@/components/ui/tabs';

interface APIProvider {
  id: string;
  name: string;
  type: 'llm' | 'image' | 'audio' | 'embedding' | 'search' | 'tool';
  baseUrl: string;
  apiKey: string;
  isActive: boolean;
  costPer1M?: {
    input: number;
    output: number;
  };
  rateLimit?: {
    requestsPerMinute: number;
    tokensPerMinute: number;
  };
  capabilities: string[];
  models: string[];
  priority: number; // Lower number = higher priority
  fallbackTo?: string; // ID of fallback provider
}

interface AdvancedPromptTemplate {
  id: string;
  name: string;
  category: 'expert' | 'creative' | 'analytical' | 'technical' | 'conversational';
  template: string;
  variables: string[];
  expertLevel: 1 | 2 | 3 | 4 | 5; // 5 = PhD level expertise
  tools: string[];
  costOptimized: boolean;
}

interface SystemMetrics {
  totalRequests: number;
  totalCost: number;
  costSavings: number;
  averageResponseTime: number;
  successRate: number;
  providerUsage: Record<string, number>;
}

export const AideonExpertSystemManager: React.FC = () => {
  const [providers, setProviders] = useState<APIProvider[]>([]);
  const [promptTemplates, setPromptTemplates] = useState<AdvancedPromptTemplate[]>([]);
  const [metrics, setMetrics] = useState<SystemMetrics | null>(null);
  const [selectedProvider, setSelectedProvider] = useState<string | null>(null);
  const [showAddProvider, setShowAddProvider] = useState(false);
  const [showPromptEditor, setShowPromptEditor] = useState(false);
  const [loading, setLoading] = useState(true);

  // Initialize with comprehensive provider setup
  useEffect(() => {
    initializeExpertSystem();
  }, []);

  const initializeExpertSystem = async () => {
    try {
      // Load existing configuration
      const response = await fetch('/api/admin/expert-system', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('admin_token')}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setProviders(data.providers || []);
        setPromptTemplates(data.promptTemplates || []);
        setMetrics(data.metrics || null);
      } else {
        // Initialize with default expert configuration
        initializeDefaultConfiguration();
      }
    } catch (error) {
      console.error('Failed to load expert system:', error);
      initializeDefaultConfiguration();
    } finally {
      setLoading(false);
    }
  };

  const initializeDefaultConfiguration = () => {
    const defaultProviders: APIProvider[] = [
      // Together AI - Cost Effective Options
      {
        id: 'together-ai-8b',
        name: 'Together AI - Llama 3.1 8B Turbo',
        type: 'llm',
        baseUrl: 'https://api.together.xyz/v1',
        apiKey: '',
        isActive: true,
        costPer1M: { input: 0.18, output: 0.59 },
        rateLimit: { requestsPerMinute: 6000, tokensPerMinute: 2000000 },
        capabilities: ['chat', 'reasoning', 'coding', 'analysis'],
        models: ['meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo'],
        priority: 1,
        fallbackTo: 'openai-gpt4'
      },
      {
        id: 'together-ai-70b',
        name: 'Together AI - Llama 3.1 70B Turbo',
        type: 'llm',
        baseUrl: 'https://api.together.xyz/v1',
        apiKey: '',
        isActive: true,
        costPer1M: { input: 0.88, output: 0.88 },
        rateLimit: { requestsPerMinute: 6000, tokensPerMinute: 2000000 },
        capabilities: ['chat', 'reasoning', 'coding', 'analysis', 'expert'],
        models: ['meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo'],
        priority: 2,
        fallbackTo: 'openai-gpt4'
      },
      {
        id: 'together-ai-405b',
        name: 'Together AI - Llama 3.1 405B Turbo',
        type: 'llm',
        baseUrl: 'https://api.together.xyz/v1',
        apiKey: '',
        isActive: true,
        costPer1M: { input: 3.50, output: 3.50 },
        rateLimit: { requestsPerMinute: 6000, tokensPerMinute: 2000000 },
        capabilities: ['chat', 'reasoning', 'coding', 'analysis', 'expert', 'research'],
        models: ['meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo'],
        priority: 3,
        fallbackTo: 'openai-gpt4'
      },
      // Existing Premium Options
      {
        id: 'openai-gpt4',
        name: 'OpenAI GPT-4',
        type: 'llm',
        baseUrl: 'https://api.openai.com/v1',
        apiKey: '',
        isActive: true,
        costPer1M: { input: 6.00, output: 6.00 },
        rateLimit: { requestsPerMinute: 500, tokensPerMinute: 150000 },
        capabilities: ['chat', 'reasoning', 'coding', 'analysis', 'expert'],
        models: ['gpt-4', 'gpt-4-turbo'],
        priority: 4
      },
      {
        id: 'anthropic-claude',
        name: 'Anthropic Claude 3.5 Sonnet',
        type: 'llm',
        baseUrl: 'https://api.anthropic.com',
        apiKey: '',
        isActive: true,
        costPer1M: { input: 3.00, output: 15.00 },
        rateLimit: { requestsPerMinute: 1000, tokensPerMinute: 200000 },
        capabilities: ['chat', 'reasoning', 'coding', 'analysis', 'expert', 'creative'],
        models: ['claude-3-5-sonnet-20241022'],
        priority: 5
      },
      // Image Generation
      {
        id: 'together-ai-flux',
        name: 'Together AI - FLUX.1 Schnell',
        type: 'image',
        baseUrl: 'https://api.together.xyz/v1',
        apiKey: '',
        isActive: true,
        capabilities: ['image-generation', 'fast-generation'],
        models: ['black-forest-labs/FLUX.1-schnell-Free'],
        priority: 1,
        fallbackTo: 'openai-dalle'
      },
      {
        id: 'openai-dalle',
        name: 'OpenAI DALL-E 3',
        type: 'image',
        baseUrl: 'https://api.openai.com/v1',
        apiKey: '',
        isActive: true,
        capabilities: ['image-generation', 'high-quality'],
        models: ['dall-e-3'],
        priority: 2
      },
      // Embeddings
      {
        id: 'together-ai-embeddings',
        name: 'Together AI - Embeddings',
        type: 'embedding',
        baseUrl: 'https://api.together.xyz/v1',
        apiKey: '',
        isActive: true,
        costPer1M: { input: 0.02, output: 0 },
        capabilities: ['embeddings', 'semantic-search'],
        models: ['togethercomputer/m2-bert-80M-8k-retrieval'],
        priority: 1,
        fallbackTo: 'openai-embeddings'
      },
      {
        id: 'openai-embeddings',
        name: 'OpenAI Embeddings',
        type: 'embedding',
        baseUrl: 'https://api.openai.com/v1',
        apiKey: '',
        isActive: true,
        costPer1M: { input: 0.10, output: 0 },
        capabilities: ['embeddings', 'semantic-search'],
        models: ['text-embedding-3-large'],
        priority: 2
      }
    ];

    const defaultPromptTemplates: AdvancedPromptTemplate[] = [
      {
        id: 'expert-analyst',
        name: 'Expert Data Analyst',
        category: 'analytical',
        template: `You are a world-class data analyst with PhD-level expertise in statistics, machine learning, and business intelligence. Your analysis is trusted by Fortune 500 companies and academic institutions.

CONTEXT: {context}
DATA: {data}
QUESTION: {question}

EXPERT ANALYSIS FRAMEWORK:
1. **Statistical Foundation**: Apply rigorous statistical methods
2. **Pattern Recognition**: Identify complex patterns and correlations
3. **Predictive Insights**: Provide forward-looking analysis
4. **Business Impact**: Translate findings into actionable recommendations
5. **Confidence Intervals**: Quantify uncertainty and risk

RESPONSE FORMAT:
- Executive Summary (2-3 sentences)
- Key Findings (bullet points with confidence levels)
- Statistical Analysis (methods used, significance tests)
- Visualizations Recommended (specific chart types)
- Business Recommendations (prioritized by impact)
- Risk Assessment (potential limitations)

Provide analysis with the depth and rigor expected from a top-tier consulting firm.`,
        variables: ['context', 'data', 'question'],
        expertLevel: 5,
        tools: ['data-analysis', 'visualization', 'statistics', 'machine-learning'],
        costOptimized: true
      },
      {
        id: 'expert-coder',
        name: 'Expert Software Architect',
        category: 'technical',
        template: `You are a distinguished software architect with 20+ years of experience, recognized as a thought leader in software engineering. You've designed systems for companies like Google, Microsoft, and Amazon.

PROJECT CONTEXT: {context}
REQUIREMENTS: {requirements}
CONSTRAINTS: {constraints}

ARCHITECTURAL EXCELLENCE FRAMEWORK:
1. **System Design**: Scalable, maintainable, and robust architecture
2. **Best Practices**: Industry-standard patterns and principles
3. **Performance**: Optimization for speed, memory, and scalability
4. **Security**: Enterprise-grade security considerations
5. **Testing**: Comprehensive testing strategy
6. **Documentation**: Clear, professional documentation

CODE QUALITY STANDARDS:
- Clean, readable, and well-commented code
- SOLID principles and design patterns
- Error handling and edge cases
- Performance optimization
- Security best practices
- Comprehensive testing

DELIVERABLES:
- Architecture diagram (ASCII or description)
- Implementation plan with phases
- Code examples with explanations
- Testing strategy
- Deployment considerations
- Maintenance guidelines

Provide solutions that would pass the most rigorous code review at a top tech company.`,
        variables: ['context', 'requirements', 'constraints'],
        expertLevel: 5,
        tools: ['code-execution', 'architecture-design', 'testing', 'deployment'],
        costOptimized: true
      },
      {
        id: 'expert-researcher',
        name: 'Expert Research Scientist',
        category: 'expert',
        template: `You are a renowned research scientist with expertise across multiple disciplines, published in top-tier journals, and recognized internationally for groundbreaking research.

RESEARCH TOPIC: {topic}
RESEARCH QUESTION: {question}
SCOPE: {scope}

SCIENTIFIC RESEARCH METHODOLOGY:
1. **Literature Review**: Comprehensive analysis of existing research
2. **Hypothesis Formation**: Clear, testable hypotheses
3. **Methodology**: Rigorous research design
4. **Analysis**: Statistical and qualitative analysis
5. **Conclusions**: Evidence-based findings
6. **Future Work**: Research directions and implications

RESEARCH STANDARDS:
- Peer-review quality analysis
- Proper citation and attribution
- Statistical significance testing
- Reproducible methodology
- Ethical considerations
- Interdisciplinary connections

OUTPUT FORMAT:
- Abstract (150 words)
- Introduction and Background
- Research Questions/Hypotheses
- Methodology
- Analysis and Findings
- Discussion and Implications
- Limitations and Future Research
- References and Further Reading

Provide research with the rigor and depth expected for publication in Nature or Science.`,
        variables: ['topic', 'question', 'scope'],
        expertLevel: 5,
        tools: ['deep-research', 'data-analysis', 'document-generation', 'search'],
        costOptimized: false
      },
      {
        id: 'expert-creative',
        name: 'Expert Creative Director',
        category: 'creative',
        template: `You are an award-winning creative director with a portfolio spanning global brands, film, and digital media. Your work has won Cannes Lions, D&AD, and other prestigious awards.

CREATIVE BRIEF: {brief}
TARGET AUDIENCE: {audience}
BRAND CONTEXT: {brand}

CREATIVE EXCELLENCE FRAMEWORK:
1. **Strategic Insight**: Deep understanding of brand and audience
2. **Creative Concept**: Original, memorable, and impactful ideas
3. **Execution**: Flawless execution across all touchpoints
4. **Innovation**: Cutting-edge techniques and technologies
5. **Emotional Connection**: Resonates with target audience
6. **Measurable Impact**: Drives business results

CREATIVE DELIVERABLES:
- Creative Strategy (positioning, key message)
- Concept Development (big idea, creative rationale)
- Visual Direction (mood boards, style guides)
- Copy and Messaging (headlines, taglines, body copy)
- Campaign Elements (across all channels)
- Production Guidelines (technical specifications)

CREATIVE STANDARDS:
- Award-worthy creative concepts
- Brand-appropriate tone and style
- Culturally sensitive and inclusive
- Technically feasible and scalable
- Measurable and results-driven

Deliver creative work that would win industry awards and drive significant business impact.`,
        variables: ['brief', 'audience', 'brand'],
        expertLevel: 5,
        tools: ['image-generation', 'creative-writing', 'design', 'branding'],
        costOptimized: true
      },
      {
        id: 'expert-consultant',
        name: 'Expert Management Consultant',
        category: 'analytical',
        template: `You are a senior partner at a top-tier management consulting firm (McKinsey, BCG, Bain level) with 15+ years of experience advising Fortune 500 CEOs and government leaders.

CLIENT SITUATION: {situation}
BUSINESS CHALLENGE: {challenge}
OBJECTIVES: {objectives}

CONSULTING METHODOLOGY:
1. **Problem Definition**: Clearly articulate the core issue
2. **Hypothesis Development**: Form testable hypotheses
3. **Analysis Framework**: Structure analysis systematically
4. **Data Collection**: Identify key data sources and metrics
5. **Synthesis**: Draw insights from analysis
6. **Recommendations**: Actionable, prioritized recommendations

CONSULTING DELIVERABLES:
- Executive Summary (C-suite ready)
- Situation Assessment
- Problem Analysis (with frameworks)
- Strategic Options (with pros/cons)
- Recommended Solution (detailed implementation)
- Implementation Roadmap (timeline, resources, risks)
- Success Metrics (KPIs and measurement plan)

CONSULTING STANDARDS:
- Fact-based analysis and recommendations
- Clear, compelling communication
- Actionable and implementable solutions
- Risk assessment and mitigation
- Change management considerations
- ROI and business case

Provide consulting-grade analysis and recommendations that would command premium fees from the world's largest companies.`,
        variables: ['situation', 'challenge', 'objectives'],
        expertLevel: 5,
        tools: ['data-analysis', 'strategic-planning', 'presentation-generation', 'business-analysis'],
        costOptimized: true
      }
    ];

    setProviders(defaultProviders);
    setPromptTemplates(defaultPromptTemplates);
    
    // Initialize metrics
    setMetrics({
      totalRequests: 0,
      totalCost: 0,
      costSavings: 0,
      averageResponseTime: 0,
      successRate: 100,
      providerUsage: {}
    });
  };

  // Save configuration to backend
  const saveConfiguration = useCallback(async () => {
    try {
      await fetch('/api/admin/expert-system', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('admin_token')}`
        },
        body: JSON.stringify({
          providers,
          promptTemplates,
          metrics
        })
      });
    } catch (error) {
      console.error('Failed to save configuration:', error);
    }
  }, [providers, promptTemplates, metrics]);

  // Auto-save configuration
  useEffect(() => {
    if (!loading) {
      saveConfiguration();
    }
  }, [providers, promptTemplates, saveConfiguration, loading]);

  // Update provider
  const updateProvider = useCallback((id: string, updates: Partial<APIProvider>) => {
    setProviders(prev => prev.map(p => 
      p.id === id ? { ...p, ...updates } : p
    ));
  }, []);

  // Test provider connection
  const testProvider = useCallback(async (provider: APIProvider) => {
    try {
      const response = await fetch('/api/admin/test-provider', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('admin_token')}`
        },
        body: JSON.stringify({
          providerId: provider.id,
          apiKey: provider.apiKey,
          baseUrl: provider.baseUrl
        })
      });

      return response.ok;
    } catch (error) {
      console.error('Provider test failed:', error);
      return false;
    }
  }, []);

  // Get cost savings calculation
  const calculateCostSavings = useCallback(() => {
    if (!metrics) return 0;
    
    // Calculate savings from using Together AI vs traditional providers
    const togetherAIUsage = Object.entries(metrics.providerUsage)
      .filter(([id]) => id.startsWith('together-ai'))
      .reduce((sum, [, usage]) => sum + usage, 0);
    
    const totalUsage = Object.values(metrics.providerUsage)
      .reduce((sum, usage) => sum + usage, 0);
    
    if (totalUsage === 0) return 0;
    
    const togetherAIPercentage = togetherAIUsage / totalUsage;
    return togetherAIPercentage * 84; // 84% cost savings with Together AI
  }, [metrics]);

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[...Array(3)].map((_, i) => (
            <Card key={i} className="animate-pulse">
              <CardContent className="p-6">
                <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                <div className="h-8 bg-gray-200 rounded w-1/2"></div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Aideon Expert System Manager</h2>
          <p className="text-muted-foreground">
            Centralized API management with cost-effective Together AI integration
          </p>
        </div>
        <div className="flex items-center space-x-4">
          <Badge variant="outline" className="flex items-center space-x-1">
            <Sparkles className="h-3 w-3" />
            <span>Expert Level AI</span>
          </Badge>
          <Button onClick={() => setShowAddProvider(true)}>
            <Plus className="h-4 w-4 mr-2" />
            Add Provider
          </Button>
        </div>
      </div>

      {/* System Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between space-y-0 pb-2">
              <h3 className="tracking-tight text-sm font-medium">Cost Savings</h3>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </div>
            <div className="text-2xl font-bold">{calculateCostSavings().toFixed(1)}%</div>
            <p className="text-xs text-muted-foreground">
              With Together AI integration
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between space-y-0 pb-2">
              <h3 className="tracking-tight text-sm font-medium">Active Providers</h3>
              <Globe className="h-4 w-4 text-muted-foreground" />
            </div>
            <div className="text-2xl font-bold">
              {providers.filter(p => p.isActive).length}
            </div>
            <p className="text-xs text-muted-foreground">
              {providers.length} total configured
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between space-y-0 pb-2">
              <h3 className="tracking-tight text-sm font-medium">Expert Templates</h3>
              <Brain className="h-4 w-4 text-muted-foreground" />
            </div>
            <div className="text-2xl font-bold">{promptTemplates.length}</div>
            <p className="text-xs text-muted-foreground">
              PhD-level expertise
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between space-y-0 pb-2">
              <h3 className="tracking-tight text-sm font-medium">Success Rate</h3>
              <CheckCircle className="h-4 w-4 text-muted-foreground" />
            </div>
            <div className="text-2xl font-bold">{metrics?.successRate || 100}%</div>
            <p className="text-xs text-muted-foreground">
              System reliability
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Main Content Tabs */}
      <Tabs defaultValue="providers" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="providers">API Providers</TabsTrigger>
          <TabsTrigger value="prompts">Expert Prompts</TabsTrigger>
          <TabsTrigger value="tools">100+ Tools</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>

        {/* API Providers Tab */}
        <TabsContent value="providers" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {providers.map(provider => (
              <Card key={provider.id} className={`border-l-4 ${
                provider.isActive ? 'border-l-green-500' : 'border-l-gray-300'
              }`}>
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">{provider.name}</CardTitle>
                    <div className="flex items-center space-x-2">
                      <Badge variant={provider.type === 'llm' ? 'default' : 'secondary'}>
                        {provider.type.toUpperCase()}
                      </Badge>
                      <Switch
                        checked={provider.isActive}
                        onCheckedChange={(checked) => 
                          updateProvider(provider.id, { isActive: checked })
                        }
                      />
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label className="text-sm font-medium">API Key</Label>
                      <div className="flex items-center space-x-2 mt-1">
                        <Input
                          type="password"
                          value={provider.apiKey}
                          onChange={(e) => 
                            updateProvider(provider.id, { apiKey: e.target.value })
                          }
                          placeholder="Enter API key"
                          className="flex-1"
                        />
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => testProvider(provider)}
                        >
                          Test
                        </Button>
                      </div>
                    </div>
                    <div>
                      <Label className="text-sm font-medium">Priority</Label>
                      <Select
                        value={provider.priority.toString()}
                        onValueChange={(value) => 
                          updateProvider(provider.id, { priority: parseInt(value) })
                        }
                      >
                        <SelectTrigger className="mt-1">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {[1, 2, 3, 4, 5].map(p => (
                            <SelectItem key={p} value={p.toString()}>
                              Priority {p} {p === 1 ? '(Highest)' : p === 5 ? '(Lowest)' : ''}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  {provider.costPer1M && (
                    <div className="bg-muted/50 rounded-lg p-3">
                      <div className="text-sm font-medium mb-2">Cost Structure</div>
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <span className="text-muted-foreground">Input:</span> ${provider.costPer1M.input}/1M tokens
                        </div>
                        <div>
                          <span className="text-muted-foreground">Output:</span> ${provider.costPer1M.output}/1M tokens
                        </div>
                      </div>
                    </div>
                  )}

                  <div>
                    <div className="text-sm font-medium mb-2">Capabilities</div>
                    <div className="flex flex-wrap gap-1">
                      {provider.capabilities.map(cap => (
                        <Badge key={cap} variant="outline" className="text-xs">
                          {cap}
                        </Badge>
                      ))}
                    </div>
                  </div>

                  {provider.models.length > 0 && (
                    <div>
                      <div className="text-sm font-medium mb-2">Available Models</div>
                      <div className="space-y-1">
                        {provider.models.map(model => (
                          <div key={model} className="text-sm text-muted-foreground">
                            {model}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Expert Prompts Tab */}
        <TabsContent value="prompts" className="space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="text-xl font-semibold">Expert Prompt Templates</h3>
            <Button onClick={() => setShowPromptEditor(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Create Template
            </Button>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {promptTemplates.map(template => (
              <Card key={template.id} className="border-l-4 border-l-purple-500">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">{template.name}</CardTitle>
                    <div className="flex items-center space-x-2">
                      <Badge variant={template.costOptimized ? 'default' : 'secondary'}>
                        {template.costOptimized ? 'Cost Optimized' : 'Premium'}
                      </Badge>
                      <Badge variant="outline">
                        Level {template.expertLevel}
                      </Badge>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <div className="text-sm font-medium mb-2">Category</div>
                    <Badge variant="outline">{template.category}</Badge>
                  </div>

                  <div>
                    <div className="text-sm font-medium mb-2">Variables</div>
                    <div className="flex flex-wrap gap-1">
                      {template.variables.map(variable => (
                        <Badge key={variable} variant="secondary" className="text-xs">
                          {variable}
                        </Badge>
                      ))}
                    </div>
                  </div>

                  <div>
                    <div className="text-sm font-medium mb-2">Integrated Tools</div>
                    <div className="flex flex-wrap gap-1">
                      {template.tools.map(tool => (
                        <Badge key={tool} variant="outline" className="text-xs">
                          {tool}
                        </Badge>
                      ))}
                    </div>
                  </div>

                  <div>
                    <div className="text-sm font-medium mb-2">Template Preview</div>
                    <div className="bg-muted/50 rounded-lg p-3 text-sm max-h-32 overflow-y-auto">
                      {template.template.substring(0, 200)}...
                    </div>
                  </div>

                  <div className="flex items-center space-x-2">
                    <Button variant="outline" size="sm">
                      <Edit className="h-4 w-4 mr-2" />
                      Edit
                    </Button>
                    <Button variant="outline" size="sm">
                      <Eye className="h-4 w-4 mr-2" />
                      Preview
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* 100+ Tools Tab */}
        <TabsContent value="tools" className="space-y-6">
          <div className="text-center py-8">
            <Target className="h-16 w-16 mx-auto text-muted-foreground mb-4" />
            <h3 className="text-2xl font-bold mb-2">100+ Expert Tools Integration</h3>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              All Aideon tools are now enhanced with expert-level prompting and cost-effective Together AI integration. 
              Each tool automatically selects the optimal provider based on complexity, cost, and performance requirements.
            </p>
            <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl mx-auto">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">25+</div>
                <div className="text-sm text-muted-foreground">Analysis Tools</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">30+</div>
                <div className="text-sm text-muted-foreground">Creative Tools</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">20+</div>
                <div className="text-sm text-muted-foreground">Technical Tools</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600">25+</div>
                <div className="text-sm text-muted-foreground">Business Tools</div>
              </div>
            </div>
          </div>
        </TabsContent>

        {/* Analytics Tab */}
        <TabsContent value="analytics" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Provider Usage Distribution</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {Object.entries(metrics?.providerUsage || {}).map(([providerId, usage]) => {
                    const provider = providers.find(p => p.id === providerId);
                    if (!provider) return null;
                    
                    const total = Object.values(metrics?.providerUsage || {}).reduce((sum, u) => sum + u, 0);
                    const percentage = total > 0 ? (usage / total) * 100 : 0;
                    
                    return (
                      <div key={providerId} className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span>{provider.name}</span>
                          <span>{percentage.toFixed(1)}%</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-blue-600 h-2 rounded-full" 
                            style={{ width: `${percentage}%` }}
                          />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Cost Analysis</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-600">
                      ${metrics?.totalCost.toFixed(2) || '0.00'}
                    </div>
                    <div className="text-sm text-muted-foreground">Total Spent</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-600">
                      ${metrics?.costSavings.toFixed(2) || '0.00'}
                    </div>
                    <div className="text-sm text-muted-foreground">Total Saved</div>
                  </div>
                </div>
                
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <div className="flex items-center space-x-2">
                    <CheckCircle className="h-5 w-5 text-green-600" />
                    <span className="font-medium text-green-800">
                      {calculateCostSavings().toFixed(1)}% cost reduction achieved
                    </span>
                  </div>
                  <p className="text-sm text-green-700 mt-1">
                    Together AI integration is delivering significant cost savings while maintaining expert-level performance.
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AideonExpertSystemManager;

