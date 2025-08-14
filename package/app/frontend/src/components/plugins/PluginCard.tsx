// src/components/plugins/PluginCard.tsx
import React from 'react';
import { ToggleLeft, ToggleRight, Settings, Info } from 'lucide-react';

interface PluginCardProps {
  name: string;
  description: string;
  version: string;
  author: string;
  isActive: boolean;
  icon: string;
  onToggle: () => void;
  onConfigure: () => void;
  onInfo: () => void;
}

const PluginCard: React.FC<PluginCardProps> = ({
  name,
  description,
  version,
  author,
  isActive,
  icon,
  onToggle,
  onConfigure,
  onInfo
}) => {
  return (
    <div className="plugin-card bg-card border border-border rounded-lg overflow-hidden">
      <div className="p-4">
        <div className="flex items-start justify-between">
          <div className="flex items-center">
            <div className="h-10 w-10 rounded-md bg-accent flex items-center justify-center mr-3">
              <span className="text-xl">{icon}</span>
            </div>
            <div>
              <h3 className="font-medium">{name}</h3>
              <div className="text-xs text-muted-foreground">v{version} • by {author}</div>
            </div>
          </div>
          <button 
            onClick={onToggle}
            className="text-primary"
          >
            {isActive ? <ToggleRight size={24} /> : <ToggleLeft size={24} />}
          </button>
        </div>
        
        <p className="text-sm text-muted-foreground mt-3 line-clamp-2">{description}</p>
        
        <div className="flex justify-end space-x-2 mt-4">
          <button 
            onClick={onInfo}
            className="p-2 rounded-md hover:bg-accent text-muted-foreground"
            title="More information"
          >
            <Info size={16} />
          </button>
          <button 
            onClick={onConfigure}
            className={`p-2 rounded-md ${isActive ? 'hover:bg-accent text-foreground' : 'text-muted-foreground opacity-50 cursor-not-allowed'}`}
            disabled={!isActive}
            title="Configure plugin"
          >
            <Settings size={16} />
          </button>
        </div>
      </div>
      
      {isActive && (
        <div className="px-4 py-2 bg-accent/30 border-t border-border">
          <div className="flex justify-between items-center">
            <span className="text-xs font-medium">Status</span>
            <span className="text-xs px-2 py-1 rounded-full bg-green-100 text-green-800">Active</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default PluginCard;
