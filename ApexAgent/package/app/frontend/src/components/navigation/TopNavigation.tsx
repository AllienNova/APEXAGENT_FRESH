// src/components/navigation/TopNavigation.tsx
import React from 'react';
import { Search, Bell, ChevronDown } from 'lucide-react';

const TopNavigation: React.FC = () => {
  return (
    <header className="h-16 border-b border-border bg-background flex items-center justify-between px-4">
      <div className="flex items-center">
        <h1 className="text-xl font-semibold">Dashboard</h1>
      </div>
      
      <div className="flex items-center space-x-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
          <input 
            type="text" 
            placeholder="Search..." 
            className="pl-10 pr-4 py-2 h-9 rounded-md border border-input bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 w-64"
          />
        </div>
        
        <button className="p-2 rounded-md hover:bg-accent relative">
          <Bell size={18} className="text-muted-foreground" />
          <span className="absolute top-1 right-1 h-2 w-2 bg-destructive rounded-full"></span>
        </button>
        
        <div className="flex items-center space-x-2 cursor-pointer hover:bg-accent p-1 rounded-md">
          <div className="h-8 w-8 bg-muted rounded-full flex items-center justify-center text-muted-foreground">
            J
          </div>
          <span className="text-sm font-medium">John Doe</span>
          <ChevronDown size={16} className="text-muted-foreground" />
        </div>
      </div>
    </header>
  );
};

export default TopNavigation;
