import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  RefreshControl,
  Dimensions,
  TouchableOpacity,
  Animated,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import { LineChart, BarChart, PieChart } from 'react-native-chart-kit';
import { useDispatch, useSelector } from 'react-redux';

import Card from '../../components/ui/Card';
import Button from '../../components/ui/Button';
import { Colors, Typography, Spacing, BorderRadius, Shadows } from '../../constants/theme';
import { RootState } from '../../store';
import { loadDashboardData } from '../../store/slices/dashboardSlice';

const { width } = Dimensions.get('window');
const chartWidth = width - (Spacing.lg * 2);

interface MetricCardProps {
  title: string;
  value: string;
  change: string;
  changeType: 'positive' | 'negative' | 'neutral';
  icon: string;
  gradient: string[];
}

const MetricCard: React.FC<MetricCardProps> = ({ title, value, change, changeType, icon, gradient }) => {
  const fadeAnim = useRef(new Animated.Value(0)).current;
  const scaleAnim = useRef(new Animated.Value(0.9)).current;

  useEffect(() => {
    Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 600,
        useNativeDriver: true,
      }),
      Animated.spring(scaleAnim, {
        toValue: 1,
        tension: 50,
        friction: 7,
        useNativeDriver: true,
      }),
    ]).start();
  }, []);

  const getChangeColor = () => {
    switch (changeType) {
      case 'positive': return Colors.success;
      case 'negative': return Colors.error;
      default: return Colors.gray[500];
    }
  };

  return (
    <Animated.View
      style={[
        styles.metricCard,
        {
          opacity: fadeAnim,
          transform: [{ scale: scaleAnim }],
        },
      ]}
    >
      <LinearGradient
        colors={gradient}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
        style={styles.metricGradient}
      >
        <View style={styles.metricHeader}>
          <View style={styles.metricIconContainer}>
            <Ionicons name={icon as any} size={24} color="#ffffff" />
          </View>
          <Text style={styles.metricTitle}>{title}</Text>
        </View>
        <Text style={styles.metricValue}>{value}</Text>
        <View style={styles.metricChange}>
          <Ionicons
            name={changeType === 'positive' ? 'trending-up' : changeType === 'negative' ? 'trending-down' : 'remove'}
            size={16}
            color={getChangeColor()}
          />
          <Text style={[styles.metricChangeText, { color: getChangeColor() }]}>
            {change}
          </Text>
        </View>
      </LinearGradient>
    </Animated.View>
  );
};

const DashboardScreen: React.FC = () => {
  const dispatch = useDispatch();
  const { data, isLoading, lastUpdated } = useSelector((state: RootState) => state.dashboard);
  const { user } = useSelector((state: RootState) => state.auth);
  
  const [refreshing, setRefreshing] = useState(false);
  const fadeAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    dispatch(loadDashboardData());
    
    Animated.timing(fadeAnim, {
      toValue: 1,
      duration: 800,
      useNativeDriver: true,
    }).start();
  }, [dispatch]);

  const handleRefresh = async () => {
    setRefreshing(true);
    await dispatch(loadDashboardData());
    setRefreshing(false);
  };

  const usageData = {
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    datasets: [
      {
        data: [20, 45, 28, 80, 99, 43, 65],
        color: (opacity = 1) => `rgba(14, 165, 233, ${opacity})`,
        strokeWidth: 3,
      },
    ],
  };

  const modelUsageData = {
    labels: ['GPT-4', 'Claude', 'Gemini', 'Others'],
    datasets: [
      {
        data: [45, 30, 20, 5],
      },
    ],
  };

  const costData = [
    { name: 'GPT-4', population: 45, color: Colors.primary[500], legendFontColor: Colors.gray[600] },
    { name: 'Claude', population: 30, color: Colors.secondary[500], legendFontColor: Colors.gray[600] },
    { name: 'Gemini', population: 20, color: Colors.warning, legendFontColor: Colors.gray[600] },
    { name: 'Others', population: 5, color: Colors.gray[400], legendFontColor: Colors.gray[600] },
  ];

  const chartConfig = {
    backgroundColor: '#ffffff',
    backgroundGradientFrom: '#ffffff',
    backgroundGradientTo: '#ffffff',
    decimalPlaces: 0,
    color: (opacity = 1) => `rgba(14, 165, 233, ${opacity})`,
    labelColor: (opacity = 1) => `rgba(107, 114, 128, ${opacity})`,
    style: {
      borderRadius: BorderRadius.lg,
    },
    propsForDots: {
      r: '6',
      strokeWidth: '2',
      stroke: Colors.primary[500],
    },
  };

  return (
    <SafeAreaView style={styles.container}>
      <LinearGradient
        colors={[Colors.primary[50], '#ffffff']}
        style={StyleSheet.absoluteFill}
      />

      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={handleRefresh} />
        }
        showsVerticalScrollIndicator={false}
      >
        {/* Header */}
        <Animated.View style={[styles.header, { opacity: fadeAnim }]}>
          <View style={styles.headerContent}>
            <View>
              <Text style={styles.greeting}>Good morning,</Text>
              <Text style={styles.userName}>{user?.name || 'User'}</Text>
            </View>
            <TouchableOpacity style={styles.profileButton}>
              <LinearGradient
                colors={Colors.gradient.primary}
                style={styles.profileGradient}
              >
                <Text style={styles.profileInitial}>
                  {user?.name?.charAt(0) || 'U'}
                </Text>
              </LinearGradient>
            </TouchableOpacity>
          </View>
          <Text style={styles.headerSubtitle}>
            Your AI productivity dashboard
          </Text>
        </Animated.View>

        {/* Quick Stats */}
        <Animated.View style={[styles.statsContainer, { opacity: fadeAnim }]}>
          <View style={styles.statsGrid}>
            <MetricCard
              title="Total Queries"
              value="1,247"
              change="+12.5%"
              changeType="positive"
              icon="chatbubbles"
              gradient={Colors.gradient.primary}
            />
            <MetricCard
              title="Cost Saved"
              value="$89.50"
              change="+8.2%"
              changeType="positive"
              icon="trending-up"
              gradient={Colors.gradient.success}
            />
            <MetricCard
              title="Active Agents"
              value="5"
              change="0%"
              changeType="neutral"
              icon="people"
              gradient={Colors.gradient.secondary}
            />
            <MetricCard
              title="Response Time"
              value="1.2s"
              change="-15%"
              changeType="positive"
              icon="flash"
              gradient={Colors.gradient.warning}
            />
          </View>
        </Animated.View>

        {/* Usage Chart */}
        <Animated.View style={[styles.chartContainer, { opacity: fadeAnim }]}>
          <Card variant="elevated" style={styles.chartCard}>
            <View style={styles.chartHeader}>
              <Text style={styles.chartTitle}>Weekly Usage</Text>
              <TouchableOpacity style={styles.chartMenuButton}>
                <Ionicons name="ellipsis-horizontal" size={20} color={Colors.gray[500]} />
              </TouchableOpacity>
            </View>
            <LineChart
              data={usageData}
              width={chartWidth - 32}
              height={200}
              chartConfig={chartConfig}
              bezier
              style={styles.chart}
            />
          </Card>
        </Animated.View>

        {/* Model Usage & Cost Distribution */}
        <Animated.View style={[styles.chartsRow, { opacity: fadeAnim }]}>
          <Card variant="elevated" style={styles.halfChart}>
            <Text style={styles.chartTitle}>Model Usage</Text>
            <BarChart
              data={modelUsageData}
              width={chartWidth / 2 - 24}
              height={180}
              chartConfig={{
                ...chartConfig,
                color: (opacity = 1) => `rgba(217, 70, 239, ${opacity})`,
              }}
              style={styles.smallChart}
            />
          </Card>

          <Card variant="elevated" style={styles.halfChart}>
            <Text style={styles.chartTitle}>Cost Distribution</Text>
            <PieChart
              data={costData}
              width={chartWidth / 2 - 24}
              height={180}
              chartConfig={chartConfig}
              accessor="population"
              backgroundColor="transparent"
              paddingLeft="0"
              style={styles.smallChart}
            />
          </Card>
        </Animated.View>

        {/* Quick Actions */}
        <Animated.View style={[styles.actionsContainer, { opacity: fadeAnim }]}>
          <Card variant="gradient" style={styles.actionsCard}>
            <Text style={styles.actionsTitle}>Quick Actions</Text>
            <View style={styles.actionsGrid}>
              <Button
                title="New Chat"
                onPress={() => {}}
                variant="outline"
                icon={<Ionicons name="add-circle-outline" size={20} color={Colors.primary[500]} />}
                style={styles.actionButton}
              />
              <Button
                title="Deploy Agent"
                onPress={() => {}}
                variant="outline"
                icon={<Ionicons name="rocket-outline" size={20} color={Colors.primary[500]} />}
                style={styles.actionButton}
              />
              <Button
                title="Upload File"
                onPress={() => {}}
                variant="outline"
                icon={<Ionicons name="cloud-upload-outline" size={20} color={Colors.primary[500]} />}
                style={styles.actionButton}
              />
              <Button
                title="View Analytics"
                onPress={() => {}}
                variant="outline"
                icon={<Ionicons name="analytics-outline" size={20} color={Colors.primary[500]} />}
                style={styles.actionButton}
              />
            </View>
          </Card>
        </Animated.View>

        {/* Recent Activity */}
        <Animated.View style={[styles.activityContainer, { opacity: fadeAnim }]}>
          <Card variant="elevated" style={styles.activityCard}>
            <View style={styles.activityHeader}>
              <Text style={styles.activityTitle}>Recent Activity</Text>
              <TouchableOpacity>
                <Text style={styles.viewAllText}>View All</Text>
              </TouchableOpacity>
            </View>
            
            {[1, 2, 3].map((item) => (
              <View key={item} style={styles.activityItem}>
                <View style={styles.activityIcon}>
                  <Ionicons name="chatbubble-outline" size={16} color={Colors.primary[500]} />
                </View>
                <View style={styles.activityContent}>
                  <Text style={styles.activityText}>
                    New conversation with GPT-4 model
                  </Text>
                  <Text style={styles.activityTime}>2 minutes ago</Text>
                </View>
              </View>
            ))}
          </Card>
        </Animated.View>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.primary[50],
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    paddingBottom: Spacing.xl,
  },
  header: {
    paddingHorizontal: Spacing.lg,
    paddingVertical: Spacing.lg,
  },
  headerContent: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: Spacing.xs,
  },
  greeting: {
    fontSize: Typography.fontSize.base,
    color: Colors.light.text.secondary,
    fontFamily: Typography.fontFamily.primary,
  },
  userName: {
    fontSize: Typography.fontSize['2xl'],
    fontWeight: Typography.fontWeight.bold,
    color: Colors.light.text.primary,
    fontFamily: Typography.fontFamily.primary,
  },
  profileButton: {
    width: 48,
    height: 48,
    borderRadius: 24,
    overflow: 'hidden',
    ...Shadows.md,
  },
  profileGradient: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  profileInitial: {
    fontSize: Typography.fontSize.lg,
    fontWeight: Typography.fontWeight.bold,
    color: '#ffffff',
    fontFamily: Typography.fontFamily.primary,
  },
  headerSubtitle: {
    fontSize: Typography.fontSize.sm,
    color: Colors.light.text.tertiary,
    fontFamily: Typography.fontFamily.primary,
  },
  statsContainer: {
    paddingHorizontal: Spacing.lg,
    marginBottom: Spacing.lg,
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  metricCard: {
    width: (width - Spacing.lg * 3) / 2,
    marginBottom: Spacing.md,
    borderRadius: BorderRadius.lg,
    overflow: 'hidden',
    ...Shadows.md,
  },
  metricGradient: {
    padding: Spacing.md,
    minHeight: 120,
  },
  metricHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: Spacing.sm,
  },
  metricIconContainer: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: Spacing.xs,
  },
  metricTitle: {
    fontSize: Typography.fontSize.sm,
    color: 'rgba(255, 255, 255, 0.9)',
    fontFamily: Typography.fontFamily.primary,
    flex: 1,
  },
  metricValue: {
    fontSize: Typography.fontSize['2xl'],
    fontWeight: Typography.fontWeight.bold,
    color: '#ffffff',
    fontFamily: Typography.fontFamily.primary,
    marginBottom: Spacing.xs,
  },
  metricChange: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  metricChangeText: {
    fontSize: Typography.fontSize.sm,
    fontFamily: Typography.fontFamily.primary,
    marginLeft: Spacing.xs,
  },
  chartContainer: {
    paddingHorizontal: Spacing.lg,
    marginBottom: Spacing.lg,
  },
  chartCard: {
    padding: Spacing.lg,
  },
  chartHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: Spacing.md,
  },
  chartTitle: {
    fontSize: Typography.fontSize.lg,
    fontWeight: Typography.fontWeight.semibold,
    color: Colors.light.text.primary,
    fontFamily: Typography.fontFamily.primary,
  },
  chartMenuButton: {
    padding: Spacing.xs,
  },
  chart: {
    borderRadius: BorderRadius.md,
  },
  chartsRow: {
    flexDirection: 'row',
    paddingHorizontal: Spacing.lg,
    marginBottom: Spacing.lg,
    gap: Spacing.md,
  },
  halfChart: {
    flex: 1,
    padding: Spacing.md,
  },
  smallChart: {
    borderRadius: BorderRadius.md,
    marginTop: Spacing.sm,
  },
  actionsContainer: {
    paddingHorizontal: Spacing.lg,
    marginBottom: Spacing.lg,
  },
  actionsCard: {
    padding: Spacing.lg,
  },
  actionsTitle: {
    fontSize: Typography.fontSize.lg,
    fontWeight: Typography.fontWeight.semibold,
    color: Colors.light.text.primary,
    fontFamily: Typography.fontFamily.primary,
    marginBottom: Spacing.md,
  },
  actionsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: Spacing.sm,
  },
  actionButton: {
    flex: 1,
    minWidth: '45%',
  },
  activityContainer: {
    paddingHorizontal: Spacing.lg,
  },
  activityCard: {
    padding: Spacing.lg,
  },
  activityHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: Spacing.md,
  },
  activityTitle: {
    fontSize: Typography.fontSize.lg,
    fontWeight: Typography.fontWeight.semibold,
    color: Colors.light.text.primary,
    fontFamily: Typography.fontFamily.primary,
  },
  viewAllText: {
    fontSize: Typography.fontSize.sm,
    color: Colors.primary[500],
    fontFamily: Typography.fontFamily.primary,
    fontWeight: Typography.fontWeight.medium,
  },
  activityItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: Spacing.sm,
    borderBottomWidth: 1,
    borderBottomColor: Colors.gray[100],
  },
  activityIcon: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: Colors.primary[50],
    alignItems: 'center',
    justifyContent: 'center',
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
    color: Colors.light.text.tertiary,
    fontFamily: Typography.fontFamily.primary,
  },
});

export default DashboardScreen;

