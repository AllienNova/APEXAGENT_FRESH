import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  KeyboardAvoidingView,
  Platform,
  TouchableOpacity,
  Alert,
  Animated,
  Dimensions,
  Image,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import { useDispatch, useSelector } from 'react-redux';
import DocumentPicker from 'react-native-document-picker';
import { Audio } from 'expo-av';

import Input from '../../components/ui/Input';
import Button from '../../components/ui/Button';
import Card from '../../components/ui/Card';
import { Colors, Typography, Spacing, BorderRadius, Shadows } from '../../constants/theme';
import { RootState } from '../../store';
import { 
  sendMessage, 
  loadMessages, 
  setSelectedModel, 
  startVoiceRecording, 
  stopVoiceRecording,
  uploadFile,
  clearChat
} from '../../store/slices/chatSlice';

const { width } = Dimensions.get('window');

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'ai';
  timestamp: Date;
  model?: string;
  attachments?: Array<{
    id: string;
    name: string;
    type: string;
    size: number;
    url: string;
  }>;
  status: 'sending' | 'sent' | 'error';
}

interface ModelOption {
  id: string;
  name: string;
  description: string;
  icon: string;
  color: string;
}

const AVAILABLE_MODELS: ModelOption[] = [
  {
    id: 'gpt-4-turbo',
    name: 'GPT-4 Turbo',
    description: 'Most capable model for complex tasks',
    icon: 'flash',
    color: Colors.primary[500],
  },
  {
    id: 'gpt-4',
    name: 'GPT-4',
    description: 'Reliable and accurate responses',
    icon: 'checkmark-circle',
    color: Colors.primary[600],
  },
  {
    id: 'claude-3',
    name: 'Claude 3',
    description: 'Excellent for analysis and reasoning',
    icon: 'analytics',
    color: Colors.secondary[500],
  },
  {
    id: 'gemini-pro',
    name: 'Gemini Pro',
    description: 'Great for creative tasks',
    icon: 'diamond',
    color: Colors.warning,
  },
];

const MessageBubble: React.FC<{ message: Message; isUser: boolean }> = ({ message, isUser }) => {
  const fadeAnim = useRef(new Animated.Value(0)).current;
  const slideAnim = useRef(new Animated.Value(20)).current;

  useEffect(() => {
    Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 300,
        useNativeDriver: true,
      }),
      Animated.timing(slideAnim, {
        toValue: 0,
        duration: 300,
        useNativeDriver: true,
      }),
    ]).start();
  }, []);

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <Animated.View
      style={[
        styles.messageContainer,
        isUser ? styles.userMessageContainer : styles.aiMessageContainer,
        {
          opacity: fadeAnim,
          transform: [{ translateY: slideAnim }],
        },
      ]}
    >
      <View style={[styles.messageBubble, isUser ? styles.userBubble : styles.aiBubble]}>
        {!isUser && (
          <View style={styles.aiHeader}>
            <View style={styles.aiIcon}>
              <Ionicons name="sparkles" size={16} color={Colors.primary[500]} />
            </View>
            <Text style={styles.aiModel}>{message.model || 'AI Assistant'}</Text>
          </View>
        )}
        
        <Text style={[styles.messageText, isUser ? styles.userText : styles.aiText]}>
          {message.text}
        </Text>
        
        {message.attachments && message.attachments.length > 0 && (
          <View style={styles.attachmentsContainer}>
            {message.attachments.map((attachment) => (
              <View key={attachment.id} style={styles.attachmentItem}>
                <Ionicons name="document" size={16} color={Colors.gray[500]} />
                <Text style={styles.attachmentName}>{attachment.name}</Text>
                <Text style={styles.attachmentSize}>
                  {(attachment.size / 1024 / 1024).toFixed(1)}MB
                </Text>
              </View>
            ))}
          </View>
        )}
        
        <View style={styles.messageFooter}>
          <Text style={[styles.timestamp, isUser ? styles.userTimestamp : styles.aiTimestamp]}>
            {formatTime(message.timestamp)}
          </Text>
          {isUser && (
            <View style={styles.statusContainer}>
              {message.status === 'sending' && (
                <Ionicons name="time" size={12} color={Colors.gray[400]} />
              )}
              {message.status === 'sent' && (
                <Ionicons name="checkmark" size={12} color={Colors.success} />
              )}
              {message.status === 'error' && (
                <Ionicons name="alert-circle" size={12} color={Colors.error} />
              )}
            </View>
          )}
        </View>
      </View>
    </Animated.View>
  );
};

const ModelSelector: React.FC<{
  visible: boolean;
  selectedModel: string;
  onSelect: (model: string) => void;
  onClose: () => void;
}> = ({ visible, selectedModel, onSelect, onClose }) => {
  const slideAnim = useRef(new Animated.Value(300)).current;

  useEffect(() => {
    if (visible) {
      Animated.spring(slideAnim, {
        toValue: 0,
        tension: 50,
        friction: 8,
        useNativeDriver: true,
      }).start();
    } else {
      Animated.timing(slideAnim, {
        toValue: 300,
        duration: 200,
        useNativeDriver: true,
      }).start();
    }
  }, [visible]);

  if (!visible) return null;

  return (
    <View style={styles.modalOverlay}>
      <TouchableOpacity style={styles.modalBackdrop} onPress={onClose} />
      <Animated.View
        style={[
          styles.modelSelectorContainer,
          {
            transform: [{ translateY: slideAnim }],
          },
        ]}
      >
        <View style={styles.modelSelectorHeader}>
          <Text style={styles.modelSelectorTitle}>Select AI Model</Text>
          <TouchableOpacity onPress={onClose}>
            <Ionicons name="close" size={24} color={Colors.gray[500]} />
          </TouchableOpacity>
        </View>
        
        <FlatList
          data={AVAILABLE_MODELS}
          keyExtractor={(item) => item.id}
          renderItem={({ item }) => (
            <TouchableOpacity
              style={[
                styles.modelOption,
                selectedModel === item.id && styles.selectedModelOption,
              ]}
              onPress={() => {
                onSelect(item.id);
                onClose();
              }}
            >
              <View style={[styles.modelIcon, { backgroundColor: item.color }]}>
                <Ionicons name={item.icon as any} size={20} color="#ffffff" />
              </View>
              <View style={styles.modelInfo}>
                <Text style={styles.modelName}>{item.name}</Text>
                <Text style={styles.modelDescription}>{item.description}</Text>
              </View>
              {selectedModel === item.id && (
                <Ionicons name="checkmark-circle" size={24} color={Colors.primary[500]} />
              )}
            </TouchableOpacity>
          )}
        />
      </Animated.View>
    </View>
  );
};

const ChatScreen: React.FC = () => {
  const dispatch = useDispatch();
  const { 
    messages, 
    selectedModel, 
    isLoading, 
    isRecording, 
    uploadProgress 
  } = useSelector((state: RootState) => state.chat);
  
  const [inputText, setInputText] = useState('');
  const [showModelSelector, setShowModelSelector] = useState(false);
  const [attachments, setAttachments] = useState<any[]>([]);
  
  const flatListRef = useRef<FlatList>(null);
  const recordingRef = useRef<Audio.Recording | null>(null);

  useEffect(() => {
    dispatch(loadMessages());
  }, [dispatch]);

  useEffect(() => {
    // Scroll to bottom when new messages arrive
    if (messages.length > 0) {
      setTimeout(() => {
        flatListRef.current?.scrollToEnd({ animated: true });
      }, 100);
    }
  }, [messages]);

  const handleSendMessage = useCallback(async () => {
    if (!inputText.trim() && attachments.length === 0) return;

    const messageData = {
      text: inputText.trim(),
      attachments: attachments,
      model: selectedModel,
    };

    dispatch(sendMessage(messageData));
    setInputText('');
    setAttachments([]);
  }, [inputText, attachments, selectedModel, dispatch]);

  const handleFileAttachment = useCallback(async () => {
    try {
      const result = await DocumentPicker.pick({
        type: [DocumentPicker.types.allFiles],
        allowMultiSelection: true,
      });

      const newAttachments = result.map((file) => ({
        id: Date.now().toString() + Math.random(),
        name: file.name,
        type: file.type,
        size: file.size,
        uri: file.uri,
      }));

      setAttachments([...attachments, ...newAttachments]);
    } catch (error) {
      if (!DocumentPicker.isCancel(error)) {
        Alert.alert('Error', 'Failed to select file');
      }
    }
  }, [attachments]);

  const handleVoiceRecording = useCallback(async () => {
    try {
      if (isRecording) {
        dispatch(stopVoiceRecording());
      } else {
        dispatch(startVoiceRecording());
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to access microphone');
    }
  }, [isRecording, dispatch]);

  const removeAttachment = useCallback((id: string) => {
    setAttachments(attachments.filter(att => att.id !== id));
  }, [attachments]);

  const handleClearChat = useCallback(() => {
    Alert.alert(
      'Clear Chat',
      'Are you sure you want to clear all messages?',
      [
        { text: 'Cancel', style: 'cancel' },
        { 
          text: 'Clear', 
          style: 'destructive',
          onPress: () => dispatch(clearChat())
        },
      ]
    );
  }, [dispatch]);

  const selectedModelData = AVAILABLE_MODELS.find(m => m.id === selectedModel) || AVAILABLE_MODELS[0];

  return (
    <SafeAreaView style={styles.container}>
      <LinearGradient
        colors={[Colors.primary[50], '#ffffff']}
        style={StyleSheet.absoluteFill}
      />

      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity
          style={styles.modelButton}
          onPress={() => setShowModelSelector(true)}
        >
          <View style={[styles.modelIndicator, { backgroundColor: selectedModelData.color }]}>
            <Ionicons name={selectedModelData.icon as any} size={16} color="#ffffff" />
          </View>
          <Text style={styles.headerTitle}>{selectedModelData.name}</Text>
          <Ionicons name="chevron-down" size={16} color={Colors.gray[500]} />
        </TouchableOpacity>
        
        <View style={styles.headerActions}>
          <TouchableOpacity style={styles.headerAction} onPress={handleClearChat}>
            <Ionicons name="trash-outline" size={20} color={Colors.gray[500]} />
          </TouchableOpacity>
          <TouchableOpacity style={styles.headerAction}>
            <Ionicons name="ellipsis-horizontal" size={20} color={Colors.gray[500]} />
          </TouchableOpacity>
        </View>
      </View>

      {/* Messages List */}
      <FlatList
        ref={flatListRef}
        data={messages}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <MessageBubble 
            message={item} 
            isUser={item.sender === 'user'} 
          />
        )}
        style={styles.messagesList}
        contentContainerStyle={styles.messagesContent}
        showsVerticalScrollIndicator={false}
        ListEmptyComponent={
          <View style={styles.emptyState}>
            <View style={styles.emptyIcon}>
              <Ionicons name="chatbubbles-outline" size={48} color={Colors.gray[300]} />
            </View>
            <Text style={styles.emptyTitle}>Start a conversation</Text>
            <Text style={styles.emptySubtitle}>
              Ask me anything! I'm here to help with your tasks.
            </Text>
          </View>
        }
      />

      {/* Attachments Preview */}
      {attachments.length > 0 && (
        <View style={styles.attachmentsPreview}>
          <FlatList
            data={attachments}
            horizontal
            keyExtractor={(item) => item.id}
            renderItem={({ item }) => (
              <View style={styles.attachmentPreview}>
                <View style={styles.attachmentIcon}>
                  <Ionicons name="document" size={16} color={Colors.primary[500]} />
                </View>
                <Text style={styles.attachmentPreviewName} numberOfLines={1}>
                  {item.name}
                </Text>
                <TouchableOpacity
                  style={styles.removeAttachment}
                  onPress={() => removeAttachment(item.id)}
                >
                  <Ionicons name="close-circle" size={16} color={Colors.error} />
                </TouchableOpacity>
              </View>
            )}
            showsHorizontalScrollIndicator={false}
          />
        </View>
      )}

      {/* Input Area */}
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.inputContainer}
      >
        <View style={styles.inputRow}>
          <TouchableOpacity
            style={styles.attachmentButton}
            onPress={handleFileAttachment}
          >
            <Ionicons name="attach" size={24} color={Colors.gray[500]} />
          </TouchableOpacity>
          
          <View style={styles.inputWrapper}>
            <Input
              placeholder="Type your message..."
              value={inputText}
              onChangeText={setInputText}
              multiline
              numberOfLines={3}
              style={styles.messageInput}
              inputStyle={styles.messageInputText}
            />
          </View>
          
          <TouchableOpacity
            style={[
              styles.voiceButton,
              isRecording && styles.voiceButtonActive,
            ]}
            onPress={handleVoiceRecording}
          >
            <Ionicons 
              name={isRecording ? "stop" : "mic"} 
              size={24} 
              color={isRecording ? Colors.error : Colors.gray[500]} 
            />
          </TouchableOpacity>
          
          <TouchableOpacity
            style={[
              styles.sendButton,
              (!inputText.trim() && attachments.length === 0) && styles.sendButtonDisabled,
            ]}
            onPress={handleSendMessage}
            disabled={!inputText.trim() && attachments.length === 0}
          >
            <LinearGradient
              colors={Colors.gradient.primary}
              style={styles.sendButtonGradient}
            >
              <Ionicons name="send" size={20} color="#ffffff" />
            </LinearGradient>
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>

      {/* Model Selector Modal */}
      <ModelSelector
        visible={showModelSelector}
        selectedModel={selectedModel}
        onSelect={(model) => dispatch(setSelectedModel(model))}
        onClose={() => setShowModelSelector(false)}
      />
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.primary[50],
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: Spacing.lg,
    paddingVertical: Spacing.md,
    backgroundColor: '#ffffff',
    borderBottomWidth: 1,
    borderBottomColor: Colors.gray[100],
    ...Shadows.sm,
  },
  modelButton: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  modelIndicator: {
    width: 24,
    height: 24,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: Spacing.xs,
  },
  headerTitle: {
    fontSize: Typography.fontSize.lg,
    fontWeight: Typography.fontWeight.semibold,
    color: Colors.light.text.primary,
    fontFamily: Typography.fontFamily.primary,
    marginRight: Spacing.xs,
  },
  headerActions: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  headerAction: {
    padding: Spacing.xs,
    marginLeft: Spacing.xs,
  },
  messagesList: {
    flex: 1,
  },
  messagesContent: {
    paddingVertical: Spacing.md,
    flexGrow: 1,
  },
  messageContainer: {
    marginVertical: Spacing.xs,
    paddingHorizontal: Spacing.lg,
  },
  userMessageContainer: {
    alignItems: 'flex-end',
  },
  aiMessageContainer: {
    alignItems: 'flex-start',
  },
  messageBubble: {
    maxWidth: width * 0.8,
    borderRadius: BorderRadius.lg,
    padding: Spacing.md,
    ...Shadows.sm,
  },
  userBubble: {
    backgroundColor: Colors.primary[500],
  },
  aiBubble: {
    backgroundColor: '#ffffff',
    borderWidth: 1,
    borderColor: Colors.gray[100],
  },
  aiHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: Spacing.xs,
  },
  aiIcon: {
    width: 20,
    height: 20,
    borderRadius: 10,
    backgroundColor: Colors.primary[50],
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: Spacing.xs,
  },
  aiModel: {
    fontSize: Typography.fontSize.xs,
    color: Colors.gray[500],
    fontFamily: Typography.fontFamily.primary,
    fontWeight: Typography.fontWeight.medium,
  },
  messageText: {
    fontSize: Typography.fontSize.base,
    lineHeight: Typography.lineHeight.relaxed * Typography.fontSize.base,
    fontFamily: Typography.fontFamily.primary,
  },
  userText: {
    color: '#ffffff',
  },
  aiText: {
    color: Colors.light.text.primary,
  },
  attachmentsContainer: {
    marginTop: Spacing.sm,
    paddingTop: Spacing.sm,
    borderTopWidth: 1,
    borderTopColor: 'rgba(255, 255, 255, 0.2)',
  },
  attachmentItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: Spacing.xs,
  },
  attachmentName: {
    fontSize: Typography.fontSize.sm,
    color: Colors.gray[600],
    fontFamily: Typography.fontFamily.primary,
    marginLeft: Spacing.xs,
    flex: 1,
  },
  attachmentSize: {
    fontSize: Typography.fontSize.xs,
    color: Colors.gray[400],
    fontFamily: Typography.fontFamily.primary,
  },
  messageFooter: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginTop: Spacing.xs,
  },
  timestamp: {
    fontSize: Typography.fontSize.xs,
    fontFamily: Typography.fontFamily.primary,
  },
  userTimestamp: {
    color: 'rgba(255, 255, 255, 0.7)',
  },
  aiTimestamp: {
    color: Colors.gray[400],
  },
  statusContainer: {
    marginLeft: Spacing.xs,
  },
  emptyState: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: Spacing.xl,
  },
  emptyIcon: {
    marginBottom: Spacing.lg,
  },
  emptyTitle: {
    fontSize: Typography.fontSize.xl,
    fontWeight: Typography.fontWeight.semibold,
    color: Colors.light.text.primary,
    fontFamily: Typography.fontFamily.primary,
    marginBottom: Spacing.xs,
  },
  emptySubtitle: {
    fontSize: Typography.fontSize.base,
    color: Colors.light.text.secondary,
    fontFamily: Typography.fontFamily.primary,
    textAlign: 'center',
    lineHeight: Typography.lineHeight.relaxed * Typography.fontSize.base,
  },
  attachmentsPreview: {
    backgroundColor: '#ffffff',
    borderTopWidth: 1,
    borderTopColor: Colors.gray[100],
    paddingVertical: Spacing.sm,
    paddingHorizontal: Spacing.lg,
  },
  attachmentPreview: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: Colors.gray[50],
    borderRadius: BorderRadius.md,
    padding: Spacing.sm,
    marginRight: Spacing.sm,
    maxWidth: 150,
  },
  attachmentIcon: {
    marginRight: Spacing.xs,
  },
  attachmentPreviewName: {
    fontSize: Typography.fontSize.sm,
    color: Colors.light.text.primary,
    fontFamily: Typography.fontFamily.primary,
    flex: 1,
  },
  removeAttachment: {
    marginLeft: Spacing.xs,
  },
  inputContainer: {
    backgroundColor: '#ffffff',
    borderTopWidth: 1,
    borderTopColor: Colors.gray[100],
    paddingHorizontal: Spacing.lg,
    paddingVertical: Spacing.md,
  },
  inputRow: {
    flexDirection: 'row',
    alignItems: 'flex-end',
  },
  attachmentButton: {
    padding: Spacing.sm,
    marginRight: Spacing.sm,
  },
  inputWrapper: {
    flex: 1,
    marginRight: Spacing.sm,
  },
  messageInput: {
    marginBottom: 0,
  },
  messageInputText: {
    maxHeight: 100,
  },
  voiceButton: {
    padding: Spacing.sm,
    marginRight: Spacing.sm,
  },
  voiceButtonActive: {
    backgroundColor: Colors.error + '20',
    borderRadius: BorderRadius.md,
  },
  sendButton: {
    width: 44,
    height: 44,
    borderRadius: 22,
    overflow: 'hidden',
  },
  sendButtonDisabled: {
    opacity: 0.5,
  },
  sendButtonGradient: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  modalOverlay: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'flex-end',
  },
  modalBackdrop: {
    flex: 1,
  },
  modelSelectorContainer: {
    backgroundColor: '#ffffff',
    borderTopLeftRadius: BorderRadius.xl,
    borderTopRightRadius: BorderRadius.xl,
    maxHeight: '70%',
  },
  modelSelectorHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: Spacing.lg,
    paddingVertical: Spacing.lg,
    borderBottomWidth: 1,
    borderBottomColor: Colors.gray[100],
  },
  modelSelectorTitle: {
    fontSize: Typography.fontSize.lg,
    fontWeight: Typography.fontWeight.semibold,
    color: Colors.light.text.primary,
    fontFamily: Typography.fontFamily.primary,
  },
  modelOption: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: Spacing.lg,
    paddingVertical: Spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: Colors.gray[50],
  },
  selectedModelOption: {
    backgroundColor: Colors.primary[50],
  },
  modelIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: Spacing.md,
  },
  modelInfo: {
    flex: 1,
  },
  modelName: {
    fontSize: Typography.fontSize.base,
    fontWeight: Typography.fontWeight.medium,
    color: Colors.light.text.primary,
    fontFamily: Typography.fontFamily.primary,
    marginBottom: 2,
  },
  modelDescription: {
    fontSize: Typography.fontSize.sm,
    color: Colors.light.text.secondary,
    fontFamily: Typography.fontFamily.primary,
  },
});

export default ChatScreen;

