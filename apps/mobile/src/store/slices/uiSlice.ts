import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { UIState, ToastMessage } from '../../types';

const initialState: UIState = {
  theme: 'light',
  isOnline: true,
  activeTab: 'Dashboard',
  modals: {},
  toasts: [],
};

const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    setTheme: (state, action: PayloadAction<'light' | 'dark'>) => {
      state.theme = action.payload;
    },
    setOnlineStatus: (state, action: PayloadAction<boolean>) => {
      state.isOnline = action.payload;
    },
    setActiveTab: (state, action: PayloadAction<string>) => {
      state.activeTab = action.payload;
    },
    openModal: (state, action: PayloadAction<string>) => {
      state.modals[action.payload] = true;
    },
    closeModal: (state, action: PayloadAction<string>) => {
      state.modals[action.payload] = false;
    },
    toggleModal: (state, action: PayloadAction<string>) => {
      state.modals[action.payload] = !state.modals[action.payload];
    },
    showToast: (state, action: PayloadAction<Omit<ToastMessage, 'id'>>) => {
      const toast: ToastMessage = {
        ...action.payload,
        id: Date.now().toString(),
      };
      state.toasts.push(toast);
    },
    hideToast: (state, action: PayloadAction<string>) => {
      state.toasts = state.toasts.filter(toast => toast.id !== action.payload);
    },
    clearAllToasts: (state) => {
      state.toasts = [];
    },
  },
});

export const {
  setTheme,
  setOnlineStatus,
  setActiveTab,
  openModal,
  closeModal,
  toggleModal,
  showToast,
  hideToast,
  clearAllToasts,
} = uiSlice.actions;

export default uiSlice.reducer;

