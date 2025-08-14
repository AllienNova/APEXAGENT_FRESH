import React, { useState } from 'react';

interface DashboardProps {
  username?: string;
}

interface ProjectSummary {
  id: string;
  name: string;
  lastModified: string;
  status: 'active' | 'completed' | 'archived';
  progress: number;
}

interface ActivityItem {
  id: string;
  type: 'file' | 'conversation' | 'system' | 'plugin';
  action: string;
  details: string;
  timestamp: string;
  project?: string;
}

interface ResourceUsage {
  cpu: number;
  memory: number;
  disk: number;
  network: number;
}

const Dashboard: React.FC<DashboardProps> = ({
  username = 'User'
}) => {
  // Sample data for demonstration
  const [projects, setProjects] = useState<ProjectSummary[]>([
    { id: '1', name: 'Website Redesign', lastModified: '2 hours ago', status: 'active', progress: 65 },
    { id: '2', name: 'Data Analysis', lastModified: 'yesterday', status: 'active', progress: 30 },
    { id: '3', name: 'Research Paper', lastModified: '3 days ago', status: 'completed', progress: 100 },
    { id: '4', name: 'Marketing Campaign', lastModified: 'last week', status: 'archived', progress: 100 }
  ]);
  
  const [recentActivity, setRecentActivity] = useState<ActivityItem[]>([
    { id: '1', type: 'conversation', action: 'Message', details: 'Analyzed quarterly sales data', timestamp: '10:32 AM', project: 'Data Analysis' },
    { id: '2', type: 'file', action: 'Created', details: '/home/user/documents/sales_analysis_summary.md', timestamp: '10:32 AM', project: 'Data Analysis' },
    { id: '3', type: 'system', action: 'Executed', details: 'python analyze.py', timestamp: '10:31 AM', project: 'Data Analysis' },
    { id: '4', type: 'file', action: 'Read', details: '/home/user/documents/quarterly_sales.xlsx', timestamp: '10:30 AM', project: 'Data Analysis' },
    { id: '5', type: 'plugin', action: 'Activated', details: 'Data Visualizer plugin', timestamp: '10:29 AM', project: 'Data Analysis' }
  ]);
  
  const [resourceUsage, setResourceUsage] = useState<ResourceUsage>({
    cpu: 24,
    memory: 15,
    disk: 24,
    network: 8
  });
  
  const [activeTab, setActiveTab] = useState<'overview' | 'projects' | 'activity'>('overview');
  
  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'file': return '📄';
      case 'conversation': return '💬';
      case 'system': return '💻';
      case 'plugin': return '🧩';
      default: return '🔍';
    }
  };
  
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'completed': return 'bg-blue-100 text-blue-800';
      case 'archived': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const renderOverviewTab = () => (
    <div className="p-4">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
        <div className="bg-card border border-border rounded-lg p-4">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-medium">Active Projects</h3>
            <span className="text-2xl">2</span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">2 in progress</span>
            <button className="text-primary hover:underline">View all</button>
          </div>
        </div>
        
        <div className="bg-card border border-border rounded-lg p-4">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-medium">Recent Files</h3>
            <span className="text-2xl">12</span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">3 modified today</span>
            <button className="text-primary hover:underline">View all</button>
          </div>
        </div>
        
        <div className="bg-card border border-border rounded-lg p-4">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-medium">Active Plugins</h3>
            <span className="text-2xl">3</span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">1 recently added</span>
            <button className="text-primary hover:underline">Manage</button>
          </div>
        </div>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <div className="bg-card border border-border rounded-lg p-4 mb-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-medium">Recent Activity</h3>
              <button className="text-primary hover:underline text-sm">View all</button>
            </div>
            
            <div className="space-y-3">
              {recentActivity.slice(0, 3).map(activity => (
                <div key={activity.id} className="flex items-start gap-3 p-2 hover:bg-accent/20 rounded-md">
                  <div className="text-lg">{getActivityIcon(activity.type)}</div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <div className="font-medium text-sm">{activity.action}</div>
                      <div className="text-xs text-muted-foreground">{activity.timestamp}</div>
                    </div>
                    <div className="text-xs text-muted-foreground truncate">{activity.details}</div>
                    {activity.project && (
                      <div className="text-xs text-primary mt-1">{activity.project}</div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
          
          <div className="bg-card border border-border rounded-lg p-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-medium">Active Projects</h3>
              <button className="text-primary hover:underline text-sm">View all</button>
            </div>
            
            <div className="space-y-4">
              {projects.filter(p => p.status === 'active').map(project => (
                <div key={project.id} className="border border-border rounded-md p-3">
                  <div className="flex items-center justify-between mb-2">
                    <div className="font-medium">{project.name}</div>
                    <div className="px-2 py-0.5 rounded-full text-xs ${getStatusColor(project.status)}">
                      {project.status.charAt(0).toUpperCase() + project.status.slice(1)}
                    </div>
                  </div>
                  <div className="flex items-center justify-between text-xs text-muted-foreground mb-2">
                    <span>Progress</span>
                    <span>{project.progress}%</span>
                  </div>
                  <div className="h-1.5 bg-muted rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-primary rounded-full" 
                      style={{width: `${project.progress}%`}}
                    ></div>
                  </div>
                  <div className="text-xs text-muted-foreground mt-2">
                    Last modified {project.lastModified}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
        
        <div className="lg:col-span-1">
          <div className="bg-card border border-border rounded-lg p-4 mb-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-medium">System Resources</h3>
              <button className="text-primary hover:underline text-sm">Details</button>
            </div>
            
            <div className="space-y-4">
              <div>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm">CPU Usage</span>
                  <span className="text-sm">{resourceUsage.cpu}%</span>
                </div>
                <div className="h-1.5 bg-muted rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-blue-500 rounded-full" 
                    style={{width: `${resourceUsage.cpu}%`}}
                  ></div>
                </div>
              </div>
              
              <div>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm">Memory Usage</span>
                  <span className="text-sm">{resourceUsage.memory}%</span>
                </div>
                <div className="h-1.5 bg-muted rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-purple-500 rounded-full" 
                    style={{width: `${resourceUsage.memory}%`}}
                  ></div>
                </div>
              </div>
              
              <div>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm">Disk Usage</span>
                  <span className="text-sm">{resourceUsage.disk}%</span>
                </div>
                <div className="h-1.5 bg-muted rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-amber-500 rounded-full" 
                    style={{width: `${resourceUsage.disk}%`}}
                  ></div>
                </div>
              </div>
              
              <div>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm">Network</span>
                  <span className="text-sm">{resourceUsage.network}%</span>
                </div>
                <div className="h-1.5 bg-muted rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-green-500 rounded-full" 
                    style={{width: `${resourceUsage.network}%`}}
                  ></div>
                </div>
              </div>
            </div>
          </div>
          
          <div className="bg-card border border-border rounded-lg p-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-medium">Quick Actions</h3>
            </div>
            
            <div className="grid grid-cols-2 gap-2">
              <button className="flex flex-col items-center justify-center p-3 bg-accent/20 rounded-md hover:bg-accent/30">
                <span className="text-xl mb-1">📁</span>
                <span className="text-xs">New Project</span>
              </button>
              
              <button className="flex flex-col items-center justify-center p-3 bg-accent/20 rounded-md hover:bg-accent/30">
                <span className="text-xl mb-1">💬</span>
                <span className="text-xs">New Chat</span>
              </button>
              
              <button className="flex flex-col items-center justify-center p-3 bg-accent/20 rounded-md hover:bg-accent/30">
                <span className="text-xl mb-1">🧩</span>
                <span className="text-xs">Add Plugin</span>
              </button>
              
              <button className="flex flex-col items-center justify-center p-3 bg-accent/20 rounded-md hover:bg-accent/30">
                <span className="text-xl mb-1">⚙️</span>
                <span className="text-xs">Settings</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
  
  const renderProjectsTab = () => (
    <div className="p-4">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <h2 className="text-xl font-semibold">Projects</h2>
          <span className="px-2 py-0.5 bg-primary/10 text-primary rounded-full text-xs">
            {projects.length} total
          </span>
        </div>
        <button className="px-3 py-1.5 bg-primary text-primary-foreground rounded-md text-sm flex items-center gap-1">
          <span>+</span>
          <span>New Project</span>
        </button>
      </div>
      
      <div className="flex items-center space-x-2 mb-4">
        <button className="px-3 py-1 bg-primary text-primary-foreground rounded-md text-sm">All</button>
        <button className="px-3 py-1 hover:bg-accent rounded-md text-sm">Active</button>
        <button className="px-3 py-1 hover:bg-accent rounded-md text-sm">Completed</button>
        <button className="px-3 py-1 hover:bg-accent rounded-md text-sm">Archived</button>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {projects.map(project => (
          <div key={project.id} className="bg-card border border-border rounded-lg p-4 hover:border-primary transition-colors">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-medium">{project.name}</h3>
              <div className={`px-2 py-0.5 rounded-full text-xs ${getStatusColor(project.status)}`}>
                {project.status.charAt(0).toUpperCase() + project.status.slice(1)}
              </div>
            </div>
            
            <div className="flex items-center justify-between text-xs text-muted-foreground mb-2">
              <span>Progress</span>
              <span>{project.progress}%</span>
            </div>
            <div className="h-1.5 bg-muted rounded-full overflow-hidden mb-4">
              <div 
                className="h-full bg-primary rounded-full" 
                style={{width: `${project.progress}%`}}
              ></div>
            </div>
            
            <div className="flex items-center justify-between">
              <div className="text-xs text-muted-foreground">
                Last modified {project.lastModified}
              </div>
              <button className="text-xs text-primary hover:underline">Open</button>
            </div>
          </div>
        ))}
        
        <div className="bg-accent/10 border border-dashed border-border rounded-lg p-4 flex flex-col items-center justify-center text-center">
          <div className="w-10 h-10 rounded-full bg-accent/20 flex items-center justify-center text-xl mb-2">
            +
          </div>
          <h3 className="font-medium mb-1">Create New Project</h3>
          <p className="text-xs text-muted-foreground mb-3">
            Start a new project to organize your work
          </p>
          <button className="px-3 py-1.5 bg-primary text-primary-foreground rounded-md text-sm">
            New Project
          </button>
        </div>
      </div>
    </div>
  );
  
  const renderActivityTab = () => (
    <div className="p-4">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <h2 className="text-xl font-semibold">Activity</h2>
          <span className="px-2 py-0.5 bg-primary/10 text-primary rounded-full text-xs">
            Today
          </span>
        </div>
        <div className="flex items-center space-x-2">
          <button className="px-2 py-1 bg-accent/20 rounded-md text-xs">Filter</button>
          <button className="px-2 py-1 bg-accent/20 rounded-md text-xs">Export</button>
        </div>
      </div>
      
      <div className="flex items-center space-x-2 mb-4">
        <button className="px-3 py-1 bg-primary text-primary-foreground rounded-md text-sm">All</button>
        <button className="px-3 py-1 hover:bg-accent rounded-md text-sm flex items-center gap-1">
          <span>📄</span>
          <span>Files</span>
        </button>
        <button className="px-3 py-1 hover:bg-accent rounded-md text-sm flex items-center gap-1">
          <span>💬</span>
          <span>Conversations</span>
        </button>
        <button className="px-3 py-1 hover:bg-accent rounded-md text-sm flex items-center gap-1">
          <span>💻</span>
          <span>System</span>
        </button>
      </div>
      
      <div className="bg-card border border-border rounded-lg">
        <div className="p-3 border-b border-border flex items-center justify-between text-sm font-medium">
          <div className="w-8"></div>
          <div className="flex-1">Action</div>
          <div className="flex-1">Details</div>
          <div className="w-24 text-right">Time</div>
        </div>
        
        {recentActivity.map(activity => (
          <div key={activity.id} className="p-3 border-b border-border flex items-center hover:bg-accent/10">
            <div className="w-8 text-lg">{getActivityIcon(activity.type)}</div>
            <div className="flex-1">
              <div className="font-medium text-sm">{activity.action}</div>
              {activity.project && (
                <div className="text-xs text-primary">{activity.project}</div>
              )}
            </div>
            <div className="flex-1 text-sm truncate">{activity.details}</div>
            <div className="w-24 text-right text-xs text-muted-foreground">{activity.timestamp}</div>
          </div>
        ))}
      </div>
      
      <div className="mt-4 flex items-center justify-between">
        <button className="px-3 py-1.5 border border-border rounded-md text-sm hover:bg-accent/10">
          Previous
        </button>
        <div className="text-sm">Page 1 of 1</div>
        <button className="px-3 py-1.5 border border-border rounded-md text-sm hover:bg-accent/10">
          Next
        </button>
      </div>
    </div>
  );

  return (
    <div className="h-full flex flex-col">
      <div className="border-b border-border p-4">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-2xl font-bold">Welcome back, {username}</h1>
          <div className="text-sm text-muted-foreground">
            {new Date().toLocaleDateString(undefined, { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
          </div>
        </div>
        
        <div className="flex items-center space-x-4">
          <button 
            className={`px-3 py-1.5 rounded-md text-sm ${activeTab === 'overview' ? 'bg-primary text-primary-foreground' : 'hover:bg-accent'}`}
            onClick={() => setActiveTab('overview')}
          >
            Overview
          </button>
          <button 
            className={`px-3 py-1.5 rounded-md text-sm ${activeTab === 'projects' ? 'bg-primary text-primary-foreground' : 'hover:bg-accent'}`}
            onClick={() => setActiveTab('projects')}
          >
            Projects
          </button>
          <button 
            className={`px-3 py-1.5 rounded-md text-sm ${activeTab === 'activity' ? 'bg-primary text-primary-foreground' : 'hover:bg-accent'}`}
            onClick={() => setActiveTab('activity')}
          >
            Activity
          </button>
        </div>
      </div>
      
      <div className="flex-1 overflow-auto">
        {activeTab === 'overview' && renderOverviewTab()}
        {activeTab === 'projects' && renderProjectsTab()}
        {activeTab === 'activity' && renderActivityTab()}
      </div>
    </div>
  );
};

export default Dashboard;
