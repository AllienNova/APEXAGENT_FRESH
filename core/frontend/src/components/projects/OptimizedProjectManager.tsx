import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { 
  Plus,
  Calendar,
  Clock,
  CheckCircle,
  AlertCircle,
  Brain,
  Zap,
  Users,
  Target,
  TrendingUp,
  BarChart3,
  Settings,
  Play,
  Pause,
  Square,
  Edit,
  Trash2,
  Eye,
  Sparkles
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

interface Task {
  id: string;
  title: string;
  description: string;
  status: 'pending' | 'in-progress' | 'completed' | 'blocked';
  priority: 'low' | 'medium' | 'high' | 'critical';
  assignee?: string;
  dueDate?: Date;
  estimatedHours?: number;
  actualHours?: number;
  tags: string[];
  aiInsights?: {
    complexity: number;
    suggestedModel: string;
    estimatedCost: number;
    recommendations: string[];
  };
}

interface Project {
  id: string;
  name: string;
  description: string;
  status: 'planning' | 'active' | 'completed' | 'on-hold';
  progress: number;
  startDate: Date;
  endDate?: Date;
  budget?: number;
  spent?: number;
  tasks: Task[];
  team: string[];
  aiAnalysis?: {
    riskLevel: 'low' | 'medium' | 'high';
    completionPrediction: Date;
    budgetPrediction: number;
    recommendations: string[];
  };
}

interface OptimizedProjectManagerProps {
  className?: string;
}

export const OptimizedProjectManager: React.FC<OptimizedProjectManagerProps> = ({ 
  className = "" 
}) => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProject, setSelectedProject] = useState<string | null>(null);
  const [showCreateProject, setShowCreateProject] = useState(false);
  const [showCreateTask, setShowCreateTask] = useState(false);
  const [loading, setLoading] = useState(true);
  const [aiAnalysisLoading, setAiAnalysisLoading] = useState(false);

  // Load projects from API/localStorage
  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      // Try to load from API first
      const response = await fetch('/api/projects', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setProjects(data);
      } else {
        // Fallback to localStorage
        const savedProjects = localStorage.getItem('aideon_projects');
        if (savedProjects) {
          setProjects(JSON.parse(savedProjects));
        } else {
          // Initialize with sample project
          const sampleProject = createSampleProject();
          setProjects([sampleProject]);
        }
      }
    } catch (error) {
      console.error('Failed to load projects:', error);
      // Use sample data
      const sampleProject = createSampleProject();
      setProjects([sampleProject]);
    } finally {
      setLoading(false);
    }
  };

  const createSampleProject = (): Project => ({
    id: 'aideon-ai-lite',
    name: 'Aideon AI Lite Production',
    description: 'Complete production deployment of Aideon AI Lite with Together AI integration',
    status: 'active',
    progress: 61.5,
    startDate: new Date('2025-06-01'),
    endDate: new Date('2025-07-15'),
    budget: 50000,
    spent: 8500,
    team: ['Lead Architect', 'Frontend Dev', 'Backend Dev', 'DevOps'],
    tasks: [
      {
        id: 'task-1',
        title: 'Complete Phase 1 GCP Foundation',
        description: 'Finish remaining Phase 1 tasks including frontend optimization',
        status: 'in-progress',
        priority: 'high',
        assignee: 'Lead Architect',
        dueDate: new Date('2025-06-15'),
        estimatedHours: 40,
        actualHours: 32,
        tags: ['gcp', 'foundation', 'phase-1'],
        aiInsights: {
          complexity: 7,
          suggestedModel: 'meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo',
          estimatedCost: 2.50,
          recommendations: [
            'Focus on React component optimization',
            'Integrate Together AI cost tracking',
            'Complete Firebase setup'
          ]
        }
      },
      {
        id: 'task-2',
        title: 'Implement Together AI Integration',
        description: 'Full integration of Together AI with 84% cost reduction',
        status: 'pending',
        priority: 'critical',
        assignee: 'Backend Dev',
        dueDate: new Date('2025-06-20'),
        estimatedHours: 60,
        tags: ['together-ai', 'integration', 'cost-optimization'],
        aiInsights: {
          complexity: 9,
          suggestedModel: 'meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo',
          estimatedCost: 5.25,
          recommendations: [
            'Start with provider abstraction layer',
            'Implement fallback mechanisms',
            'Add comprehensive monitoring'
          ]
        }
      },
      {
        id: 'task-3',
        title: 'Deploy Production Infrastructure',
        description: 'Complete deployment with monitoring and scaling',
        status: 'pending',
        priority: 'high',
        assignee: 'DevOps',
        dueDate: new Date('2025-07-01'),
        estimatedHours: 80,
        tags: ['deployment', 'infrastructure', 'monitoring'],
        aiInsights: {
          complexity: 8,
          suggestedModel: 'meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo',
          estimatedCost: 3.75,
          recommendations: [
            'Use Firebase hosting for frontend',
            'Implement auto-scaling',
            'Set up comprehensive monitoring'
          ]
        }
      }
    ],
    aiAnalysis: {
      riskLevel: 'medium',
      completionPrediction: new Date('2025-07-10'),
      budgetPrediction: 42000,
      recommendations: [
        'Together AI integration will reduce operational costs by 84%',
        'Consider parallel development of Phase 2 features',
        'Allocate more resources to testing and optimization'
      ]
    }
  });

  // AI-powered project analysis
  const analyzeProjectWithAI = useCallback(async (project: Project) => {
    setAiAnalysisLoading(true);
    
    try {
      const response = await fetch('/api/ai/analyze-project', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        },
        body: JSON.stringify({
          project: {
            name: project.name,
            description: project.description,
            tasks: project.tasks.map(t => ({
              title: t.title,
              description: t.description,
              status: t.status,
              priority: t.priority,
              estimatedHours: t.estimatedHours,
              actualHours: t.actualHours
            })),
            progress: project.progress,
            budget: project.budget,
            spent: project.spent
          }
        })
      });

      if (response.ok) {
        const analysis = await response.json();
        
        // Update project with AI analysis
        setProjects(prev => prev.map(p => 
          p.id === project.id 
            ? { ...p, aiAnalysis: analysis }
            : p
        ));
      }
    } catch (error) {
      console.error('AI analysis failed:', error);
    } finally {
      setAiAnalysisLoading(false);
    }
  }, []);

  // Get task status color
  const getStatusColor = (status: Task['status']) => {
    switch (status) {
      case 'completed': return 'bg-green-500';
      case 'in-progress': return 'bg-blue-500';
      case 'blocked': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  // Get priority color
  const getPriorityColor = (priority: Task['priority']) => {
    switch (priority) {
      case 'critical': return 'destructive';
      case 'high': return 'default';
      case 'medium': return 'secondary';
      default: return 'outline';
    }
  };

  const currentProject = projects.find(p => p.id === selectedProject) || projects[0];

  if (loading) {
    return (
      <div className={`space-y-6 ${className}`}>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
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
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Project Manager</h2>
          <p className="text-muted-foreground">
            AI-powered project management with Together AI insights
          </p>
        </div>
        <div className="flex items-center space-x-4">
          <Button onClick={() => setShowCreateProject(true)}>
            <Plus className="h-4 w-4 mr-2" />
            New Project
          </Button>
        </div>
      </div>

      {/* Project Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between space-y-0 pb-2">
              <h3 className="tracking-tight text-sm font-medium">Active Projects</h3>
              <Target className="h-4 w-4 text-muted-foreground" />
            </div>
            <div className="text-2xl font-bold">{projects.filter(p => p.status === 'active').length}</div>
            <p className="text-xs text-muted-foreground">
              {projects.filter(p => p.status === 'completed').length} completed
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between space-y-0 pb-2">
              <h3 className="tracking-tight text-sm font-medium">Total Tasks</h3>
              <CheckCircle className="h-4 w-4 text-muted-foreground" />
            </div>
            <div className="text-2xl font-bold">
              {projects.reduce((sum, p) => sum + p.tasks.length, 0)}
            </div>
            <p className="text-xs text-muted-foreground">
              {projects.reduce((sum, p) => sum + p.tasks.filter(t => t.status === 'completed').length, 0)} completed
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between space-y-0 pb-2">
              <h3 className="tracking-tight text-sm font-medium">Budget Efficiency</h3>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </div>
            <div className="text-2xl font-bold">84%</div>
            <p className="text-xs text-muted-foreground">
              Cost savings with Together AI
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between space-y-0 pb-2">
              <h3 className="tracking-tight text-sm font-medium">AI Insights</h3>
              <Brain className="h-4 w-4 text-muted-foreground" />
            </div>
            <div className="text-2xl font-bold">
              {projects.filter(p => p.aiAnalysis).length}
            </div>
            <p className="text-xs text-muted-foreground">
              Projects analyzed
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Project Selection and Details */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Project List */}
        <Card>
          <CardHeader>
            <CardTitle>Projects</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {projects.map(project => (
              <div
                key={project.id}
                className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                  selectedProject === project.id ? 'border-primary bg-primary/5' : 'hover:bg-muted/50'
                }`}
                onClick={() => setSelectedProject(project.id)}
              >
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-semibold">{project.name}</h4>
                  <Badge variant={project.status === 'active' ? 'default' : 'secondary'}>
                    {project.status}
                  </Badge>
                </div>
                <div className="space-y-2">
                  <Progress value={project.progress} className="h-2" />
                  <div className="flex justify-between text-sm text-muted-foreground">
                    <span>{project.progress.toFixed(1)}% complete</span>
                    <span>{project.tasks.length} tasks</span>
                  </div>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Project Details */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center space-x-2">
                <span>{currentProject?.name}</span>
                {currentProject?.aiAnalysis && (
                  <Badge variant="outline" className="flex items-center space-x-1">
                    <Sparkles className="h-3 w-3" />
                    <span>AI Analyzed</span>
                  </Badge>
                )}
              </CardTitle>
              <div className="flex items-center space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => currentProject && analyzeProjectWithAI(currentProject)}
                  disabled={aiAnalysisLoading}
                >
                  {aiAnalysisLoading ? (
                    <div className="animate-spin h-4 w-4 border-2 border-current border-t-transparent rounded-full" />
                  ) : (
                    <Brain className="h-4 w-4" />
                  )}
                  AI Analysis
                </Button>
                <Button size="sm" onClick={() => setShowCreateTask(true)}>
                  <Plus className="h-4 w-4 mr-2" />
                  Add Task
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-6">
            {currentProject && (
              <>
                {/* Project Stats */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-600">
                      {currentProject.progress.toFixed(1)}%
                    </div>
                    <div className="text-sm text-muted-foreground">Progress</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-600">
                      {currentProject.tasks.filter(t => t.status === 'completed').length}
                    </div>
                    <div className="text-sm text-muted-foreground">Completed</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-orange-600">
                      {currentProject.tasks.filter(t => t.status === 'in-progress').length}
                    </div>
                    <div className="text-sm text-muted-foreground">In Progress</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-purple-600">
                      {currentProject.budget && currentProject.spent 
                        ? `$${(currentProject.budget - currentProject.spent).toLocaleString()}`
                        : 'N/A'
                      }
                    </div>
                    <div className="text-sm text-muted-foreground">Remaining</div>
                  </div>
                </div>

                {/* AI Analysis */}
                {currentProject.aiAnalysis && (
                  <Card className="border-blue-200 bg-blue-50/50">
                    <CardHeader className="pb-3">
                      <CardTitle className="text-lg flex items-center space-x-2">
                        <Brain className="h-5 w-5 text-blue-600" />
                        <span>AI Project Analysis</span>
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div>
                          <div className="text-sm font-medium mb-1">Risk Level</div>
                          <Badge variant={
                            currentProject.aiAnalysis.riskLevel === 'high' ? 'destructive' :
                            currentProject.aiAnalysis.riskLevel === 'medium' ? 'default' : 'secondary'
                          }>
                            {currentProject.aiAnalysis.riskLevel}
                          </Badge>
                        </div>
                        <div>
                          <div className="text-sm font-medium mb-1">Predicted Completion</div>
                          <div className="text-sm">
                            {currentProject.aiAnalysis.completionPrediction.toLocaleDateString()}
                          </div>
                        </div>
                        <div>
                          <div className="text-sm font-medium mb-1">Budget Prediction</div>
                          <div className="text-sm">
                            ${currentProject.aiAnalysis.budgetPrediction.toLocaleString()}
                          </div>
                        </div>
                      </div>
                      <div>
                        <div className="text-sm font-medium mb-2">AI Recommendations</div>
                        <ul className="space-y-1">
                          {currentProject.aiAnalysis.recommendations.map((rec, index) => (
                            <li key={index} className="text-sm flex items-start space-x-2">
                              <Zap className="h-3 w-3 mt-0.5 text-blue-600 flex-shrink-0" />
                              <span>{rec}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </CardContent>
                  </Card>
                )}

                {/* Tasks */}
                <div>
                  <h4 className="font-semibold mb-4">Tasks</h4>
                  <div className="space-y-3">
                    {currentProject.tasks.map(task => (
                      <Card key={task.id} className="border-l-4" style={{
                        borderLeftColor: task.status === 'completed' ? '#10b981' :
                                        task.status === 'in-progress' ? '#3b82f6' :
                                        task.status === 'blocked' ? '#ef4444' : '#6b7280'
                      }}>
                        <CardContent className="p-4">
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <div className="flex items-center space-x-2 mb-2">
                                <h5 className="font-medium">{task.title}</h5>
                                <Badge variant={getPriorityColor(task.priority)}>
                                  {task.priority}
                                </Badge>
                                <Badge variant="outline">
                                  {task.status}
                                </Badge>
                              </div>
                              <p className="text-sm text-muted-foreground mb-3">
                                {task.description}
                              </p>
                              
                              {task.aiInsights && (
                                <div className="bg-muted/50 rounded-lg p-3 mb-3">
                                  <div className="flex items-center space-x-2 mb-2">
                                    <Sparkles className="h-4 w-4 text-purple-600" />
                                    <span className="text-sm font-medium">AI Insights</span>
                                  </div>
                                  <div className="grid grid-cols-2 gap-4 text-xs">
                                    <div>
                                      <span className="font-medium">Complexity:</span> {task.aiInsights.complexity}/10
                                    </div>
                                    <div>
                                      <span className="font-medium">Est. Cost:</span> ${task.aiInsights.estimatedCost}
                                    </div>
                                  </div>
                                  <div className="mt-2">
                                    <div className="text-xs font-medium mb-1">Recommendations:</div>
                                    <ul className="text-xs space-y-1">
                                      {task.aiInsights.recommendations.map((rec, index) => (
                                        <li key={index} className="flex items-start space-x-1">
                                          <span>•</span>
                                          <span>{rec}</span>
                                        </li>
                                      ))}
                                    </ul>
                                  </div>
                                </div>
                              )}
                              
                              <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                                {task.assignee && (
                                  <span className="flex items-center space-x-1">
                                    <Users className="h-3 w-3" />
                                    <span>{task.assignee}</span>
                                  </span>
                                )}
                                {task.dueDate && (
                                  <span className="flex items-center space-x-1">
                                    <Calendar className="h-3 w-3" />
                                    <span>{task.dueDate.toLocaleDateString()}</span>
                                  </span>
                                )}
                                {task.estimatedHours && (
                                  <span className="flex items-center space-x-1">
                                    <Clock className="h-3 w-3" />
                                    <span>{task.actualHours || 0}/{task.estimatedHours}h</span>
                                  </span>
                                )}
                              </div>
                            </div>
                            <div className="flex items-center space-x-2">
                              <Button variant="ghost" size="sm">
                                <Edit className="h-4 w-4" />
                              </Button>
                              <Button variant="ghost" size="sm">
                                <Eye className="h-4 w-4" />
                              </Button>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </div>
              </>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default OptimizedProjectManager;

