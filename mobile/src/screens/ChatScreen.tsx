/**
 * ChatScreen - Mobile AI Chat Interface
 * 
 * Comprehensive mobile chat interface optimized for touch interactions
 * with multi-model AI capabilities, voice input, and real-time features.
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
  StyleSheet,
  Dimensions,
  Alert,
  Vibration,
  ActivityIndicator,
  Modal,
  FlatList,
  Animated,
  PanResponder,
  StatusBar,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation, useRoute, useFocusEffect } from '@react-navigation/native';
import LinearGradient from 'react-native-linear-gradient';
import Icon from 'react-native-vector-icons/MaterialIcons';
import Voice from '@react-native-voice/voice';
import Sound from 'react-native-sound';
import Tts from 'react-native-tts';
import { BlurView } from '@react-native-blur/blur';
import Animated as ReanimatedAnimated, {
  useSharedValue,
  useAnimatedStyle,
  withSpring,
  withTiming,
  runOnJS,
} from 'react-native-reanimated';
import { Gesture, GestureDetector } from 'react-native-gesture-handler';
import HapticFeedback from 'react-native-haptic-feedback';
import DeviceInfo from 'react-native-device-info';
import NetInfo from '@react-native-community/netinfo';

// Hooks
import { useAuth } from '../hooks/useAuth';
import { useChat } from '../hooks/useChat';
import { useModels } from '../hooks/useModels';
import { useWebSocket } from '../hooks/useWebSocket';
import { useSettings } from '../hooks/useSettings';
import { useAnalytics } from '../hooks/useAnalytics';

// Components
import ChatMessage from '../components/ChatMessage';
import ModelSelector from '../components/ModelSelector';
import VoiceRecorder from '../components/VoiceRecorder';
import TypingIndicator from '../components/TypingIndicator';
import MessageInput from '../components/MessageInput';
import ActionSheet from '../components/ActionSheet';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorBoundary from '../components/ErrorBoundary';

// Utils
import { formatTime, formatTokens, formatCost } from '../utils/formatters';
import { hapticFeedback, playSound } from '../utils/feedback';
import { validateMessage, sanitizeInput } from '../utils/validation';
import { trackEvent } from '../utils/analytics';

// Types
import { ChatMessage as ChatMessageType, ConversationSettings, AIModel } from '../types';

// Constants
const { width: SCREEN_WIDTH, height: SCREEN_HEIGHT } = Dimensions.get('window');
const HEADER_HEIGHT = 60;
const INPUT_HEIGHT = 80;
const MESSAGE_PADDING = 16;

interface ChatScreenProps {
  conversationId?: string;
}

const ChatScreen: React.FC = () => {
  const navigation = useNavigation();
  const route = useRoute();
  const { conversationId } = route.params as ChatScreenProps;

  // Hooks
  const { user } = useAuth();
  const { socket, isConnected } = useWebSocket();
  const { settings, updateSettings } = useSettings();
  const analytics = useAnalytics();

  // Chat hooks
  const {
    messages,
    isLoading,
    isStreaming,
    streamingMessage,
    sendMessage,
    loadMoreMessages,
    hasMoreMessages,
  } = useChat(conversationId);

  const { models, selectedModel, setSelectedModel } = useModels();

  // State
  const [inputText, setInputText] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [showModelSelector, setShowModelSelector] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [isOnline, setIsOnline] = useState(true);
  const [keyboardHeight, setKeyboardHeight] = useState(0);
  const [messageToReply, setMessageToReply] = useState<ChatMessageType | null>(null);

  // Refs
  const scrollViewRef = useRef<ScrollView>(null);
  const inputRef = useRef<TextInput>(null);
  const messagesRef = useRef<ChatMessageType[]>([]);

  // Animated values
  const inputOpacity = useSharedValue(1);
  const recordingScale = useSharedValue(1);
  const headerOpacity = useSharedValue(1);

  // Effects
  useEffect(() => {
    messagesRef.current = messages;
  }, [messages]);

  useEffect(() => {
    // Network status monitoring
    const unsubscribe = NetInfo.addEventListener(state => {
      setIsOnline(state.isConnected ?? false);
    });

    return unsubscribe;
  }, []);

  useEffect(() => {
    // Voice recognition setup
    Voice.onSpeechStart = onSpeechStart;
    Voice.onSpeechRecognized = onSpeechRecognized;
    Voice.onSpeechEnd = onSpeechEnd;
    Voice.onSpeechError = onSpeechError;
    Voice.onSpeechResults = onSpeechResults;

    return () => {
      Voice.destroy().then(Voice.removeAllListeners);
    };
  }, []);

  useEffect(() => {
    // Keyboard handling
    const keyboardDidShowListener = Keyboard.addListener('keyboardDidShow', (e) => {
      setKeyboardHeight(e.endCoordinates.height);
    });
    
    const keyboardDidHideListener = Keyboard.addListener('keyboardDidHide', () => {
      setKeyboardHeight(0);
    });

    return () => {
      keyboardDidShowListener?.remove();
      keyboardDidHideListener?.remove();
    };
  }, []);

  useEffect(() => {
    // Auto-scroll to bottom when new messages arrive
    if (messages.length > 0) {
      setTimeout(() => {
        scrollViewRef.current?.scrollToEnd({ animated: true });
      }, 100);
    }
  }, [messages, streamingMessage]);

  useFocusEffect(
    useCallback(() => {
      // Track screen view
      analytics.track('chat_screen_viewed', {
        conversationId,
        userId: user?.uid,
        modelSelected: selectedModel?.id,
      });

      return () => {
        // Cleanup when screen loses focus
        if (isRecording) {
          stopRecording();
        }
      };
    }, [conversationId, user?.uid, selectedModel?.id, isRecording])
  );

  // Voice recognition handlers
  const onSpeechStart = (e: any) => {
    console.log('Speech started', e);
  };

  const onSpeechRecognized = (e: any) => {
    console.log('Speech recognized', e);
  };

  const onSpeechEnd = (e: any) => {
    console.log('Speech ended', e);
    setIsRecording(false);
    recordingScale.value = withSpring(1);
  };

  const onSpeechError = (e: any) => {
    console.log('Speech error', e);
    setIsRecording(false);
    recordingScale.value = withSpring(1);
    Alert.alert('Voice Recognition Error', 'Please try again.');
  };

  const onSpeechResults = (e: any) => {
    const result = e.value?.[0];
    if (result) {
      setInputText(result);
      hapticFeedback('success');
    }
  };

  // Handlers
  const handleSendMessage = useCallback(async () => {
    if (!inputText.trim() || isStreaming || !isOnline) return;

    const messageContent = sanitizeInput(inputText.trim());
    
    if (!validateMessage(messageContent)) {
      Alert.alert('Invalid Message', 'Please enter a valid message.');
      return;
    }

    try {
      hapticFeedback('light');
      
      await sendMessage({
        content: messageContent,
        model: selectedModel?.id || 'gpt-4-turbo',
        replyTo: messageToReply?.id,
        settings: {
          temperature: settings.temperature,
          maxTokens: settings.maxTokens,
          stream: settings.streamResponses,
        },
      });

      setInputText('');
      setMessageToReply(null);
      
      // Track analytics
      analytics.track('message_sent', {
        conversationId,
        model: selectedModel?.id,
        messageLength: messageContent.length,
        hasReply: !!messageToReply,
      });

      // Play send sound
      playSound('message_sent');

    } catch (error) {
      console.error('Send message error:', error);
      hapticFeedback('error');
      Alert.alert('Send Failed', 'Failed to send message. Please try again.');
    }
  }, [inputText, isStreaming, isOnline, selectedModel, messageToReply, settings, sendMessage, conversationId, analytics]);

  const startRecording = useCallback(async () => {
    try {
      await Voice.start('en-US');
      setIsRecording(true);
      recordingScale.value = withSpring(1.2);
      hapticFeedback('medium');
      
      // Visual feedback
      Vibration.vibrate([0, 100, 50, 100]);
      
      analytics.track('voice_recording_started', {
        conversationId,
        userId: user?.uid,
      });
    } catch (error) {
      console.error('Voice recording error:', error);
      Alert.alert('Recording Error', 'Unable to start voice recording.');
    }
  }, [conversationId, user?.uid, analytics]);

  const stopRecording = useCallback(async () => {
    try {
      await Voice.stop();
      setIsRecording(false);
      recordingScale.value = withSpring(1);
      hapticFeedback('light');
    } catch (error) {
      console.error('Stop recording error:', error);
    }
  }, []);

  const handleLongPressMessage = useCallback((message: ChatMessageType) => {
    hapticFeedback('medium');
    
    const options = [
      { text: 'Reply', onPress: () => setMessageToReply(message) },
      { text: 'Copy', onPress: () => Clipboard.setString(message.content) },
      { text: 'Share', onPress: () => shareMessage(message) },
      { text: 'Speak', onPress: () => speakMessage(message) },
      { text: 'Cancel', style: 'cancel' },
    ];

    if (message.role === 'user') {
      options.splice(3, 0, { text: 'Edit', onPress: () => editMessage(message) });
      options.splice(4, 0, { text: 'Delete', onPress: () => deleteMessage(message), style: 'destructive' });
    }

    ActionSheet.showActionSheetWithOptions(
      {
        options: options.map(opt => opt.text),
        cancelButtonIndex: options.length - 1,
        destructiveButtonIndex: options.findIndex(opt => opt.style === 'destructive'),
      },
      (buttonIndex) => {
        if (buttonIndex !== undefined && buttonIndex < options.length - 1) {
          options[buttonIndex].onPress();
        }
      }
    );
  }, []);

  const speakMessage = useCallback((message: ChatMessageType) => {
    Tts.speak(message.content, {
      androidParams: {
        KEY_PARAM_PAN: -1,
        KEY_PARAM_VOLUME: 0.8,
        KEY_PARAM_STREAM: 'STREAM_MUSIC',
      },
    });
    
    analytics.track('message_spoken', {
      conversationId,
      messageId: message.id,
      messageLength: message.content.length,
    });
  }, [conversationId, analytics]);

  const shareMessage = useCallback(async (message: ChatMessageType) => {
    try {
      await Share.share({
        message: message.content,
        title: 'ApexAgent Conversation',
      });
      
      analytics.track('message_shared', {
        conversationId,
        messageId: message.id,
      });
    } catch (error) {
      console.error('Share error:', error);
    }
  }, [conversationId, analytics]);

  const editMessage = useCallback((message: ChatMessageType) => {
    setInputText(message.content);
    setMessageToReply(null);
    inputRef.current?.focus();
  }, []);

  const deleteMessage = useCallback((message: ChatMessageType) => {
    Alert.alert(
      'Delete Message',
      'Are you sure you want to delete this message?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: () => {
            // Implement delete message logic
            analytics.track('message_deleted', {
              conversationId,
              messageId: message.id,
            });
          },
        },
      ]
    );
  }, [conversationId, analytics]);

  const handleModelSelect = useCallback((model: AIModel) => {
    setSelectedModel(model);
    setShowModelSelector(false);
    hapticFeedback('light');
    
    analytics.track('model_selected', {
      conversationId,
      modelId: model.id,
      provider: model.provider,
    });
  }, [conversationId, analytics, setSelectedModel]);

  const handleRefresh = useCallback(() => {
    if (hasMoreMessages && !isLoading) {
      loadMoreMessages();
      hapticFeedback('light');
    }
  }, [hasMoreMessages, isLoading, loadMoreMessages]);

  // Animated styles
  const recordingButtonStyle = useAnimatedStyle(() => {
    return {
      transform: [{ scale: recordingScale.value }],
    };
  });

  const inputStyle = useAnimatedStyle(() => {
    return {
      opacity: inputOpacity.value,
    };
  });

  // Render methods
  const renderMessage = useCallback(({ item, index }: { item: ChatMessageType; index: number }) => {
    return (
      <ChatMessage
        message={item}
        isUser={item.role === 'user'}
        onLongPress={() => handleLongPressMessage(item)}
        showAvatar={index === 0 || messages[index - 1]?.role !== item.role}
        showTimestamp={index === messages.length - 1 || 
          (messages[index + 1] && 
           new Date(messages[index + 1].timestamp).getTime() - new Date(item.timestamp).getTime() > 300000)}
      />
    );
  }, [messages, handleLongPressMessage]);

  const renderHeader = () => (
    <ReanimatedAnimated.View style={[styles.header, { opacity: headerOpacity.value }]}>
      <LinearGradient
        colors={['#6366f1', '#8b5cf6']}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 0 }}
        style={styles.headerGradient}
      >
        <SafeAreaView style={styles.headerContent}>
          <TouchableOpacity
            style={styles.headerButton}
            onPress={() => navigation.goBack()}
          >
            <Icon name="arrow-back" size={24} color="#ffffff" />
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.modelSelector}
            onPress={() => setShowModelSelector(true)}
          >
            <Text style={styles.modelName} numberOfLines={1}>
              {selectedModel?.name || 'Select Model'}
            </Text>
            <Icon name="expand-more" size={20} color="#ffffff" />
          </TouchableOpacity>

          <View style={styles.headerActions}>
            <TouchableOpacity
              style={styles.headerButton}
              onPress={() => setShowSettings(true)}
            >
              <Icon name="settings" size={20} color="#ffffff" />
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.headerButton}
              onPress={handleRefresh}
              disabled={isLoading}
            >
              <Icon 
                name="refresh" 
                size={20} 
                color={isLoading ? "#999999" : "#ffffff"} 
              />
            </TouchableOpacity>
          </View>
        </SafeAreaView>
      </LinearGradient>

      {/* Connection status */}
      {!isOnline && (
        <View style={styles.offlineBar}>
          <Icon name="wifi-off" size={16} color="#ffffff" />
          <Text style={styles.offlineText}>Offline</Text>
        </View>
      )}

      {/* Reply indicator */}
      {messageToReply && (
        <View style={styles.replyIndicator}>
          <Text style={styles.replyText} numberOfLines={1}>
            Replying to: {messageToReply.content}
          </Text>
          <TouchableOpacity
            onPress={() => setMessageToReply(null)}
            style={styles.replyCancel}
          >
            <Icon name="close" size={16} color="#666666" />
          </TouchableOpacity>
        </View>
      )}
    </ReanimatedAnimated.View>
  );

  const renderInput = () => (
    <ReanimatedAnimated.View style={[styles.inputContainer, inputStyle]}>
      <BlurView
        style={styles.inputBlur}
        blurType="dark"
        blurAmount={10}
        reducedTransparencyFallbackColor="#1a1a2e"
      >
        <View style={styles.inputContent}>
          <TextInput
            ref={inputRef}
            style={styles.textInput}
            value={inputText}
            onChangeText={setInputText}
            placeholder="Type your message..."
            placeholderTextColor="#666666"
            multiline
            maxLength={10000}
            editable={!isStreaming && isOnline}
            returnKeyType="send"
            onSubmitEditing={handleSendMessage}
            blurOnSubmit={false}
          />

          <View style={styles.inputActions}>
            <TouchableOpacity
              style={[styles.actionButton, isRecording && styles.recordingButton]}
              onPress={isRecording ? stopRecording : startRecording}
              disabled={isStreaming}
            >
              <ReanimatedAnimated.View style={recordingButtonStyle}>
                <Icon 
                  name={isRecording ? "stop" : "mic"} 
                  size={20} 
                  color={isRecording ? "#ef4444" : "#6366f1"} 
                />
              </ReanimatedAnimated.View>
            </TouchableOpacity>

            <TouchableOpacity
              style={[
                styles.sendButton,
                (!inputText.trim() || isStreaming || !isOnline) && styles.sendButtonDisabled
              ]}
              onPress={handleSendMessage}
              disabled={!inputText.trim() || isStreaming || !isOnline}
            >
              {isStreaming ? (
                <ActivityIndicator size="small" color="#ffffff" />
              ) : (
                <Icon name="send" size={20} color="#ffffff" />
              )}
            </TouchableOpacity>
          </View>
        </View>
      </BlurView>
    </ReanimatedAnimated.View>
  );

  return (
    <ErrorBoundary>
      <View style={styles.container}>
        <StatusBar barStyle="light-content" backgroundColor="#6366f1" />
        
        {renderHeader()}

        <KeyboardAvoidingView
          style={styles.content}
          behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
          keyboardVerticalOffset={Platform.OS === 'ios' ? 0 : 20}
        >
          <FlatList
            ref={scrollViewRef}
            data={messages}
            renderItem={renderMessage}
            keyExtractor={(item) => item.id}
            style={styles.messagesList}
            contentContainerStyle={styles.messagesContent}
            showsVerticalScrollIndicator={false}
            onRefresh={handleRefresh}
            refreshing={isLoading}
            onEndReached={hasMoreMessages ? loadMoreMessages : undefined}
            onEndReachedThreshold={0.1}
            ListFooterComponent={() => (
              <>
                {isStreaming && streamingMessage && (
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
                )}
                {isStreaming && <TypingIndicator />}
              </>
            )}
          />

          {renderInput()}
        </KeyboardAvoidingView>

        {/* Model Selector Modal */}
        <Modal
          visible={showModelSelector}
          animationType="slide"
          presentationStyle="pageSheet"
          onRequestClose={() => setShowModelSelector(false)}
        >
          <ModelSelector
            models={models}
            selectedModel={selectedModel}
            onSelect={handleModelSelect}
            onClose={() => setShowModelSelector(false)}
          />
        </Modal>

        {/* Settings Modal */}
        <Modal
          visible={showSettings}
          animationType="slide"
          presentationStyle="pageSheet"
          onRequestClose={() => setShowSettings(false)}
        >
          <ChatSettings
            settings={settings}
            onUpdate={updateSettings}
            onClose={() => setShowSettings(false)}
          />
        </Modal>
      </View>
    </ErrorBoundary>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0f0f23',
  },
  header: {
    zIndex: 1000,
  },
  headerGradient: {
    paddingTop: Platform.OS === 'ios' ? 0 : StatusBar.currentHeight,
  },
  headerContent: {
    flexDirection: 'row',
    alignItems: 'center',
    height: HEADER_HEIGHT,
    paddingHorizontal: 16,
  },
  headerButton: {
    padding: 8,
    borderRadius: 20,
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
  },
  modelSelector: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginHorizontal: 16,
    padding: 8,
    borderRadius: 20,
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
  },
  modelName: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
    marginRight: 4,
  },
  headerActions: {
    flexDirection: 'row',
    gap: 8,
  },
  offlineBar: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#ef4444',
    paddingVertical: 4,
    gap: 4,
  },
  offlineText: {
    color: '#ffffff',
    fontSize: 12,
    fontWeight: '500',
  },
  replyIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    marginHorizontal: 16,
    marginTop: 8,
    padding: 12,
    borderRadius: 8,
  },
  replyText: {
    flex: 1,
    color: '#ffffff',
    fontSize: 14,
  },
  replyCancel: {
    padding: 4,
  },
  content: {
    flex: 1,
  },
  messagesList: {
    flex: 1,
  },
  messagesContent: {
    paddingVertical: 16,
  },
  inputContainer: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
  },
  inputBlur: {
    paddingHorizontal: 16,
    paddingVertical: 12,
    paddingBottom: Platform.OS === 'ios' ? 34 : 12,
  },
  inputContent: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    borderRadius: 24,
    paddingHorizontal: 16,
    paddingVertical: 8,
    minHeight: 48,
  },
  textInput: {
    flex: 1,
    color: '#ffffff',
    fontSize: 16,
    maxHeight: 120,
    paddingVertical: 8,
  },
  inputActions: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginLeft: 8,
  },
  actionButton: {
    padding: 8,
    borderRadius: 20,
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
  },
  recordingButton: {
    backgroundColor: 'rgba(239, 68, 68, 0.2)',
  },
  sendButton: {
    padding: 12,
    borderRadius: 20,
    backgroundColor: '#6366f1',
  },
  sendButtonDisabled: {
    backgroundColor: '#374151',
  },
});

export default ChatScreen;

