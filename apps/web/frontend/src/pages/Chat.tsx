/**
 * Chat Page - Multi-Model AI Interface
 * 
 * Comprehensive chat interface with horizontal tabs for different AI capabilities:
 * - Chat: Multi-model conversation interface
 * - Artifacts: AI-generated content management
 * - Models: AI model selection and configuration
 * - Agents: Specialized AI agent orchestration
 * - Files: File management and processing
 * - Analytics: Real-time performance metrics
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Container,
  Paper,
  Tabs,
  Tab,
  Typography,
  TextField,
  Button,
  IconButton,
  Avatar,
  Chip,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Slider,
  Switch,
  FormControlLabel,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  ListItemSecondaryAction,
  Card,
  CardContent,
  CardActions,
  Grid,
  LinearProgress,
  Tooltip,
  Badge,
  Menu,
  MenuList,
  ListItemIcon,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Fab,
  SpeedDial,
  SpeedDialAction,
  SpeedDialIcon,
} from '@mui/material';
import {
  Send as SendIcon,
  Mic as MicIcon,
  AttachFile as AttachFileIcon,
  MoreVert as MoreVertIcon,
  SmartToy as SmartToyIcon,
  Code as CodeIcon,
  Image as ImageIcon,
  Description as DescriptionIcon,
  Analytics as AnalyticsIcon,
  Settings as SettingsIcon,
  Refresh as RefreshIcon,
  Download as DownloadIcon,
  Share as ShareIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  Copy as CopyIcon,
  Bookmark as BookmarkIcon,
  History as HistoryIcon,
  TrendingUp as TrendingUpIcon,
  Speed as SpeedIcon,
  Memory as MemoryIcon,
  Psychology as PsychologyIcon,
  AutoAwesome as AutoAwesomeIcon,
  Lightbulb as LightbulbIcon,
  Science as ScienceIcon,
  Build as BuildIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'react-toastify';
import { motion, AnimatePresence } from 'framer-motion';

// Hooks
import { useAuth } from '../hooks/useAuth';
import { useWebSocket } from '../hooks/useWebSocket';
import { useChat } from '../hooks/useChat';
import { useModels } from '../hooks/useModels';
import { useAgents } from '../hooks/useAgents';
import { useFiles } from '../hooks/useFiles';
import { useAnalytics } from '../hooks/useAnalytics';

// Components
import ChatMessage from '../components/chat/ChatMessage';
import ModelSelector from '../components/chat/ModelSelector';
import AgentOrchestrator from '../components/agents/AgentOrchestrator';
import FileManager from '../components/files/FileManager';
import ArtifactViewer from '../components/artifacts/ArtifactViewer';
import AnalyticsDashboard from '../components/analytics/AnalyticsDashboard';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorAlert from '../components/common/ErrorAlert';

// Types
interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  model?: string;
  timestamp: Date;
  tokens?: number;
  cost?: number;
  processingTime?: number;
  artifacts?: any[];
}

interface ConversationSettings {
  model: string;
  temperature: number;
  maxTokens: number;
  systemPrompt: string;
  stream: boolean;
}

// Tab Panel Component
function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`chat-tabpanel-${index}`}
      aria-labelledby={`chat-tab-${index}`}
      {...other}
      style={{ height: '100%', overflow: 'hidden' }}
    >
      {value === index && (
        <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
          {children}
        </Box>
      )}
    </div>
  );
}

function a11yProps(index: number) {
  return {
    id: `chat-tab-${index}`,
    'aria-controls': `chat-tabpanel-${index}`,
  };
}

const Chat: React.FC = () => {
  const { conversationId } = useParams<{ conversationId: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  const { socket, isConnected } = useWebSocket();
  const queryClient = useQueryClient();

  // State management
  const [activeTab, setActiveTab] = useState(0);
  const [message, setMessage] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [settings, setSettings] = useState<ConversationSettings>({
    model: 'gpt-4-turbo',
    temperature: 0.7,
    maxTokens: 2000,
    systemPrompt: '',
    stream: true,
  });

  // Refs
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messageInputRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Custom hooks
  const {
    messages,
    isLoading: isChatLoading,
    sendMessage,
    streamingMessage,
    isStreaming,
  } = useChat(conversationId);

  const { models, isLoading: isModelsLoading } = useModels();
  const { agents, isLoading: isAgentsLoading } = useAgents();
  const { files, uploadFile, isUploading } = useFiles();
  const { analytics } = useAnalytics();

  // Effects
  useEffect(() => {
    scrollToBottom();
  }, [messages, streamingMessage]);

  useEffect(() => {
    // Focus message input when component mounts
    if (messageInputRef.current) {
      messageInputRef.current.focus();
    }
  }, []);

  useEffect(() => {
    // WebSocket event listeners
    if (socket) {
      socket.on('message_received', handleMessageReceived);
      socket.on('agent_status_update', handleAgentStatusUpdate);
      socket.on('file_processed', handleFileProcessed);

      return () => {
        socket.off('message_received');
        socket.off('agent_status_update');
        socket.off('file_processed');
      };
    }
  }, [socket]);

  // Event handlers
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const handleSendMessage = useCallback(async () => {
    if (!message.trim() || isStreaming) return;

    try {
      await sendMessage({
        content: message,
        model: settings.model,
        temperature: settings.temperature,
        maxTokens: settings.maxTokens,
        systemPrompt: settings.systemPrompt,
        stream: settings.stream,
      });

      setMessage('');
      
      // Track analytics
      if (analytics) {
        analytics.track('message_sent', {
          model: settings.model,
          messageLength: message.length,
          conversationId,
        });
      }
    } catch (error) {
      toast.error('Failed to send message');
      console.error('Send message error:', error);
    }
  }, [message, settings, sendMessage, isStreaming, analytics, conversationId]);

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSendMessage();
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    try {
      for (const file of Array.from(files)) {
        await uploadFile(file);
        toast.success(`File "${file.name}" uploaded successfully`);
      }
    } catch (error) {
      toast.error('Failed to upload file');
      console.error('File upload error:', error);
    }
  };

  const handleVoiceRecording = () => {
    if (isRecording) {
      // Stop recording
      setIsRecording(false);
      // Implement voice recording stop logic
    } else {
      // Start recording
      setIsRecording(true);
      // Implement voice recording start logic
    }
  };

  const handleMessageReceived = (data: any) => {
    // Handle real-time message updates
    queryClient.invalidateQueries(['chat', conversationId]);
  };

  const handleAgentStatusUpdate = (data: any) => {
    // Handle agent status updates
    queryClient.invalidateQueries(['agents']);
  };

  const handleFileProcessed = (data: any) => {
    // Handle file processing completion
    queryClient.invalidateQueries(['files']);
    toast.success(`File "${data.filename}" processed successfully`);
  };

  const handleModelChange = (newModel: string) => {
    setSettings(prev => ({ ...prev, model: newModel }));
  };

  const handleSettingsChange = (key: keyof ConversationSettings, value: any) => {
    setSettings(prev => ({ ...prev, [key]: value }));
  };

  // Speed dial actions
  const speedDialActions = [
    {
      icon: <AttachFileIcon />,
      name: 'Upload File',
      onClick: () => fileInputRef.current?.click(),
    },
    {
      icon: <MicIcon />,
      name: isRecording ? 'Stop Recording' : 'Voice Input',
      onClick: handleVoiceRecording,
    },
    {
      icon: <SmartToyIcon />,
      name: 'Launch Agent',
      onClick: () => setActiveTab(3),
    },
    {
      icon: <CodeIcon />,
      name: 'Code Assistant',
      onClick: () => {
        setMessage('/code ');
        messageInputRef.current?.focus();
      },
    },
  ];

  if (isChatLoading && !messages.length) {
    return <LoadingSpinner />;
  }

  return (
    <Container maxWidth={false} sx={{ height: '100vh', display: 'flex', flexDirection: 'column', p: 0 }}>
      {/* Header with Tabs */}
      <Paper 
        elevation={0} 
        sx={{ 
          borderBottom: 1, 
          borderColor: 'divider',
          backgroundColor: 'background.paper',
        }}
      >
        <Tabs
          value={activeTab}
          onChange={handleTabChange}
          variant="scrollable"
          scrollButtons="auto"
          sx={{
            '& .MuiTab-root': {
              minWidth: 120,
              fontWeight: 500,
            },
          }}
        >
          <Tab 
            icon={<SmartToyIcon />} 
            label="Chat" 
            {...a11yProps(0)}
            iconPosition="start"
          />
          <Tab 
            icon={<AutoAwesomeIcon />} 
            label="Artifacts" 
            {...a11yProps(1)}
            iconPosition="start"
          />
          <Tab 
            icon={<PsychologyIcon />} 
            label="Models" 
            {...a11yProps(2)}
            iconPosition="start"
          />
          <Tab 
            icon={<ScienceIcon />} 
            label="Agents" 
            {...a11yProps(3)}
            iconPosition="start"
          />
          <Tab 
            icon={<DescriptionIcon />} 
            label="Files" 
            {...a11yProps(4)}
            iconPosition="start"
          />
          <Tab 
            icon={<AnalyticsIcon />} 
            label="Analytics" 
            {...a11yProps(5)}
            iconPosition="start"
          />
        </Tabs>
      </Paper>

      {/* Tab Content */}
      <Box sx={{ flexGrow: 1, overflow: 'hidden' }}>
        {/* Chat Tab */}
        <TabPanel value={activeTab} index={0}>
          <Box sx={{ display: 'flex', height: '100%' }}>
            {/* Main Chat Area */}
            <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
              {/* Messages Area */}
              <Box 
                sx={{ 
                  flexGrow: 1, 
                  overflow: 'auto', 
                  p: 2,
                  backgroundColor: 'background.default',
                }}
              >
                <AnimatePresence>
                  {messages.map((msg, index) => (
                    <motion.div
                      key={msg.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      transition={{ duration: 0.3, delay: index * 0.1 }}
                    >
                      <ChatMessage
                        message={msg}
                        isUser={msg.role === 'user'}
                        model={msg.model}
                        timestamp={msg.timestamp}
                        tokens={msg.tokens}
                        cost={msg.cost}
                        processingTime={msg.processingTime}
                        artifacts={msg.artifacts}
                      />
                    </motion.div>
                  ))}
                </AnimatePresence>

                {/* Streaming Message */}
                {isStreaming && streamingMessage && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                  >
                    <ChatMessage
                      message={{
                        id: 'streaming',
                        role: 'assistant',
                        content: streamingMessage,
                        timestamp: new Date(),
                      }}
                      isUser={false}
                      isStreaming={true}
                    />
                  </motion.div>
                )}

                <div ref={messagesEndRef} />
              </Box>

              {/* Message Input Area */}
              <Paper 
                elevation={3}
                sx={{ 
                  p: 2, 
                  m: 2, 
                  backgroundColor: 'background.paper',
                  border: '1px solid',
                  borderColor: 'divider',
                }}
              >
                {/* Model Selector */}
                <Box sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 2 }}>
                  <ModelSelector
                    value={settings.model}
                    onChange={handleModelChange}
                    models={models}
                    disabled={isStreaming}
                  />
                  
                  <Chip
                    icon={<SpeedIcon />}
                    label={`${settings.temperature}°`}
                    size="small"
                    variant="outlined"
                  />
                  
                  <Chip
                    icon={<MemoryIcon />}
                    label={`${settings.maxTokens} tokens`}
                    size="small"
                    variant="outlined"
                  />

                  {isConnected ? (
                    <Chip
                      icon={<TrendingUpIcon />}
                      label="Connected"
                      size="small"
                      color="success"
                    />
                  ) : (
                    <Chip
                      icon={<TrendingUpIcon />}
                      label="Disconnected"
                      size="small"
                      color="error"
                    />
                  )}
                </Box>

                {/* Message Input */}
                <Box sx={{ display: 'flex', alignItems: 'flex-end', gap: 1 }}>
                  <TextField
                    ref={messageInputRef}
                    fullWidth
                    multiline
                    maxRows={6}
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Type your message... (Enter to send, Shift+Enter for new line)"
                    disabled={isStreaming}
                    variant="outlined"
                    sx={{
                      '& .MuiOutlinedInput-root': {
                        backgroundColor: 'background.default',
                      },
                    }}
                  />
                  
                  <IconButton
                    color="primary"
                    onClick={handleSendMessage}
                    disabled={!message.trim() || isStreaming}
                    size="large"
                    sx={{
                      backgroundColor: 'primary.main',
                      color: 'primary.contrastText',
                      '&:hover': {
                        backgroundColor: 'primary.dark',
                      },
                      '&:disabled': {
                        backgroundColor: 'action.disabled',
                      },
                    }}
                  >
                    <SendIcon />
                  </IconButton>
                </Box>

                {/* Progress indicator for streaming */}
                {isStreaming && (
                  <LinearProgress 
                    sx={{ mt: 1, borderRadius: 1 }}
                    color="primary"
                  />
                )}
              </Paper>
            </Box>

            {/* Settings Sidebar */}
            <Paper 
              elevation={0}
              sx={{ 
                width: 300, 
                borderLeft: 1, 
                borderColor: 'divider',
                p: 2,
                overflow: 'auto',
              }}
            >
              <Typography variant="h6" gutterBottom>
                Chat Settings
              </Typography>

              <Divider sx={{ mb: 2 }} />

              {/* Temperature Control */}
              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Temperature: {settings.temperature}
                </Typography>
                <Slider
                  value={settings.temperature}
                  onChange={(_, value) => handleSettingsChange('temperature', value)}
                  min={0}
                  max={2}
                  step={0.1}
                  marks={[
                    { value: 0, label: 'Focused' },
                    { value: 1, label: 'Balanced' },
                    { value: 2, label: 'Creative' },
                  ]}
                  disabled={isStreaming}
                />
              </Box>

              {/* Max Tokens Control */}
              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Max Tokens: {settings.maxTokens}
                </Typography>
                <Slider
                  value={settings.maxTokens}
                  onChange={(_, value) => handleSettingsChange('maxTokens', value)}
                  min={100}
                  max={8000}
                  step={100}
                  marks={[
                    { value: 500, label: '500' },
                    { value: 2000, label: '2K' },
                    { value: 4000, label: '4K' },
                    { value: 8000, label: '8K' },
                  ]}
                  disabled={isStreaming}
                />
              </Box>

              {/* System Prompt */}
              <Box sx={{ mb: 3 }}>
                <TextField
                  fullWidth
                  multiline
                  rows={3}
                  label="System Prompt"
                  value={settings.systemPrompt}
                  onChange={(e) => handleSettingsChange('systemPrompt', e.target.value)}
                  placeholder="Enter system instructions..."
                  disabled={isStreaming}
                  variant="outlined"
                  size="small"
                />
              </Box>

              {/* Stream Toggle */}
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.stream}
                    onChange={(e) => handleSettingsChange('stream', e.target.checked)}
                    disabled={isStreaming}
                  />
                }
                label="Stream responses"
              />
            </Paper>
          </Box>
        </TabPanel>

        {/* Artifacts Tab */}
        <TabPanel value={activeTab} index={1}>
          <ArtifactViewer conversationId={conversationId} />
        </TabPanel>

        {/* Models Tab */}
        <TabPanel value={activeTab} index={2}>
          <Box sx={{ p: 3 }}>
            <Typography variant="h4" gutterBottom>
              AI Models
            </Typography>
            <Typography variant="body1" color="text.secondary" paragraph>
              Manage and configure AI models for different tasks.
            </Typography>
            
            {/* Model grid will be implemented here */}
            <Grid container spacing={3}>
              {models?.map((model) => (
                <Grid item xs={12} sm={6} md={4} key={model.id}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6">{model.name}</Typography>
                      <Typography variant="body2" color="text.secondary">
                        {model.description}
                      </Typography>
                      <Chip 
                        label={model.provider} 
                        size="small" 
                        sx={{ mt: 1 }}
                      />
                    </CardContent>
                    <CardActions>
                      <Button size="small">Configure</Button>
                      <Button size="small">Test</Button>
                    </CardActions>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Box>
        </TabPanel>

        {/* Agents Tab */}
        <TabPanel value={activeTab} index={3}>
          <AgentOrchestrator />
        </TabPanel>

        {/* Files Tab */}
        <TabPanel value={activeTab} index={4}>
          <FileManager />
        </TabPanel>

        {/* Analytics Tab */}
        <TabPanel value={activeTab} index={5}>
          <AnalyticsDashboard />
        </TabPanel>
      </Box>

      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        multiple
        onChange={handleFileUpload}
        style={{ display: 'none' }}
        accept=".txt,.md,.pdf,.doc,.docx,.json,.csv,.xlsx"
      />

      {/* Speed Dial for quick actions */}
      <SpeedDial
        ariaLabel="Chat actions"
        sx={{ position: 'fixed', bottom: 24, right: 24 }}
        icon={<SpeedDialIcon />}
        direction="up"
      >
        {speedDialActions.map((action) => (
          <SpeedDialAction
            key={action.name}
            icon={action.icon}
            tooltipTitle={action.name}
            onClick={action.onClick}
          />
        ))}
      </SpeedDial>
    </Container>
  );
};

export default Chat;

