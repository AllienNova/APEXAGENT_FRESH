import React, { useState, useEffect } from 'react';
import { 
  Shield, 
  Settings, 
  BarChart3, 
  Users, 
  Key, 
  Activity,
  Globe,
  Zap,
  Lock,
  DollarSign,
  Bell,
  Search,
  Menu,
  X,
  Home,
  ChevronDown,
  LogOut,
  User,
  HelpCircle
} from 'lucide-react';

// Import the dashboard components
import { EnhancedAdminDashboard } from '../admin/EnhancedAdminDashboard';
import { OAuthConnectionManager } from '../auth/OAuthConnectionManager';
import { SecurityMonitoringDashboard } from '../security/SecurityMonitoringDashboard';
import { CostOptimizationDashboard } from '../analytics/CostOptimizationDashboard';
import { AuthenticationInterface } from '../auth/AuthenticationInterface';

// Main Aideon Admin Application
export const AideonAdminApp = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const [notifications, setNotifications] = useState(3);

  const tabs = [
    {
      id: 'dashboard',
      name: 'Dashboard',
      icon: Home,
      component: EnhancedAdminDashboard,
      description: 'System overview and key metrics'
    },
    {
      id: 'authentication',
      name: 'Authentication',
      icon: Lock,
      component: AuthenticationInterface,
      description: 'User authentication and access control'
    },
    {
      id: 'oauth',
      name: 'OAuth Connections',
      icon: Globe,
      component: OAuthConnectionManager,
      description: 'Manage platform integrations'
    },
    {
      id: 'security',
      name: 'Security Monitor',
      icon: Shield,
      component: SecurityMonitoringDashboard,
      description: 'Real-time threat detection'
    },
    {
      id: 'cost',
      name: 'Cost Analytics',
      icon: DollarSign,
      component: CostOptimizationDashboard,
      description: 'AI cost optimization insights'
    },
    {
      id: 'users',
      name: 'User Management',
      icon: Users,
      component: () => <div className="p-6">User Management Component (Coming Soon)</div>,
      description: 'Manage user accounts and permissions'
    },
    {
      id: 'api-keys',
      name: 'API Keys',
      icon: Key,
      component: () => <div className="p-6">API Key Management Component (Coming Soon)</div>,
      description: 'Manage API keys and credentials'
    },
    {
      id: 'analytics',
      name: 'System Analytics',
      icon: BarChart3,
      component: () => <div className="p-6">System Analytics Component (Coming Soon)</div>,
      description: 'Detailed system performance analytics'
    }
  ];

  const currentTab = tabs.find(tab => tab.id === activeTab);
  const CurrentComponent = currentTab?.component || (() => <div>Component not found</div>);

  return (
    <div className="h-screen bg-gray-50 flex overflow-hidden">
      {/* Sidebar */}
      <div className={`${sidebarOpen ? 'w-64' : 'w-16'} bg-white shadow-lg transition-all duration-300 flex flex-col`}>
        {/* Sidebar Header */}
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            {sidebarOpen && (
              <div>
                <h1 className="text-xl font-bold text-gray-900">Aideon AI</h1>
                <p className="text-sm text-gray-600">Admin Console</p>
              </div>
            )}
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
            >
              {sidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </button>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg transition-colors ${
                  isActive 
                    ? 'bg-indigo-100 text-indigo-700 border border-indigo-200' 
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
                title={!sidebarOpen ? tab.name : ''}
              >
                <Icon className={`h-5 w-5 ${isActive ? 'text-indigo-600' : 'text-gray-500'}`} />
                {sidebarOpen && (
                  <div className="flex-1 text-left">
                    <p className="font-medium">{tab.name}</p>
                    <p className="text-xs text-gray-500">{tab.description}</p>
                  </div>
                )}
              </button>
            );
          })}
        </nav>

        {/* Sidebar Footer */}
        <div className="p-4 border-t border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-indigo-600 rounded-full flex items-center justify-center">
              <User className="h-4 w-4 text-white" />
            </div>
            {sidebarOpen && (
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900">Admin User</p>
                <p className="text-xs text-gray-500">admin@aideon.ai</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Header */}
        <header className="bg-white shadow-sm border-b border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">{currentTab?.name}</h2>
              <p className="text-sm text-gray-600">{currentTab?.description}</p>
            </div>
            
            <div className="flex items-center space-x-4">
              {/* Search */}
              <div className="relative">
                <Search className="h-4 w-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search..."
                  className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
              </div>

              {/* Notifications */}
              <button className="relative p-2 text-gray-400 hover:text-gray-600 transition-colors">
                <Bell className="h-5 w-5" />
                {notifications > 0 && (
                  <span className="absolute -top-1 -right-1 h-4 w-4 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
                    {notifications}
                  </span>
                )}
              </button>

              {/* User Menu */}
              <div className="relative">
                <button
                  onClick={() => setUserMenuOpen(!userMenuOpen)}
                  className="flex items-center space-x-2 p-2 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <div className="w-8 h-8 bg-indigo-600 rounded-full flex items-center justify-center">
                    <User className="h-4 w-4 text-white" />
                  </div>
                  <ChevronDown className="h-4 w-4 text-gray-500" />
                </button>

                {userMenuOpen && (
                  <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-50">
                    <a href="#" className="flex items-center space-x-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">
                      <User className="h-4 w-4" />
                      <span>Profile</span>
                    </a>
                    <a href="#" className="flex items-center space-x-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">
                      <Settings className="h-4 w-4" />
                      <span>Settings</span>
                    </a>
                    <a href="#" className="flex items-center space-x-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">
                      <HelpCircle className="h-4 w-4" />
                      <span>Help</span>
                    </a>
                    <hr className="my-1" />
                    <a href="#" className="flex items-center space-x-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">
                      <LogOut className="h-4 w-4" />
                      <span>Sign Out</span>
                    </a>
                  </div>
                )}
              </div>
            </div>
          </div>
        </header>

        {/* Horizontal Tabs */}
        <div className="bg-white border-b border-gray-200">
          <div className="px-6">
            <div className="flex space-x-8 overflow-x-auto">
              {tabs.map((tab) => {
                const Icon = tab.icon;
                const isActive = activeTab === tab.id;
                
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap transition-colors ${
                      isActive
                        ? 'border-indigo-500 text-indigo-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    <Icon className="h-4 w-4" />
                    <span>{tab.name}</span>
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* Main Content Area */}
        <main className="flex-1 overflow-y-auto bg-gray-50">
          <CurrentComponent />
        </main>
      </div>

      {/* Click outside to close user menu */}
      {userMenuOpen && (
        <div 
          className="fixed inset-0 z-40" 
          onClick={() => setUserMenuOpen(false)}
        ></div>
      )}
    </div>
  );
};

export default AideonAdminApp;

