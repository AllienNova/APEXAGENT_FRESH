import React, { useState } from 'react';
import { Terminal, Code, FileText, Settings, ChevronRight, ChevronLeft, Search, Send, Maximize2, X, Plus, MessageSquare, Cpu, Zap, Folder, BarChart2, Clock, Monitor, HardDrive, PieChart, Database, Layers, Activity, AlertCircle, ArrowRight, GitBranch, Save, Trash2, FileCode, Sun, Moon, Brain, Play, Pause, Sliders, ChevronDown, CheckCircle, AlertTriangle, RotateCcw, Eye, Compass, Thermometer, Minimize, Coffee, Maximize, Lock, List, Grid, Shield, Command, Server, RefreshCw, CornerUpRight, AlertOctagon, BookOpen, BarChart, Globe, Check, XCircle, Layout, CreditCard, DollarSign, Users, Package, Award, Star, Briefcase, Building, Cpu as CpuIcon, Zap as ZapIcon } from 'lucide-react';

const ApexAgentCombinedUI = () => {
  // State management
  const [activeTab, setActiveTab] = useState('pricing');
  const [theme, setTheme] = useState('light');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [contextPanelVisible, setContextPanelVisible] = useState(true);
  const [showActionPopup, setShowActionPopup] = useState(true);
  const [selectedPricingTier, setSelectedPricingTier] = useState('pro');
  const [apiKeyOption, setApiKeyOption] = useState('apex'); // 'apex' or 'user'
  
  // Toggle functions
  const toggleSidebar = () => setSidebarCollapsed(!sidebarCollapsed);
  const toggleContextPanel = () => setContextPanelVisible(!contextPanelVisible);
  const toggleTheme = () => setTheme(theme === 'light' ? 'dark' : 'light');
  
  // Get theme colors
  const getThemeColors = () => {
    switch(theme) {
      case 'dark':
        return {
          bg: 'bg-gray-900',
          sidebar: 'bg-gray-800',
          card: 'bg-gray-800',
          cardBorder: 'border-gray-700',
          text: 'text-gray-100',
          textSecondary: 'text-gray-400',
          input: 'bg-gray-700',
          inputBorder: 'border-gray-600',
          hover: 'hover:bg-gray-700',
          table: 'bg-gray-800',
          tableHeader: 'bg-gray-700',
          tableBorder: 'border-gray-700',
          userMessage: 'bg-blue-900',
          agentMessage: 'bg-gray-800 border-gray-700'
        };
      default: // light
        return {
          bg: 'bg-gray-50',
          sidebar: 'bg-white',
          card: 'bg-white',
          cardBorder: 'border-gray-100',
          text: 'text-gray-800',
          textSecondary: 'text-gray-500',
          input: 'bg-gray-50',
          inputBorder: 'border-gray-100',
          hover: 'hover:bg-gray-100',
          table: 'bg-white',
          tableHeader: 'bg-gray-50',
          tableBorder: 'border-gray-100',
          userMessage: 'bg-blue-50',
          agentMessage: 'bg-white border-gray-100'
        };
    }
  };
  
  const colors = getThemeColors();
  
  // Pricing tiers data
  const pricingTiers = {
    basic: {
      name: 'Basic',
      apexPrice: 24.99,
      userPrice: 19.99,
      credits: 2000,
      standardLLMs: 2,
      advancedLLMs: 0,
      features: [
        'Document creation and editing',
        'Up to 2 standard LLMs',
        'Unlimited concurrent tasks',
        'Basic file system access'
      ]
    },
    pro: {
      name: 'Pro',
      apexPrice: 89.99,
      userPrice: 49.99,
      credits: 5000,
      standardLLMs: 3,
      advancedLLMs: 2,
      features: [
        'Document creation and editing',
        'Up to 3 standard LLMs',
        'Up to 2 High Reasoning LLMs',
        'Unlimited concurrent tasks',
        'Enhanced stability',
        'Extended context length',
        'Priority access during peak hours',
        'File system integration',
        'System integration'
      ]
    },
    expert: {
      name: 'Expert',
      apexPrice: 149.99,
      userPrice: 99.99,
      credits: 15000,
      standardLLMs: 'Unlimited',
      advancedLLMs: 'Unlimited',
      features: [
        'Document creation and editing',
        'Unlimited standard LLMs',
        'Unlimited High Reasoning LLMs',
        'Unlimited concurrent tasks',
        'Enhanced stability',
        'Extended context length',
        'Priority access during peak hours',
        'File system integration',
        'System integration',
        'Custom plugins',
        'Advanced analytics',
        'API access',
        'Priority support',
        'Early access to new features',
        'High-effort mode'
      ]
    },
    enterprise: {
      name: 'Enterprise',
      apexPrice: 'Custom',
      userPrice: 'Custom',
      credits: 'Custom allocation',
      standardLLMs: 'Unlimited',
      advancedLLMs: 'Unlimited',
      features: [
        'All Expert features',
        'Custom deployment options',
        'Advanced security features',
        'Account management',
        'Custom integrations',
        'Team collaboration',
        'Admin dashboard',
        'SSO integration',
        'Compliance features',
        'Per-seat, per-device, or site licensing'
      ]
    }
  };
  
  // Enterprise pricing options
  const enterprisePricing = {
    perSeat: {
      small: { range: '5-20 users', price: '$79/user/month' },
      medium: { range: '21-100 users', price: '$69/user/month' },
      large: { range: '101-500 users', price: '$59/user/month' },
      enterprise: { range: '500+ users', price: 'Custom pricing' }
    },
    perDevice: {
      standard: { price: '$129/device/month' },
      highUsage: { price: '$189/device/month' },
      shared: { price: '$259/device/month' }
    },
    siteLicense: {
      small: { range: 'Up to 500 users', price: '$18,000/year' },
      medium: { range: '501-2,000 users', price: '$39,000/year' },
      large: { range: '2,001-10,000 users', price: '$79,000/year' },
      enterprise: { range: '10,000+ users', price: 'Custom pricing' }
    }
  };
  
  // Credit management features
  const creditManagement = {
    tracking: [
      'Real-time credit balance monitoring',
      'Separate tracking for user-provided vs. ApexAgent APIs',
      'Detailed analytics on model usage and consumption rates',
      'Usage forecasting based on historical patterns',
      'Cost optimization recommendations'
    ],
    enterprise: [
      'Administrator-defined quotas for departments, teams, or users',
      'Role-based credit allocation',
      'Project-based budgeting',
      'Auto-scaling controls with approval workflows',
      'Usage governance policies'
    ]
  };
  
  // Render appropriate content based on active tab
  const renderContent = () => {
    switch(activeTab) {
      case 'pricing':
        return <PricingView 
          colors={colors} 
          pricingTiers={pricingTiers} 
          enterprisePricing={enterprisePricing}
          creditManagement={creditManagement}
          selectedTier={selectedPricingTier}
          setSelectedTier={setSelectedPricingTier}
          apiKeyOption={apiKeyOption}
          setApiKeyOption={setApiKeyOption}
        />;
      case 'chat':
        return <div className="p-6">Chat View</div>;
      case 'system':
        return <div className="p-6">System Monitor View</div>;
      case 'models':
        return <div className="p-6">LLM Models View</div>;
      default:
        return <PricingView 
          colors={colors} 
          pricingTiers={pricingTiers} 
          enterprisePricing={enterprisePricing}
          creditManagement={creditManagement}
          selectedTier={selectedPricingTier}
          setSelectedTier={setSelectedPricingTier}
          apiKeyOption={apiKeyOption}
          setApiKeyOption={setApiKeyOption}
        />;
    }
  };

  return (
    <div className={`flex h-screen w-full ${colors.bg} ${colors.text} overflow-hidden font-sans`}>
      {/* Left Sidebar - Navigation */}
      <div className={`${sidebarCollapsed ? 'w-16' : 'w-64'} h-full ${colors.sidebar} border-r ${colors.cardBorder} flex flex-col transition-all duration-200`}>
        <div className="p-4 flex items-center justify-between border-b border-gray-100">
          {!sidebarCollapsed && (
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-md bg-blue-600 flex items-center justify-center text-white font-bold">A</div>
              <h1 className="text-lg font-bold">ApexAgent</h1>
            </div>
          )}
          {sidebarCollapsed && (
            <div className="w-8 h-8 rounded-md bg-blue-600 flex items-center justify-center text-white font-bold mx-auto">A</div>
          )}
          <button 
            onClick={toggleSidebar} 
            className="p-1 rounded-md hover:bg-gray-100"
          >
            {sidebarCollapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
          </button>
        </div>
        
        <div className="flex-1 overflow-y-auto py-4">
          <div className="px-3 mb-2">
            <div className={`text-xs uppercase font-semibold mb-2 ${sidebarCollapsed ? 'text-center' : 'ml-2'} ${colors.textSecondary}`}>
              {!sidebarCollapsed && 'Main'}
            </div>
            <div className="space-y-1">
              <button 
                onClick={() => setActiveTab('pricing')}
                className={`flex items-center w-full py-2 px-2 rounded transition-colors ${
                  activeTab === 'pricing' 
                    ? 'bg-blue-100 text-blue-700' 
                    : `${colors.textSecondary} ${colors.hover}`
                }`}
              >
                <CreditCard size={18} className={`${sidebarCollapsed ? 'mx-auto' : 'mr-3'}`} />
                {!sidebarCollapsed && <span>Pricing</span>}
              </button>
              
              <button 
                onClick={() => setActiveTab('chat')}
                className={`flex items-center w-full py-2 px-2 rounded transition-colors ${
                  activeTab === 'chat' 
                    ? 'bg-blue-100 text-blue-700' 
                    : `${colors.textSecondary} ${colors.hover}`
                }`}
              >
                <MessageSquare size={18} className={`${sidebarCollapsed ? 'mx-auto' : 'mr-3'}`} />
                {!sidebarCollapsed && <span>Conversation</span>}
              </button>
              
              <button 
                onClick={() => setActiveTab('system')}
                className={`flex items-center w-full py-2 px-2 rounded transition-colors ${
                  activeTab === 'system' 
                    ? 'bg-blue-100 text-blue-700' 
                    : `${colors.textSecondary} ${colors.hover}`
                }`}
              >
                <Activity size={18} className={`${sidebarCollapsed ? 'mx-auto' : 'mr-3'}`} />
                {!sidebarCollapsed && <span>System Monitor</span>}
              </button>
              
              <button 
                onClick={() => setActiveTab('models')}
                className={`flex items-center w-full py-2 px-2 rounded transition-colors ${
                  activeTab === 'models' 
                    ? 'bg-blue-100 text-blue-700' 
                    : `${colors.textSecondary} ${colors.hover}`
                }`}
              >
                <Brain size={18} className={`${sidebarCollapsed ? 'mx-auto' : 'mr-3'}`} />
                {!sidebarCollapsed && <span>LLM Models</span>}
              </button>
            </div>
          </div>
          
          {!sidebarCollapsed && (
            <div className="px-3 mt-6">
              <div className={`text-xs uppercase font-semibold mb-2 ml-2 ${colors.textSecondary}`}>
                System Access
              </div>
              <div className="space-y-1">
                <button className={`flex items-center w-full py-2 px-2 rounded transition-colors ${colors.textSecondary} ${colors.hover}`}>
                  <Terminal size={18} className="mr-3" />
                  <span>Terminal</span>
                </button>
                
                <button className={`flex items-center w-full py-2 px-2 rounded transition-colors ${colors.textSecondary} ${colors.hover}`}>
                  <FileText size={18} className="mr-3" />
                  <span>File Explorer</span>
                </button>
                
                <button className={`flex items-center w-full py-2 px-2 rounded transition-colors ${colors.textSecondary} ${colors.hover}`}>
                  <Database size={18} className="mr-3" />
                  <span>Databases</span>
                </button>
              </div>
            </div>
          )}
        </div>
        
        <div className={`p-4 border-t ${colors.cardBorder}`}>
          {!sidebarCollapsed ? (
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <div className="w-8 h-8 rounded-full bg-gray-300"></div>
                <div className="ml-2">
                  <div className="text-sm font-medium">John Doe</div>
                  <div className="text-xs text-gray-500">Pro Plan</div>
                </div>
              </div>
              <button 
                onClick={toggleTheme}
                className={`${colors.textSecondary} hover:text-blue-500`}
              >
                {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
              </button>
            </div>
          ) : (
            <div className="flex flex-col items-center space-y-4">
              <div className="w-8 h-8 rounded-full bg-gray-300"></div>
              <button 
                onClick={toggleTheme}
                className={`${colors.textSecondary} hover:text-blue-500`}
              >
                {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
              </button>
            </div>
          )}
        </div>
      </div>
      
      {/* Main content area */}
      <div className="flex-1 flex flex-col h-full overflow-hidden">
        {/* Header with search and context panel toggle */}
        <div className={`h-16 px-6 flex items-center justify-between border-b ${colors.cardBorder}`}>
          <div className={`text-lg font-light ${colors.text}`}>
            {activeTab === 'pricing' && 'ApexAgent Pricing'}
            {activeTab === 'chat' && 'Conversation'}
            {activeTab === 'system' && 'System Monitor'}
            {activeTab === 'models' && 'LLM Models'}
          </div>
          <div className="flex items-center space-x-4">
            <div className={`w-64 h-9 ${colors.input} rounded-full flex items-center px-3 border ${colors.inputBorder}`}>
              <Search size={16} className={`${colors.textSecondary} mr-2`} />
              <input 
                type="text" 
                placeholder="Search..." 
                className={`bg-transparent border-none outline-none text-sm w-full ${colors.text}`} 
              />
            </div>
            
            <button 
              onClick={toggleContextPanel}
              className={`p-1.5 rounded ${colors.hover} ${colors.textSecondary}`}
            >
              {contextPanelVisible ? <Maximize2 size={18} /> : <Minimize size={18} />}
            </button>
          </div>
        </div>
        
        {/* Content area with optional right panel */}
        <div className="flex-1 flex overflow-hidden">
          {/* Main content */}
          <div className={`${contextPanelVisible ? 'flex-1' : 'w-full'} overflow-auto`}>
            {renderContent()}
          </div>
          
          {/* Right context panel */}
          {contextPanelVisible && (
            <div className={`w-80 h-full ${colors.sidebar} border-l ${colors.cardBorder} flex flex-col`}>
              <div className="p-4 border-b border-gray-100 flex items-center justify-between">
                <h2 className="text-sm font-medium">Usage & Credits</h2>
                <button className={`p-1 rounded ${colors.hover} ${colors.textSecondary}`}>
                  <RefreshCw size={14} />
                </button>
              </div>
              
              <div className="p-4">
                <div className="mb-4">
                  <div className="flex items-center justify-between mb-1">
                    <div className="text-xs text-gray-500">Current Plan</div>
                    <div className="text-xs font-medium text-blue-600">Upgrade</div>
                  </div>
                  <div className="flex items-center">
                    <div className="w-3 h-3 rounded-full bg-blue-500 mr-2"></div>
                    <div className="text-sm font-medium">Pro Plan</div>
                  </div>
                </div>
                
                <div className="mb-4">
                  <div className="flex items-center justify-between mb-1">
                    <div className="text-xs text-gray-500">Credits Remaining</div>
                    <div className="text-xs font-medium">3,245 / 5,000</div>
                  </div>
                  <div className="h-2 w-full bg-gray-100 rounded-full overflow-hidden">
                    <div className="h-full bg-blue-500 rounded-full" style={{width: "65%"}}></div>
                  </div>
                </div>
                
                <div className="mb-4">
                  <div className="flex items-center justify-between mb-1">
                    <div className="text-xs text-gray-500">Usage Forecast</div>
                    <div className="text-xs font-medium text-yellow-600">21 days left</div>
                  </div>
                  <div className={`p-3 rounded-lg ${colors.input} text-xs`}>
                    <div className="flex items-center justify-between mb-2">
                      <span>Daily average:</span>
                      <span className="font-medium">85 credits</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span>Monthly forecast:</span>
                      <span className="font-medium">2,550 credits</span>
                    </div>
                  </div>
                </div>
                
                <div className="mb-4">
                  <div className="text-xs text-gray-500 mb-2">Credit Usage by Type</div>
                  <div className="space-y-2">
                    <div>
                      <div className="flex items-center justify-between text-xs mb-1">
                        <span>LLM API Calls</span>
                        <span>68%</span>
                      </div>
                      <div className="h-1.5 w-full bg-gray-100 rounded-full overflow-hidden">
                        <div className="h-full bg-blue-500 rounded-full" style={{width: "68%"}}></div>
                      </div>
                    </div>
                    <div>
                      <div className="flex items-center justify-between text-xs mb-1">
                        <span>Document Processing</span>
                        <span>15%</span>
                      </div>
                      <div className="h-1.5 w-full bg-gray-100 rounded-full overflow-hidden">
                        <div className="h-full bg-green-500 rounded-full" style={{width: "15%"}}></div>
                      </div>
                    </div>
                    <div>
                      <div className="flex items-center justify-between text-xs mb-1">
                        <span>Code Execution</span>
                        <span>12%</span>
                      </div>
                      <div className="h-1.5 w-full bg-gray-100 rounded-full overflow-hidden">
                        <div className="h-full bg-purple-500 rounded-full" style={{width: "12%"}}></div>
                      </div>
                    </div>
                    <div>
                      <div className="flex items-center justify-between text-xs mb-1">
                        <span>Other</span>
                        <span>5%</span>
                      </div>
                      <div className="h-1.5 w-full bg-gray-100 rounded-full overflow-hidden">
                        <div className="h-full bg-gray-500 rounded-full" style={{width: "5%"}}></div>
                      </div>
                    </div>
                  </div>
                </div>
                
                <button className="w-full py-2 px-4 bg-blue-500 hover:bg-blue-600 text-white rounded-lg text-sm font-medium transition-colors">
                  Purchase Additional Credits
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
      
      {/* Agent Action Popup - subtle, unobtrusive */}
      {showActionPopup && (
        <div className="fixed bottom-24 right-8 flex flex-col space-y-2 items-end">
          <div className={`${theme === 'dark' ? 'bg-gray-800 bg-opacity-90 border-gray-700' : 'bg-white bg-opacity-90 border-gray-100'} backdrop-blur-sm rounded-lg shadow-md px-4 py-3 max-w-xs border flex items-center text-sm animate-fade-in-right`}>
            <div className="mr-3 w-8 h-8 rounded-full bg-blue-50 flex items-center justify-center">
              <CreditCard size={16} className="text-blue-500" />
            </div>
            <div className="flex-1">
              <div className={colors.text + " font-medium"}>Pricing model updated</div>
              <div className={colors.textSecondary + " text-xs mt-0.5"}>New credit system implemented</div>
            </div>
            <button 
              onClick={() => setShowActionPopup(false)}
              className="ml-2 text-gray-400 hover:text-gray-600"
            >
              <X size={14} />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

// Pricing View Component
const PricingView = ({ 
  colors, 
  pricingTiers, 
  enterprisePricing, 
  creditManagement,
  selectedTier,
  setSelectedTier,
  apiKeyOption,
  setApiKeyOption
}) => {
  return (
    <div className="flex-1 p-6 overflow-auto">
      <div className="max-w-6xl mx-auto">
        <div className="mb-8">
          <h1 className={`text-3xl font-light ${colors.text} mb-4`}>ApexAgent Pricing</h1>
          <p className={`text-lg ${colors.textSecondary}`}>
            Choose the plan that fits your needs with our flexible pricing options.
          </p>
        </div>
        
        {/* API Key Option Toggle */}
        <div className="mb-8">
          <div className="inline-flex p-1 rounded-lg bg-gray-100">
            <button
              onClick={() => setApiKeyOption('apex')}
              className={`py-2 px-4 rounded-md text-sm font-medium transition-colors ${
                apiKeyOption === 'apex' 
                  ? 'bg-white text-blue-700 shadow-sm' 
                  : 'text-gray-600'
              }`}
            >
              ApexAgent-Provided API Keys
            </button>
            <button
              onClick={() => setApiKeyOption('user')}
              className={`py-2 px-4 rounded-md text-sm font-medium transition-colors ${
                apiKeyOption === 'user' 
                  ? 'bg-white text-blue-700 shadow-sm' 
                  : 'text-gray-600'
              }`}
            >
              User-Provided API Keys
            </button>
          </div>
          <p className="mt-2 text-sm text-gray-500">
            {apiKeyOption === 'apex' 
              ? 'ApexAgent manages all API keys and handles billing with LLM providers.' 
              : 'Provide your own API keys for LLM providers and pay them directly.'}
          </p>
        </div>
        
        {/* Pricing Tiers */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          {Object.keys(pricingTiers).map((tier) => {
            const tierData = pricingTiers[tier];
            const isSelected = selectedTier === tier;
            const price = apiKeyOption === 'apex' ? tierData.apexPrice : tierData.userPrice;
            
            return (
              <div 
                key={tier}
                className={`${colors.card} rounded-xl shadow-sm border-2 transition-all ${
                  isSelected 
                    ? 'border-blue-500 shadow-md transform scale-[1.02]' 
                    : `${colors.cardBorder} hover:border-blue-200`
                } overflow-hidden`}
              >
                <div className={`p-6 ${isSelected ? 'bg-blue-50' : ''}`}>
                  <h3 className="text-xl font-semibold mb-2">{tierData.name}</h3>
                  <div className="flex items-end mb-4">
                    <span className="text-3xl font-bold">
                      {typeof price === 'number' ? `$${price}` : price}
                    </span>
                    {typeof price === 'number' && <span className="text-gray-500 ml-1">/month</span>}
                  </div>
                  
                  <div className="mb-6">
                    <div className="flex items-center mb-2">
                      <CreditCard size={16} className="text-blue-500 mr-2" />
                      <span className="text-sm font-medium">{tierData.credits} credits/month</span>
                    </div>
                    <div className="flex items-center mb-2">
                      <Brain size={16} className="text-blue-500 mr-2" />
                      <span className="text-sm font-medium">{tierData.standardLLMs} standard LLMs</span>
                    </div>
                    <div className="flex items-center">
                      <ZapIcon size={16} className="text-blue-500 mr-2" />
                      <span className="text-sm font-medium">{tierData.advancedLLMs} High Reasoning LLMs</span>
                    </div>
                  </div>
                  
                  <button
                    onClick={() => setSelectedTier(tier)}
                    className={`w-full py-2 rounded-lg transition-colors ${
                      isSelected
                        ? 'bg-blue-500 text-white'
                        : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
                    }`}
                  >
                    {isSelected ? 'Selected' : 'Select Plan'}
                  </button>
                </div>
                
                <div className="px-6 py-4 border-t border-gray-100 bg-gray-50">
                  <h4 className="text-sm font-medium mb-3">Features</h4>
                  <ul className="space-y-2">
                    {tierData.features.map((feature, index) => (
                      <li key={index} className="flex items-start">
                        <Check size={16} className="text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                        <span className="text-sm">{feature}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            );
          })}
        </div>
        
        {/* Enterprise Options */}
        {selectedTier === 'enterprise' && (
          <div className={`${colors.card} rounded-xl shadow-sm border ${colors.cardBorder} overflow-hidden mb-12`}>
            <div className="p-6 border-b border-gray-100">
              <h2 className="text-xl font-semibold mb-2">Enterprise Deployment Options</h2>
              <p className="text-gray-500">Flexible licensing options for organizations of all sizes.</p>
            </div>
            
            <div className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* Per-Seat Licensing */}
                <div className={`${colors.card} rounded-lg border ${colors.cardBorder} overflow-hidden`}>
                  <div className="p-4 bg-blue-50 border-b border-blue-100">
                    <div className="flex items-center">
                      <Users size={18} className="text-blue-600 mr-2" />
                      <h3 className="text-lg font-medium">Per-Seat Licensing</h3>
                    </div>
                  </div>
                  
                  <div className="p-4">
                    <p className="text-sm text-gray-500 mb-4">
                      License based on number of individual users.
                    </p>
                    
                    <div className="space-y-3">
                      {Object.keys(enterprisePricing.perSeat).map((tier) => {
                        const data = enterprisePricing.perSeat[tier];
                        return (
                          <div key={tier} className="flex justify-between items-center text-sm">
                            <span>{data.range}</span>
                            <span className="font-medium">{data.price}</span>
                          </div>
                        );
                      })}
                    </div>
                    
                    <div className="mt-4 text-xs text-blue-600">
                      * Educational institutions receive 35% discount
                    </div>
                  </div>
                </div>
                
                {/* Per-Device Licensing */}
                <div className={`${colors.card} rounded-lg border ${colors.cardBorder} overflow-hidden`}>
                  <div className="p-4 bg-purple-50 border-b border-purple-100">
                    <div className="flex items-center">
                      <Monitor size={18} className="text-purple-600 mr-2" />
                      <h3 className="text-lg font-medium">Per-Device Licensing</h3>
                    </div>
                  </div>
                  
                  <div className="p-4">
                    <p className="text-sm text-gray-500 mb-4">
                      License based on number of devices.
                    </p>
                    
                    <div className="space-y-3">
                      <div className="flex justify-between items-center text-sm">
                        <span>Standard Usage</span>
                        <span className="font-medium">{enterprisePricing.perDevice.standard.price}</span>
                      </div>
                      <div className="flex justify-between items-center text-sm">
                        <span>High Usage</span>
                        <span className="font-medium">{enterprisePricing.perDevice.highUsage.price}</span>
                      </div>
                      <div className="flex justify-between items-center text-sm">
                        <span>Shared Device</span>
                        <span className="font-medium">{enterprisePricing.perDevice.shared.price}</span>
                      </div>
                    </div>
                    
                    <div className="mt-4 text-xs text-purple-600">
                      * Volume discounts available for 50+ devices
                    </div>
                  </div>
                </div>
                
                {/* Site License */}
                <div className={`${colors.card} rounded-lg border ${colors.cardBorder} overflow-hidden`}>
                  <div className="p-4 bg-green-50 border-b border-green-100">
                    <div className="flex items-center">
                      <Building size={18} className="text-green-600 mr-2" />
                      <h3 className="text-lg font-medium">Site License</h3>
                    </div>
                  </div>
                  
                  <div className="p-4">
                    <p className="text-sm text-gray-500 mb-4">
                      Organization-wide license for educational and healthcare institutions.
                    </p>
                    
                    <div className="space-y-3">
                      {Object.keys(enterprisePricing.siteLicense).map((tier) => {
                        const data = enterprisePricing.siteLicense[tier];
                        return (
                          <div key={tier} className="flex justify-between items-center text-sm">
                            <span>{data.range}</span>
                            <span className="font-medium">{data.price}</span>
                          </div>
                        );
                      })}
                    </div>
                    
                    <div className="mt-4 text-xs text-green-600">
                      * Healthcare institutions receive 20% discount
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
        
        {/* Credit System */}
        <div className={`${colors.card} rounded-xl shadow-sm border ${colors.cardBorder} overflow-hidden mb-12`}>
          <div className="p-6 border-b border-gray-100">
            <h2 className="text-xl font-semibold mb-2">Credit System</h2>
            <p className="text-gray-500">
              {apiKeyOption === 'apex' 
                ? 'All plans include a monthly credit allocation. Additional credits can be purchased as needed.' 
                : 'When using your own API keys, credits are only consumed for operations using ApexAgent APIs.'}
            </p>
          </div>
          
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div>
                <h3 className="text-lg font-medium mb-4">Credit Consumption</h3>
                
                <div className={`${colors.table} rounded-lg border ${colors.tableBorder} overflow-hidden`}>
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className={`${colors.tableHeader}`}>
                      <tr>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Operation</th>
                        <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Credit Cost</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      <tr>
                        <td className="px-4 py-3 text-sm">Standard LLM API Call</td>
                        <td className="px-4 py-3 text-sm text-right">1.0 per 1K tokens</td>
                      </tr>
                      <tr>
                        <td className="px-4 py-3 text-sm">High Reasoning LLM API Call</td>
                        <td className="px-4 py-3 text-sm text-right">3.0 per 1K tokens</td>
                      </tr>
                      <tr>
                        <td className="px-4 py-3 text-sm">Document Processing</td>
                        <td className="px-4 py-3 text-sm text-right">2.0 per document</td>
                      </tr>
                      <tr>
                        <td className="px-4 py-3 text-sm">Code Execution</td>
                        <td className="px-4 py-3 text-sm text-right">5.0 per execution</td>
                      </tr>
                      <tr>
                        <td className="px-4 py-3 text-sm">System Integration</td>
                        <td className="px-4 py-3 text-sm text-right">3.0 per operation</td>
                      </tr>
                      <tr>
                        <td className="px-4 py-3 text-sm">File Operation</td>
                        <td className="px-4 py-3 text-sm text-right">0.5 per operation</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                
                <div className="mt-4">
                  <h4 className="text-md font-medium mb-2">Additional Credits</h4>
                  <div className="flex items-center justify-between text-sm border-b border-gray-100 py-2">
                    <span>Pay-as-you-go</span>
                    <span className="font-medium">$0.018 per credit</span>
                  </div>
                  <div className="flex items-center justify-between text-sm border-b border-gray-100 py-2">
                    <span>Credit Pack (1,000 credits)</span>
                    <span className="font-medium">$14.00 (22% savings)</span>
                  </div>
                  <div className="flex items-center justify-between text-sm py-2">
                    <span>Enterprise Bulk Credits</span>
                    <span className="font-medium">Volume discounts available</span>
                  </div>
                </div>
              </div>
              
              <div>
                <h3 className="text-lg font-medium mb-4">Credit Management</h3>
                
                <div className="mb-6">
                  <h4 className="text-md font-medium mb-2">Usage Tracking</h4>
                  <ul className="space-y-2">
                    {creditManagement.tracking.map((feature, index) => (
                      <li key={index} className="flex items-start">
                        <Check size={16} className="text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                        <span className="text-sm">{feature}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                
                <div>
                  <h4 className="text-md font-medium mb-2">Enterprise Controls</h4>
                  <ul className="space-y-2">
                    {creditManagement.enterprise.map((feature, index) => (
                      <li key={index} className="flex items-start">
                        <Check size={16} className="text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                        <span className="text-sm">{feature}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                
                {apiKeyOption === 'user' && (
                  <div className="mt-6 p-4 bg-blue-50 border border-blue-100 rounded-lg">
                    <h4 className="text-md font-medium mb-2 text-blue-700">User-Provided API Keys</h4>
                    <p className="text-sm text-blue-700 mb-2">
                      When you provide your own API keys:
                    </p>
                    <ul className="space-y-2">
                      <li className="flex items-start">
                        <Check size={16} className="text-blue-500 mr-2 mt-0.5 flex-shrink-0" />
                        <span className="text-sm">Operations using your API keys don't consume credits</span>
                      </li>
                      <li className="flex items-start">
                        <Check size={16} className="text-blue-500 mr-2 mt-0.5 flex-shrink-0" />
                        <span className="text-sm">Operations using ApexAgent's API keys consume credits from your allocation</span>
                      </li>
                      <li className="flex items-start">
                        <Check size={16} className="text-blue-500 mr-2 mt-0.5 flex-shrink-0" />
                        <span className="text-sm">Automatic switching between API sources based on availability</span>
                      </li>
                    </ul>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
        
        {/* FAQ Section */}
        <div className={`${colors.card} rounded-xl shadow-sm border ${colors.cardBorder} overflow-hidden`}>
          <div className="p-6 border-b border-gray-100">
            <h2 className="text-xl font-semibold">Frequently Asked Questions</h2>
          </div>
          
          <div className="p-6">
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-medium mb-2">What happens when I run out of credits?</h3>
                <p className="text-gray-600">
                  When you run out of credits, you can purchase additional credits immediately to continue using the service without interruption. You can set up auto-purchasing to ensure continuous operation.
                </p>
              </div>
              
              <div>
                <h3 className="text-lg font-medium mb-2">Can I switch between plans?</h3>
                <p className="text-gray-600">
                  Yes, you can upgrade or downgrade your plan at any time. When upgrading, the change takes effect immediately. When downgrading, the change takes effect at the end of your current billing cycle.
                </p>
              </div>
              
              <div>
                <h3 className="text-lg font-medium mb-2">How does the user-provided API keys option work?</h3>
                <p className="text-gray-600">
                  When you choose to use your own API keys, you'll need to provide valid API keys for the LLM providers you want to use. Operations using your API keys won't consume credits from your ApexAgent allocation. If you don't have an API key for a specific provider, ApexAgent will use its own API keys and deduct credits accordingly.
                </p>
              </div>
              
              <div>
                <h3 className="text-lg font-medium mb-2">Do unused credits roll over to the next month?</h3>
                <p className="text-gray-600">
                  No, credits do not roll over to the next month. Your credit allocation is refreshed at the beginning of each billing cycle.
                </p>
              </div>
              
              <div>
                <h3 className="text-lg font-medium mb-2">Are there any limits on concurrent tasks?</h3>
                <p className="text-gray-600">
                  All plans support unlimited concurrent tasks. This means you can run multiple operations simultaneously without restrictions, though each operation will consume credits according to the pricing table.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ApexAgentCombinedUI;
