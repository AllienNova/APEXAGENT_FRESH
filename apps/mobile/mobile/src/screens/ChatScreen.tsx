import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  FlatList,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  Alert,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useSelector, useDispatch } from 'react-redux';
import { apiService } from '../services/api.service';
import { authService } from '../services/auth.service';
import { RootState } from '../store';

interface Message {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: Date;
  model?: string;
  tokens?: number;
}

interface ChatScreenProps {
  navigation: any;
}

export const ChatScreen: React.FC<ChatScreenProps> = ({ navigation }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedModel, setSelectedModel] = useState('gpt-4o');
  const flatListRef = useRef<FlatList>(null);
  
  const { user, isAuthenticated } = useSelector((state: RootState) => state.auth);
  const dispatch = useDispatch();

  useEffect(() => {
    if (!isAuthenticated) {
      navigation.navigate('Auth');
      return;
    }
    loadChatHistory();
  }, [isAuthenticated]);

  const loadChatHistory = async () => {
    try {
      const history = await apiService.getChatHistory();
      setMessages(history.map((msg: any) => ({
        ...msg,
        timestamp: new Date(msg.timestamp),
      })));
    } catch (error) {
      console.error('Failed to load chat history:', error);
    }
  };

  const sendMessage = async () => {
    if (!inputText.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputText.trim(),
      isUser: true,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsLoading(true);

    try {
      const response = await apiService.sendChatMessage({
        message: userMessage.text,
        model: selectedModel,
        conversation_id: user?.currentConversationId,
      });

      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: response.response,
        isUser: false,
        timestamp: new Date(),
        model: response.model,
        tokens: response.tokens_used,
      };

      setMessages(prev => [...prev, aiMessage]);
      
      // Auto-scroll to bottom
      setTimeout(() => {
        flatListRef.current?.scrollToEnd({ animated: true });
      }, 100);

    } catch (error) {
      console.error('Failed to send message:', error);
      Alert.alert('Error', 'Failed to send message. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const renderMessage = ({ item }: { item: Message }) => (
    <View style={[
      styles.messageContainer,
      item.isUser ? styles.userMessage : styles.aiMessage
    ]}>
      <Text style={[
        styles.messageText,
        item.isUser ? styles.userMessageText : styles.aiMessageText
      ]}>
        {item.text}
      </Text>
      {!item.isUser && item.model && (
        <Text style={styles.messageInfo}>
          {item.model} • {item.tokens} tokens • {item.timestamp.toLocaleTimeString()}
        </Text>
      )}
    </View>
  );

  const availableModels = [
    { id: 'gpt-4o', name: 'GPT-4o', provider: 'OpenAI' },
    { id: 'claude-3-5-sonnet', name: 'Claude 3.5 Sonnet', provider: 'Anthropic' },
    { id: 'gemini-2-0-flash', name: 'Gemini 2.0 Flash', provider: 'Google' },
    { id: 'llama-3-3-70b', name: 'Llama 3.3 70B', provider: 'Together AI' },
  ];

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>AI Chat</Text>
        <TouchableOpacity 
          style={styles.modelSelector}
          onPress={() => {
            // Show model selection modal
            Alert.alert(
              'Select AI Model',
              'Choose your preferred AI model',
              availableModels.map(model => ({
                text: `${model.name} (${model.provider})`,
                onPress: () => setSelectedModel(model.id),
              }))
            );
          }}
        >
          <Text style={styles.modelSelectorText}>
            {availableModels.find(m => m.id === selectedModel)?.name || 'Select Model'}
          </Text>
        </TouchableOpacity>
      </View>

      <FlatList
        ref={flatListRef}
        data={messages}
        renderItem={renderMessage}
        keyExtractor={item => item.id}
        style={styles.messagesList}
        contentContainerStyle={styles.messagesContainer}
        showsVerticalScrollIndicator={false}
      />

      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.inputContainer}
      >
        <View style={styles.inputRow}>
          <TextInput
            style={styles.textInput}
            value={inputText}
            onChangeText={setInputText}
            placeholder="Ask me anything..."
            placeholderTextColor="#666"
            multiline
            maxLength={4000}
            editable={!isLoading}
          />
          <TouchableOpacity
            style={[
              styles.sendButton,
              (!inputText.trim() || isLoading) && styles.sendButtonDisabled
            ]}
            onPress={sendMessage}
            disabled={!inputText.trim() || isLoading}
          >
            <Text style={styles.sendButtonText}>
              {isLoading ? '...' : 'Send'}
            </Text>
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  modelSelector: {
    backgroundColor: '#007AFF',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
  },
  modelSelectorText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '600',
  },
  messagesList: {
    flex: 1,
  },
  messagesContainer: {
    paddingVertical: 16,
  },
  messageContainer: {
    marginHorizontal: 16,
    marginVertical: 4,
    padding: 12,
    borderRadius: 16,
    maxWidth: '80%',
  },
  userMessage: {
    alignSelf: 'flex-end',
    backgroundColor: '#007AFF',
  },
  aiMessage: {
    alignSelf: 'flex-start',
    backgroundColor: '#fff',
    borderWidth: 1,
    borderColor: '#e0e0e0',
  },
  messageText: {
    fontSize: 16,
    lineHeight: 22,
  },
  userMessageText: {
    color: '#fff',
  },
  aiMessageText: {
    color: '#333',
  },
  messageInfo: {
    fontSize: 11,
    color: '#666',
    marginTop: 4,
  },
  inputContainer: {
    backgroundColor: '#fff',
    borderTopWidth: 1,
    borderTopColor: '#e0e0e0',
  },
  inputRow: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    paddingHorizontal: 16,
    paddingVertical: 12,
  },
  textInput: {
    flex: 1,
    borderWidth: 1,
    borderColor: '#e0e0e0',
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 12,
    marginRight: 12,
    maxHeight: 100,
    fontSize: 16,
    color: '#333',
    backgroundColor: '#f9f9f9',
  },
  sendButton: {
    backgroundColor: '#007AFF',
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
  sendButtonDisabled: {
    backgroundColor: '#ccc',
  },
  sendButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
});

