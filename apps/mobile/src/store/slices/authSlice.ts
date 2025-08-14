import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { AuthState, User, LoginCredentials, RegisterData } from '../../types';
import { apiService } from '../../services/api.service';
import { biometricService } from '../../services/biometric.service';

const initialState: AuthState = {
  isAuthenticated: false,
  user: null,
  token: null,
  refreshToken: null,
  isLoading: false,
  error: null,
  biometricAvailable: false,
  biometricEnabled: false,
};

// Async thunks
export const loginUser = createAsyncThunk(
  'auth/loginUser',
  async (credentials: LoginCredentials, { rejectWithValue }) => {
    try {
      const response = await apiService.login(credentials.email, credentials.password);
      
      if (!response.success || !response.data) {
        throw new Error(response.error || 'Login failed');
      }

      // Store token
      await apiService.setAuthToken(response.data.token);

      // Enable biometric if requested and available
      if (credentials.biometric && await biometricService.isAvailable()) {
        await biometricService.enableBiometric(credentials.email, credentials.password);
      }

      return {
        user: response.data.user,
        token: response.data.token,
        refreshToken: response.data.refreshToken,
      };
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : 'Login failed');
    }
  }
);

export const registerUser = createAsyncThunk(
  'auth/registerUser',
  async (userData: RegisterData, { rejectWithValue }) => {
    try {
      const response = await apiService.register({
        email: userData.email,
        password: userData.password,
        name: userData.name,
      });

      if (!response.success || !response.data) {
        throw new Error(response.error || 'Registration failed');
      }

      // Store token
      await apiService.setAuthToken(response.data.token);

      return {
        user: response.data.user,
        token: response.data.token,
        refreshToken: response.data.refreshToken,
      };
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : 'Registration failed');
    }
  }
);

export const biometricLogin = createAsyncThunk(
  'auth/biometricLogin',
  async (_, { rejectWithValue }) => {
    try {
      const credentials = await biometricService.authenticate();
      
      if (!credentials) {
        throw new Error('Biometric authentication failed');
      }

      const response = await apiService.login(credentials.email, credentials.password);
      
      if (!response.success || !response.data) {
        throw new Error(response.error || 'Login failed');
      }

      await apiService.setAuthToken(response.data.token);

      return {
        user: response.data.user,
        token: response.data.token,
        refreshToken: response.data.refreshToken,
      };
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : 'Biometric login failed');
    }
  }
);

export const refreshAuthToken = createAsyncThunk(
  'auth/refreshToken',
  async (_, { rejectWithValue }) => {
    try {
      const response = await apiService.refreshToken();
      
      if (!response.success || !response.data) {
        throw new Error(response.error || 'Token refresh failed');
      }

      await apiService.setAuthToken(response.data.token);

      return {
        token: response.data.token,
      };
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : 'Token refresh failed');
    }
  }
);

export const logoutUser = createAsyncThunk(
  'auth/logoutUser',
  async (_, { rejectWithValue }) => {
    try {
      await apiService.clearAuthToken();
      await biometricService.clearBiometric();
      return null;
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : 'Logout failed');
    }
  }
);

export const checkBiometricAvailability = createAsyncThunk(
  'auth/checkBiometricAvailability',
  async () => {
    const isAvailable = await biometricService.isAvailable();
    const isEnabled = await biometricService.isBiometricEnabled();
    
    return {
      biometricAvailable: isAvailable,
      biometricEnabled: isEnabled,
    };
  }
);

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    updateUser: (state, action: PayloadAction<Partial<User>>) => {
      if (state.user) {
        state.user = { ...state.user, ...action.payload };
      }
    },
    setBiometricEnabled: (state, action: PayloadAction<boolean>) => {
      state.biometricEnabled = action.payload;
    },
  },
  extraReducers: (builder) => {
    // Login
    builder
      .addCase(loginUser.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(loginUser.fulfilled, (state, action) => {
        state.isLoading = false;
        state.isAuthenticated = true;
        state.user = action.payload.user;
        state.token = action.payload.token;
        state.refreshToken = action.payload.refreshToken;
        state.error = null;
      })
      .addCase(loginUser.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });

    // Register
    builder
      .addCase(registerUser.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(registerUser.fulfilled, (state, action) => {
        state.isLoading = false;
        state.isAuthenticated = true;
        state.user = action.payload.user;
        state.token = action.payload.token;
        state.refreshToken = action.payload.refreshToken;
        state.error = null;
      })
      .addCase(registerUser.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });

    // Biometric Login
    builder
      .addCase(biometricLogin.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(biometricLogin.fulfilled, (state, action) => {
        state.isLoading = false;
        state.isAuthenticated = true;
        state.user = action.payload.user;
        state.token = action.payload.token;
        state.refreshToken = action.payload.refreshToken;
        state.error = null;
      })
      .addCase(biometricLogin.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });

    // Refresh Token
    builder
      .addCase(refreshAuthToken.fulfilled, (state, action) => {
        state.token = action.payload.token;
      })
      .addCase(refreshAuthToken.rejected, (state) => {
        state.isAuthenticated = false;
        state.user = null;
        state.token = null;
        state.refreshToken = null;
      });

    // Logout
    builder
      .addCase(logoutUser.fulfilled, (state) => {
        state.isAuthenticated = false;
        state.user = null;
        state.token = null;
        state.refreshToken = null;
        state.error = null;
      });

    // Biometric Availability
    builder
      .addCase(checkBiometricAvailability.fulfilled, (state, action) => {
        state.biometricAvailable = action.payload.biometricAvailable;
        state.biometricEnabled = action.payload.biometricEnabled;
      });
  },
});

export const { clearError, updateUser, setBiometricEnabled } = authSlice.actions;
export default authSlice.reducer;

