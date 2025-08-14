import React, { useState } from 'react';

/**
 * Navigation Layout Component
 * 
 * This component implements the main navigation structure for Aideon AI Lite,
 * including the sidebar, header, and horizontal tabs.
 */
const MainLayout = ({ children }) => {
  // State for mobile sidebar visibility
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);
  
  // State for active tab
  const [activeTab, setActiveTab] = useState('chat');
  
  // Navigation items
  const navItems = [
    { id: 'chat', label: 'Chat', icon: 'comment-dots' },
    { id: 'projects', label: 'Projects', icon: 'folder-open' },
    { id: 'documents', label: 'Documents', icon: 'file-alt' },
    { id: 'dr-tardis', label: 'Dr. TARDIS', icon: 'robot' },
    { id: 'settings', label: 'Settings', icon: 'cog' }
  ];
  
  // Tab items
  const tabItems = {
    chat: [
      { id: 'chat', label: 'Chat' },
      { id: 'artifacts', label: 'Artifacts' },
      { id: 'llm-orchestration', label: 'LLM Orchestration' },
      { id: 'project-files', label: 'Project Files' },
      { id: 'agent-monitoring', label: 'Agent Monitoring' }
    ],
    projects: [
      { id: 'all-projects', label: 'All Projects' },
      { id: 'active', label: 'Active' },
      { id: 'archived', label: 'Archived' },
      { id: 'shared', label: 'Shared with Me' }
    ],
    documents: [
      { id: 'all-documents', label: 'All Documents' },
      { id: 'recent', label: 'Recent' },
      { id: 'shared', label: 'Shared' },
      { id: 'templates', label: 'Templates' }
    ],
    'dr-tardis': [
      { id: 'dashboard', label: 'Dashboard' },
      { id: 'diagnostics', label: 'Diagnostics' },
      { id: 'monitoring', label: 'Monitoring' },
      { id: 'help', label: 'Help & Support' }
    ],
    settings: [
      { id: 'profile', label: 'Profile' },
      { id: 'preferences', label: 'Preferences' },
      { id: 'api-keys', label: 'API Keys' },
      { id: 'billing', label: 'Billing' }
    ]
  };
  
  // State for active sub-tab
  const [activeSubTab, setActiveSubTab] = useState(tabItems[activeTab][0].id);
  
  // Handle navigation item click
  const handleNavClick = (id) => {
    setActiveTab(id);
    setActiveSubTab(tabItems[id][0].id);
  };
  
  // Handle sub-tab click
  const handleSubTabClick = (id) => {
    setActiveSubTab(id);
  };
  
  // Toggle mobile sidebar
  const toggleMobileSidebar = () => {
    setMobileSidebarOpen(!mobileSidebarOpen);
  };
  
  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar - desktop */}
      <div className="hidden md:flex md:flex-shrink-0">
        <div className="flex flex-col w-64 bg-indigo-800">
          <div className="flex items-center h-16 px-4 bg-indigo-900">
            <span className="text-xl font-bold text-white">Aideon AI Lite</span>
          </div>
          <div className="flex flex-col flex-1 overflow-y-auto">
            <div className="px-4 py-2 bg-indigo-700">
              <p className="text-sm text-indigo-200 italic">Intelligence Everywhere, Limits Nowhere</p>
            </div>
            <nav className="flex-1 px-2 py-4 space-y-1">
              {navItems.map((item) => (
                <a
                  key={item.id}
                  href="#"
                  onClick={(e) => {
                    e.preventDefault();
                    handleNavClick(item.id);
                  }}
                  className={`flex items-center px-2 py-2 text-sm font-medium rounded-md ${
                    activeTab === item.id
                      ? 'text-white bg-indigo-700'
                      : 'text-indigo-100 hover:bg-indigo-700'
                  }`}
                >
                  <i className={`fas fa-${item.icon} mr-3`}></i>
                  {item.label}
                </a>
              ))}
            </nav>
            <div className="px-2 py-4 space-y-2">
              <div className="flex items-center px-2 py-2 text-sm font-medium text-indigo-100">
                <i className="fas fa-user-circle mr-3"></i>
                <span>John Doe</span>
              </div>
              <div className="flex items-center px-2 py-2 text-sm font-medium text-indigo-100">
                <i className="fas fa-credit-card mr-3"></i>
                <span>Pro Plan</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Mobile sidebar */}
      {mobileSidebarOpen && (
        <div className="fixed inset-0 z-40 flex md:hidden">
          <div className="fixed inset-0 bg-gray-600 bg-opacity-75" onClick={toggleMobileSidebar}></div>
          <div className="relative flex flex-col w-full max-w-xs bg-indigo-800">
            <div className="flex items-center justify-between h-16 px-4 bg-indigo-900">
              <span className="text-xl font-bold text-white">Aideon AI Lite</span>
              <button
                className="text-white focus:outline-none"
                onClick={toggleMobileSidebar}
              >
                <i className="fas fa-times"></i>
              </button>
            </div>
            <div className="flex flex-col flex-1 overflow-y-auto">
              <div className="px-4 py-2 bg-indigo-700">
                <p className="text-sm text-indigo-200 italic">Intelligence Everywhere, Limits Nowhere</p>
              </div>
              <nav className="flex-1 px-2 py-4 space-y-1">
                {navItems.map((item) => (
                  <a
                    key={item.id}
                    href="#"
                    onClick={(e) => {
                      e.preventDefault();
                      handleNavClick(item.id);
                      toggleMobileSidebar();
                    }}
                    className={`flex items-center px-2 py-2 text-sm font-medium rounded-md ${
                      activeTab === item.id
                        ? 'text-white bg-indigo-700'
                        : 'text-indigo-100 hover:bg-indigo-700'
                    }`}
                  >
                    <i className={`fas fa-${item.icon} mr-3`}></i>
                    {item.label}
                  </a>
                ))}
              </nav>
              <div className="px-2 py-4 space-y-2">
                <div className="flex items-center px-2 py-2 text-sm font-medium text-indigo-100">
                  <i className="fas fa-user-circle mr-3"></i>
                  <span>John Doe</span>
                </div>
                <div className="flex items-center px-2 py-2 text-sm font-medium text-indigo-100">
                  <i className="fas fa-credit-card mr-3"></i>
                  <span>Pro Plan</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Main content */}
      <div className="flex flex-col flex-1 overflow-hidden">
        {/* Top navigation */}
        <header className="bg-white shadow">
          <div className="px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-16">
              <div className="flex items-center">
                <button
                  className="md:hidden px-4 text-gray-500 focus:outline-none"
                  onClick={toggleMobileSidebar}
                >
                  <i className="fas fa-bars"></i>
                </button>
                <h1 className="text-xl font-semibold text-gray-900">{navItems.find(item => item.id === activeTab)?.label}</h1>
                <span className="ml-4 text-sm text-gray-500 italic">Intelligence Everywhere, Limits Nowhere</span>
              </div>
              <div className="flex items-center space-x-4">
                <button className="p-2 rounded-full bg-gray-100 text-gray-500 hover:bg-gray-200">
                  <i className="fas fa-bell"></i>
                </button>
                <button className="p-2 rounded-full bg-gray-100 text-gray-500 hover:bg-gray-200">
                  <i className="fas fa-question-circle"></i>
                </button>
                <div className="relative">
                  <button className="flex items-center text-sm font-medium text-gray-700 focus:outline-none">
                    <img className="h-8 w-8 rounded-full" src="https://via.placeholder.com/150" alt="User avatar" />
                  </button>
                </div>
              </div>
            </div>
            
            {/* Horizontal tabs */}
            <div className="mt-2 border-b border-gray-200">
              <nav className="-mb-px flex space-x-8 overflow-x-auto">
                {tabItems[activeTab].map((tab) => (
                  <a
                    key={tab.id}
                    href="#"
                    onClick={(e) => {
                      e.preventDefault();
                      handleSubTabClick(tab.id);
                    }}
                    className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm ${
                      activeSubTab === tab.id
                        ? 'border-indigo-500 text-indigo-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    {tab.label}
                  </a>
                ))}
              </nav>
            </div>
          </div>
        </header>

        {/* Main content area */}
        <main className="flex-1 overflow-y-auto p-6 bg-gray-50">
          {children}
        </main>
      </div>
    </div>
  );
};

export default MainLayout;
