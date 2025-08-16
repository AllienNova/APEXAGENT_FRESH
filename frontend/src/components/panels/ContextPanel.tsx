// src/components/panels/ContextPanel.tsx
import React from 'react';
import { X, ExternalLink } from 'lucide-react';

const ContextPanel: React.FC = () => {
  return (
    <aside className="context-panel w-80 border-l border-border bg-card overflow-y-auto">
      <div className="p-4 border-b border-border flex items-center justify-between">
        <h2 className="font-semibold">Context</h2>
        <button className="p-1 rounded-md hover:bg-accent text-muted-foreground">
          <X size={16} />
        </button>
      </div>
      
      <div className="p-4">
        <div className="mb-6">
          <h3 className="text-sm font-medium mb-2">Current Task</h3>
          <div className="bg-background rounded-md p-3 border border-border">
            <h4 className="font-medium text-sm">Website Development</h4>
            <p className="text-xs text-muted-foreground mt-1">Creating a responsive small business website with multiple sections</p>
            <div className="mt-3">
              <div className="flex items-center justify-between text-xs mb-1">
                <span>Progress: 25%</span>
              </div>
              <div className="h-2 bg-muted rounded-full overflow-hidden">
                <div className="h-full bg-primary rounded-full" style={{ width: '25%' }}></div>
              </div>
            </div>
          </div>
        </div>
        
        <div className="mb-6">
          <h3 className="text-sm font-medium mb-2">Resources</h3>
          <ul className="space-y-2">
            {[
              { icon: 'file', name: 'website_requirements.txt' },
              { icon: 'image', name: 'logo.png' },
              { icon: 'link', name: 'https://example.com/inspiration' }
            ].map((item, index) => (
              <li key={index} className="flex items-center p-2 rounded-md hover:bg-accent text-sm">
                <span className="mr-2">
                  {item.icon === 'file' && '📄'}
                  {item.icon === 'image' && '🖼️'}
                  {item.icon === 'link' && '🔗'}
                </span>
                <span className="flex-1 truncate">{item.name}</span>
                <button className="p-1 rounded-md hover:bg-muted text-muted-foreground">
                  <ExternalLink size={14} />
                </button>
              </li>
            ))}
          </ul>
        </div>
        
        <div>
          <h3 className="text-sm font-medium mb-2">Active Tools</h3>
          <div className="space-y-2">
            {[
              { icon: '🌐', name: 'Web Browser', status: 'Active' },
              { icon: '📝', name: 'Code Editor', status: 'Ready' }
            ].map((tool, index) => (
              <div key={index} className="bg-background rounded-md p-3 border border-border">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <span className="mr-2">{tool.icon}</span>
                    <span className="text-sm font-medium">{tool.name}</span>
                  </div>
                  <span className={`text-xs px-2 py-1 rounded-full ${
                    tool.status === 'Active' ? 'bg-green-100 text-green-800' : 'bg-blue-100 text-blue-800'
                  }`}>
                    {tool.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </aside>
  );
};

export default ContextPanel;
