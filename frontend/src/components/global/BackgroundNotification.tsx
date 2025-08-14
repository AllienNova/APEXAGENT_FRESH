import React, { useState } from 'react';

/**
 * Background Notification Component
 * 
 * This component displays a notification for background processing tasks
 * with progress tracking and minimize/close functionality.
 */
const BackgroundNotification = ({ 
  isVisible = true,
  task = 'Processing',
  progress = 0,
  onClose = () => {},
  onMinimize = () => {}
}) => {
  // State for component visibility
  const [visible, setVisible] = useState(isVisible);
  
  // State for minimized status
  const [minimized, setMinimized] = useState(false);
  
  // Handle minimize toggle
  const handleMinimize = () => {
    setMinimized(!minimized);
    onMinimize(!minimized);
  };
  
  // Handle close
  const handleClose = () => {
    setVisible(false);
    onClose();
  };
  
  // If not visible, don't render anything
  if (!visible) return null;
  
  return (
    <div className="fixed bottom-4 right-4 bg-white rounded-lg shadow-lg border border-indigo-200 w-80">
      <div className="p-4">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center">
            <div className="h-8 w-8 rounded-full bg-indigo-100 flex items-center justify-center mr-3">
              <i className="fas fa-cog fa-spin text-indigo-600"></i>
            </div>
            <h3 className="font-medium">Background Processing</h3>
          </div>
          <div className="flex">
            <button 
              onClick={handleMinimize}
              className="p-1 text-gray-400 hover:text-gray-500"
              aria-label={minimized ? "Expand" : "Minimize"}
            >
              <i className={`fas ${minimized ? 'fa-plus' : 'fa-minus'}`}></i>
            </button>
            <button 
              onClick={handleClose}
              className="p-1 text-gray-400 hover:text-gray-500 ml-1"
              aria-label="Close"
            >
              <i className="fas fa-times"></i>
            </button>
          </div>
        </div>
        
        {!minimized && (
          <>
            <p className="text-sm text-gray-600 mb-3">
              Aideon is continuing to work in the background on your {task.toLowerCase()}.
            </p>
            <div className="w-full bg-gray-200 rounded-full h-2.5 mb-1">
              <div 
                className="bg-indigo-600 h-2.5 rounded-full" 
                style={{ width: `${progress}%` }}
              ></div>
            </div>
            <div className="flex justify-between text-xs text-gray-500">
              <span>{task}</span>
              <span>{progress}%</span>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default BackgroundNotification;
