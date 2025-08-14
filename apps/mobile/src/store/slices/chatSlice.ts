import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { ChatState, Message, Conversation, AIModel } from '../../types';
import { apiService } from '../../services/api.service';

const initialState: ChatState = {
  conversations: [],
  activeConversationId: null,
  isLoading: false,
  isTyping: false,
  error: null,
  models: [],
  selectedModel: 'gpt-4o',
};

// Async thunks
export const loadConversations = createAsyncThunk(
  'chat/loadConversations',
  async (_, { rejectWithValue }) => {
    try {
      const conversations = await apiService.getConversations();
      return conversations;
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : 'Failed to load conversations');
    }
  }
);

export const loadChatHistory = createAsyncThunk(
  'chat/loadChatHistory',
  async (conversationId: string, { rejectWithValue }) => {
    try {
      const messages = await apiService.getChatHistory(conversationId);
      return { conversationId, messages };
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : 'Failed to load chat history');
    }
  }
);

export const sendMessage = createAsyncThunk(
  'chat/sendMessage',
  async (
    { 
      message, 
      conversationId, 
      model, 
      attachments 
    }: { 
      message: string; 
      conversationId?: string; 
      model: string;
      attachments?: any[];
    }, 
    { rejectWithValue, getState }
  ) => {
    try {
      const userMessage: Message = {
        id: Date.now().toString(),
        text: message,
        isUser: true,
        timestamp: new Date(),
        status: 'sending',
        attachments: attachments?.map(att => ({
          id: att.id,
          type: att.type,
          url: att.url,
          name: att.name,
          size: att.size,
          mimeType: att.mimeType,
        })),
      };

      // Send to API
      const response = await apiService.sendChatMessage({
        message,
        model,
        conversation_id: conversationId,
        attachments,
      });

      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: response.response,
        isUser: false,
        timestamp: new Date(),
        model: response.model,
        tokens: response.tokens_used,
        status: 'delivered',
        metadata: {
          processingTime: response.processing_time || 0,
          confidence: response.confidence || 0.95,
          sources: response.sources,
          reasoning: response.reasoning,
        },
      };

      return {
        userMessage: { ...userMessage, status: 'delivered' as const },
        aiMessage,
        conversationId: response.conversation_id,
        cost: response.cost,
      };
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : 'Failed to send message');
    }
  }
);

export const loadAvailableModels = createAsyncThunk(
  'chat/loadAvailableModels',
  async (_, { rejectWithValue }) => {
    try {
      const models = await apiService.getAvailableModels();
      return models;
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : 'Failed to load models');
    }
  }
);

export const createNewConversation = createAsyncThunk(
  'chat/createNewConversation',
  async ({ title, model }: { title?: string; model: string }, { rejectWithValue }) => {
    try {
      const conversation: Conversation = {
        id: Date.now().toString(),
        title: title || 'New Conversation',
        messages: [],
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        model,
        totalTokens: 0,
        totalCost: 0,
        isArchived: false,
        tags: [],
      };

      return conversation;
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : 'Failed to create conversation');
    }
  }
);

export const deleteConversation = createAsyncThunk(
  'chat/deleteConversation',
  async (conversationId: string, { rejectWithValue }) => {
    try {
      // Call API to delete conversation
      await apiService.deleteConversation(conversationId);
      return conversationId;
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : 'Failed to delete conversation');
    }
  }
);

export const archiveConversation = createAsyncThunk(
  'chat/archiveConversation',
  async (conversationId: string, { rejectWithValue }) => {
    try {
      await apiService.archiveConversation(conversationId);
      return conversationId;
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : 'Failed to archive conversation');
    }
  }
);

const chatSlice = createSlice({
  name: 'chat',
  initialState,
  reducers: {
    setActiveConversation: (state, action: PayloadAction<string | null>) => {
      state.activeConversationId = action.payload;
    },
    setSelectedModel: (state, action: PayloadAction<string>) => {
      state.selectedModel = action.payload;
    },
    setTyping: (state, action: PayloadAction<boolean>) => {
      state.isTyping = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
    updateMessageStatus: (state, action: PayloadAction<{ messageId: string; status: Message['status'] }>) => {
      const { messageId, status } = action.payload;
      state.conversations.forEach(conversation => {
        const message = conversation.messages.find(msg => msg.id === messageId);
        if (message) {
          message.status = status;
        }
      });
    },
    addOptimisticMessage: (state, action: PayloadAction<{ conversationId: string; message: Message }>) => {
      const { conversationId, message } = action.payload;
      const conversation = state.conversations.find(conv => conv.id === conversationId);
      if (conversation) {
        conversation.messages.push(message);
        conversation.updatedAt = new Date().toISOString();
      }
    },
    updateConversationTitle: (state, action: PayloadAction<{ conversationId: string; title: string }>) => {
      const { conversationId, title } = action.payload;
      const conversation = state.conversations.find(conv => conv.id === conversationId);
      if (conversation) {
        conversation.title = title;
        conversation.updatedAt = new Date().toISOString();
      }
    },
  },
  extraReducers: (builder) => {
    // Load Conversations
    builder
      .addCase(loadConversations.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(loadConversations.fulfilled, (state, action) => {
        state.isLoading = false;
        state.conversations = action.payload;
      })
      .addCase(loadConversations.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });

    // Load Chat History
    builder
      .addCase(loadChatHistory.fulfilled, (state, action) => {
        const { conversationId, messages } = action.payload;
        const conversation = state.conversations.find(conv => conv.id === conversationId);
        if (conversation) {
          conversation.messages = messages;
        }
      });

    // Send Message
    builder
      .addCase(sendMessage.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(sendMessage.fulfilled, (state, action) => {
        state.isLoading = false;
        const { userMessage, aiMessage, conversationId, cost } = action.payload;
        
        let conversation = state.conversations.find(conv => conv.id === conversationId);
        
        if (!conversation) {
          // Create new conversation
          conversation = {
            id: conversationId,
            title: userMessage.text.slice(0, 50) + (userMessage.text.length > 50 ? '...' : ''),
            messages: [],
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
            model: state.selectedModel,
            totalTokens: 0,
            totalCost: 0,
            isArchived: false,
            tags: [],
          };
          state.conversations.unshift(conversation);
          state.activeConversationId = conversationId;
        }

        // Update existing user message or add new one
        const existingUserMessage = conversation.messages.find(msg => msg.id === userMessage.id);
        if (existingUserMessage) {
          Object.assign(existingUserMessage, userMessage);
        } else {
          conversation.messages.push(userMessage);
        }

        // Add AI message
        conversation.messages.push(aiMessage);
        conversation.updatedAt = new Date().toISOString();
        conversation.totalTokens += aiMessage.tokens || 0;
        conversation.totalCost += cost || 0;
      })
      .addCase(sendMessage.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });

    // Load Available Models
    builder
      .addCase(loadAvailableModels.fulfilled, (state, action) => {
        state.models = action.payload;
      });

    // Create New Conversation
    builder
      .addCase(createNewConversation.fulfilled, (state, action) => {
        state.conversations.unshift(action.payload);
        state.activeConversationId = action.payload.id;
      });

    // Delete Conversation
    builder
      .addCase(deleteConversation.fulfilled, (state, action) => {
        state.conversations = state.conversations.filter(conv => conv.id !== action.payload);
        if (state.activeConversationId === action.payload) {
          state.activeConversationId = state.conversations[0]?.id || null;
        }
      });

    // Archive Conversation
    builder
      .addCase(archiveConversation.fulfilled, (state, action) => {
        const conversation = state.conversations.find(conv => conv.id === action.payload);
        if (conversation) {
          conversation.isArchived = true;
        }
      });
  },
});

export const {
  setActiveConversation,
  setSelectedModel,
  setTyping,
  clearError,
  updateMessageStatus,
  addOptimisticMessage,
  updateConversationTitle,
} = chatSlice.actions;

export default chatSlice.reducer;

