import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { 
  Send, 
  Bot, 
  User, 
  Brain, 
  Zap, 
  DollarSign, 
  Clock,
  Settings,
  Sparkles,
  MessageSquare,
  Cpu,
  Globe,
  CheckCircle,
  AlertCircle,
  Loader2
} from 'lucide-react';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
  model?: string;
  provider?: string;
  tokens?: {
    input: number;
    output: number;
  };
  cost?: number;
  responseTime?: number;
}

interface ModelConfig {
  id: string;
  name: string;
  provider: 'together-ai' | 'openai' | 'anthropic';
  costPer1M: {
    input: number;
    output: number;
  };
  maxTokens: number;
  description: string;
  capabilities: string[];
}

interface OptimizedChatInterfaceProps {
  className?: string;
  onMessage?: (message: Message) => void;
}

const AVAILABLE_MODELS: ModelConfig[] = [
  {
    id: 'meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo',
    name: 'Llama 3.1 8B Turbo',
    provider: 'together-ai',
    costPer1M: { input: 0.18, output: 0.59 },
    maxTokens: 8192,
    description: 'Fast, cost-effective model for general tasks',
    capabilities: ['chat', 'reasoning', 'coding']
  },
  {
    id: 'meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo',
    name: 'Llama 3.1 70B Turbo',
    provider: 'together-ai',
    costPer1M: { input: 0.88, output: 0.88 },
    maxTokens: 8192,
    description: 'Powerful model for complex reasoning',
    capabilities: ['chat', 'reasoning', 'coding', 'analysis']
  },
  {
    id: 'meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo',
    name: 'Llama 3.1 405B Turbo',
    provider: 'together-ai',
    costPer1M: { input: 3.50, output: 3.50 },
    maxTokens: 8192,
    description: 'State-of-the-art model for highest quality',
    capabilities: ['chat', 'reasoning', 'coding', 'analysis', 'creative']
  },
  {
    id: 'gpt-4',
    name: 'GPT-4',
    provider: 'openai',
    costPer1M: { input: 6.00, output: 6.00 },
    maxTokens: 8192,
    description: 'OpenAI flagship model (fallback)',
    capabilities: ['chat', 'reasoning', 'coding', 'analysis']
  }
];

export const OptimizedChatInterface: React.FC<OptimizedChatInterfaceProps> = ({ 
  className = "",
  onMessage 
}) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedModel, setSelectedModel] = useState(AVAILABLE_MODELS[0].id);
  const [totalCost, setTotalCost] = useState(0);
  const [totalTokens, setTotalTokens] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [showSettings, setShowSettings] = useState(false);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Auto-scroll to bottom
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  // Estimate tokens (rough approximation)
  const estimateTokens = useCallback((text: string): number => {
    return Math.ceil(text.split(/\s+/).length * 1.3);
  }, []);

  // Calculate cost for a message
  const calculateCost = useCallback((inputTokens: number, outputTokens: number, modelId: string): number => {
    const model = AVAILABLE_MODELS.find(m => m.id === modelId);
    if (!model) return 0;
    
    return (inputTokens * model.costPer1M.input + outputTokens * model.costPer1M.output) / 1000000;
  }, []);

  // Smart model selection based on input complexity
  const selectOptimalModel = useCallback((input: string): string => {
    const wordCount = input.split(/\s+/).length;
    const hasCodeKeywords = /\b(function|class|import|export|const|let|var|if|for|while)\b/i.test(input);
    const hasComplexKeywords = /\b(analyze|explain|complex|detailed|comprehensive)\b/i.test(input);
    
    if (wordCount > 100 || hasComplexKeywords) {
      return 'meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo'; // Medium model for complex tasks
    } else if (hasCodeKeywords) {
      return 'meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo'; // Fast model for coding
    } else {
      return 'meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo'; // Default to fast model
    }
  }, []);

  // Send message with optimized provider selection
  const sendMessage = useCallback(async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: input.trim(),
      role: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);
    setError(null);

    try {
      // Auto-select optimal model if not manually chosen
      const modelToUse = showSettings ? selectedModel : selectOptimalModel(input);
      const model = AVAILABLE_MODELS.find(m => m.id === modelToUse);
      
      const startTime = Date.now();
      
      // Try Together AI first, fallback to OpenAI
      const response = await sendToProvider(userMessage.content, modelToUse);
      
      const responseTime = Date.now() - startTime;
      const inputTokens = estimateTokens(userMessage.content);
      const outputTokens = estimateTokens(response.content);
      const cost = calculateCost(inputTokens, outputTokens, modelToUse);

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: response.content,
        role: 'assistant',
        timestamp: new Date(),
        model: model?.name,
        provider: model?.provider,
        tokens: { input: inputTokens, output: outputTokens },
        cost,
        responseTime
      };

      setMessages(prev => [...prev, assistantMessage]);
      setTotalCost(prev => prev + cost);
      setTotalTokens(prev => prev + inputTokens + outputTokens);

      if (onMessage) {
        onMessage(assistantMessage);
      }

    } catch (err) {
      console.error('Chat error:', err);
      setError('Failed to send message. Please try again.');
      
      // Add error message to chat
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: 'Sorry, I encountered an error processing your request. Please try again.',
        role: 'assistant',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  }, [input, isLoading, selectedModel, showSettings, selectOptimalModel, estimateTokens, calculateCost, onMessage]);

  // Send to AI provider with fallback
  const sendToProvider = async (content: string, modelId: string) => {
    const model = AVAILABLE_MODELS.find(m => m.id === modelId);
    
    if (model?.provider === 'together-ai') {
      try {
        return await sendToTogetherAI(content, modelId);
      } catch (err) {
        console.warn('Together AI failed, falling back to OpenAI:', err);
        return await sendToOpenAI(content);
      }
    } else {
      return await sendToOpenAI(content);
    }
  };

  // Together AI API call
  const sendToTogetherAI = async (content: string, modelId: string) => {
    const response = await fetch('/api/chat/together', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
      },
      body: JSON.stringify({
        model: modelId,
        messages: [
          { role: 'system', content: 'You are Aideon AI, a helpful and intelligent assistant.' },
          { role: 'user', content }
        ],
        max_tokens: 2000,
        temperature: 0.7
      })
    });

    if (!response.ok) {
      throw new Error(`Together AI API error: ${response.status}`);
    }

    const data = await response.json();
    return { content: data.choices[0].message.content };
  };

  // OpenAI API call (fallback)
  const sendToOpenAI = async (content: string) => {
    const response = await fetch('/api/chat/openai', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
      },
      body: JSON.stringify({
        model: 'gpt-4',
        messages: [
          { role: 'system', content: 'You are Aideon AI, a helpful and intelligent assistant.' },
          { role: 'user', content }
        ],
        max_tokens: 2000,
        temperature: 0.7
      })
    });

    if (!response.ok) {
      throw new Error(`OpenAI API error: ${response.status}`);
    }

    const data = await response.json();
    return { content: data.choices[0].message.content };
  };

  // Handle Enter key
  const handleKeyPress = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  }, [sendMessage]);

  // Clear chat
  const clearChat = useCallback(() => {
    setMessages([]);
    setTotalCost(0);
    setTotalTokens(0);
    setError(null);
  }, []);

  const selectedModelConfig = AVAILABLE_MODELS.find(m => m.id === selectedModel);

  return (
    <div className={`flex flex-col h-full ${className}`}>
      {/* Header with stats */}
      <Card className="mb-4">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center space-x-2">
              <MessageSquare className="h-5 w-5" />
              <span>Aideon AI Chat</span>
            </CardTitle>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2 text-sm">
                <DollarSign className="h-4 w-4" />
                <span>${totalCost.toFixed(4)}</span>
              </div>
              <div className="flex items-center space-x-2 text-sm">
                <Cpu className="h-4 w-4" />
                <span>{totalTokens.toLocaleString()} tokens</span>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowSettings(!showSettings)}
              >
                <Settings className="h-4 w-4" />
              </Button>
            </div>
          </div>
          
          {showSettings && (
            <div className="mt-4 p-4 border rounded-lg bg-muted/50">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium mb-2 block">Model Selection</label>
                  <Select value={selectedModel} onValueChange={setSelectedModel}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {AVAILABLE_MODELS.map(model => (
                        <SelectItem key={model.id} value={model.id}>
                          <div className="flex items-center space-x-2">
                            <Badge variant={model.provider === 'together-ai' ? 'default' : 'secondary'}>
                              {model.provider}
                            </Badge>
                            <span>{model.name}</span>
                            <span className="text-xs text-muted-foreground">
                              ${model.costPer1M.input}/1M
                            </span>
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  {selectedModelConfig && (
                    <p className="text-xs text-muted-foreground mt-1">
                      {selectedModelConfig.description}
                    </p>
                  )}
                </div>
                <div className="flex items-center space-x-2">
                  <Button variant="outline" size="sm" onClick={clearChat}>
                    Clear Chat
                  </Button>
                  <Badge variant="outline" className="flex items-center space-x-1">
                    <Globe className="h-3 w-3" />
                    <span>84% cost savings</span>
                  </Badge>
                </div>
              </div>
            </div>
          )}
        </CardHeader>
      </Card>

      {/* Messages */}
      <Card className="flex-1 flex flex-col">
        <CardContent className="flex-1 p-4 overflow-y-auto">
          <div className="space-y-4">
            {messages.length === 0 && (
              <div className="text-center py-8">
                <Bot className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                <h3 className="text-lg font-semibold mb-2">Welcome to Aideon AI</h3>
                <p className="text-muted-foreground">
                  Start a conversation with our AI assistant powered by Together AI
                </p>
              </div>
            )}
            
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] rounded-lg p-3 ${
                    message.role === 'user'
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-muted'
                  }`}
                >
                  <div className="flex items-start space-x-2">
                    {message.role === 'assistant' && (
                      <Bot className="h-5 w-5 mt-0.5 flex-shrink-0" />
                    )}
                    {message.role === 'user' && (
                      <User className="h-5 w-5 mt-0.5 flex-shrink-0" />
                    )}
                    <div className="flex-1">
                      <div className="prose prose-sm max-w-none">
                        {message.content}
                      </div>
                      {message.role === 'assistant' && (
                        <div className="flex items-center space-x-4 mt-2 text-xs opacity-70">
                          {message.model && (
                            <span className="flex items-center space-x-1">
                              <Brain className="h-3 w-3" />
                              <span>{message.model}</span>
                            </span>
                          )}
                          {message.responseTime && (
                            <span className="flex items-center space-x-1">
                              <Clock className="h-3 w-3" />
                              <span>{message.responseTime}ms</span>
                            </span>
                          )}
                          {message.cost && (
                            <span className="flex items-center space-x-1">
                              <DollarSign className="h-3 w-3" />
                              <span>${message.cost.toFixed(4)}</span>
                            </span>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
            
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-muted rounded-lg p-3 flex items-center space-x-2">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span>Thinking...</span>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>
        </CardContent>

        {/* Input */}
        <div className="p-4 border-t">
          {error && (
            <div className="mb-3 p-2 bg-red-50 border border-red-200 rounded-lg flex items-center space-x-2">
              <AlertCircle className="h-4 w-4 text-red-500" />
              <span className="text-red-700 text-sm">{error}</span>
            </div>
          )}
          
          <div className="flex space-x-2">
            <Textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message..."
              className="flex-1 min-h-[60px] resize-none"
              disabled={isLoading}
            />
            <Button
              onClick={sendMessage}
              disabled={!input.trim() || isLoading}
              size="lg"
              className="px-6"
            >
              {isLoading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </Button>
          </div>
          
          <div className="flex items-center justify-between mt-2 text-xs text-muted-foreground">
            <span>Press Enter to send, Shift+Enter for new line</span>
            {selectedModelConfig && (
              <span className="flex items-center space-x-1">
                <Sparkles className="h-3 w-3" />
                <span>Using {selectedModelConfig.name}</span>
              </span>
            )}
          </div>
        </div>
      </Card>
    </div>
  );
};

export default OptimizedChatInterface;

