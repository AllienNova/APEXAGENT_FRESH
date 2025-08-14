import React, { useState, useEffect } from 'react';
import { ConversationApi } from '../api/apiService';

// Import components
import MessageThread from './MessageThread';
import InputArea from './InputArea';

interface ConversationInterfaceProps {
  conversationId?: string;
  showSystemActions?: boolean;
}

interface Message {
  id: string;
  content: string;
  sender: 'user' | 'agent';
  timestamp: string;
  systemActions?: SystemAction[];
  codeBlocks?: CodeBlock[];
}

interface SystemAction {
  type: 'file' | 'shell' | 'network';
  action: string;
  details: string;
  status: 'success' | 'error' | 'pending';
}

interface CodeBlock {
  language: string;
  code: string;
}

const ConversationInterface: React.FC<ConversationInterfaceProps> = ({
  conversationId,
  showSystemActions = true
}) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch conversation messages when conversationId changes
  useEffect(() => {
    if (conversationId) {
      fetchConversation(conversationId);
    } else {
      // If no conversationId, initialize with empty state
      setMessages([]);
    }
  }, [conversationId]);

  const fetchConversation = async (id: string) => {
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await ConversationApi.getConversation(id);
      
      if (response.data && response.data.messages) {
        setMessages(response.data.messages);
      }
    } catch (err: any) {
      console.error('Failed to fetch conversation:', err);
      setError(err.message || 'Failed to load conversation');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = async (message: string, attachments: File[]) => {
    if (!message.trim() && attachments.length === 0) return;
    
    // Optimistically add user message to UI
    const newUserMessage: Message = {
      id: `temp-${Date.now()}`,
      content: message,
      sender: 'user',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };
    
    setMessages(prev => [...prev, newUserMessage]);
    
    // Add temporary "thinking" message from agent
    const tempAgentMessage: Message = {
      id: `temp-agent-${Date.now()}`,
      content: "Processing your request...",
      sender: 'agent',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      systemActions: showSystemActions ? [
        {
          type: 'system',
          action: 'processing',
          details: 'Analyzing request',
          status: 'pending'
        }
      ] : []
    };
    
    setMessages(prev => [...prev, tempAgentMessage]);
    
    try {
      // Handle file uploads if any
      let attachmentPaths: string[] = [];
      
      if (attachments.length > 0) {
        // In a real implementation, this would upload files to the backend
        // and return their paths or IDs
        attachmentPaths = attachments.map(file => `/uploads/${file.name}`);
      }
      
      // Send message to backend
      const response = await ConversationApi.sendMessage(
        conversationId || 'new', 
        message,
        attachmentPaths
      );
      
      // Remove temporary messages
      setMessages(prev => prev.filter(msg => 
        !msg.id.startsWith('temp-')
      ));
      
      // Add the real response from the backend
      if (response.data && response.data.messages) {
        setMessages(prev => [...prev, ...response.data.messages]);
      }
    } catch (err: any) {
      console.error('Failed to send message:', err);
      
      // Update the temporary agent message to show the error
      setMessages(prev => prev.map(msg => 
        msg.id === tempAgentMessage.id 
          ? {
              ...msg,
              content: "Sorry, there was an error processing your request.",
              systemActions: [{
                type: 'system',
                action: 'error',
                details: err.message || 'Unknown error',
                status: 'error'
              }]
            }
          : msg
      ));
    }
  };

  return (
    <div className="flex flex-col h-full">
      <div className="border-b border-border p-3 flex items-center justify-between">
        <h1 className="font-semibold">Conversation</h1>
        <div className="flex items-center space-x-2">
          <button className="p-1 rounded-md hover:bg-accent text-muted-foreground" title="Start new conversation">
            ➕
          </button>
          <button className="p-1 rounded-md hover:bg-accent text-muted-foreground" title="More options">
            ⋯
          </button>
        </div>
      </div>
      
      {isLoading ? (
        <div className="flex-1 flex items-center justify-center">
          <div className="text-muted-foreground">Loading conversation...</div>
        </div>
      ) : error ? (
        <div className="flex-1 flex items-center justify-center">
          <div className="text-red-500">{error}</div>
        </div>
      ) : (
        <MessageThread messages={messages} />
      )}
      
      <InputArea 
        onSendMessage={handleSendMessage} 
        disabled={isLoading}
      />
    </div>
  );
};

export default ConversationInterface;
