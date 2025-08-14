import React, { useState } from 'react';

interface MainLayoutProps {
  children: React.ReactNode;
  sidebar?: React.ReactNode;
  contextPanel?: React.ReactNode;
  showContextPanel?: boolean;
}

const MainLayout: React.FC<MainLayoutProps> = ({
  children,
  sidebar,
  contextPanel,
  showContextPanel = true
}) => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [contextPanelVisible, setContextPanelVisible] = useState(showContextPanel);

  const toggleSidebar = () => {
    setSidebarCollapsed(!sidebarCollapsed);
  };

  const toggleContextPanel = () => {
    setContextPanelVisible(!contextPanelVisible);
  };

  return (
    <div className="flex h-screen bg-background text-foreground">
      {/* Sidebar */}
      <div className={`border-r border-border bg-card transition-all ${
        sidebarCollapsed ? 'w-16' : 'w-64'
      }`}>
        {sidebar || (
          <div className="flex flex-col h-full">
            <div className="p-4 border-b border-border flex items-center justify-between">
              <h1 className={`font-bold ${sidebarCollapsed ? 'hidden' : 'block'}`}>ApexAgent</h1>
              <button 
                onClick={toggleSidebar}
                className="p-1 rounded-md hover:bg-accent text-muted-foreground"
              >
                {sidebarCollapsed ? '▶' : '◀'}
              </button>
            </div>
            <div className="flex-1 overflow-auto p-2">
              {/* Sidebar content placeholder */}
              {!sidebarCollapsed && (
                <div className="text-sm text-muted-foreground">Sidebar content</div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {children}
      </div>

      {/* Context panel */}
      {contextPanelVisible && (
        <div className="w-80 border-l border-border bg-card overflow-hidden flex flex-col">
          <div className="p-4 border-b border-border flex items-center justify-between">
            <h2 className="font-semibold text-sm">Context Panel</h2>
            <button 
              onClick={toggleContextPanel}
              className="p-1 rounded-md hover:bg-accent text-muted-foreground"
            >
              ✖
            </button>
          </div>
          <div className="flex-1 overflow-auto p-4">
            {contextPanel || (
              <div className="text-sm text-muted-foreground">Context panel content</div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default MainLayout;
