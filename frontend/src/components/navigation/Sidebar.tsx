import React, { useState } from 'react';

interface SidebarProps {
  collapsed?: boolean;
  onToggleCollapse?: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({
  collapsed = false,
  onToggleCollapse
}) => {
  const [activeSection, setActiveSection] = useState('projects');

  const handleSectionChange = (section: string) => {
    setActiveSection(section);
  };

  return (
    <div className={`h-full flex flex-col ${collapsed ? 'w-16' : 'w-64'} transition-all duration-200`}>
      {/* Header */}
      <div className="p-3 border-b border-border flex items-center justify-between">
        {!collapsed && <h1 className="font-bold text-lg">ApexAgent</h1>}
        <button 
          onClick={onToggleCollapse}
          className="p-1 rounded-md hover:bg-accent text-muted-foreground"
          title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          {collapsed ? '▶' : '◀'}
        </button>
      </div>

      {/* Navigation sections */}
      <div className="p-2 border-b border-border">
        <div className="flex flex-col gap-1">
          <button 
            className={`flex items-center gap-2 py-2 px-3 rounded-md ${
              activeSection === 'projects' ? 'bg-primary text-primary-foreground' : 'hover:bg-accent/50'
            } transition-colors`}
            onClick={() => handleSectionChange('projects')}
          >
            <span className="text-lg">📁</span>
            {!collapsed && <span>Projects</span>}
          </button>
          
          <button 
            className={`flex items-center gap-2 py-2 px-3 rounded-md ${
              activeSection === 'files' ? 'bg-primary text-primary-foreground' : 'hover:bg-accent/50'
            } transition-colors`}
            onClick={() => handleSectionChange('files')}
          >
            <span className="text-lg">📄</span>
            {!collapsed && <span>Files</span>}
          </button>
          
          <button 
            className={`flex items-center gap-2 py-2 px-3 rounded-md ${
              activeSection === 'plugins' ? 'bg-primary text-primary-foreground' : 'hover:bg-accent/50'
            } transition-colors`}
            onClick={() => handleSectionChange('plugins')}
          >
            <span className="text-lg">🧩</span>
            {!collapsed && <span>Plugins</span>}
          </button>
        </div>
      </div>

      {/* Content based on active section */}
      <div className="flex-1 overflow-auto">
        {activeSection === 'projects' && !collapsed && (
          <div className="p-2">
            <div className="mb-2 flex items-center justify-between">
              <h3 className="text-xs uppercase text-muted-foreground font-semibold">Recent Projects</h3>
              <button className="text-xs text-primary hover:underline">New</button>
            </div>
            
            <div className="space-y-1">
              <div className="rounded-md bg-accent/30 p-2">
                <div className="font-medium text-sm">Website Redesign</div>
                <div className="text-xs text-muted-foreground">Last opened 2 hours ago</div>
              </div>
              
              <div className="rounded-md hover:bg-accent/30 p-2">
                <div className="font-medium text-sm">Data Analysis</div>
                <div className="text-xs text-muted-foreground">Last opened yesterday</div>
              </div>
              
              <div className="rounded-md hover:bg-accent/30 p-2">
                <div className="font-medium text-sm">Research Paper</div>
                <div className="text-xs text-muted-foreground">Last opened 3 days ago</div>
              </div>
            </div>
          </div>
        )}
        
        {activeSection === 'files' && !collapsed && (
          <div className="p-2">
            <div className="mb-2 flex items-center justify-between">
              <h3 className="text-xs uppercase text-muted-foreground font-semibold">File System</h3>
              <button className="text-xs text-primary hover:underline">Browse</button>
            </div>
            
            <div className="space-y-1">
              <div className="flex items-center gap-1 p-1 hover:bg-accent/30 rounded">
                <span className="text-blue-600">📁</span>
                <span className="text-sm">Documents</span>
              </div>
              
              <div className="flex items-center gap-1 p-1 hover:bg-accent/30 rounded ml-4">
                <span className="text-amber-600">📄</span>
                <span className="text-sm">report.docx</span>
              </div>
              
              <div className="flex items-center gap-1 p-1 hover:bg-accent/30 rounded ml-4">
                <span className="text-amber-600">📄</span>
                <span className="text-sm">analysis.xlsx</span>
              </div>
              
              <div className="flex items-center gap-1 p-1 hover:bg-accent/30 rounded">
                <span className="text-blue-600">📁</span>
                <span className="text-sm">Downloads</span>
              </div>
              
              <div className="flex items-center gap-1 p-1 hover:bg-accent/30 rounded">
                <span className="text-blue-600">📁</span>
                <span className="text-sm">Pictures</span>
              </div>
            </div>
          </div>
        )}
        
        {activeSection === 'plugins' && !collapsed && (
          <div className="p-2">
            <div className="mb-2 flex items-center justify-between">
              <h3 className="text-xs uppercase text-muted-foreground font-semibold">Active Plugins</h3>
              <button className="text-xs text-primary hover:underline">Browse</button>
            </div>
            
            <div className="space-y-1">
              <div className="rounded-md bg-accent/30 p-2">
                <div className="flex items-center justify-between">
                  <div className="font-medium text-sm">Code Assistant</div>
                  <div className="h-4 w-8 bg-primary rounded-full relative">
                    <div className="h-3 w-3 bg-white rounded-full absolute top-0.5 right-0.5"></div>
                  </div>
                </div>
              </div>
              
              <div className="rounded-md bg-accent/30 p-2">
                <div className="flex items-center justify-between">
                  <div className="font-medium text-sm">Data Visualizer</div>
                  <div className="h-4 w-8 bg-primary rounded-full relative">
                    <div className="h-3 w-3 bg-white rounded-full absolute top-0.5 right-0.5"></div>
                  </div>
                </div>
              </div>
              
              <div className="rounded-md bg-accent/10 p-2">
                <div className="flex items-center justify-between">
                  <div className="font-medium text-sm">PDF Analyzer</div>
                  <div className="h-4 w-8 bg-muted rounded-full relative">
                    <div className="h-3 w-3 bg-white rounded-full absolute top-0.5 left-0.5"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="border-t border-border p-2">
        <div className="flex items-center gap-2 p-2 hover:bg-accent/30 rounded-md">
          <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center text-primary-foreground">
            U
          </div>
          {!collapsed && (
            <div>
              <div className="text-sm font-medium">User</div>
              <div className="text-xs text-muted-foreground">Settings</div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
