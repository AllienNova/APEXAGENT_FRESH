import React, { useState } from 'react';

interface SystemActivityMonitorProps {
  collapsed?: boolean;
  onToggleCollapse?: () => void;
}

const SystemActivityMonitor: React.FC<SystemActivityMonitorProps> = ({
  collapsed = false,
  onToggleCollapse
}) => {
  const [activeTab, setActiveTab] = useState('activity');
  const [filterType, setFilterType] = useState('all');

  // Sample activity data
  const activities = [
    { id: 1, type: 'file', action: 'read', path: '/home/user/documents/report.docx', timestamp: '10:32:45', status: 'success' },
    { id: 2, type: 'shell', action: 'execute', command: 'python analyze.py', timestamp: '10:32:30', status: 'success' },
    { id: 3, type: 'file', action: 'write', path: '/home/user/documents/results.csv', timestamp: '10:32:15', status: 'success' },
    { id: 4, type: 'network', action: 'request', url: 'https://api.example.com/data', timestamp: '10:31:50', status: 'success' },
    { id: 5, type: 'file', action: 'create', path: '/home/user/downloads/image.jpg', timestamp: '10:31:20', status: 'success' }
  ];

  // Filter activities based on selected type
  const filteredActivities = filterType === 'all' 
    ? activities 
    : activities.filter(activity => activity.type === filterType);

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'file': return '📄';
      case 'shell': return '💻';
      case 'network': return '🌐';
      default: return '🔍';
    }
  };

  const getActionColor = (action: string) => {
    switch (action) {
      case 'read': return 'text-blue-600';
      case 'write': return 'text-amber-600';
      case 'create': return 'text-green-600';
      case 'delete': return 'text-red-600';
      case 'execute': return 'text-purple-600';
      case 'request': return 'text-cyan-600';
      default: return 'text-muted-foreground';
    }
  };

  return (
    <div className={`h-full flex flex-col ${collapsed ? 'w-16' : 'w-80'} transition-all duration-200`}>
      {/* Header */}
      <div className="p-3 border-b border-border flex items-center justify-between">
        {!collapsed && <h2 className="font-semibold text-sm">System Activity</h2>}
        <div className="flex items-center space-x-1">
          {!collapsed && (
            <button className="p-1 rounded-md hover:bg-accent text-muted-foreground" title="Clear">
              🗑️
            </button>
          )}
          <button 
            onClick={onToggleCollapse}
            className="p-1 rounded-md hover:bg-accent text-muted-foreground"
            title={collapsed ? "Expand panel" : "Collapse panel"}
          >
            {collapsed ? '◀' : '▶'}
          </button>
        </div>
      </div>

      {/* Tabs */}
      {!collapsed && (
        <div className="flex border-b border-border">
          <button 
            className={`flex-1 p-2 text-sm font-medium ${activeTab === 'activity' ? 'border-b-2 border-primary' : 'text-muted-foreground'}`}
            onClick={() => setActiveTab('activity')}
          >
            Activity
          </button>
          <button 
            className={`flex-1 p-2 text-sm font-medium ${activeTab === 'resources' ? 'border-b-2 border-primary' : 'text-muted-foreground'}`}
            onClick={() => setActiveTab('resources')}
          >
            Resources
          </button>
          <button 
            className={`flex-1 p-2 text-sm font-medium ${activeTab === 'permissions' ? 'border-b-2 border-primary' : 'text-muted-foreground'}`}
            onClick={() => setActiveTab('permissions')}
          >
            Permissions
          </button>
        </div>
      )}

      {/* Content */}
      <div className="flex-1 overflow-auto">
        {collapsed ? (
          <div className="flex flex-col items-center py-4 space-y-4">
            <button className="w-8 h-8 rounded-full bg-accent/30 flex items-center justify-center" title="Activity">
              🔍
            </button>
            <button className="w-8 h-8 rounded-full bg-accent/30 flex items-center justify-center" title="Resources">
              📊
            </button>
            <button className="w-8 h-8 rounded-full bg-accent/30 flex items-center justify-center" title="Permissions">
              🔒
            </button>
          </div>
        ) : (
          <>
            {activeTab === 'activity' && (
              <div className="p-3">
                <div className="mb-3 flex items-center justify-between">
                  <div className="flex items-center space-x-1">
                    <button 
                      className={`px-2 py-1 text-xs rounded-md ${filterType === 'all' ? 'bg-primary text-primary-foreground' : 'hover:bg-accent'}`}
                      onClick={() => setFilterType('all')}
                    >
                      All
                    </button>
                    <button 
                      className={`px-2 py-1 text-xs rounded-md ${filterType === 'file' ? 'bg-primary text-primary-foreground' : 'hover:bg-accent'}`}
                      onClick={() => setFilterType('file')}
                    >
                      Files
                    </button>
                    <button 
                      className={`px-2 py-1 text-xs rounded-md ${filterType === 'shell' ? 'bg-primary text-primary-foreground' : 'hover:bg-accent'}`}
                      onClick={() => setFilterType('shell')}
                    >
                      Shell
                    </button>
                    <button 
                      className={`px-2 py-1 text-xs rounded-md ${filterType === 'network' ? 'bg-primary text-primary-foreground' : 'hover:bg-accent'}`}
                      onClick={() => setFilterType('network')}
                    >
                      Network
                    </button>
                  </div>
                  <button className="text-xs text-primary hover:underline">
                    Export
                  </button>
                </div>

                <div className="space-y-2">
                  {filteredActivities.map((activity) => (
                    <div key={activity.id} className="bg-accent/10 rounded-md p-2">
                      <div className="flex items-center justify-between mb-1">
                        <div className="flex items-center gap-2">
                          <span className="text-lg">{getActivityIcon(activity.type)}</span>
                          <span className={`font-medium text-sm ${getActionColor(activity.action)}`}>
                            {activity.action.charAt(0).toUpperCase() + activity.action.slice(1)}
                          </span>
                        </div>
                        <span className="text-xs text-muted-foreground">{activity.timestamp}</span>
                      </div>
                      <div className="text-xs truncate">
                        {activity.type === 'file' && activity.path}
                        {activity.type === 'shell' && activity.command}
                        {activity.type === 'network' && activity.url}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {activeTab === 'resources' && (
              <div className="p-3">
                <div className="mb-3">
                  <h3 className="text-sm font-medium mb-2">System Resources</h3>
                  
                  <div className="space-y-3">
                    {/* CPU Usage */}
                    <div>
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs font-medium">CPU Usage</span>
                        <span className="text-xs">24%</span>
                      </div>
                      <div className="h-2 bg-muted rounded-full overflow-hidden">
                        <div className="h-full bg-blue-500 rounded-full" style={{width: '24%'}}></div>
                      </div>
                    </div>
                    
                    {/* Memory Usage */}
                    <div>
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs font-medium">Memory Usage</span>
                        <span className="text-xs">1.2 GB / 8 GB</span>
                      </div>
                      <div className="h-2 bg-muted rounded-full overflow-hidden">
                        <div className="h-full bg-purple-500 rounded-full" style={{width: '15%'}}></div>
                      </div>
                    </div>
                    
                    {/* Disk Usage */}
                    <div>
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs font-medium">Disk Usage</span>
                        <span className="text-xs">120 GB / 500 GB</span>
                      </div>
                      <div className="h-2 bg-muted rounded-full overflow-hidden">
                        <div className="h-full bg-amber-500 rounded-full" style={{width: '24%'}}></div>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div>
                  <h3 className="text-sm font-medium mb-2">Active Processes</h3>
                  <div className="bg-accent/10 rounded-md p-2">
                    <table className="w-full text-xs">
                      <thead>
                        <tr className="text-muted-foreground">
                          <th className="text-left pb-1">Process</th>
                          <th className="text-right pb-1">CPU</th>
                          <th className="text-right pb-1">Memory</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr>
                          <td className="py-1">ApexAgent</td>
                          <td className="text-right py-1">12%</td>
                          <td className="text-right py-1">450 MB</td>
                        </tr>
                        <tr>
                          <td className="py-1">LLM Engine</td>
                          <td className="text-right py-1">8%</td>
                          <td className="text-right py-1">350 MB</td>
                        </tr>
                        <tr>
                          <td className="py-1">File Indexer</td>
                          <td className="text-right py-1">4%</td>
                          <td className="text-right py-1">120 MB</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'permissions' && (
              <div className="p-3">
                <div className="mb-3">
                  <h3 className="text-sm font-medium mb-2">System Access</h3>
                  
                  <div className="space-y-2">
                    <div className="bg-accent/10 rounded-md p-2">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <span className="text-lg">📁</span>
                          <div>
                            <div className="text-sm font-medium">File System</div>
                            <div className="text-xs text-muted-foreground">Read and write files</div>
                          </div>
                        </div>
                        <div className="h-5 w-10 bg-primary rounded-full relative">
                          <div className="h-4 w-4 bg-white rounded-full absolute top-0.5 right-0.5"></div>
                        </div>
                      </div>
                    </div>
                    
                    <div className="bg-accent/10 rounded-md p-2">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <span className="text-lg">💻</span>
                          <div>
                            <div className="text-sm font-medium">Shell Commands</div>
                            <div className="text-xs text-muted-foreground">Execute system commands</div>
                          </div>
                        </div>
                        <div className="h-5 w-10 bg-primary rounded-full relative">
                          <div className="h-4 w-4 bg-white rounded-full absolute top-0.5 right-0.5"></div>
                        </div>
                      </div>
                    </div>
                    
                    <div className="bg-accent/10 rounded-md p-2">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <span className="text-lg">🌐</span>
                          <div>
                            <div className="text-sm font-medium">Network Access</div>
                            <div className="text-xs text-muted-foreground">Connect to internet</div>
                          </div>
                        </div>
                        <div className="h-5 w-10 bg-primary rounded-full relative">
                          <div className="h-4 w-4 bg-white rounded-full absolute top-0.5 right-0.5"></div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div>
                  <h3 className="text-sm font-medium mb-2">Directory Permissions</h3>
                  
                  <div className="space-y-2">
                    <div className="bg-accent/10 rounded-md p-2">
                      <div className="flex items-center justify-between mb-1">
                        <div className="text-sm font-medium">/home/user/documents</div>
                        <span className="px-2 py-0.5 bg-green-100 text-green-800 text-xs rounded-full">Full Access</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-xs px-1 bg-green-100 text-green-800 rounded">Read</span>
                        <span className="text-xs px-1 bg-green-100 text-green-800 rounded">Write</span>
                        <span className="text-xs px-1 bg-green-100 text-green-800 rounded">Execute</span>
                      </div>
                    </div>
                    
                    <div className="bg-accent/10 rounded-md p-2">
                      <div className="flex items-center justify-between mb-1">
                        <div className="text-sm font-medium">/home/user/downloads</div>
                        <span className="px-2 py-0.5 bg-amber-100 text-amber-800 text-xs rounded-full">Limited Access</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-xs px-1 bg-green-100 text-green-800 rounded">Read</span>
                        <span className="text-xs px-1 bg-green-100 text-green-800 rounded">Write</span>
                        <span className="text-xs px-1 bg-muted text-muted-foreground rounded">Execute</span>
                      </div>
                    </div>
                    
                    <div className="bg-accent/10 rounded-md p-2">
                      <div className="flex items-center justify-between mb-1">
                        <div className="text-sm font-medium">/home/user/private</div>
                        <span className="px-2 py-0.5 bg-red-100 text-red-800 text-xs rounded-full">No Access</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-xs px-1 bg-muted text-muted-foreground rounded">Read</span>
                        <span className="text-xs px-1 bg-muted text-muted-foreground rounded">Write</span>
                        <span className="text-xs px-1 bg-muted text-muted-foreground rounded">Execute</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default SystemActivityMonitor;
