import React, { useEffect } from 'react';
import { StatusBar, Platform } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { Provider } from 'react-redux';
import { PersistGate } from 'redux-persist/integration/react';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import SplashScreen from 'react-native-splash-screen';
import Toast from 'react-native-toast-message';

// Store
import { store, persistor } from './src/store';

// Navigation
import { RootStackParamList } from './src/types';
import { navigationRef } from './src/navigation/NavigationService';

// Screens
import SplashScreenComponent from './src/screens/SplashScreen';
import AuthNavigator from './src/navigation/AuthNavigator';
import MainNavigator from './src/navigation/MainNavigator';

// Components
import LoadingScreen from './src/components/common/LoadingScreen';
import ErrorBoundary from './src/components/common/ErrorBoundary';

// Services
import { initializeApp } from './src/services/AppInitializationService';

const Stack = createStackNavigator<RootStackParamList>();

const App: React.FC = () => {
  useEffect(() => {
    const initApp = async () => {
      try {
        await initializeApp();
      } catch (error) {
        console.error('App initialization failed:', error);
      } finally {
        if (Platform.OS === 'android') {
          SplashScreen.hide();
        }
      }
    };

    initApp();
  }, []);

  return (
    <ErrorBoundary>
      <Provider store={store}>
        <PersistGate loading={<LoadingScreen />} persistor={persistor}>
          <SafeAreaProvider>
            <NavigationContainer ref={navigationRef}>
              <StatusBar
                barStyle="dark-content"
                backgroundColor="transparent"
                translucent
              />
              <Stack.Navigator
                screenOptions={{
                  headerShown: false,
                  gestureEnabled: true,
                  cardStyleInterpolator: ({ current, layouts }) => {
                    return {
                      cardStyle: {
                        transform: [
                          {
                            translateX: current.progress.interpolate({
                              inputRange: [0, 1],
                              outputRange: [layouts.screen.width, 0],
                            }),
                          },
                        ],
                      },
                    };
                  },
                }}
              >
                <Stack.Screen name="Splash" component={SplashScreenComponent} />
                <Stack.Screen name="Auth" component={AuthNavigator} />
                <Stack.Screen name="Main" component={MainNavigator} />
              </Stack.Navigator>
              <Toast />
            </NavigationContainer>
          </SafeAreaProvider>
        </PersistGate>
      </Provider>
    </ErrorBoundary>
  );
};

export default App;

