/**
 * ApexAgent Frontend Application
 * 
 * Main React application component providing comprehensive AI system interface
 * with multi-model chat, project management, and real-time capabilities.
 */

import React, { Suspense, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Provider } from 'react-redux';
import { PersistGate } from 'redux-persist/integration/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline, GlobalStyles } from '@mui/material';
import { HelmetProvider } from 'react-helmet-async';
import { ToastContainer } from 'react-toastify';
import { ErrorBoundary } from 'react-error-boundary';

// Redux store
import { store, persistor } from './store';

// Contexts
import { AuthProvider } from './contexts/AuthContext';
import { WebSocketProvider } from './contexts/WebSocketContext';
import { SettingsProvider } from './contexts/SettingsContext';

// Components
import LoadingScreen from './components/common/LoadingScreen';
import ErrorFallback from './components/common/ErrorFallback';
import ProtectedRoute from './components/auth/ProtectedRoute';
import Layout from './components/layout/Layout';

// Pages (lazy loaded)
const Dashboard = React.lazy(() => import('./pages/Dashboard'));
const Chat = React.lazy(() => import('./pages/Chat'));
const Projects = React.lazy(() => import('./pages/Projects'));
const Agents = React.lazy(() => import('./pages/Agents'));
const Analytics = React.lazy(() => import('./pages/Analytics'));
const Settings = React.lazy(() => import('./pages/Settings'));
const Login = React.lazy(() => import('./pages/auth/Login'));
const Register = React.lazy(() => import('./pages/auth/Register'));
const ForgotPassword = React.lazy(() => import('./pages/auth/ForgotPassword'));
const Profile = React.lazy(() => import('./pages/Profile'));
const Models = React.lazy(() => import('./pages/Models'));
const Files = React.lazy(() => import('./pages/Files'));
const Artifacts = React.lazy(() => import('./pages/Artifacts'));
const Monitoring = React.lazy(() => import('./pages/Monitoring'));

// Styles
import 'react-toastify/dist/ReactToastify.css';
import './styles/global.css';

// Create React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 3,
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
      refetchOnWindowFocus: false,
    },
    mutations: {
      retry: 1,
    },
  },
});

// Create Material-UI theme
const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#6366f1', // Indigo
      light: '#818cf8',
      dark: '#4338ca',
    },
    secondary: {
      main: '#f59e0b', // Amber
      light: '#fbbf24',
      dark: '#d97706',
    },
    background: {
      default: '#0f0f23',
      paper: '#1a1a2e',
    },
    text: {
      primary: '#ffffff',
      secondary: '#a1a1aa',
    },
    error: {
      main: '#ef4444',
    },
    warning: {
      main: '#f59e0b',
    },
    info: {
      main: '#3b82f6',
    },
    success: {
      main: '#10b981',
    },
  },
  typography: {
    fontFamily: [
      'Inter',
      '-apple-system',
      'BlinkMacSystemFont',
      'Segoe UI',
      'Roboto',
      'Oxygen',
      'Ubuntu',
      'Cantarell',
      'sans-serif',
    ].join(','),
    h1: {
      fontWeight: 700,
      fontSize: '2.5rem',
    },
    h2: {
      fontWeight: 600,
      fontSize: '2rem',
    },
    h3: {
      fontWeight: 600,
      fontSize: '1.5rem',
    },
    h4: {
      fontWeight: 600,
      fontSize: '1.25rem',
    },
    h5: {
      fontWeight: 500,
      fontSize: '1.125rem',
    },
    h6: {
      fontWeight: 500,
      fontSize: '1rem',
    },
    body1: {
      fontSize: '0.875rem',
      lineHeight: 1.6,
    },
    body2: {
      fontSize: '0.75rem',
      lineHeight: 1.5,
    },
  },
  shape: {
    borderRadius: 8,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 500,
          borderRadius: 8,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
          border: '1px solid rgba(255, 255, 255, 0.1)',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
        },
      },
    },
  },
});

// Global styles
const globalStyles = (
  <GlobalStyles
    styles={{
      '*': {
        boxSizing: 'border-box',
      },
      html: {
        height: '100%',
        width: '100%',
      },
      body: {
        height: '100%',
        width: '100%',
        margin: 0,
        padding: 0,
        fontFamily: theme.typography.fontFamily,
        backgroundColor: theme.palette.background.default,
        color: theme.palette.text.primary,
      },
      '#root': {
        height: '100%',
        width: '100%',
      },
      // Custom scrollbar
      '::-webkit-scrollbar': {
        width: '8px',
        height: '8px',
      },
      '::-webkit-scrollbar-track': {
        background: 'rgba(255, 255, 255, 0.05)',
        borderRadius: '4px',
      },
      '::-webkit-scrollbar-thumb': {
        background: 'rgba(255, 255, 255, 0.2)',
        borderRadius: '4px',
        '&:hover': {
          background: 'rgba(255, 255, 255, 0.3)',
        },
      },
      // Selection styles
      '::selection': {
        backgroundColor: theme.palette.primary.main,
        color: theme.palette.primary.contrastText,
      },
      // Focus styles
      '*:focus-visible': {
        outline: `2px solid ${theme.palette.primary.main}`,
        outlineOffset: '2px',
      },
    }}
  />
);

function App() {
  useEffect(() => {
    // Register service worker for PWA
    if ('serviceWorker' in navigator && process.env.NODE_ENV === 'production') {
      navigator.serviceWorker.register('/sw.js')
        .then((registration) => {
          console.log('SW registered: ', registration);
        })
        .catch((registrationError) => {
          console.log('SW registration failed: ', registrationError);
        });
    }

    // Set up global error handling
    window.addEventListener('unhandledrejection', (event) => {
      console.error('Unhandled promise rejection:', event.reason);
      // You could send this to an error reporting service
    });

    window.addEventListener('error', (event) => {
      console.error('Global error:', event.error);
      // You could send this to an error reporting service
    });

    return () => {
      window.removeEventListener('unhandledrejection', () => {});
      window.removeEventListener('error', () => {});
    };
  }, []);

  return (
    <ErrorBoundary
      FallbackComponent={ErrorFallback}
      onError={(error, errorInfo) => {
        console.error('App Error Boundary:', error, errorInfo);
        // Send to error reporting service
      }}
    >
      <HelmetProvider>
        <Provider store={store}>
          <PersistGate loading={<LoadingScreen />} persistor={persistor}>
            <QueryClientProvider client={queryClient}>
              <ThemeProvider theme={theme}>
                <CssBaseline />
                {globalStyles}
                <AuthProvider>
                  <SettingsProvider>
                    <WebSocketProvider>
                      <Router>
                        <div className="app">
                          <Suspense fallback={<LoadingScreen />}>
                            <Routes>
                              {/* Public routes */}
                              <Route path="/login" element={<Login />} />
                              <Route path="/register" element={<Register />} />
                              <Route path="/forgot-password" element={<ForgotPassword />} />
                              
                              {/* Protected routes */}
                              <Route path="/" element={
                                <ProtectedRoute>
                                  <Layout />
                                </ProtectedRoute>
                              }>
                                <Route index element={<Navigate to="/dashboard" replace />} />
                                <Route path="dashboard" element={<Dashboard />} />
                                <Route path="chat" element={<Chat />} />
                                <Route path="chat/:conversationId" element={<Chat />} />
                                <Route path="projects" element={<Projects />} />
                                <Route path="projects/:projectId" element={<Projects />} />
                                <Route path="agents" element={<Agents />} />
                                <Route path="models" element={<Models />} />
                                <Route path="files" element={<Files />} />
                                <Route path="artifacts" element={<Artifacts />} />
                                <Route path="analytics" element={<Analytics />} />
                                <Route path="monitoring" element={<Monitoring />} />
                                <Route path="settings" element={<Settings />} />
                                <Route path="profile" element={<Profile />} />
                              </Route>

                              {/* Catch all route */}
                              <Route path="*" element={<Navigate to="/dashboard" replace />} />
                            </Routes>
                          </Suspense>
                        </div>
                      </Router>
                    </WebSocketProvider>
                  </SettingsProvider>
                </AuthProvider>
              </ThemeProvider>
              
              {/* React Query DevTools (only in development) */}
              {process.env.NODE_ENV === 'development' && (
                <ReactQueryDevtools initialIsOpen={false} />
              )}
            </QueryClientProvider>
          </PersistGate>
        </Provider>

        {/* Toast notifications */}
        <ToastContainer
          position="top-right"
          autoClose={5000}
          hideProgressBar={false}
          newestOnTop
          closeOnClick
          rtl={false}
          pauseOnFocusLoss
          draggable
          pauseOnHover
          theme="dark"
          toastStyle={{
            backgroundColor: theme.palette.background.paper,
            color: theme.palette.text.primary,
            border: `1px solid ${theme.palette.divider}`,
          }}
        />
      </HelmetProvider>
    </ErrorBoundary>
  );
}

export default App;

