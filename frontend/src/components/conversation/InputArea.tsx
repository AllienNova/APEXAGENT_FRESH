import React, { useState, useRef } from 'react';

interface InputAreaProps {
  onSendMessage: (message: string, attachments: File[]) => void;
  placeholder?: string;
  disabled?: boolean;
}

const InputArea: React.FC<InputAreaProps> = ({
  onSendMessage,
  placeholder = 'Type a message...',
  disabled = false
}) => {
  const [message, setMessage] = useState('');
  const [attachments, setAttachments] = useState<File[]>([]);
  const [isRecording, setIsRecording] = useState(false);
  const [showEmojiPicker, setShowEmojiPicker] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleSendMessage = () => {
    if (message.trim() || attachments.length > 0) {
      onSendMessage(message, attachments);
      setMessage('');
      setAttachments([]);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const newFiles = Array.from(e.target.files);
      setAttachments([...attachments, ...newFiles]);
    }
  };

  const handleRemoveAttachment = (index: number) => {
    const newAttachments = [...attachments];
    newAttachments.splice(index, 1);
    setAttachments(newAttachments);
  };

  const toggleRecording = () => {
    setIsRecording(!isRecording);
    // In a real implementation, this would start/stop voice recording
  };

  return (
    <div className="border-t border-border p-3">
      {/* Attachments preview */}
      {attachments.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-2">
          {attachments.map((file, index) => (
            <div key={index} className="bg-accent/30 rounded-md px-2 py-1 flex items-center gap-1">
              <span className="text-xs">{file.name}</span>
              <button 
                onClick={() => handleRemoveAttachment(index)}
                className="text-muted-foreground hover:text-foreground"
              >
                ✕
              </button>
            </div>
          ))}
        </div>
      )}
      
      {/* Input area */}
      <div className="flex items-end gap-2">
        <div className="flex-1 bg-background border border-input rounded-md">
          {/* Toolbar */}
          <div className="flex items-center px-3 py-2 border-b border-border">
            <button 
              className="p-1 rounded hover:bg-accent text-muted-foreground"
              onClick={() => fileInputRef.current?.click()}
              title="Attach file"
            >
              📎
            </button>
            <input 
              type="file" 
              ref={fileInputRef} 
              onChange={handleFileChange} 
              className="hidden" 
              multiple 
            />
            
            <button 
              className={`p-1 rounded hover:bg-accent ${isRecording ? 'text-red-500' : 'text-muted-foreground'}`}
              onClick={toggleRecording}
              title={isRecording ? 'Stop recording' : 'Start voice recording'}
            >
              🎤
            </button>
            
            <button 
              className="p-1 rounded hover:bg-accent text-muted-foreground"
              onClick={() => setShowEmojiPicker(!showEmojiPicker)}
              title="Insert emoji"
            >
              😊
            </button>
            
            <div className="flex-1"></div>
            
            <button 
              className="p-1 rounded hover:bg-accent text-muted-foreground"
              title="More options"
            >
              ⋯
            </button>
          </div>
          
          {/* Text input */}
          <div className="px-3 py-2">
            <textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={placeholder}
              disabled={disabled}
              className="w-full resize-none bg-transparent outline-none min-h-[60px] max-h-[200px] text-sm"
              rows={1}
            />
          </div>
          
          {/* Emoji picker (simplified) */}
          {showEmojiPicker && (
            <div className="border-t border-border p-2 max-h-[200px] overflow-y-auto">
              <div className="grid grid-cols-8 gap-1">
                {['😊', '😂', '🤔', '👍', '👎', '❤️', '🎉', '🔥', '👀', '🙏', '💯', '🤖', '💻', '📊', '📈', '🔍'].map((emoji, index) => (
                  <button 
                    key={index}
                    className="p-1 hover:bg-accent rounded"
                    onClick={() => {
                      setMessage(message + emoji);
                      setShowEmojiPicker(false);
                    }}
                  >
                    {emoji}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
        
        {/* Send button */}
        <button 
          onClick={handleSendMessage}
          disabled={!message.trim() && attachments.length === 0 || disabled}
          className={`p-3 rounded-md ${
            !message.trim() && attachments.length === 0 || disabled
              ? 'bg-muted text-muted-foreground'
              : 'bg-primary text-primary-foreground hover:bg-primary/90'
          }`}
          title="Send message"
        >
          📤
        </button>
      </div>
      
      {/* System suggestions */}
      <div className="mt-2 flex flex-wrap gap-1">
        <button className="px-2 py-1 text-xs bg-accent/30 rounded-full hover:bg-accent/50">
          Generate report
        </button>
        <button className="px-2 py-1 text-xs bg-accent/30 rounded-full hover:bg-accent/50">
          Analyze data
        </button>
        <button className="px-2 py-1 text-xs bg-accent/30 rounded-full hover:bg-accent/50">
          Write code
        </button>
      </div>
    </div>
  );
};

export default InputArea;
