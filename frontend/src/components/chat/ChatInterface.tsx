import React, { useState } from 'react';

/**
 * Main Chat Interface Component
 * 
 * This component implements the primary user interaction interface for Aideon AI Lite.
 * It handles message display, user input, and AI responses with thinking visualization.
 */
const ChatInterface = () => {
  // State for message history
  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: 'ai',
      content: "Hello! I'm Aideon AI Lite, your intelligent assistant. How can I help you today?",
      timestamp: new Date().toISOString(),
    }
  ]);
  
  // State for user input
  const [userInput, setUserInput] = useState('');
  
  // State for AI thinking process
  const [thinking, setThinking] = useState(false);
  const [thinkingProcess, setThinkingProcess] = useState('');
  
  // State for processing status
  const [processing, setProcessing] = useState(false);
  const [processingProgress, setProcessingProgress] = useState(0);
  const [processingTask, setProcessingTask] = useState('');
  
  // State for selected model
  const [selectedModel, setSelectedModel] = useState('GPT-4');
  
  // Handle user input change
  const handleInputChange = (e) => {
    setUserInput(e.target.value);
  };
  
  // Handle message submission
  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!userInput.trim()) return;
    
    // Add user message to history
    const newUserMessage = {
      id: messages.length + 1,
      sender: 'user',
      content: userInput,
      timestamp: new Date().toISOString(),
    };
    
    setMessages([...messages, newUserMessage]);
    setUserInput('');
    
    // Simulate AI thinking process
    simulateThinking(newUserMessage.content);
  };
  
  // Simulate AI thinking process
  const simulateThinking = (userMessage) => {
    setThinking(true);
    
    // Example thinking process for a data analysis request
    if (userMessage.toLowerCase().includes('analysis') || userMessage.toLowerCase().includes('data')) {
      setThinkingProcess(
        "To create a comprehensive analysis, I'll need to:\n" +
        "1. Gather the relevant data\n" +
        "2. Analyze key metrics (revenue, growth, product performance)\n" +
        "3. Create visualizations to highlight trends\n" +
        "4. Compare with previous periods and targets\n" +
        "5. Generate actionable insights"
      );
      
      // Simulate AI response after thinking
      setTimeout(() => {
        setThinking(false);
        
        const aiResponse = {
          id: messages.length + 2,
          sender: 'ai',
          content: "I'd be happy to help with your analysis. To get started, I'll need access to your data. You can either upload files, connect to a database, or point me to existing project files. Which would you prefer?",
          timestamp: new Date().toISOString(),
        };
        
        setMessages(prev => [...prev, aiResponse]);
        
        // Simulate processing after response
        simulateProcessing();
      }, 3000);
    } else {
      // Generic thinking process for other requests
      setThinkingProcess(
        "I'm analyzing your request to determine the best approach. I'll consider:\n" +
        "1. The specific task requirements\n" +
        "2. Available resources and data\n" +
        "3. Most efficient methods to accomplish this\n" +
        "4. How to present results clearly"
      );
      
      // Simulate AI response after thinking
      setTimeout(() => {
        setThinking(false);
        
        const aiResponse = {
          id: messages.length + 2,
          sender: 'ai',
          content: "I understand what you're looking for. Let me help you with that. What specific details or constraints should I be aware of for this task?",
          timestamp: new Date().toISOString(),
        };
        
        setMessages(prev => [...prev, aiResponse]);
      }, 2000);
    }
  };
  
  // Simulate processing with progress updates
  const simulateProcessing = () => {
    setProcessing(true);
    setProcessingTask('Analyzing data');
    
    // Simulate progress updates
    let progress = 0;
    const interval = setInterval(() => {
      progress += 5;
      setProcessingProgress(progress);
      
      if (progress >= 100) {
        clearInterval(interval);
        setProcessing(false);
        
        // Add results message
        const resultsMessage = {
          id: messages.length + 3,
          sender: 'ai',
          content: "I've completed the analysis of your data. Here are the key findings:\n\n" +
                   "- Total revenue increased by 12.3% compared to last quarter\n" +
                   "- Customer retention improved by 5.7%\n" +
                   "- The Western region showed the strongest growth at 18.5%\n" +
                   "- Product A continues to be the top performer\n\n" +
                   "Would you like me to generate a detailed report with visualizations?",
          timestamp: new Date().toISOString(),
        };
        
        setMessages(prev => [...prev, resultsMessage]);
      } else if (progress === 25) {
        setProcessingTask('Processing metrics');
      } else if (progress === 50) {
        setProcessingTask('Generating visualizations');
      } else if (progress === 75) {
        setProcessingTask('Preparing insights');
      }
    }, 300);
  };
  
  // Format timestamp
  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };
  
  return (
    <div className="flex flex-col h-full">
      {/* Chat history */}
      <div className="flex-1 overflow-y-auto mb-4 space-y-4 p-4">
        {messages.map((message) => (
          <div 
            key={message.id} 
            className={`flex items-start ${message.sender === 'user' ? 'justify-end' : ''}`}
          >
            {message.sender === 'ai' && (
              <div className="flex-shrink-0 h-10 w-10 rounded-full bg-indigo-100 flex items-center justify-center">
                <i className="fas fa-robot text-indigo-600"></i>
              </div>
            )}
            
            <div 
              className={`mx-3 p-4 rounded-lg shadow-sm max-w-3xl ${
                message.sender === 'user' 
                  ? 'bg-indigo-600 text-white' 
                  : 'bg-white text-gray-800'
              }`}
            >
              <p>{message.content}</p>
              <div className="text-xs mt-1 text-right opacity-70">
                {formatTime(message.timestamp)}
              </div>
            </div>
            
            {message.sender === 'user' && (
              <div className="flex-shrink-0 h-10 w-10 rounded-full bg-gray-300 flex items-center justify-center">
                <i className="fas fa-user text-gray-600"></i>
              </div>
            )}
          </div>
        ))}
        
        {/* AI thinking visualization */}
        {thinking && (
          <div className="flex items-start">
            <div className="flex-shrink-0 h-10 w-10 rounded-full bg-indigo-100 flex items-center justify-center">
              <i className="fas fa-robot text-indigo-600"></i>
            </div>
            <div className="ml-3 space-y-3 max-w-3xl">
              <div className="bg-gray-100 p-3 rounded-lg shadow-sm">
                <p className="text-sm text-gray-600 font-medium mb-1">Thinking...</p>
                <p className="text-gray-700 text-sm whitespace-pre-line">
                  {thinkingProcess}
                </p>
              </div>
            </div>
          </div>
        )}
        
        {/* Processing status */}
        {processing && (
          <div className="flex items-start">
            <div className="flex-shrink-0 h-10 w-10 rounded-full bg-indigo-100 flex items-center justify-center">
              <i className="fas fa-robot text-indigo-600"></i>
            </div>
            <div className="ml-3 bg-white p-4 rounded-lg shadow-sm max-w-3xl">
              <p className="text-gray-800 mb-3">
                {processingTask}. This should take a moment to complete.
              </p>
              <div className="w-full bg-gray-200 rounded-full h-2.5 mb-1">
                <div 
                  className="bg-indigo-600 h-2.5 rounded-full" 
                  style={{ width: `${processingProgress}%` }}
                ></div>
              </div>
              <p className="text-xs text-gray-500">Processing: {processingProgress}% complete</p>
            </div>
          </div>
        )}
      </div>
      
      {/* Input area */}
      <div className="bg-white rounded-lg shadow-sm p-4">
        <form onSubmit={handleSubmit} className="flex items-center">
          <button 
            type="button" 
            className="p-2 rounded-full text-gray-500 hover:bg-gray-100"
          >
            <i className="fas fa-paperclip"></i>
          </button>
          <button 
            type="button" 
            className="p-2 rounded-full text-gray-500 hover:bg-gray-100"
          >
            <i className="fas fa-microphone"></i>
          </button>
          <div className="flex-1 mx-2">
            <input 
              type="text" 
              value={userInput}
              onChange={handleInputChange}
              placeholder="Type your message..." 
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>
          <button 
            type="submit" 
            className="p-2 rounded-full bg-indigo-600 text-white hover:bg-indigo-700"
          >
            <i className="fas fa-paper-plane"></i>
          </button>
        </form>
        <div className="flex justify-between mt-2 px-2">
          <div className="text-xs text-gray-500">
            <span className="font-medium">{selectedModel}</span> • <span>Default</span>
          </div>
          <div className="flex space-x-2">
            <button 
              onClick={() => {/* Model selection logic */}} 
              className="text-xs text-indigo-600 hover:text-indigo-800"
            >
              Change Model
            </button>
            <button 
              onClick={() => {/* Advanced options logic */}} 
              className="text-xs text-indigo-600 hover:text-indigo-800"
            >
              Advanced Options
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;
