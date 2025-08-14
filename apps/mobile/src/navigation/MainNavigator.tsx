import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import DashboardScreen from '../screens/dashboard/DashboardScreen';
import ChatScreen from '../screens/chat/ChatScreen';
import AgentsScreen from '../screens/agents/AgentsScreen';
import FilesScreen from '../screens/files/FilesScreen';
import SettingsScreen from '../screens/settings/SettingsScreen';

import { Colors, Typography, Spacing, BorderRadius } from '../constants/theme';

export type MainTabParamList = {
  Dashboard: undefined;
  Chat: undefined;
  Agents: undefined;
  Files: undefined;
  Settings: undefined;
};

const Tab = createBottomTabNavigator<MainTabParamList>();

interface TabBarIconProps {
  focused: boolean;
  color: string;
  size: number;
  name: string;
}

const TabBarIcon: React.FC<TabBarIconProps> = ({ focused, name }) => {
  return (
    <View style={[styles.tabIconContainer, focused && styles.tabIconFocused]}>
      {focused && (
        <LinearGradient
          colors={Colors.gradient.primary}
          style={styles.tabIconGradient}
        />
      )}
      <Ionicons
        name={name as any}
        size={24}
        color={focused ? '#ffffff' : Colors.gray[400]}
      />
    </View>
  );
};

interface TabBarLabelProps {
  focused: boolean;
  children: string;
}

const TabBarLabel: React.FC<TabBarLabelProps> = ({ focused, children }) => {
  return (
    <Text
      style={[
        styles.tabLabel,
        {
          color: focused ? Colors.primary[500] : Colors.gray[400],
          fontWeight: focused ? Typography.fontWeight.semibold : Typography.fontWeight.normal,
        },
      ]}
    >
      {children}
    </Text>
  );
};

const MainNavigator: React.FC = () => {
  const insets = useSafeAreaInsets();

  return (
    <Tab.Navigator
      screenOptions={{
        headerShown: false,
        tabBarStyle: [
          styles.tabBar,
          {
            paddingBottom: insets.bottom + 8,
            height: 80 + insets.bottom,
          },
        ],
        tabBarShowLabel: true,
        tabBarActiveTintColor: Colors.primary[500],
        tabBarInactiveTintColor: Colors.gray[400],
      }}
    >
      <Tab.Screen
        name="Dashboard"
        component={DashboardScreen}
        options={{
          tabBarIcon: (props) => <TabBarIcon {...props} name="grid-outline" />,
          tabBarLabel: (props) => <TabBarLabel {...props}>Dashboard</TabBarLabel>,
        }}
      />
      <Tab.Screen
        name="Chat"
        component={ChatScreen}
        options={{
          tabBarIcon: (props) => <TabBarIcon {...props} name="chatbubbles-outline" />,
          tabBarLabel: (props) => <TabBarLabel {...props}>Chat</TabBarLabel>,
        }}
      />
      <Tab.Screen
        name="Agents"
        component={AgentsScreen}
        options={{
          tabBarIcon: (props) => <TabBarIcon {...props} name="people-outline" />,
          tabBarLabel: (props) => <TabBarLabel {...props}>Agents</TabBarLabel>,
        }}
      />
      <Tab.Screen
        name="Files"
        component={FilesScreen}
        options={{
          tabBarIcon: (props) => <TabBarIcon {...props} name="folder-outline" />,
          tabBarLabel: (props) => <TabBarLabel {...props}>Files</TabBarLabel>,
        }}
      />
      <Tab.Screen
        name="Settings"
        component={SettingsScreen}
        options={{
          tabBarIcon: (props) => <TabBarIcon {...props} name="settings-outline" />,
          tabBarLabel: (props) => <TabBarLabel {...props}>Settings</TabBarLabel>,
        }}
      />
    </Tab.Navigator>
  );
};

const styles = StyleSheet.create({
  tabBar: {
    backgroundColor: '#ffffff',
    borderTopWidth: 1,
    borderTopColor: Colors.gray[100],
    paddingTop: Spacing.sm,
    paddingHorizontal: Spacing.sm,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: -2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 8,
  },
  tabIconContainer: {
    width: 48,
    height: 32,
    borderRadius: BorderRadius.lg,
    alignItems: 'center',
    justifyContent: 'center',
    overflow: 'hidden',
  },
  tabIconFocused: {
    shadowColor: Colors.primary[500],
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 4,
    elevation: 4,
  },
  tabIconGradient: {
    ...StyleSheet.absoluteFillObject,
    borderRadius: BorderRadius.lg,
  },
  tabLabel: {
    fontSize: Typography.fontSize.xs,
    fontFamily: Typography.fontFamily.primary,
    marginTop: 2,
  },
});

export default MainNavigator;

