import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  Alert,
  Animated,
  Dimensions,
  Modal,
  ScrollView,
  Switch,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import { useDispatch, useSelector } from 'react-redux';

import Button from '../../components/ui/Button';
import Input from '../../components/ui/Input';
import Card from '../../components/ui/Card';
import { Colors, Typography, Spacing, BorderRadius, Shadows } from '../../constants/theme';
import { RootState } from '../../store';
import { 
  loadAgents, 
  createAgent, 
  updateAgent, 
  deleteAgent, 
  deployAgent, 
  stopAgent,
  loadAgentTemplates,
  loadAgentStats
} from '../../store/slices/agentsSlice';

const { width } = Dimensions.get('window');

interface Agent {
  id: string;
  name: string;
  description: string;
  model: string;
  status: 'active' | 'idle' | 'offline' | 'error';
  tasksCompleted: number;
  lastActivity: Date;
  configuration: {
    temperature: number;
    maxTokens: number;
    systemPrompt: string;
    tools: string[];
  };
  performance: {
    successRate: number;
    avgResponseTime: number;
    totalCost: number;
  };
}

interface AgentTemplate {
  id: string;
  name: string;
  description: string;
  icon: string;
  category: string;
  model: string;
  systemPrompt: string;
  tools: string[];
  color: string;
}

const AGENT_TEMPLATES: AgentTemplate[] = [
  {
    id: 'data-analyst',
    name: 'Data Analyst Pro',
    description: 'Specialized in data analysis and visualization',
    icon: 'analytics',
    category: 'Analytics',
    model: 'gpt-4-turbo',
    systemPrompt: 'You are a professional data analyst...',
    tools: ['python', 'pandas', 'matplotlib', 'sql'],
    color: Colors.primary[500],
  },
  {
    id: 'content-creator',
    name: 'Content Creator',
    description: 'Blog posts and marketing copy',
    icon: 'create',
    category: 'Writing',
    model: 'claude-3',
    systemPrompt: 'You are a creative content writer...',
    tools: ['writing', 'research', 'seo'],
    color: Colors.secondary[500],
  },
  {
    id: 'code-assistant',
    name: 'Code Assistant',
    description: 'Programming and debugging help',
    icon: 'code-slash',
    category: 'Development',
    model: 'gpt-4',
    systemPrompt: 'You are an expert software developer...',
    tools: ['coding', 'debugging', 'testing'],
    color: Colors.success,
  },
  {
    id: 'design-helper',
    name: 'Design Helper',
    description: 'UI/UX design and creativity',
    icon: 'color-palette',
    category: 'Design',
    model: 'dall-e-3',
    systemPrompt: 'You are a creative design assistant...',
    tools: ['design', 'image-generation', 'ui-ux'],
    color: Colors.warning,
  },
];

const AgentCard: React.FC<{ 
  agent: Agent; 
  onConfigure: () => void;
  onDeploy: () => void;
  onStats: () => void;
  onDelete: () => void;
}> = ({ agent, onConfigure, onDeploy, onStats, onDelete }) => {
  const fadeAnim = useRef(new Animated.Value(0)).current;
  const scaleAnim = useRef(new Animated.Value(0.95)).current;

  useEffect(() => {
    Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 400,
        useNativeDriver: true,
      }),
      Animated.spring(scaleAnim, {
        toValue: 1,
        tension: 50,
        friction: 8,
        useNativeDriver: true,
      }),
    ]).start();
  }, []);

  const getStatusColor = () => {
    switch (agent.status) {
      case 'active': return Colors.success;
      case 'idle': return Colors.warning;
      case 'offline': return Colors.gray[400];
      case 'error': return Colors.error;
      default: return Colors.gray[400];
    }
  };

  const getStatusIcon = () => {
    switch (agent.status) {
      case 'active': return 'play-circle';
      case 'idle': return 'pause-circle';
      case 'offline': return 'stop-circle';
      case 'error': return 'alert-circle';
      default: return 'help-circle';
    }
  };

  const formatLastActivity = (date: Date) => {
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (days > 0) return `${days}d ago`;
    if (hours > 0) return `${hours}h ago`;
    if (minutes > 0) return `${minutes}m ago`;
    return 'Just now';
  };

  return (
    <Animated.View
      style={[
        styles.agentCard,
        {
          opacity: fadeAnim,
          transform: [{ scale: scaleAnim }],
        },
      ]}
    >
      <Card variant="elevated" style={styles.agentCardContent}>
        <View style={styles.agentHeader}>
          <View style={styles.agentInfo}>
            <View style={styles.agentTitleRow}>
              <Text style={styles.agentName}>{agent.name}</Text>
              <View style={[styles.statusIndicator, { backgroundColor: getStatusColor() }]}>
                <Ionicons name={getStatusIcon() as any} size={12} color="#ffffff" />
              </View>
            </View>
            <Text style={styles.agentDescription}>{agent.description}</Text>
            <View style={styles.agentMeta}>
              <Text style={styles.agentModel}>{agent.model}</Text>
              <Text style={styles.agentSeparator}>•</Text>
              <Text style={styles.agentTasks}>{agent.tasksCompleted} tasks</Text>
              <Text style={styles.agentSeparator}>•</Text>
              <Text style={styles.agentActivity}>{formatLastActivity(agent.lastActivity)}</Text>
            </View>
          </View>
          <TouchableOpacity style={styles.agentMenu} onPress={onDelete}>
            <Ionicons name="ellipsis-vertical" size={20} color={Colors.gray[400]} />
          </TouchableOpacity>
        </View>

        <View style={styles.agentStats}>
          <View style={styles.statItem}>
            <Text style={styles.statValue}>{agent.performance.successRate}%</Text>
            <Text style={styles.statLabel}>Success Rate</Text>
          </View>
          <View style={styles.statItem}>
            <Text style={styles.statValue}>{agent.performance.avgResponseTime}s</Text>
            <Text style={styles.statLabel}>Avg Response</Text>
          </View>
          <View style={styles.statItem}>
            <Text style={styles.statValue}>${agent.performance.totalCost}</Text>
            <Text style={styles.statLabel}>Total Cost</Text>
          </View>
        </View>

        <View style={styles.agentActions}>
          <Button
            title="Configure"
            onPress={onConfigure}
            variant="outline"
            size="sm"
            style={styles.actionButton}
          />
          <Button
            title={agent.status === 'active' ? 'Stop' : 'Deploy'}
            onPress={onDeploy}
            variant={agent.status === 'active' ? 'outline' : 'primary'}
            size="sm"
            style={styles.actionButton}
          />
          <Button
            title="Stats"
            onPress={onStats}
            variant="ghost"
            size="sm"
            style={styles.actionButton}
          />
        </View>
      </Card>
    </Animated.View>
  );
};

const AgentConfigModal: React.FC<{
  visible: boolean;
  agent: Agent | null;
  onSave: (config: any) => void;
  onClose: () => void;
}> = ({ visible, agent, onSave, onClose }) => {
  const [config, setConfig] = useState({
    name: '',
    description: '',
    model: 'gpt-4-turbo',
    temperature: 0.7,
    maxTokens: 2048,
    systemPrompt: '',
    tools: [] as string[],
  });

  useEffect(() => {
    if (agent) {
      setConfig({
        name: agent.name,
        description: agent.description,
        model: agent.model,
        temperature: agent.configuration.temperature,
        maxTokens: agent.configuration.maxTokens,
        systemPrompt: agent.configuration.systemPrompt,
        tools: agent.configuration.tools,
      });
    }
  }, [agent]);

  const handleSave = () => {
    onSave(config);
    onClose();
  };

  return (
    <Modal visible={visible} animationType="slide" presentationStyle="pageSheet">
      <SafeAreaView style={styles.modalContainer}>
        <View style={styles.modalHeader}>
          <TouchableOpacity onPress={onClose}>
            <Text style={styles.modalCancel}>Cancel</Text>
          </TouchableOpacity>
          <Text style={styles.modalTitle}>
            {agent ? 'Configure Agent' : 'Create Agent'}
          </Text>
          <TouchableOpacity onPress={handleSave}>
            <Text style={styles.modalSave}>Save</Text>
          </TouchableOpacity>
        </View>

        <ScrollView style={styles.modalContent} showsVerticalScrollIndicator={false}>
          <Input
            label="Agent Name"
            placeholder="Enter agent name"
            value={config.name}
            onChangeText={(text) => setConfig({ ...config, name: text })}
          />

          <Input
            label="Description"
            placeholder="Describe what this agent does"
            value={config.description}
            onChangeText={(text) => setConfig({ ...config, description: text })}
            multiline
            numberOfLines={3}
          />

          <View style={styles.configSection}>
            <Text style={styles.configSectionTitle}>Model Configuration</Text>
            
            <View style={styles.configRow}>
              <Text style={styles.configLabel}>Model</Text>
              <TouchableOpacity style={styles.configSelector}>
                <Text style={styles.configValue}>{config.model}</Text>
                <Ionicons name="chevron-down" size={16} color={Colors.gray[400]} />
              </TouchableOpacity>
            </View>

            <View style={styles.configRow}>
              <Text style={styles.configLabel}>Temperature</Text>
              <View style={styles.sliderContainer}>
                <Text style={styles.sliderValue}>{config.temperature}</Text>
              </View>
            </View>

            <View style={styles.configRow}>
              <Text style={styles.configLabel}>Max Tokens</Text>
              <Input
                value={config.maxTokens.toString()}
                onChangeText={(text) => setConfig({ ...config, maxTokens: parseInt(text) || 0 })}
                keyboardType="numeric"
                style={styles.tokenInput}
              />
            </View>
          </View>

          <View style={styles.configSection}>
            <Text style={styles.configSectionTitle}>System Prompt</Text>
            <Input
              placeholder="Enter system prompt for the agent"
              value={config.systemPrompt}
              onChangeText={(text) => setConfig({ ...config, systemPrompt: text })}
              multiline
              numberOfLines={6}
            />
          </View>

          <View style={styles.configSection}>
            <Text style={styles.configSectionTitle}>Available Tools</Text>
            <View style={styles.toolsGrid}>
              {['python', 'web-search', 'file-upload', 'image-generation', 'code-execution'].map((tool) => (
                <TouchableOpacity
                  key={tool}
                  style={[
                    styles.toolItem,
                    config.tools.includes(tool) && styles.toolItemSelected,
                  ]}
                  onPress={() => {
                    const newTools = config.tools.includes(tool)
                      ? config.tools.filter(t => t !== tool)
                      : [...config.tools, tool];
                    setConfig({ ...config, tools: newTools });
                  }}
                >
                  <Text style={[
                    styles.toolText,
                    config.tools.includes(tool) && styles.toolTextSelected,
                  ]}>
                    {tool}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>
        </ScrollView>
      </SafeAreaView>
    </Modal>
  );
};

const AgentStatsModal: React.FC<{
  visible: boolean;
  agent: Agent | null;
  onClose: () => void;
}> = ({ visible, agent, onClose }) => {
  if (!agent) return null;

  return (
    <Modal visible={visible} animationType="slide" presentationStyle="pageSheet">
      <SafeAreaView style={styles.modalContainer}>
        <View style={styles.modalHeader}>
          <View />
          <Text style={styles.modalTitle}>{agent.name} Stats</Text>
          <TouchableOpacity onPress={onClose}>
            <Text style={styles.modalCancel}>Close</Text>
          </TouchableOpacity>
        </View>

        <ScrollView style={styles.modalContent}>
          <View style={styles.statsGrid}>
            <Card style={styles.statCard}>
              <Text style={styles.statCardValue}>{agent.tasksCompleted}</Text>
              <Text style={styles.statCardLabel}>Tasks Completed</Text>
            </Card>
            <Card style={styles.statCard}>
              <Text style={styles.statCardValue}>{agent.performance.successRate}%</Text>
              <Text style={styles.statCardLabel}>Success Rate</Text>
            </Card>
            <Card style={styles.statCard}>
              <Text style={styles.statCardValue}>{agent.performance.avgResponseTime}s</Text>
              <Text style={styles.statCardLabel}>Avg Response Time</Text>
            </Card>
            <Card style={styles.statCard}>
              <Text style={styles.statCardValue}>${agent.performance.totalCost}</Text>
              <Text style={styles.statCardLabel}>Total Cost</Text>
            </Card>
          </View>

          <Card style={styles.chartCard}>
            <Text style={styles.chartTitle}>Performance Over Time</Text>
            <View style={styles.chartPlaceholder}>
              <Ionicons name="analytics" size={48} color={Colors.gray[300]} />
              <Text style={styles.chartPlaceholderText}>Chart will be implemented</Text>
            </View>
          </Card>

          <Card style={styles.activityCard}>
            <Text style={styles.activityTitle}>Recent Activity</Text>
            {[1, 2, 3, 4, 5].map((item) => (
              <View key={item} style={styles.activityItem}>
                <View style={styles.activityIcon}>
                  <Ionicons name="checkmark-circle" size={16} color={Colors.success} />
                </View>
                <View style={styles.activityContent}>
                  <Text style={styles.activityText}>Completed data analysis task</Text>
                  <Text style={styles.activityTime}>2 hours ago</Text>
                </View>
              </View>
            ))}
          </Card>
        </ScrollView>
      </SafeAreaView>
    </Modal>
  );
};

const AgentsScreen: React.FC = () => {
  const dispatch = useDispatch();
  const { agents, templates, isLoading } = useSelector((state: RootState) => state.agents);
  
  const [showConfigModal, setShowConfigModal] = useState(false);
  const [showStatsModal, setShowStatsModal] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState<string>('all');

  useEffect(() => {
    dispatch(loadAgents());
    dispatch(loadAgentTemplates());
  }, [dispatch]);

  const filteredAgents = agents.filter(agent => {
    const matchesSearch = agent.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         agent.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesFilter = filterStatus === 'all' || agent.status === filterStatus;
    return matchesSearch && matchesFilter;
  });

  const handleCreateAgent = useCallback((template?: AgentTemplate) => {
    setSelectedAgent(null);
    setShowConfigModal(true);
  }, []);

  const handleConfigureAgent = useCallback((agent: Agent) => {
    setSelectedAgent(agent);
    setShowConfigModal(true);
  }, []);

  const handleViewStats = useCallback((agent: Agent) => {
    setSelectedAgent(agent);
    setShowStatsModal(true);
  }, []);

  const handleDeployAgent = useCallback((agent: Agent) => {
    if (agent.status === 'active') {
      Alert.alert(
        'Stop Agent',
        `Are you sure you want to stop ${agent.name}?`,
        [
          { text: 'Cancel', style: 'cancel' },
          { 
            text: 'Stop', 
            style: 'destructive',
            onPress: () => dispatch(stopAgent(agent.id))
          },
        ]
      );
    } else {
      dispatch(deployAgent(agent.id));
    }
  }, [dispatch]);

  const handleDeleteAgent = useCallback((agent: Agent) => {
    Alert.alert(
      'Delete Agent',
      `Are you sure you want to delete ${agent.name}? This action cannot be undone.`,
      [
        { text: 'Cancel', style: 'cancel' },
        { 
          text: 'Delete', 
          style: 'destructive',
          onPress: () => dispatch(deleteAgent(agent.id))
        },
      ]
    );
  }, [dispatch]);

  const handleSaveAgent = useCallback((config: any) => {
    if (selectedAgent) {
      dispatch(updateAgent({ id: selectedAgent.id, ...config }));
    } else {
      dispatch(createAgent(config));
    }
  }, [selectedAgent, dispatch]);

  return (
    <SafeAreaView style={styles.container}>
      <LinearGradient
        colors={[Colors.primary[50], '#ffffff']}
        style={StyleSheet.absoluteFill}
      />

      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>AI Agents</Text>
        <TouchableOpacity
          style={styles.addButton}
          onPress={() => handleCreateAgent()}
        >
          <LinearGradient
            colors={Colors.gradient.primary}
            style={styles.addButtonGradient}
          >
            <Ionicons name="add" size={24} color="#ffffff" />
          </LinearGradient>
        </TouchableOpacity>
      </View>

      {/* Search and Filters */}
      <View style={styles.searchContainer}>
        <Input
          placeholder="Search agents..."
          value={searchQuery}
          onChangeText={setSearchQuery}
          leftIcon="search"
          style={styles.searchInput}
        />
        
        <ScrollView 
          horizontal 
          showsHorizontalScrollIndicator={false}
          style={styles.filtersContainer}
        >
          {['all', 'active', 'idle', 'offline'].map((status) => (
            <TouchableOpacity
              key={status}
              style={[
                styles.filterChip,
                filterStatus === status && styles.filterChipActive,
              ]}
              onPress={() => setFilterStatus(status)}
            >
              <Text style={[
                styles.filterChipText,
                filterStatus === status && styles.filterChipTextActive,
              ]}>
                {status.charAt(0).toUpperCase() + status.slice(1)}
              </Text>
            </TouchableOpacity>
          ))}
        </ScrollView>
      </View>

      {/* Agents List */}
      <FlatList
        data={filteredAgents}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <AgentCard
            agent={item}
            onConfigure={() => handleConfigureAgent(item)}
            onDeploy={() => handleDeployAgent(item)}
            onStats={() => handleViewStats(item)}
            onDelete={() => handleDeleteAgent(item)}
          />
        )}
        style={styles.agentsList}
        contentContainerStyle={styles.agentsContent}
        showsVerticalScrollIndicator={false}
        ListEmptyComponent={
          <View style={styles.emptyState}>
            <View style={styles.emptyIcon}>
              <Ionicons name="people-outline" size={64} color={Colors.gray[300]} />
            </View>
            <Text style={styles.emptyTitle}>No agents yet</Text>
            <Text style={styles.emptySubtitle}>
              Create your first AI agent to automate tasks and boost productivity
            </Text>
            <Button
              title="Create Agent"
              onPress={() => handleCreateAgent()}
              variant="gradient"
              style={styles.emptyButton}
            />
          </View>
        }
      />

      {/* Agent Templates */}
      {agents.length > 0 && (
        <View style={styles.templatesSection}>
          <Text style={styles.templatesTitle}>Quick Start Templates</Text>
          <ScrollView 
            horizontal 
            showsHorizontalScrollIndicator={false}
            style={styles.templatesContainer}
          >
            {AGENT_TEMPLATES.map((template) => (
              <TouchableOpacity
                key={template.id}
                style={styles.templateCard}
                onPress={() => handleCreateAgent(template)}
              >
                <View style={[styles.templateIcon, { backgroundColor: template.color }]}>
                  <Ionicons name={template.icon as any} size={24} color="#ffffff" />
                </View>
                <Text style={styles.templateName}>{template.name}</Text>
                <Text style={styles.templateCategory}>{template.category}</Text>
              </TouchableOpacity>
            ))}
          </ScrollView>
        </View>
      )}

      {/* Configuration Modal */}
      <AgentConfigModal
        visible={showConfigModal}
        agent={selectedAgent}
        onSave={handleSaveAgent}
        onClose={() => setShowConfigModal(false)}
      />

      {/* Stats Modal */}
      <AgentStatsModal
        visible={showStatsModal}
        agent={selectedAgent}
        onClose={() => setShowStatsModal(false)}
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
    paddingVertical: Spacing.lg,
  },
  headerTitle: {
    fontSize: Typography.fontSize['2xl'],
    fontWeight: Typography.fontWeight.bold,
    color: Colors.light.text.primary,
    fontFamily: Typography.fontFamily.primary,
  },
  addButton: {
    width: 44,
    height: 44,
    borderRadius: 22,
    overflow: 'hidden',
    ...Shadows.md,
  },
  addButtonGradient: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  searchContainer: {
    paddingHorizontal: Spacing.lg,
    marginBottom: Spacing.md,
  },
  searchInput: {
    marginBottom: Spacing.sm,
  },
  filtersContainer: {
    flexDirection: 'row',
  },
  filterChip: {
    paddingHorizontal: Spacing.md,
    paddingVertical: Spacing.xs,
    borderRadius: BorderRadius.full,
    backgroundColor: Colors.gray[100],
    marginRight: Spacing.sm,
  },
  filterChipActive: {
    backgroundColor: Colors.primary[500],
  },
  filterChipText: {
    fontSize: Typography.fontSize.sm,
    color: Colors.gray[600],
    fontFamily: Typography.fontFamily.primary,
    fontWeight: Typography.fontWeight.medium,
  },
  filterChipTextActive: {
    color: '#ffffff',
  },
  agentsList: {
    flex: 1,
  },
  agentsContent: {
    paddingHorizontal: Spacing.lg,
    paddingBottom: Spacing.xl,
  },
  agentCard: {
    marginBottom: Spacing.md,
  },
  agentCardContent: {
    padding: Spacing.lg,
  },
  agentHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: Spacing.md,
  },
  agentInfo: {
    flex: 1,
  },
  agentTitleRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: Spacing.xs,
  },
  agentName: {
    fontSize: Typography.fontSize.lg,
    fontWeight: Typography.fontWeight.semibold,
    color: Colors.light.text.primary,
    fontFamily: Typography.fontFamily.primary,
    flex: 1,
  },
  statusIndicator: {
    width: 20,
    height: 20,
    borderRadius: 10,
    alignItems: 'center',
    justifyContent: 'center',
    marginLeft: Spacing.sm,
  },
  agentDescription: {
    fontSize: Typography.fontSize.sm,
    color: Colors.light.text.secondary,
    fontFamily: Typography.fontFamily.primary,
    marginBottom: Spacing.xs,
  },
  agentMeta: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  agentModel: {
    fontSize: Typography.fontSize.xs,
    color: Colors.primary[500],
    fontFamily: Typography.fontFamily.primary,
    fontWeight: Typography.fontWeight.medium,
  },
  agentSeparator: {
    fontSize: Typography.fontSize.xs,
    color: Colors.gray[400],
    marginHorizontal: Spacing.xs,
  },
  agentTasks: {
    fontSize: Typography.fontSize.xs,
    color: Colors.gray[500],
    fontFamily: Typography.fontFamily.primary,
  },
  agentActivity: {
    fontSize: Typography.fontSize.xs,
    color: Colors.gray[500],
    fontFamily: Typography.fontFamily.primary,
  },
  agentMenu: {
    padding: Spacing.xs,
  },
  agentStats: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    paddingVertical: Spacing.md,
    borderTopWidth: 1,
    borderBottomWidth: 1,
    borderColor: Colors.gray[100],
    marginBottom: Spacing.md,
  },
  statItem: {
    alignItems: 'center',
  },
  statValue: {
    fontSize: Typography.fontSize.lg,
    fontWeight: Typography.fontWeight.bold,
    color: Colors.light.text.primary,
    fontFamily: Typography.fontFamily.primary,
  },
  statLabel: {
    fontSize: Typography.fontSize.xs,
    color: Colors.gray[500],
    fontFamily: Typography.fontFamily.primary,
    marginTop: 2,
  },
  agentActions: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  actionButton: {
    flex: 1,
    marginHorizontal: Spacing.xs,
  },
  emptyState: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: Spacing.xl,
    paddingVertical: Spacing['3xl'],
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
    marginBottom: Spacing.xl,
  },
  emptyButton: {
    paddingHorizontal: Spacing.xl,
  },
  templatesSection: {
    backgroundColor: '#ffffff',
    borderTopWidth: 1,
    borderTopColor: Colors.gray[100],
    paddingVertical: Spacing.lg,
  },
  templatesTitle: {
    fontSize: Typography.fontSize.lg,
    fontWeight: Typography.fontWeight.semibold,
    color: Colors.light.text.primary,
    fontFamily: Typography.fontFamily.primary,
    paddingHorizontal: Spacing.lg,
    marginBottom: Spacing.md,
  },
  templatesContainer: {
    paddingHorizontal: Spacing.lg,
  },
  templateCard: {
    alignItems: 'center',
    backgroundColor: Colors.gray[50],
    borderRadius: BorderRadius.lg,
    padding: Spacing.md,
    marginRight: Spacing.md,
    width: 100,
  },
  templateIcon: {
    width: 48,
    height: 48,
    borderRadius: 24,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: Spacing.sm,
  },
  templateName: {
    fontSize: Typography.fontSize.sm,
    fontWeight: Typography.fontWeight.medium,
    color: Colors.light.text.primary,
    fontFamily: Typography.fontFamily.primary,
    textAlign: 'center',
    marginBottom: 2,
  },
  templateCategory: {
    fontSize: Typography.fontSize.xs,
    color: Colors.gray[500],
    fontFamily: Typography.fontFamily.primary,
    textAlign: 'center',
  },
  modalContainer: {
    flex: 1,
    backgroundColor: '#ffffff',
  },
  modalHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: Spacing.lg,
    paddingVertical: Spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: Colors.gray[100],
  },
  modalTitle: {
    fontSize: Typography.fontSize.lg,
    fontWeight: Typography.fontWeight.semibold,
    color: Colors.light.text.primary,
    fontFamily: Typography.fontFamily.primary,
  },
  modalCancel: {
    fontSize: Typography.fontSize.base,
    color: Colors.gray[500],
    fontFamily: Typography.fontFamily.primary,
  },
  modalSave: {
    fontSize: Typography.fontSize.base,
    color: Colors.primary[500],
    fontFamily: Typography.fontFamily.primary,
    fontWeight: Typography.fontWeight.semibold,
  },
  modalContent: {
    flex: 1,
    paddingHorizontal: Spacing.lg,
    paddingVertical: Spacing.md,
  },
  configSection: {
    marginBottom: Spacing.xl,
  },
  configSectionTitle: {
    fontSize: Typography.fontSize.lg,
    fontWeight: Typography.fontWeight.semibold,
    color: Colors.light.text.primary,
    fontFamily: Typography.fontFamily.primary,
    marginBottom: Spacing.md,
  },
  configRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: Spacing.md,
  },
  configLabel: {
    fontSize: Typography.fontSize.base,
    color: Colors.light.text.primary,
    fontFamily: Typography.fontFamily.primary,
    flex: 1,
  },
  configSelector: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: Colors.gray[50],
    borderRadius: BorderRadius.md,
    paddingHorizontal: Spacing.md,
    paddingVertical: Spacing.sm,
    flex: 1,
    marginLeft: Spacing.md,
  },
  configValue: {
    fontSize: Typography.fontSize.sm,
    color: Colors.light.text.primary,
    fontFamily: Typography.fontFamily.primary,
    flex: 1,
  },
  sliderContainer: {
    flex: 1,
    marginLeft: Spacing.md,
  },
  sliderValue: {
    fontSize: Typography.fontSize.sm,
    color: Colors.light.text.primary,
    fontFamily: Typography.fontFamily.primary,
    textAlign: 'right',
  },
  tokenInput: {
    flex: 1,
    marginLeft: Spacing.md,
    marginBottom: 0,
  },
  toolsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: Spacing.sm,
  },
  toolItem: {
    paddingHorizontal: Spacing.md,
    paddingVertical: Spacing.sm,
    borderRadius: BorderRadius.md,
    backgroundColor: Colors.gray[100],
    borderWidth: 1,
    borderColor: Colors.gray[200],
  },
  toolItemSelected: {
    backgroundColor: Colors.primary[50],
    borderColor: Colors.primary[500],
  },
  toolText: {
    fontSize: Typography.fontSize.sm,
    color: Colors.gray[600],
    fontFamily: Typography.fontFamily.primary,
  },
  toolTextSelected: {
    color: Colors.primary[500],
    fontWeight: Typography.fontWeight.medium,
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: Spacing.md,
    marginBottom: Spacing.lg,
  },
  statCard: {
    flex: 1,
    minWidth: (width - Spacing.lg * 3) / 2,
    alignItems: 'center',
    padding: Spacing.lg,
  },
  statCardValue: {
    fontSize: Typography.fontSize['2xl'],
    fontWeight: Typography.fontWeight.bold,
    color: Colors.light.text.primary,
    fontFamily: Typography.fontFamily.primary,
    marginBottom: Spacing.xs,
  },
  statCardLabel: {
    fontSize: Typography.fontSize.sm,
    color: Colors.gray[500],
    fontFamily: Typography.fontFamily.primary,
    textAlign: 'center',
  },
  chartCard: {
    padding: Spacing.lg,
    marginBottom: Spacing.lg,
  },
  chartTitle: {
    fontSize: Typography.fontSize.lg,
    fontWeight: Typography.fontWeight.semibold,
    color: Colors.light.text.primary,
    fontFamily: Typography.fontFamily.primary,
    marginBottom: Spacing.md,
  },
  chartPlaceholder: {
    height: 200,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: Colors.gray[50],
    borderRadius: BorderRadius.md,
  },
  chartPlaceholderText: {
    fontSize: Typography.fontSize.sm,
    color: Colors.gray[400],
    fontFamily: Typography.fontFamily.primary,
    marginTop: Spacing.sm,
  },
  activityCard: {
    padding: Spacing.lg,
  },
  activityTitle: {
    fontSize: Typography.fontSize.lg,
    fontWeight: Typography.fontWeight.semibold,
    color: Colors.light.text.primary,
    fontFamily: Typography.fontFamily.primary,
    marginBottom: Spacing.md,
  },
  activityItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: Spacing.sm,
    borderBottomWidth: 1,
    borderBottomColor: Colors.gray[100],
  },
  activityIcon: {
    marginRight: Spacing.sm,
  },
  activityContent: {
    flex: 1,
  },
  activityText: {
    fontSize: Typography.fontSize.sm,
    color: Colors.light.text.primary,
    fontFamily: Typography.fontFamily.primary,
    marginBottom: 2,
  },
  activityTime: {
    fontSize: Typography.fontSize.xs,
    color: Colors.gray[400],
    fontFamily: Typography.fontFamily.primary,
  },
});

export default AgentsScreen;

