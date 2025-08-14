import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { DashboardState, DashboardData } from '../../types';
import { apiService } from '../../services/api.service';

const initialState: DashboardState = {
  data: null,
  isLoading: false,
  error: null,
  lastUpdated: null,
};

export const loadDashboardData = createAsyncThunk(
  'dashboard/loadDashboardData',
  async (_, { rejectWithValue }) => {
    try {
      const data = await apiService.getDashboardData();
      return data;
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : 'Failed to load dashboard data');
    }
  }
);

export const refreshDashboardData = createAsyncThunk(
  'dashboard/refreshDashboardData',
  async (_, { rejectWithValue }) => {
    try {
      const data = await apiService.getDashboardData();
      return data;
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : 'Failed to refresh dashboard data');
    }
  }
);

const dashboardSlice = createSlice({
  name: 'dashboard',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    // Load Dashboard Data
    builder
      .addCase(loadDashboardData.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(loadDashboardData.fulfilled, (state, action) => {
        state.isLoading = false;
        state.data = action.payload;
        state.lastUpdated = new Date().toISOString();
      })
      .addCase(loadDashboardData.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });

    // Refresh Dashboard Data
    builder
      .addCase(refreshDashboardData.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(refreshDashboardData.fulfilled, (state, action) => {
        state.isLoading = false;
        state.data = action.payload;
        state.lastUpdated = new Date().toISOString();
      })
      .addCase(refreshDashboardData.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });
  },
});

export const { clearError } = dashboardSlice.actions;
export default dashboardSlice.reducer;

