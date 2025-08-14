import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  Switch,
  Modal,
  Linking,
  Share,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import { useDispatch, useSelector } from 'react-redux';
import * as LocalAuthentication from 'expo-local-authentication';
import * as Notifications from 'expo-notifications';

import Button from '../../components/ui/Button';
import Input from '../../components/ui/Input';
import Card from '../../components/ui/Card';
import { Colors, Typography, Spacing, BorderRadius, Shadows } from '../../constants/theme';
import { RootState } from '../../store';
import { 
  updateProfile,
  updatePreferences,
  updateSecuritySettings,
  updateNotificationSettings,
  logout,
  deleteAccount,
  exportData,
  clearCache
} from '../../store/slices/settingsSlice';

interface SettingItem {
  id: string;
  title: string;
  subtitle?: string;
  icon: string;
  type: 'toggle' | 'navigation' | 'action' | 'info';
  value?: boolean | string;
  onPress?: () => void;
  onToggle?: (value: boolean) => void;
  color?: string;
  badge?: string;
}

interface SettingSection {
  title: string;
  items: SettingItem[];
}

const SettingRow: React.FC<{ 
  item: SettingItem;
  isLast?: boolean;
}> = ({ item, isLast }) => {
  const renderRightComponent = () => {
    switch (item.type) {
      case 'toggle':
        return (
          <Switch
            value={item.value as boolean}
            onValueChange={item.onToggle}
            trackColor={{ false: Colors.gray[300], true: Colors.primary[500] }}
            thumbColor={item.value ? '#ffffff' : '#ffffff'}
          />
        );
      case 'navigation':
        return (
          <View style={styles.navigationRight}>
            {item.badge && (
              <View style={styles.badge}>
                <Text style={styles.badgeText}>{item.badge}</Text>
              </View>
            )}
            {item.value && (
              <Text style={styles.settingValue}>{item.value}</Text>
            )}
            <Ionicons name="chevron-forward" size={16} color={Colors.gray[400]} />
          </View>
        );
      case 'info':
        return item.value ? (
          <Text style={styles.settingValue}>{item.value}</Text>
        ) : null;
      default:
        return null;
    }
  };

  return (
    <TouchableOpacity
      style={[
        styles.settingRow,
        !isLast && styles.settingRowBorder,
      ]}
      onPress={item.onPress}
      disabled={item.type === 'toggle' || item.type === 'info'}
    >
      <View style={[
        styles.settingIcon,
        { backgroundColor: item.color ? item.color + '20' : Colors.gray[100] }
      ]}>
        <Ionicons 
          name={item.icon as any} 
          size={20} 
          color={item.color || Colors.gray[600]} 
        />
      </View>
      
      <View style={styles.settingContent}>
        <Text style={styles.settingTitle}>{item.title}</Text>
        {item.subtitle && (
          <Text style={styles.settingSubtitle}>{item.subtitle}</Text>
        )}
      </View>
      
      {renderRightComponent()}
    </TouchableOpacity>
  );
};

const ProfileModal: React.FC<{
  visible: boolean;
  onClose: () => void;
  onSave: (profile: any) => void;
}> = ({ visible, onClose, onSave }) => {
  const { user } = useSelector((state: RootState) => state.settings);
  const [profile, setProfile] = useState({
    name: '',
    email: '',
    avatar: '',
    bio: '',
    company: '',
    location: '',
  });

  useEffect(() => {
    if (user) {
      setProfile({
        name: user.name || '',
        email: user.email || '',
        avatar: user.avatar || '',
        bio: user.bio || '',
        company: user.company || '',
        location: user.location || '',
      });
    }
  }, [user]);

  const handleSave = () => {
    onSave(profile);
    onClose();
  };

  return (
    <Modal visible={visible} animationType="slide" presentationStyle="pageSheet">
      <SafeAreaView style={styles.modalContainer}>
        <View style={styles.modalHeader}>
          <TouchableOpacity onPress={onClose}>
            <Text style={styles.modalCancel}>Cancel</Text>
          </TouchableOpacity>
          <Text style={styles.modalTitle}>Edit Profile</Text>
          <TouchableOpacity onPress={handleSave}>
            <Text style={styles.modalSave}>Save</Text>
          </TouchableOpacity>
        </View>

        <ScrollView style={styles.modalContent} showsVerticalScrollIndicator={false}>
          <View style={styles.avatarSection}>
            <View style={styles.avatarContainer}>
              <View style={styles.avatar}>
                <Ionicons name="person" size={48} color={Colors.gray[400]} />
              </View>
              <TouchableOpacity style={styles.avatarEdit}>
                <Ionicons name="camera" size={16} color="#ffffff" />
              </TouchableOpacity>
            </View>
            <Text style={styles.avatarText}>Tap to change photo</Text>
          </View>

          <Input
            label="Full Name"
            placeholder="Enter your full name"
            value={profile.name}
            onChangeText={(text) => setProfile({ ...profile, name: text })}
          />

          <Input
            label="Email"
            placeholder="Enter your email"
            value={profile.email}
            onChangeText={(text) => setProfile({ ...profile, email: text })}
            keyboardType="email-address"
            autoCapitalize="none"
          />

          <Input
            label="Bio"
            placeholder="Tell us about yourself"
            value={profile.bio}
            onChangeText={(text) => setProfile({ ...profile, bio: text })}
            multiline
            numberOfLines={3}
          />

          <Input
            label="Company"
            placeholder="Your company or organization"
            value={profile.company}
            onChangeText={(text) => setProfile({ ...profile, company: text })}
          />

          <Input
            label="Location"
            placeholder="Your location"
            value={profile.location}
            onChangeText={(text) => setProfile({ ...profile, location: text })}
          />
        </ScrollView>
      </SafeAreaView>
    </Modal>
  );
};

const ThemeModal: React.FC<{
  visible: boolean;
  currentTheme: string;
  onClose: () => void;
  onSelect: (theme: string) => void;
}> = ({ visible, currentTheme, onClose, onSelect }) => {
  const themes = [
    { id: 'light', name: 'Light', icon: 'sunny', color: Colors.warning },
    { id: 'dark', name: 'Dark', icon: 'moon', color: Colors.gray[700] },
    { id: 'auto', name: 'Auto', icon: 'phone-portrait', color: Colors.primary[500] },
  ];

  return (
    <Modal visible={visible} animationType="slide" presentationStyle="pageSheet">
      <SafeAreaView style={styles.modalContainer}>
        <View style={styles.modalHeader}>
          <TouchableOpacity onPress={onClose}>
            <Text style={styles.modalCancel}>Cancel</Text>
          </TouchableOpacity>
          <Text style={styles.modalTitle}>Theme</Text>
          <View style={{ width: 60 }} />
        </View>

        <View style={styles.modalContent}>
          {themes.map((theme) => (
            <TouchableOpacity
              key={theme.id}
              style={[
                styles.themeOption,
                currentTheme === theme.id && styles.themeOptionSelected,
              ]}
              onPress={() => {
                onSelect(theme.id);
                onClose();
              }}
            >
              <View style={[styles.themeIcon, { backgroundColor: theme.color + '20' }]}>
                <Ionicons name={theme.icon as any} size={24} color={theme.color} />
              </View>
              <Text style={styles.themeName}>{theme.name}</Text>
              {currentTheme === theme.id && (
                <Ionicons name="checkmark-circle" size={24} color={Colors.primary[500]} />
              )}
            </TouchableOpacity>
          ))}
        </View>
      </SafeAreaView>
    </Modal>
  );
};

const SettingsScreen: React.FC = () => {
  const dispatch = useDispatch();
  const { 
    user, 
    preferences, 
    security, 
    notifications 
  } = useSelector((state: RootState) => state.settings);
  
  const [showProfileModal, setShowProfileModal] = useState(false);
  const [showThemeModal, setShowThemeModal] = useState(false);
  const [biometricAvailable, setBiometricAvailable] = useState(false);

  useEffect(() => {
    checkBiometricAvailability();
  }, []);

  const checkBiometricAvailability = async () => {
    const available = await LocalAuthentication.hasHardwareAsync();
    const enrolled = await LocalAuthentication.isEnrolledAsync();
    setBiometricAvailable(available && enrolled);
  };

  const handleProfileUpdate = useCallback((profile: any) => {
    dispatch(updateProfile(profile));
  }, [dispatch]);

  const handleThemeChange = useCallback((theme: string) => {
    dispatch(updatePreferences({ ...preferences, theme }));
  }, [dispatch, preferences]);

  const handleBiometricToggle = useCallback(async (enabled: boolean) => {
    if (enabled) {
      const result = await LocalAuthentication.authenticateAsync({
        promptMessage: 'Enable biometric authentication',
        fallbackLabel: 'Use passcode',
      });
      
      if (result.success) {
        dispatch(updateSecuritySettings({ ...security, biometricEnabled: true }));
      }
    } else {
      dispatch(updateSecuritySettings({ ...security, biometricEnabled: false }));
    }
  }, [dispatch, security]);

  const handleNotificationToggle = useCallback((key: string, value: boolean) => {
    dispatch(updateNotificationSettings({ ...notifications, [key]: value }));
  }, [dispatch, notifications]);

  const handleExportData = useCallback(async () => {
    try {
      const result = await dispatch(exportData()).unwrap();
      await Share.share({
        url: result.downloadUrl,
        title: 'Export Data',
      });
    } catch (error) {
      Alert.alert('Error', 'Failed to export data');
    }
  }, [dispatch]);

  const handleClearCache = useCallback(() => {
    Alert.alert(
      'Clear Cache',
      'This will clear all cached data and may slow down the app temporarily. Continue?',
      [
        { text: 'Cancel', style: 'cancel' },
        { 
          text: 'Clear', 
          onPress: () => dispatch(clearCache())
        },
      ]
    );
  }, [dispatch]);

  const handleLogout = useCallback(() => {
    Alert.alert(
      'Sign Out',
      'Are you sure you want to sign out?',
      [
        { text: 'Cancel', style: 'cancel' },
        { 
          text: 'Sign Out', 
          style: 'destructive',
          onPress: () => dispatch(logout())
        },
      ]
    );
  }, [dispatch]);

  const handleDeleteAccount = useCallback(() => {
    Alert.alert(
      'Delete Account',
      'This action cannot be undone. All your data will be permanently deleted.',
      [
        { text: 'Cancel', style: 'cancel' },
        { 
          text: 'Delete', 
          style: 'destructive',
          onPress: () => {
            Alert.prompt(
              'Confirm Deletion',
              'Type "DELETE" to confirm:',
              [
                { text: 'Cancel', style: 'cancel' },
                { 
                  text: 'Delete',
                  style: 'destructive',
                  onPress: (text) => {
                    if (text === 'DELETE') {
                      dispatch(deleteAccount());
                    } else {
                      Alert.alert('Error', 'Confirmation text does not match');
                    }
                  }
                },
              ],
              'plain-text'
            );
          }
        },
      ]
    );
  }, [dispatch]);

  const sections: SettingSection[] = [
    {
      title: 'Account',
      items: [
        {
          id: 'profile',
          title: 'Profile',
          subtitle: user?.name || 'Set up your profile',
          icon: 'person',
          type: 'navigation',
          onPress: () => setShowProfileModal(true),
          color: Colors.primary[500],
        },
        {
          id: 'subscription',
          title: 'Subscription',
          subtitle: 'Pro Plan',
          icon: 'diamond',
          type: 'navigation',
          badge: 'Active',
          color: Colors.warning,
        },
        {
          id: 'usage',
          title: 'Usage & Billing',
          subtitle: 'View your usage statistics',
          icon: 'analytics',
          type: 'navigation',
          color: Colors.success,
        },
      ],
    },
    {
      title: 'Preferences',
      items: [
        {
          id: 'theme',
          title: 'Theme',
          subtitle: 'Customize app appearance',
          icon: 'color-palette',
          type: 'navigation',
          value: preferences?.theme || 'Auto',
          onPress: () => setShowThemeModal(true),
          color: Colors.secondary[500],
        },
        {
          id: 'language',
          title: 'Language',
          subtitle: 'App language',
          icon: 'language',
          type: 'navigation',
          value: 'English',
          color: Colors.blue[500],
        },
        {
          id: 'defaultModel',
          title: 'Default AI Model',
          subtitle: 'Choose your preferred model',
          icon: 'flash',
          type: 'navigation',
          value: preferences?.defaultModel || 'GPT-4 Turbo',
          color: Colors.purple[500],
        },
        {
          id: 'autoSave',
          title: 'Auto-save Conversations',
          subtitle: 'Automatically save chat history',
          icon: 'save',
          type: 'toggle',
          value: preferences?.autoSave ?? true,
          onToggle: (value) => dispatch(updatePreferences({ ...preferences, autoSave: value })),
          color: Colors.green[500],
        },
      ],
    },
    {
      title: 'Security & Privacy',
      items: [
        {
          id: 'biometric',
          title: 'Biometric Authentication',
          subtitle: biometricAvailable ? 'Use Face ID or Touch ID' : 'Not available on this device',
          icon: 'finger-print',
          type: 'toggle',
          value: security?.biometricEnabled ?? false,
          onToggle: handleBiometricToggle,
          color: Colors.red[500],
        },
        {
          id: 'twoFactor',
          title: 'Two-Factor Authentication',
          subtitle: 'Add an extra layer of security',
          icon: 'shield-checkmark',
          type: 'navigation',
          badge: security?.twoFactorEnabled ? 'Enabled' : undefined,
          color: Colors.orange[500],
        },
        {
          id: 'privacy',
          title: 'Privacy Settings',
          subtitle: 'Control your data sharing',
          icon: 'lock-closed',
          type: 'navigation',
          color: Colors.gray[600],
        },
        {
          id: 'dataRetention',
          title: 'Data Retention',
          subtitle: 'Manage how long data is stored',
          icon: 'time',
          type: 'navigation',
          value: '30 days',
          color: Colors.indigo[500],
        },
      ],
    },
    {
      title: 'Notifications',
      items: [
        {
          id: 'pushNotifications',
          title: 'Push Notifications',
          subtitle: 'Receive notifications on this device',
          icon: 'notifications',
          type: 'toggle',
          value: notifications?.pushEnabled ?? true,
          onToggle: (value) => handleNotificationToggle('pushEnabled', value),
          color: Colors.blue[500],
        },
        {
          id: 'emailNotifications',
          title: 'Email Notifications',
          subtitle: 'Receive updates via email',
          icon: 'mail',
          type: 'toggle',
          value: notifications?.emailEnabled ?? true,
          onToggle: (value) => handleNotificationToggle('emailEnabled', value),
          color: Colors.cyan[500],
        },
        {
          id: 'taskCompletions',
          title: 'Task Completions',
          subtitle: 'Notify when agents complete tasks',
          icon: 'checkmark-circle',
          type: 'toggle',
          value: notifications?.taskCompletions ?? true,
          onToggle: (value) => handleNotificationToggle('taskCompletions', value),
          color: Colors.green[500],
        },
        {
          id: 'systemUpdates',
          title: 'System Updates',
          subtitle: 'Important app and system updates',
          icon: 'download',
          type: 'toggle',
          value: notifications?.systemUpdates ?? true,
          onToggle: (value) => handleNotificationToggle('systemUpdates', value),
          color: Colors.purple[500],
        },
      ],
    },
    {
      title: 'Support & About',
      items: [
        {
          id: 'help',
          title: 'Help Center',
          subtitle: 'Get help and support',
          icon: 'help-circle',
          type: 'navigation',
          onPress: () => Linking.openURL('https://help.aideon.ai'),
          color: Colors.blue[500],
        },
        {
          id: 'feedback',
          title: 'Send Feedback',
          subtitle: 'Help us improve the app',
          icon: 'chatbubble',
          type: 'navigation',
          color: Colors.green[500],
        },
        {
          id: 'version',
          title: 'Version',
          icon: 'information-circle',
          type: 'info',
          value: '1.0.0 (Build 1)',
          color: Colors.gray[500],
        },
        {
          id: 'terms',
          title: 'Terms of Service',
          icon: 'document-text',
          type: 'navigation',
          onPress: () => Linking.openURL('https://aideon.ai/terms'),
          color: Colors.gray[600],
        },
        {
          id: 'privacy-policy',
          title: 'Privacy Policy',
          icon: 'shield',
          type: 'navigation',
          onPress: () => Linking.openURL('https://aideon.ai/privacy'),
          color: Colors.gray[600],
        },
      ],
    },
    {
      title: 'Data & Storage',
      items: [
        {
          id: 'exportData',
          title: 'Export Data',
          subtitle: 'Download your data',
          icon: 'download-outline',
          type: 'action',
          onPress: handleExportData,
          color: Colors.blue[500],
        },
        {
          id: 'clearCache',
          title: 'Clear Cache',
          subtitle: 'Free up storage space',
          icon: 'trash-outline',
          type: 'action',
          onPress: handleClearCache,
          color: Colors.orange[500],
        },
      ],
    },
    {
      title: 'Account Actions',
      items: [
        {
          id: 'logout',
          title: 'Sign Out',
          icon: 'log-out',
          type: 'action',
          onPress: handleLogout,
          color: Colors.warning,
        },
        {
          id: 'deleteAccount',
          title: 'Delete Account',
          subtitle: 'Permanently delete your account',
          icon: 'trash',
          type: 'action',
          onPress: handleDeleteAccount,
          color: Colors.error,
        },
      ],
    },
  ];

  return (
    <SafeAreaView style={styles.container}>
      <LinearGradient
        colors={[Colors.primary[50], '#ffffff']}
        style={StyleSheet.absoluteFill}
      />

      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Settings</Text>
      </View>

      {/* User Profile Card */}
      <TouchableOpacity 
        style={styles.profileCard}
        onPress={() => setShowProfileModal(true)}
      >
        <Card style={styles.profileCardContent}>
          <View style={styles.profileInfo}>
            <View style={styles.profileAvatar}>
              <Ionicons name="person" size={32} color={Colors.gray[400]} />
            </View>
            <View style={styles.profileDetails}>
              <Text style={styles.profileName}>{user?.name || 'User Name'}</Text>
              <Text style={styles.profileEmail}>{user?.email || 'user@example.com'}</Text>
              <Text style={styles.profilePlan}>Pro Plan • Active</Text>
            </View>
          </View>
          <Ionicons name="chevron-forward" size={20} color={Colors.gray[400]} />
        </Card>
      </TouchableOpacity>

      {/* Settings Sections */}
      <ScrollView 
        style={styles.settingsList}
        contentContainerStyle={styles.settingsContent}
        showsVerticalScrollIndicator={false}
      >
        {sections.map((section, sectionIndex) => (
          <View key={sectionIndex} style={styles.settingSection}>
            <Text style={styles.sectionTitle}>{section.title}</Text>
            <Card style={styles.sectionCard}>
              {section.items.map((item, itemIndex) => (
                <SettingRow
                  key={item.id}
                  item={item}
                  isLast={itemIndex === section.items.length - 1}
                />
              ))}
            </Card>
          </View>
        ))}
      </ScrollView>

      {/* Profile Modal */}
      <ProfileModal
        visible={showProfileModal}
        onClose={() => setShowProfileModal(false)}
        onSave={handleProfileUpdate}
      />

      {/* Theme Modal */}
      <ThemeModal
        visible={showThemeModal}
        currentTheme={preferences?.theme || 'auto'}
        onClose={() => setShowThemeModal(false)}
        onSelect={handleThemeChange}
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
    paddingHorizontal: Spacing.lg,
    paddingVertical: Spacing.lg,
  },
  headerTitle: {
    fontSize: Typography.fontSize['2xl'],
    fontWeight: Typography.fontWeight.bold,
    color: Colors.light.text.primary,
    fontFamily: Typography.fontFamily.primary,
  },
  profileCard: {
    marginHorizontal: Spacing.lg,
    marginBottom: Spacing.lg,
  },
  profileCardContent: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: Spacing.lg,
  },
  profileInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  profileAvatar: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: Colors.gray[100],
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: Spacing.md,
  },
  profileDetails: {
    flex: 1,
  },
  profileName: {
    fontSize: Typography.fontSize.lg,
    fontWeight: Typography.fontWeight.semibold,
    color: Colors.light.text.primary,
    fontFamily: Typography.fontFamily.primary,
    marginBottom: 2,
  },
  profileEmail: {
    fontSize: Typography.fontSize.sm,
    color: Colors.light.text.secondary,
    fontFamily: Typography.fontFamily.primary,
    marginBottom: 2,
  },
  profilePlan: {
    fontSize: Typography.fontSize.xs,
    color: Colors.primary[500],
    fontFamily: Typography.fontFamily.primary,
    fontWeight: Typography.fontWeight.medium,
  },
  settingsList: {
    flex: 1,
  },
  settingsContent: {
    paddingHorizontal: Spacing.lg,
    paddingBottom: Spacing.xl,
  },
  settingSection: {
    marginBottom: Spacing.lg,
  },
  sectionTitle: {
    fontSize: Typography.fontSize.sm,
    fontWeight: Typography.fontWeight.semibold,
    color: Colors.light.text.secondary,
    fontFamily: Typography.fontFamily.primary,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
    marginBottom: Spacing.sm,
    paddingHorizontal: Spacing.xs,
  },
  sectionCard: {
    padding: 0,
    overflow: 'hidden',
  },
  settingRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: Spacing.lg,
    paddingVertical: Spacing.md,
  },
  settingRowBorder: {
    borderBottomWidth: 1,
    borderBottomColor: Colors.gray[100],
  },
  settingIcon: {
    width: 36,
    height: 36,
    borderRadius: 18,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: Spacing.md,
  },
  settingContent: {
    flex: 1,
  },
  settingTitle: {
    fontSize: Typography.fontSize.base,
    fontWeight: Typography.fontWeight.medium,
    color: Colors.light.text.primary,
    fontFamily: Typography.fontFamily.primary,
    marginBottom: 2,
  },
  settingSubtitle: {
    fontSize: Typography.fontSize.sm,
    color: Colors.light.text.secondary,
    fontFamily: Typography.fontFamily.primary,
  },
  navigationRight: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  settingValue: {
    fontSize: Typography.fontSize.sm,
    color: Colors.gray[500],
    fontFamily: Typography.fontFamily.primary,
    marginRight: Spacing.sm,
  },
  badge: {
    backgroundColor: Colors.primary[500],
    borderRadius: BorderRadius.sm,
    paddingHorizontal: Spacing.xs,
    paddingVertical: 2,
    marginRight: Spacing.sm,
  },
  badgeText: {
    fontSize: Typography.fontSize.xs,
    color: '#ffffff',
    fontFamily: Typography.fontFamily.primary,
    fontWeight: Typography.fontWeight.medium,
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
  avatarSection: {
    alignItems: 'center',
    paddingVertical: Spacing.xl,
    marginBottom: Spacing.lg,
  },
  avatarContainer: {
    position: 'relative',
    marginBottom: Spacing.sm,
  },
  avatar: {
    width: 100,
    height: 100,
    borderRadius: 50,
    backgroundColor: Colors.gray[100],
    alignItems: 'center',
    justifyContent: 'center',
  },
  avatarEdit: {
    position: 'absolute',
    bottom: 0,
    right: 0,
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: Colors.primary[500],
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 3,
    borderColor: '#ffffff',
  },
  avatarText: {
    fontSize: Typography.fontSize.sm,
    color: Colors.light.text.secondary,
    fontFamily: Typography.fontFamily.primary,
  },
  themeOption: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: Spacing.lg,
    paddingVertical: Spacing.lg,
    borderBottomWidth: 1,
    borderBottomColor: Colors.gray[100],
  },
  themeOptionSelected: {
    backgroundColor: Colors.primary[50],
  },
  themeIcon: {
    width: 48,
    height: 48,
    borderRadius: 24,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: Spacing.md,
  },
  themeName: {
    fontSize: Typography.fontSize.base,
    fontWeight: Typography.fontWeight.medium,
    color: Colors.light.text.primary,
    fontFamily: Typography.fontFamily.primary,
    flex: 1,
  },
});

export default SettingsScreen;

