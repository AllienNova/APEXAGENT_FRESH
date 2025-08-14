// src/components/plugins/PluginInterface.tsx
import React, { useState } from 'react';
import { Search, Filter, Plus } from 'lucide-react';
import PluginCard from './PluginCard';

const PluginInterface: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [activeFilter, setActiveFilter] = useState('all');
  
  // Sample plugin data
  const [plugins, setPlugins] = useState([
    {
      id: '1',
      name: 'Web Browser',
      description: 'Browse the web, search for information, and interact with websites.',
      version: '2.3.1',
      author: 'ApexAgent',
      isActive: true,
      icon: '🌐'
    },
    {
      id: '2',
      name: 'File Manager',
      description: 'Manage files, create directories, and organize your documents.',
      version: '1.8.0',
      author: 'ApexAgent',
      isActive: true,
      icon: '📁'
    },
    {
      id: '3',
      name: 'Data Analyzer',
      description: 'Analyze data, create visualizations, and generate insights from your datasets.',
      version: '3.2.4',
      author: 'ApexAgent',
      isActive: true,
      icon: '📊'
    },
    {
      id: '4',
      name: 'Code Generator',
      description: 'Generate code in various programming languages based on your requirements.',
      version: '1.5.2',
      author: 'ApexAgent',
      isActive: false,
      icon: '💻'
    },
    {
      id: '5',
      name: 'Image Creator',
      description: 'Create and edit images using AI-powered tools and templates.',
      version: '2.0.1',
      author: 'ApexAgent',
      isActive: false,
      icon: '🎨'
    },
    {
      id: '6',
      name: 'PDF Processor',
      description: 'Extract text, analyze, and manipulate PDF documents.',
      version: '1.2.3',
      author: 'ApexAgent',
      isActive: false,
      icon: '📄'
    }
  ]);
  
  const handleTogglePlugin = (pluginId: string) => {
    setPlugins(plugins.map(plugin => 
      plugin.id === pluginId 
        ? { ...plugin, isActive: !plugin.isActive } 
        : plugin
    ));
  };
  
  const filteredPlugins = plugins.filter(plugin => {
    const matchesSearch = plugin.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
                         plugin.description.toLowerCase().includes(searchQuery.toLowerCase());
    
    if (activeFilter === 'all') return matchesSearch;
    if (activeFilter === 'active') return matchesSearch && plugin.isActive;
    if (activeFilter === 'inactive') return matchesSearch && !plugin.isActive;
    
    return matchesSearch;
  });
  
  return (
    <div className="plugin-interface p-6">
      <header className="mb-6">
        <h1 className="text-2xl font-bold">Plugins</h1>
        <p className="text-muted-foreground">Manage and configure your plugins</p>
      </header>
      
      <div className="flex flex-col md:flex-row justify-between mb-6 space-y-4 md:space-y-0">
        <div className="relative w-full md:w-96">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
          <input 
            type="text" 
            placeholder="Search plugins..." 
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10 pr-4 py-2 h-10 w-full rounded-md border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
          />
        </div>
        
        <div className="flex space-x-2">
          <div className="flex items-center bg-card rounded-md border border-border">
            <button 
              onClick={() => setActiveFilter('all')}
              className={`px-3 py-2 text-sm rounded-l-md ${activeFilter === 'all' ? 'bg-primary text-primary-foreground' : 'hover:bg-accent'}`}
            >
              All
            </button>
            <button 
              onClick={() => setActiveFilter('active')}
              className={`px-3 py-2 text-sm ${activeFilter === 'active' ? 'bg-primary text-primary-foreground' : 'hover:bg-accent'}`}
            >
              Active
            </button>
            <button 
              onClick={() => setActiveFilter('inactive')}
              className={`px-3 py-2 text-sm rounded-r-md ${activeFilter === 'inactive' ? 'bg-primary text-primary-foreground' : 'hover:bg-accent'}`}
            >
              Inactive
            </button>
          </div>
          
          <button className="flex items-center space-x-1 px-3 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90">
            <Plus size={16} />
            <span>Add Plugin</span>
          </button>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredPlugins.map(plugin => (
          <PluginCard 
            key={plugin.id}
            name={plugin.name}
            description={plugin.description}
            version={plugin.version}
            author={plugin.author}
            isActive={plugin.isActive}
            icon={plugin.icon}
            onToggle={() => handleTogglePlugin(plugin.id)}
            onConfigure={() => console.log('Configure plugin:', plugin.id)}
            onInfo={() => console.log('Plugin info:', plugin.id)}
          />
        ))}
      </div>
      
      {filteredPlugins.length === 0 && (
        <div className="flex flex-col items-center justify-center p-8 bg-card rounded-lg border border-border">
          <div className="text-4xl mb-4">🔍</div>
          <h3 className="text-lg font-medium mb-2">No plugins found</h3>
          <p className="text-muted-foreground text-center">
            We couldn't find any plugins matching your search criteria.
          </p>
        </div>
      )}
    </div>
  );
};

export default PluginInterface;
