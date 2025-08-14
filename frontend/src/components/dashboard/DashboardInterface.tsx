// src/components/dashboard/DashboardInterface.tsx
import React from 'react';
import { ArrowUp, ArrowDown, ChevronRight } from 'lucide-react';

const DashboardInterface: React.FC = () => {
  return (
    <div className="dashboard-interface p-6">
      <header className="mb-6">
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <p className="text-muted-foreground">Welcome back, John Doe</p>
      </header>
      
      {/* Activity Summary Section */}
      <section className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold">Activity Summary</h2>
          <span className="text-sm text-muted-foreground">Last 7 days</span>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            { label: 'Conversations', value: '12', trend: '+20%', positive: true },
            { label: 'Tasks Completed', value: '48', trend: '+15%', positive: true },
            { label: 'Avg. Response Time (s)', value: '8.2', trend: '-5%', positive: false },
            { label: 'Task Success Rate', value: '94%', trend: '+2%', positive: true }
          ].map((stat, index) => (
            <div key={index} className="stat-card bg-card rounded-lg border border-border p-4">
              <div className="text-2xl font-bold">{stat.value}</div>
              <div className="text-sm text-muted-foreground">{stat.label}</div>
              <div className={`text-xs mt-2 flex items-center ${
                stat.positive ? 'text-green-600' : 'text-red-600'
              }`}>
                {stat.positive ? <ArrowUp size={12} /> : <ArrowDown size={12} />}
                <span className="ml-1">{stat.trend}</span>
              </div>
            </div>
          ))}
        </div>
      </section>
      
      {/* Recent Activity Section */}
      <section className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold">Recent Activity</h2>
          <button className="text-sm text-primary hover:underline">View All</button>
        </div>
        
        <div className="bg-card rounded-lg border border-border overflow-hidden">
          {[
            { icon: '💬', title: 'Website Development', description: 'Generated responsive HTML template', time: '30 minutes ago' },
            { icon: '📊', title: 'Data Analysis Project', description: 'Processed sales data and created visualization', time: '2 hours ago' },
            { icon: '📁', title: 'File Management', description: 'Organized project files into categories', time: 'Yesterday' }
          ].map((activity, index) => (
            <div key={index} className={`p-4 flex items-center ${
              index !== 2 ? 'border-b border-border' : ''
            }`}>
              <div className="h-10 w-10 rounded-full bg-accent flex items-center justify-center mr-4">
                <span>{activity.icon}</span>
              </div>
              <div className="flex-1">
                <div className="font-medium">{activity.title}</div>
                <div className="text-sm text-muted-foreground">{activity.description}</div>
                <div className="text-xs text-muted-foreground mt-1">{activity.time}</div>
              </div>
              <button className="p-2 rounded-md hover:bg-accent text-muted-foreground">
                <ChevronRight size={16} />
              </button>
            </div>
          ))}
        </div>
      </section>
      
      {/* Resource Usage Section */}
      <section className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold">Resource Usage</h2>
          <div className="text-sm text-muted-foreground">This Month</div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[
            { label: 'API Calls', used: '1,245', total: '5,000', percentage: 25 },
            { label: 'Storage', used: '2.4 GB', total: '10 GB', percentage: 24 },
            { label: 'Processing Time', used: '45 min', total: '180 min', percentage: 25 }
          ].map((resource, index) => (
            <div key={index} className="bg-card rounded-lg border border-border p-4">
              <div className="flex justify-between items-center mb-2">
                <h3 className="font-medium">{resource.label}</h3>
                <div className="text-sm">
                  <span className="font-medium">{resource.used}</span>
                  <span className="text-muted-foreground"> / {resource.total}</span>
                </div>
              </div>
              <div className="h-2 bg-muted rounded-full overflow-hidden">
                <div 
                  className="h-full bg-primary rounded-full" 
                  style={{ width: `${resource.percentage}%` }}
                ></div>
              </div>
            </div>
          ))}
        </div>
      </section>
      
      {/* Quick Actions Section */}
      <section className="mb-8">
        <h2 className="text-lg font-semibold mb-4">Quick Actions</h2>
        
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-4">
          {[
            { icon: '💬', label: 'New Conversation' },
            { icon: '📊', label: 'Data Analysis' },
            { icon: '🌐', label: 'Web Search' },
            { icon: '📝', label: 'Content Creation' },
            { icon: '📁', label: 'File Management' },
            { icon: '⚙️', label: 'Configure Plugins' }
          ].map((action, index) => (
            <button key={index} className="bg-card hover:bg-accent rounded-lg border border-border p-4 flex flex-col items-center justify-center text-center h-24">
              <div className="text-2xl mb-2">{action.icon}</div>
              <div className="text-sm">{action.label}</div>
            </button>
          ))}
        </div>
      </section>
      
      {/* Recent Files Section */}
      <section>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold">Recent Files</h2>
          <button className="text-sm text-primary hover:underline">View All</button>
        </div>
        
        <div className="bg-card rounded-lg border border-border overflow-hidden">
          {[
            { icon: '📄', name: 'website_requirements.txt', type: 'Text Document', size: '24 KB', time: 'Modified 30 minutes ago' },
            { icon: '🖼️', name: 'logo.png', type: 'Image', size: '156 KB', time: 'Modified 2 hours ago' },
            { icon: '📊', name: 'sales_analysis.xlsx', type: 'Spreadsheet', size: '1.2 MB', time: 'Modified Yesterday' }
          ].map((file, index) => (
            <div key={index} className={`p-4 flex items-center ${
              index !== 2 ? 'border-b border-border' : ''
            }`}>
              <div className="h-10 w-10 rounded-full bg-accent flex items-center justify-center mr-4">
                <span>{file.icon}</span>
              </div>
              <div className="flex-1">
                <div className="font-medium">{file.name}</div>
                <div className="text-sm text-muted-foreground">{file.type} • {file.size}</div>
                <div className="text-xs text-muted-foreground mt-1">{file.time}</div>
              </div>
              <div className="flex space-x-2">
                <button className="p-2 rounded-md hover:bg-accent text-muted-foreground">
                  👁️
                </button>
                <button className="p-2 rounded-md hover:bg-accent text-muted-foreground">
                  ⬇️
                </button>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
};

export default DashboardInterface;
