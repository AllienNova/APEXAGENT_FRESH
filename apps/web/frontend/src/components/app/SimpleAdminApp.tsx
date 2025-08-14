import React, { useState } from 'react';

const SimpleAdminApp = () => {
  const [activeTab, setActiveTab] = useState('dashboard');

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return (
          <div className="p-6">
            <h2 className="text-2xl font-bold text-white mb-4">Dashboard</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="bg-blue-600 p-4 rounded-lg">
                <h3 className="text-white text-lg">Credits</h3>
                <p className="text-white text-2xl font-bold">2,847</p>
              </div>
              <div className="bg-green-600 p-4 rounded-lg">
                <h3 className="text-white text-lg">System Status</h3>
                <p className="text-white text-2xl font-bold">Optimal</p>
              </div>
              <div className="bg-purple-600 p-4 rounded-lg">
                <h3 className="text-white text-lg">Processing</h3>
                <p className="text-white text-2xl font-bold">Hybrid</p>
              </div>
              <div className="bg-red-600 p-4 rounded-lg">
                <h3 className="text-white text-lg">Threats Blocked</h3>
                <p className="text-white text-2xl font-bold">1,247</p>
              </div>
            </div>
          </div>
        );
      case 'chat':
        return (
          <div className="p-6">
            <h2 className="text-2xl font-bold text-white mb-4">AI Chat</h2>
            <div className="bg-gray-800 rounded-lg p-4 h-96">
              <div className="text-white">Chat interface would go here...</div>
            </div>
          </div>
        );
      case 'projects':
        return (
          <div className="p-6">
            <h2 className="text-2xl font-bold text-white mb-4">Projects</h2>
            <div className="text-white">Projects management interface...</div>
          </div>
        );
      default:
        return (
          <div className="p-6">
            <h2 className="text-2xl font-bold text-white mb-4">{activeTab}</h2>
            <div className="text-white">Content for {activeTab} section...</div>
          </div>
        );
    }
  };

  return (
    <div className="min-h-screen bg-gray-900">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700">
        <div className="flex items-center justify-between px-6 py-4">
          <div className="flex items-center space-x-4">
            <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
              <span className="text-white font-bold">A</span>
            </div>
            <div>
              <h1 className="text-xl font-bold text-white">Aideon Lite AI</h1>
              <p className="text-sm text-gray-400">The World's First Hybrid Autonomous AI System</p>
            </div>
          </div>
          <div className="flex items-center space-x-6 text-sm">
            <div className="text-green-400">
              <span className="font-semibold">2,847</span> Credits
            </div>
            <div className="text-blue-400">
              Hybrid Processing <span className="font-semibold">67% Local, 33% Cloud</span>
            </div>
            <div className="text-yellow-400">
              System <span className="font-semibold">Optimal 2.3x Faster</span>
            </div>
            <div className="text-red-400">
              AI Guardian <span className="font-semibold">1,247 Threats Blocked</span>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-gray-800 border-b border-gray-700">
        <div className="flex space-x-8 px-6">
          {[
            { id: 'dashboard', name: 'Dashboard', icon: '📊' },
            { id: 'chat', name: 'Chat', icon: '💬' },
            { id: 'projects', name: 'Projects', icon: '📁' },
            { id: 'artifacts', name: 'Artifacts', icon: '🎨', badge: '12' },
            { id: 'files', name: 'Files', icon: '📄' },
            { id: 'agents', name: 'Agents', icon: '🤖' },
            { id: 'security', name: 'Security', icon: '🔒' },
            { id: 'analytics', name: 'Analytics', icon: '📈' },
            { id: 'settings', name: 'Settings', icon: '⚙️' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center space-x-2 py-4 px-2 border-b-2 transition-colors ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-400'
                  : 'border-transparent text-gray-400 hover:text-white hover:border-gray-300'
              }`}
            >
              <span>{tab.icon}</span>
              <span>{tab.name}</span>
              {tab.badge && (
                <span className="bg-red-500 text-white text-xs px-2 py-1 rounded-full">
                  {tab.badge}
                </span>
              )}
            </button>
          ))}
        </div>
      </nav>

      {/* Main Content */}
      <main className="flex-1">
        {renderContent()}
      </main>
    </div>
  );
};

export default SimpleAdminApp;

