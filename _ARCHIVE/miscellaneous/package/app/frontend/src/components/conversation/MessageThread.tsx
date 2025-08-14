import React, { useState } from 'react';

interface MessageProps {
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

const Message: React.FC<MessageProps> = ({
  content,
  sender,
  timestamp,
  systemActions = [],
  codeBlocks = []
}) => {
  const [showActions, setShowActions] = useState(false);

  const getActionIcon = (type: string) => {
    switch (type) {
      case 'file': return '📄';
      case 'shell': return '💻';
      case 'network': return '🌐';
      default: return '🔍';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success': return '✅';
      case 'error': return '❌';
      case 'pending': return '⏳';
      default: return '⏳';
    }
  };

  return (
    <div className={`mb-4 ${sender === 'user' ? 'mr-12' : 'ml-12'}`}>
      <div className={`p-4 rounded-lg ${
        sender === 'user' 
          ? 'bg-primary/10 border border-primary/20' 
          : 'bg-accent/30 border border-border'
      }`}>
        <div className="flex items-center justify-between mb-2">
          <div className="font-medium">
            {sender === 'user' ? 'You' : 'ApexAgent'}
          </div>
          <div className="text-xs text-muted-foreground">{timestamp}</div>
        </div>
        
        <div className="text-sm whitespace-pre-wrap mb-3">{content}</div>
        
        {/* Code blocks */}
        {codeBlocks.length > 0 && (
          <div className="space-y-3 mb-3">
            {codeBlocks.map((block, index) => (
              <div key={index} className="bg-card border border-border rounded-md overflow-hidden">
                <div className="bg-muted px-3 py-1 text-xs flex items-center justify-between">
                  <span>{block.language}</span>
                  <button className="hover:text-primary">Copy</button>
                </div>
                <pre className="p-3 text-xs overflow-x-auto">
                  <code>{block.code}</code>
                </pre>
              </div>
            ))}
          </div>
        )}
        
        {/* System actions */}
        {systemActions.length > 0 && (
          <div>
            <button 
              className="text-xs text-primary hover:underline flex items-center gap-1"
              onClick={() => setShowActions(!showActions)}
            >
              {showActions ? 'Hide' : 'Show'} system actions ({systemActions.length})
              <span>{showActions ? '▲' : '▼'}</span>
            </button>
            
            {showActions && (
              <div className="mt-2 space-y-1 border-t border-border pt-2">
                {systemActions.map((action, index) => (
                  <div key={index} className="text-xs flex items-center gap-1 p-1 rounded hover:bg-accent/20">
                    <span>{getActionIcon(action.type)}</span>
                    <span className="font-medium">{action.action}</span>
                    <span className="text-muted-foreground flex-1 truncate">{action.details}</span>
                    <span>{getStatusIcon(action.status)}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

interface MessageThreadProps {
  messages: MessageProps[];
}

const MessageThread: React.FC<MessageThreadProps> = ({ messages }) => {
  return (
    <div className="flex-1 overflow-y-auto p-4">
      {messages.map((message, index) => (
        <Message key={index} {...message} />
      ))}
    </div>
  );
};

export default MessageThread;
