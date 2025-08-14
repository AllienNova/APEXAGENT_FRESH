import { configureStore, combineReducers } from '@reduxjs/toolkit';
import { persistStore, persistReducer } from 'redux-persist';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { createLogger } from 'redux-logger';

// Slices
import authSlice from './slices/authSlice';
import chatSlice from './slices/chatSlice';
import dashboardSlice from './slices/dashboardSlice';
import agentsSlice from './slices/agentsSlice';
import filesSlice from './slices/filesSlice';
import projectsSlice from './slices/projectsSlice';
import settingsSlice from './slices/settingsSlice';
import uiSlice from './slices/uiSlice';

// Middleware
import { apiMiddleware } from './middleware/apiMiddleware';
import { offlineMiddleware } from './middleware/offlineMiddleware';
import { analyticsMiddleware } from './middleware/analyticsMiddleware';

const rootReducer = combineReducers({
  auth: authSlice,
  chat: chatSlice,
  dashboard: dashboardSlice,
  agents: agentsSlice,
  files: filesSlice,
  projects: projectsSlice,
  settings: settingsSlice,
  ui: uiSlice,
});

const persistConfig = {
  key: 'root',
  storage: AsyncStorage,
  whitelist: ['auth', 'settings', 'ui'], // Only persist these slices
  blacklist: ['chat', 'dashboard'], // Don't persist real-time data
};

const persistedReducer = persistReducer(persistConfig, rootReducer);

const middleware = [
  apiMiddleware,
  offlineMiddleware,
  analyticsMiddleware,
];

// Add logger in development
if (__DEV__) {
  const logger = createLogger({
    collapsed: true,
    duration: true,
    timestamp: true,
  });
  middleware.push(logger);
}

export const store = configureStore({
  reducer: persistedReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST', 'persist/REHYDRATE'],
      },
    }).concat(middleware),
  devTools: __DEV__,
});

export const persistor = persistStore(store);

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

