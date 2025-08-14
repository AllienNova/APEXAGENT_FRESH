// Dr. TARDIS Multimodal Interface Component
import React, { useState, useEffect, useRef } from 'react';
import { Mic, MicOff, Camera, CameraOff, Send, Image, FileText, Play, Pause, SkipBack, SkipForward, Volume2, VolumeX, Maximize, Minimize, HelpCircle, Info, X, ChevronRight, ChevronDown, MessageSquare, Clock, RefreshCw, Download, Share2, Bookmark, Settings, User, Zap, Brain, Database, Server, Globe, Shield, Activity, Layers, Cpu } from 'lucide-react';

// Mock data for demonstration
const conversationHistory = [
  { id: 1, role: 'system', content: 'Hello! I\'m Dr. TARDIS, your multimodal assistant. How can I help you today?', timestamp: '2025-05-27 09:15:23', hasVisual: false },
  { id: 2, role: 'user', content: 'Can you explain how the agent orchestration works?', timestamp: '2025-05-27 09:15:45', hasVisual: false },
  { id: 3, role: 'system', content: 'The agent orchestration system in Aideon AI Lite coordinates multiple specialized agents to complete complex tasks. Let me show you a visualization of how it works.', timestamp: '2025-05-27 09:16:12', hasVisual: true, visualType: 'diagram', visualSrc: '/agent_orchestration_diagram.png' },
  { id: 4, role: 'system', content: 'As you can see, the Planner Agent first analyzes your request and creates a detailed execution plan. Then, specialized agents like the Execution Agent, Verification Agent, and Security Agent work together to complete different aspects of the task. The Optimization Agent ensures efficient resource usage, while the Learning Agent improves performance over time.', timestamp: '2025-05-27 09:16:45', hasVisual: false },
  { id: 5, role: 'user', content: 'That\'s interesting. Can you show me what\'s happening with my current task?', timestamp: '2025-05-27 09:17:10', hasVisual: false },
  { id: 6, role: 'system', content: 'Currently, your system is processing a complex data analysis task. Here\'s the real-time visualization of the agent activities:', timestamp: '2025-05-27 09:17:32', hasVisual: true, visualType: 'activity', visualSrc: '/agent_activity_visualization.png' },
  { id: 7, role: 'system', content: 'The Execution Agent is currently processing the data extraction subtask, which is about 65% complete. The Verification Agent is preparing to validate the results, and the Security Agent is continuously monitoring for any potential issues.', timestamp: '2025-05-27 09:18:05', hasVisual: false },
];

const suggestedQuestions = [
  "How does the zero-trust security architecture work?",
  "Can you explain the multi-region deployment capabilities?",
  "Show me the current system performance metrics",
  "What's happening with my current project?",
  "How does the vector database integration work?",
  "Explain the predictive failure detection system"
];

const DrTardisMultimodalInterface = () => {
  const [activeTab, setActiveTab] = useState('chat');
  const [inputValue, setInputValue] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [isCameraOn, setIsCameraOn] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [showExplanationPanel, setShowExplanationPanel] = useState(false);
  const [selectedMessage, setSelectedMessage] = useState(null);
  const [currentExplanation, setCurrentExplanation] = useState(null);
  const [showSuggestions, setShowSuggestions] = useState(true);
  
  const messagesEndRef = useRef(null);
  const chatContainerRef = useRef(null);
  
  // Scroll to bottom of messages
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [conversationHistory]);
  
  // Handle input submission
  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputValue.trim() === '') return;
    
    // In a real implementation, this would send the message to the backend
    console.log('Sending message:', inputValue);
    
    // Clear input
    setInputValue('');
    
    // Hide suggestions after user sends a message
    setShowSuggestions(false);
  };
  
  // Toggle recording
  const toggleRecording = () => {
    setIsRecording(!isRecording);
    // In a real implementation, this would start/stop audio recording
  };
  
  // Toggle camera
  const toggleCamera = () => {
    setIsCameraOn(!isCameraOn);
    // In a real implementation, this would start/stop camera
  };
  
  // Toggle playback
  const togglePlayback = () => {
    setIsPlaying(!isPlaying);
    // In a real implementation, this would control audio/video playback
  };
  
  // Toggle mute
  const toggleMute = () => {
    setIsMuted(!isMuted);
    // In a real implementation, this would mute/unmute audio
  };
  
  // Toggle fullscreen
  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
    // In a real implementation, this would toggle fullscreen mode
  };
  
  // Show explanation panel for a message
  const showExplanation = (message) => {
    setSelectedMessage(message);
    setShowExplanationPanel(true);
    
    // In a real implementation, this would fetch detailed explanations from the backend
    setCurrentExplanation({
      title: 'Agent Orchestration System',
      description: 'The Agent Orchestration System is the core coordination mechanism in Aideon AI Lite that enables multiple specialized agents to work together seamlessly.',
      details: [
        {
          title: 'Planner Agent',
          description: 'Analyzes user requests, breaks them down into subtasks, and creates execution plans.'
        },
        {
          title: 'Execution Agent',
          description: 'Carries out the actual tasks using 100+ integrated tools and APIs.'
        },
        {
          title: 'Verification Agent',
          description: 'Validates results against expected outcomes and quality standards.'
        },
        {
          title: 'Security Agent',
          description: 'Monitors operations for security threats and ensures compliance.'
        },
        {
          title: 'Optimization Agent',
          description: 'Manages resources and improves performance in real-time.'
        },
        {
          title: 'Learning Agent',
          description: 'Captures insights from each task to improve future performance.'
        }
      ],
      relatedConcepts: [
        'Multi-Agent Coordination',
        'Task Decomposition',
        'Parallel Processing',
        'Adaptive Learning'
      ],
      visualizations: [
        {
          type: 'diagram',
          title: 'Agent Interaction Flow',
          src: '/agent_interaction_flow.png'
        },
        {
          type: 'chart',
          title: 'Performance Metrics',
          src: '/agent_performance_metrics.png'
        }
      ]
    });
  };
  
  // Close explanation panel
  const closeExplanation = () => {
    setShowExplanationPanel(false);
    setSelectedMessage(null);
    setCurrentExplanation(null);
  };
  
  // Use a suggested question
  const useSuggestedQuestion = (question) => {
    setInputValue(question);
    // Focus the input field
    document.getElementById('message-input').focus();
  };
  
  // Message component
  const Message = ({ message }) => (
    <div className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`max-w-3/4 ${message.role === 'user' ? 'bg-blue-500 text-white' : 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700'} rounded-lg px-4 py-3 shadow`}>
        <div className="flex items-center mb-1">
          {message.role === 'system' && (
            <div className="w-6 h-6 rounded-full bg-purple-100 dark:bg-purple-900/20 flex items-center justify-center text-purple-500 mr-2">
              <Zap className="w-3 h-3" />
            </div>
          )}
          {message.role === 'user' && (
            <div className="w-6 h-6 rounded-full bg-blue-100 dark:bg-blue-900/20 flex items-center justify-center text-blue-500 mr-2">
              <User className="w-3 h-3" />
            </div>
          )}
          <span className="text-xs text-gray-500 dark:text-gray-400">{message.timestamp}</span>
          {message.role === 'system' && (
            <button 
              className="ml-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              onClick={() => showExplanation(message)}
            >
              <Info className="w-3 h-3" />
            </button>
          )}
        </div>
        <p className={`text-sm ${message.role === 'user' ? 'text-white' : 'text-gray-800 dark:text-gray-200'}`}>
          {message.content}
        </p>
        {message.hasVisual && (
          <div className="mt-2 rounded-lg overflow-hidden border border-gray-200 dark:border-gray-700">
            <img 
              src={message.visualSrc} 
              alt={`Visual for ${message.visualType}`} 
              className="w-full h-auto max-h-64 object-contain bg-gray-50 dark:bg-gray-900"
            />
            <div className="p-2 bg-gray-50 dark:bg-gray-900 text-xs text-gray-500 dark:text-gray-400 flex justify-between items-center">
              <span>{message.visualType === 'diagram' ? 'Diagram' : 'Visualization'}</span>
              <div className="flex space-x-2">
                <button className="hover:text-gray-700 dark:hover:text-gray-300">
                  <Maximize className="w-3 h-3" />
                </button>
                <button className="hover:text-gray-700 dark:hover:text-gray-300">
                  <Download className="w-3 h-3" />
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
  
  // Explanation panel component
  const ExplanationPanel = () => (
    <div className="fixed inset-y-0 right-0 w-1/3 bg-white dark:bg-gray-900 border-l border-gray-200 dark:border-gray-700 overflow-y-auto z-10 p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">{currentExplanation?.title}</h3>
        <button 
          className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
          onClick={closeExplanation}
        >
          <X className="w-5 h-5" />
        </button>
      </div>
      
      <p className="text-sm text-gray-600 dark:text-gray-400 mb-6">
        {currentExplanation?.description}
      </p>
      
      {currentExplanation?.visualizations && (
        <div className="mb-6">
          <h4 className="text-sm font-medium mb-2">Visualizations</h4>
          <div className="grid grid-cols-1 gap-4">
            {currentExplanation.visualizations.map((viz, index) => (
              <div key={index} className="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
                <img 
                  src={viz.src} 
                  alt={viz.title} 
                  className="w-full h-auto object-contain bg-gray-50 dark:bg-gray-900"
                />
                <div className="p-2 bg-gray-50 dark:bg-gray-900 text-xs">
                  <span className="font-medium">{viz.title}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {currentExplanation?.details && (
        <div className="mb-6">
          <h4 className="text-sm font-medium mb-2">Components</h4>
          <div className="space-y-3">
            {currentExplanation.details.map((detail, index) => (
              <div key={index} className="bg-gray-50 dark:bg-gray-800 rounded-lg p-3">
                <h5 className="text-sm font-medium mb-1">{detail.title}</h5>
                <p className="text-xs text-gray-600 dark:text-gray-400">
                  {detail.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {currentExplanation?.relatedConcepts && (
        <div>
          <h4 className="text-sm font-medium mb-2">Related Concepts</h4>
          <div className="flex flex-wrap gap-2">
            {currentExplanation.relatedConcepts.map((concept, index) => (
              <span 
                key={index} 
                className="px-2 py-1 bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-300 rounded-full text-xs"
              >
                {concept}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
  
  // Visual explanation component
  const VisualExplanation = () => (
    <div className="h-full flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold">System Visualization</h2>
        <div className="flex items-center space-x-3">
          <select className="px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800">
            <option>Agent Orchestration</option>
            <option>Security Architecture</option>
            <option>Memory Management</option>
            <option>Multi-Region Deployment</option>
          </select>
          <button className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg">
            <RefreshCw className="w-5 h-5" />
          </button>
        </div>
      </div>
      
      <div className="flex-grow bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 p-4 mb-4">
        <div className="h-full flex items-center justify-center">
          <div className="relative h-[500px] w-full">
            {/* This is a simplified visualization - in a real implementation, this would be a proper interactive diagram */}
            <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
              <div className="w-24 h-24 rounded-full bg-blue-100 dark:bg-blue-900/20 flex items-center justify-center text-blue-500 border-2 border-blue-500">
                <Brain className="w-12 h-12" />
              </div>
              <div className="text-center mt-2 font-medium">Orchestration Core</div>
            </div>
            
            <div className="absolute top-1/4 left-1/4">
              <div className="w-20 h-20 rounded-full bg-purple-100 dark:bg-purple-900/20 flex items-center justify-center text-purple-500 border-2 border-purple-500">
                <Layers className="w-10 h-10" />
              </div>
              <div className="text-center mt-2 font-medium text-sm">Planner Agent</div>
            </div>
            
            <div className="absolute top-1/4 right-1/4">
              <div className="w-20 h-20 rounded-full bg-green-100 dark:bg-green-900/20 flex items-center justify-center text-green-500 border-2 border-green-500">
                <Zap className="w-10 h-10" />
              </div>
              <div className="text-center mt-2 font-medium text-sm">Execution Agent</div>
            </div>
            
            <div className="absolute bottom-1/4 left-1/4">
              <div className="w-20 h-20 rounded-full bg-orange-100 dark:bg-orange-900/20 flex items-center justify-center text-orange-500 border-2 border-orange-500">
                <Shield className="w-10 h-10" />
              </div>
              <div className="text-center mt-2 font-medium text-sm">Security Agent</div>
            </div>
            
            <div className="absolute bottom-1/4 right-1/4">
              <div className="w-20 h-20 rounded-full bg-red-100 dark:bg-red-900/20 flex items-center justify-center text-red-500 border-2 border-red-500">
                <Activity className="w-10 h-10" />
              </div>
              <div className="text-center mt-2 font-medium text-sm">Verification Agent</div>
            </div>
            
            <div className="absolute top-[15%] left-1/2 transform -translate-x-1/2">
              <div className="w-20 h-20 rounded-full bg-yellow-100 dark:bg-yellow-900/20 flex items-center justify-center text-yellow-500 border-2 border-yellow-500">
                <Cpu className="w-10 h-10" />
              </div>
              <div className="text-center mt-2 font-medium text-sm">Optimization Agent</div>
            </div>
            
            <div className="absolute bottom-[15%] left-1/2 transform -translate-x-1/2">
              <div className="w-20 h-20 rounded-full bg-indigo-100 dark:bg-indigo-900/20 flex items-center justify-center text-indigo-500 border-2 border-indigo-500">
                <Database className="w-10 h-10" />
              </div>
              <div className="text-center mt-2 font-medium text-sm">Learning Agent</div>
            </div>
            
            {/* Connection lines would be SVG paths in a real implementation */}
            <svg className="absolute inset-0 w-full h-full pointer-events-none" style={{ zIndex: 0 }}>
              <path d="M 250,250 L 150,125" stroke="#8B5CF6" strokeWidth="2" fill="none" />
              <path d="M 250,250 L 350,125" stroke="#10B981" strokeWidth="2" fill="none" />
              <path d="M 250,250 L 150,375" stroke="#F97316" strokeWidth="2" fill="none" />
              <path d="M 250,250 L 350,375" stroke="#EF4444" strokeWidth="2" fill="none" />
              <path d="M 250,250 L 250,75" stroke="#EAB308" strokeWidth="2" fill="none" />
              <path d="M 250,250 L 250,425" stroke="#6366F1" strokeWidth="2" fill="none" />
            </svg>
          </div>
        </div>
      </div>
      
      <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
        <h3 className="font-semibold mb-3">Current System Activity</h3>
        <div className="space-y-3">
          <div>
            <div className="flex justify-between text-sm mb-1">
              <span className="flex items-center">
                <div className="w-2 h-2 rounded-full bg-green-500 mr-2"></div>
                Planner Agent
              </span>
              <span className="font-medium">Active</span>
            </div>
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
              <div className="h-2 rounded-full bg-green-500" style={{width: '100%'}}></div>
            </div>
          </div>
          
          <div>
            <div className="flex justify-between text-sm mb-1">
              <span className="flex items-center">
                <div className="w-2 h-2 rounded-full bg-green-500 mr-2"></div>
                Execution Agent
              </span>
              <span className="font-medium">Processing (65%)</span>
            </div>
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
              <div className="h-2 rounded-full bg-green-500" style={{width: '65%'}}></div>
            </div>
          </div>
          
          <div>
            <div className="flex justify-between text-sm mb-1">
              <span className="flex items-center">
                <div className="w-2 h-2 rounded-full bg-yellow-500 mr-2"></div>
                Verification Agent
              </span>
              <span className="font-medium">Standby</span>
            </div>
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
              <div className="h-2 rounded-full bg-yellow-500" style={{width: '10%'}}></div>
            </div>
          </div>
          
          <div>
            <div className="flex justify-between text-sm mb-1">
              <span className="flex items-center">
                <div className="w-2 h-2 rounded-full bg-green-500 mr-2"></div>
                Security Agent
              </span>
              <span className="font-medium">Monitoring</span>
            </div>
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
              <div className="h-2 rounded-full bg-green-500" style={{width: '100%'}}></div>
            </div>
          </div>
          
          <div>
            <div className="flex justify-between text-sm mb-1">
              <span className="flex items-center">
                <div className="w-2 h-2 rounded-full bg-green-500 mr-2"></div>
                Optimization Agent
              </span>
              <span className="font-medium">Active</span>
            </div>
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
              <div className="h-2 rounded-full bg-green-500" style={{width: '100%'}}></div>
            </div>
          </div>
          
          <div>
            <div className="flex justify-between text-sm mb-1">
              <span className="flex items-center">
                <div className="w-2 h-2 rounded-full bg-blue-500 mr-2"></div>
                Learning Agent
              </span>
              <span className="font-medium">Collecting Data</span>
            </div>
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
              <div className="h-2 rounded-full bg-blue-500" style={{width: '45%'}}></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
  
  // System monitoring component
  const SystemMonitoring = () => (
    <div className="h-full flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold">System Monitoring</h2>
        <div className="flex items-center space-x-3">
          <select className="px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800">
            <option>Last 1 Hour</option>
            <option>Last 24 Hours</option>
            <option>Last 7 Days</option>
            <option>Last 30 Days</option>
          </select>
          <button className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg">
            <RefreshCw className="w-5 h-5" />
          </button>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
        <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-medium text-sm">System Status</h3>
            <div className="w-2 h-2 rounded-full bg-green-500"></div>
          </div>
          <p className="text-2xl font-bold mb-1">Operational</p>
          <div className="flex items-center text-xs text-green-600">
            <span>All systems normal</span>
          </div>
        </div>
        
        <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-medium text-sm">Response Time</h3>
            <Activity className="w-5 h-5 text-blue-500" />
          </div>
          <p className="text-2xl font-bold mb-1">1.2s</p>
          <div className="flex items-center text-xs text-green-600">
            <span>Below 2s SLA target</span>
          </div>
        </div>
        
        <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-medium text-sm">Uptime</h3>
            <Clock className="w-5 h-5 text-purple-500" />
          </div>
          <p className="text-2xl font-bold mb-1">99.99%</p>
          <div className="flex items-center text-xs text-green-600">
            <span>Meeting SLA target</span>
          </div>
        </div>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="p-4 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold">Resource Usage</h3>
              <button className="text-xs text-blue-600 dark:text-blue-400 hover:underline">
                View Details
              </button>
            </div>
          </div>
          <div className="p-4">
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>CPU Usage</span>
                  <span className="font-medium">42%</span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div className="h-2 rounded-full bg-blue-500" style={{width: '42%'}}></div>
                </div>
              </div>
              
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Memory Usage</span>
                  <span className="font-medium">65%</span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div className="h-2 rounded-full bg-green-500" style={{width: '65%'}}></div>
                </div>
              </div>
              
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Storage Usage</span>
                  <span className="font-medium">28%</span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div className="h-2 rounded-full bg-purple-500" style={{width: '28%'}}></div>
                </div>
              </div>
              
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Network Bandwidth</span>
                  <span className="font-medium">37%</span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div className="h-2 rounded-full bg-yellow-500" style={{width: '37%'}}></div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="p-4 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold">Active Regions</h3>
              <button className="text-xs text-blue-600 dark:text-blue-400 hover:underline">
                View Map
              </button>
            </div>
          </div>
          <div className="p-4">
            <div className="space-y-3">
              <div className="flex items-center justify-between p-2 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800">
                <div className="flex items-center space-x-3">
                  <div className="w-2 h-2 rounded-full bg-green-500"></div>
                  <div>
                    <h4 className="text-sm font-medium">US East (N. Virginia)</h4>
                    <p className="text-xs text-gray-500">Primary</p>
                  </div>
                </div>
                <div className="text-sm font-medium">
                  12ms
                </div>
              </div>
              
              <div className="flex items-center justify-between p-2 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800">
                <div className="flex items-center space-x-3">
                  <div className="w-2 h-2 rounded-full bg-green-500"></div>
                  <div>
                    <h4 className="text-sm font-medium">US West (Oregon)</h4>
                    <p className="text-xs text-gray-500">Active</p>
                  </div>
                </div>
                <div className="text-sm font-medium">
                  45ms
                </div>
              </div>
              
              <div className="flex items-center justify-between p-2 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800">
                <div className="flex items-center space-x-3">
                  <div className="w-2 h-2 rounded-full bg-green-500"></div>
                  <div>
                    <h4 className="text-sm font-medium">EU (Ireland)</h4>
                    <p className="text-xs text-gray-500">Active</p>
                  </div>
                </div>
                <div className="text-sm font-medium">
                  78ms
                </div>
              </div>
              
              <div className="flex items-center justify-between p-2 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800">
                <div className="flex items-center space-x-3">
                  <div className="w-2 h-2 rounded-full bg-green-500"></div>
                  <div>
                    <h4 className="text-sm font-medium">Asia Pacific (Tokyo)</h4>
                    <p className="text-xs text-gray-500">Active</p>
                  </div>
                </div>
                <div className="text-sm font-medium">
                  112ms
                </div>
              </div>
              
              <div className="flex items-center justify-between p-2 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800">
                <div className="flex items-center space-x-3">
                  <div className="w-2 h-2 rounded-full bg-green-500"></div>
                  <div>
                    <h4 className="text-sm font-medium">Asia Pacific (Sydney)</h4>
                    <p className="text-xs text-gray-500">Active</p>
                  </div>
                </div>
                <div className="text-sm font-medium">
                  135ms
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 flex-grow">
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold">System Events</h3>
            <button className="text-xs text-blue-600 dark:text-blue-400 hover:underline">
              View All
            </button>
          </div>
        </div>
        <div className="p-4">
          <div className="space-y-3">
            <div className="flex items-start space-x-3 p-2 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800">
              <div className="w-8 h-8 rounded-lg bg-green-100 dark:bg-green-900/20 flex items-center justify-center text-green-500 flex-shrink-0">
                <RefreshCw className="w-4 h-4" />
              </div>
              <div>
                <div className="flex items-center space-x-2">
                  <h4 className="text-sm font-medium">System Update Completed</h4>
                  <span className="text-xs text-gray-500">10 minutes ago</span>
                </div>
                <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                  System updated to version 4.2.1 with enhanced security features
                </p>
              </div>
            </div>
            
            <div className="flex items-start space-x-3 p-2 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800">
              <div className="w-8 h-8 rounded-lg bg-blue-100 dark:bg-blue-900/20 flex items-center justify-center text-blue-500 flex-shrink-0">
                <Globe className="w-4 h-4" />
              </div>
              <div>
                <div className="flex items-center space-x-2">
                  <h4 className="text-sm font-medium">Region Failover Test</h4>
                  <span className="text-xs text-gray-500">1 hour ago</span>
                </div>
                <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                  Scheduled failover test completed successfully with 0.8s transition time
                </p>
              </div>
            </div>
            
            <div className="flex items-start space-x-3 p-2 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800">
              <div className="w-8 h-8 rounded-lg bg-purple-100 dark:bg-purple-900/20 flex items-center justify-center text-purple-500 flex-shrink-0">
                <Database className="w-4 h-4" />
              </div>
              <div>
                <div className="flex items-center space-x-2">
                  <h4 className="text-sm font-medium">Database Optimization</h4>
                  <span className="text-xs text-gray-500">3 hours ago</span>
                </div>
                <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                  Automatic database optimization reduced query times by 15%
                </p>
              </div>
            </div>
            
            <div className="flex items-start space-x-3 p-2 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800">
              <div className="w-8 h-8 rounded-lg bg-yellow-100 dark:bg-yellow-900/20 flex items-center justify-center text-yellow-500 flex-shrink-0">
                <Shield className="w-4 h-4" />
              </div>
              <div>
                <div className="flex items-center space-x-2">
                  <h4 className="text-sm font-medium">Security Scan Completed</h4>
                  <span className="text-xs text-gray-500">6 hours ago</span>
                </div>
                <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                  Weekly security scan completed with no critical vulnerabilities detected
                </p>
              </div>
            </div>
            
            <div className="flex items-start space-x-3 p-2 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800">
              <div className="w-8 h-8 rounded-lg bg-red-100 dark:bg-red-900/20 flex items-center justify-center text-red-500 flex-shrink-0">
                <Server className="w-4 h-4" />
              </div>
              <div>
                <div className="flex items-center space-x-2">
                  <h4 className="text-sm font-medium">Resource Scaling</h4>
                  <span className="text-xs text-gray-500">12 hours ago</span>
                </div>
                <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                  Automatic scaling added 2 compute units to handle increased load
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
  
  return (
    <div className={`h-full flex flex-col ${isFullscreen ? 'fixed inset-0 z-50 bg-white dark:bg-gray-900 p-4' : ''}`}>
      <div className="flex border-b border-gray-200 dark:border-gray-700 mb-6">
        <button 
          className={`px-4 py-2 font-medium text-sm ${activeTab === 'chat' ? 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-500' : 'text-gray-600 dark:text-gray-400'}`}
          onClick={() => setActiveTab('chat')}
        >
          Chat
        </button>
        <button 
          className={`px-4 py-2 font-medium text-sm ${activeTab === 'visual' ? 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-500' : 'text-gray-600 dark:text-gray-400'}`}
          onClick={() => setActiveTab('visual')}
        >
          Visual Explanation
        </button>
        <button 
          className={`px-4 py-2 font-medium text-sm ${activeTab === 'monitoring' ? 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-500' : 'text-gray-600 dark:text-gray-400'}`}
          onClick={() => setActiveTab('monitoring')}
        >
          System Monitoring
        </button>
        <div className="ml-auto flex items-center">
          <button 
            className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
            onClick={toggleFullscreen}
          >
            {isFullscreen ? <Minimize className="w-5 h-5" /> : <Maximize className="w-5 h-5" />}
          </button>
          <button className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200">
            <Settings className="w-5 h-5" />
          </button>
          <button className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200">
            <HelpCircle className="w-5 h-5" />
          </button>
        </div>
      </div>
      
      <div className="flex-grow relative">
        {activeTab === 'chat' && (
          <div className="h-full flex flex-col" ref={chatContainerRef}>
            <div className="flex-grow overflow-y-auto p-4">
              {conversationHistory.map(message => (
                <Message key={message.id} message={message} />
              ))}
              <div ref={messagesEndRef} />
              
              {showSuggestions && (
                <div className="mt-6">
                  <h3 className="text-sm font-medium mb-2">Suggested Questions</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                    {suggestedQuestions.map((question, index) => (
                      <button 
                        key={index}
                        className="text-left p-2 text-sm bg-gray-50 dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
                        onClick={() => useSuggestedQuestion(question)}
                      >
                        {question}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
            
            <div className="p-4 border-t border-gray-200 dark:border-gray-700">
              <form onSubmit={handleSubmit} className="flex items-end space-x-2">
                <div className="flex-grow relative">
                  <textarea
                    id="message-input"
                    className="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none bg-white dark:bg-gray-800"
                    placeholder="Ask Dr. TARDIS anything..."
                    rows={1}
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                  />
                  <div className="absolute bottom-2 right-2 flex space-x-1">
                    <button 
                      type="button" 
                      className={`p-1 rounded-full ${isRecording ? 'text-red-500 bg-red-100 dark:bg-red-900/20' : 'text-gray-400 hover:text-gray-600 dark:hover:text-gray-300'}`}
                      onClick={toggleRecording}
                    >
                      {isRecording ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
                    </button>
                    <button 
                      type="button" 
                      className={`p-1 rounded-full ${isCameraOn ? 'text-blue-500 bg-blue-100 dark:bg-blue-900/20' : 'text-gray-400 hover:text-gray-600 dark:hover:text-gray-300'}`}
                      onClick={toggleCamera}
                    >
                      {isCameraOn ? <CameraOff className="w-4 h-4" /> : <Camera className="w-4 h-4" />}
                    </button>
                    <button 
                      type="button" 
                      className="p-1 rounded-full text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                    >
                      <Image className="w-4 h-4" />
                    </button>
                    <button 
                      type="button" 
                      className="p-1 rounded-full text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                    >
                      <FileText className="w-4 h-4" />
                    </button>
                  </div>
                </div>
                <button 
                  type="submit" 
                  className="p-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
                  disabled={inputValue.trim() === ''}
                >
                  <Send className="w-5 h-5" />
                </button>
              </form>
              
              {(isRecording || isCameraOn) && (
                <div className="mt-3 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    {isRecording && <Mic className="w-4 h-4 text-red-500" />}
                    {isCameraOn && <Camera className="w-4 h-4 text-blue-500" />}
                    <span className="text-sm">
                      {isRecording && isCameraOn ? 'Recording audio and video...' : 
                       isRecording ? 'Recording audio...' : 'Camera active...'}
                    </span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <button 
                      className="p-1 rounded-full text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                      onClick={togglePlayback}
                    >
                      {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                    </button>
                    <button 
                      className="p-1 rounded-full text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                    >
                      <SkipBack className="w-4 h-4" />
                    </button>
                    <button 
                      className="p-1 rounded-full text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                    >
                      <SkipForward className="w-4 h-4" />
                    </button>
                    <button 
                      className="p-1 rounded-full text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                      onClick={toggleMute}
                    >
                      {isMuted ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
        
        {activeTab === 'visual' && <VisualExplanation />}
        {activeTab === 'monitoring' && <SystemMonitoring />}
        
        {showExplanationPanel && currentExplanation && <ExplanationPanel />}
      </div>
    </div>
  );
};

export default DrTardisMultimodalInterface;
