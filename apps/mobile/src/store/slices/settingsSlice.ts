import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { SettingsState, AppSettings, UserPreferences } from '../../types';
import { apiService } from '../../services/api.service';

const initialState: SettingsState = {
  app: {
    theme: {
      mode: 'auto',
      primaryColor: '#007AFF',
      accentColor: '#FF3B30',
      fontSize: 'medium',
    },
    notifications: {
      push: true,
      email: true,
      taskCompletion: true,
      systemUpdates: true,
      securityAlerts: true,
    },
    privacy: {
      dataCollection: true,
      analytics: true,
      crashReporting: true,
      locationTracking: false,
      biometricData: true,
    },
    performance: {
      cacheSize: 100, // MB
      offlineMode: true,
      backgroundSync: true,
      imageQuality: 'medium',
      videoQuality: 'medium',
    },
    accessibility: {
      screenReader: false,
      highContrast: false,
      largeText: false,
      reduceMotion: false,
      voiceControl: false,
    },
  },
  user: {
    theme: 'auto',
    language: 'en',
    notifications: {
      push: true,
      email: true,
      taskCompletion: true,
      systemUpdates: true,
      securityAlerts: true,
    },
    defaultModel: 'gpt-4o',
    voiceEnabled: true,
    biometricEnabled: false,
    autoSave: true,
    offlineMode: true,
  },
  isLoading: false,
  error: null,
};

export const loadUserSettings = createAsyncThunk(
  'settings/loadUserSettings',
  async (_, { rejectWithValue }) => {
    try {
      const settings = await apiService.getUserSettings();
      return settings;
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : 'Failed to load settings');
    }
  }
);

export const updateUserSettings = createAsyncThunk(
  'settings/updateUserSettings',
  async (settings: Partial<UserPreferences>, { rejectWithValue }) => {
    try {
      await apiService.updateUserSettings(settings);
      return settings;
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : 'Failed to update settings');
    }
  }
);

const settingsSlice = createSlice({
  name: 'settings',
  initialState,
  reducers: {
    updateAppSettings: (state, action: PayloadAction<Partial<AppSettings>>) => {
      state.app = { ...state.app, ...action.payload };
    },
    updateThemeSettings: (state, action: PayloadAction<Partial<AppSettings['theme']>>) => {
      state.app.theme = { ...state.app.theme, ...action.payload };
    },
    updateNotificationSettings: (state, action: PayloadAction<Partial<AppSettings['notifications']>>) => {
      state.app.notifications = { ...state.app.notifications, ...action.payload };
      state.user.notifications = { ...state.user.notifications, ...action.payload };
    },
    updatePrivacySettings: (state, action: PayloadAction<Partial<AppSettings['privacy']>>) => {
      state.app.privacy = { ...state.app.privacy, ...action.payload };
    },
    updatePerformanceSettings: (state, action: PayloadAction<Partial<AppSettings['performance']>>) => {
      state.app.performance = { ...state.app.performance, ...action.payload };
    },
    updateAccessibilitySettings: (state, action: PayloadAction<Partial<AppSettings['accessibility']>>) => {
      state.app.accessibility = { ...state.app.accessibility, ...action.payload };
    },
    updateUserPreferences: (state, action: PayloadAction<Partial<UserPreferences>>) => {
      state.user = { ...state.user, ...action.payload };
    },
    setDefaultModel: (state, action: PayloadAction<string>) => {
      state.user.defaultModel = action.payload;
    },
    toggleVoiceEnabled: (state) => {
      state.user.voiceEnabled = !state.user.voiceEnabled;
    },
    toggleBiometricEnabled: (state) => {
      state.user.biometricEnabled = !state.user.biometricEnabled;
    },
    toggleAutoSave: (state) => {
      state.user.autoSave = !state.user.autoSave;
    },
    toggleOfflineMode: (state) => {
      state.user.offlineMode = !state.user.offlineMode;
      state.app.performance.offlineMode = !state.app.performance.offlineMode;
    },
    setLanguage: (state, action: PayloadAction<string>) => {
      state.user.language = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
    resetToDefaults: (state) => {
      state.app = initialState.app;
      state.user = initialState.user;
    },
  },
  extraReducers: (builder) => {
    // Load User Settings
    builder
      .addCase(loadUserSettings.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(loadUserSettings.fulfilled, (state, action) => {
        state.isLoading = false;
        state.user = { ...state.user, ...action.payload };
      })
      .addCase(loadUserSettings.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });

    // Update User Settings
    builder
      .addCase(updateUserSettings.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(updateUserSettings.fulfilled, (state, action) => {
        state.isLoading = false;
        state.user = { ...state.user, ...action.payload };
      })
      .addCase(updateUserSettings.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });
  },
});

export const {
  updateAppSettings,
  updateThemeSettings,
  updateNotificationSettings,
  updatePrivacySettings,
  updatePerformanceSettings,
  updateAccessibilitySettings,
  updateUserPreferences,
  setDefaultModel,
  toggleVoiceEnabled,
  toggleBiometricEnabled,
  toggleAutoSave,
  toggleOfflineMode,
  setLanguage,
  clearError,
  resetToDefaults,
} = settingsSlice.actions;

export default settingsSlice.reducer;

