import React, { useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Animated,
  Dimensions,
  StatusBar,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useNavigation } from '@react-navigation/native';
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '../store';
import { checkBiometricAvailability } from '../store/slices/authSlice';
import { Colors, Typography, Spacing } from '../constants/theme';

const { width, height } = Dimensions.get('window');

const SplashScreen: React.FC = () => {
  const navigation = useNavigation();
  const dispatch = useDispatch();
  const { isAuthenticated } = useSelector((state: RootState) => state.auth);
  
  const fadeAnim = useRef(new Animated.Value(0)).current;
  const scaleAnim = useRef(new Animated.Value(0.8)).current;
  const slideAnim = useRef(new Animated.Value(50)).current;
  const logoRotateAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    // Start animations
    Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 1000,
        useNativeDriver: true,
      }),
      Animated.spring(scaleAnim, {
        toValue: 1,
        tension: 50,
        friction: 7,
        useNativeDriver: true,
      }),
      Animated.timing(slideAnim, {
        toValue: 0,
        duration: 800,
        delay: 300,
        useNativeDriver: true,
      }),
      Animated.loop(
        Animated.timing(logoRotateAnim, {
          toValue: 1,
          duration: 3000,
          useNativeDriver: true,
        })
      ),
    ]).start();

    // Initialize app
    const initializeApp = async () => {
      try {
        // Check biometric availability
        dispatch(checkBiometricAvailability());
        
        // Simulate app initialization
        await new Promise(resolve => setTimeout(resolve, 2500));
        
        // Navigate based on auth state
        if (isAuthenticated) {
          navigation.navigate('Main' as never);
        } else {
          navigation.navigate('Auth' as never);
        }
      } catch (error) {
        console.error('App initialization failed:', error);
        navigation.navigate('Auth' as never);
      }
    };

    initializeApp();
  }, [dispatch, navigation, isAuthenticated]);

  const logoRotate = logoRotateAnim.interpolate({
    inputRange: [0, 1],
    outputRange: ['0deg', '360deg'],
  });

  return (
    <View style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="transparent" translucent />
      
      <LinearGradient
        colors={Colors.gradient.primary}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
        style={StyleSheet.absoluteFill}
      />
      
      {/* Animated background elements */}
      <View style={styles.backgroundElements}>
        {[...Array(6)].map((_, index) => (
          <Animated.View
            key={index}
            style={[
              styles.floatingElement,
              {
                opacity: fadeAnim,
                transform: [
                  {
                    translateY: slideAnim.interpolate({
                      inputRange: [0, 50],
                      outputRange: [0, 50 * (index + 1)],
                    }),
                  },
                  {
                    rotate: logoRotateAnim.interpolate({
                      inputRange: [0, 1],
                      outputRange: ['0deg', `${360 * (index % 2 === 0 ? 1 : -1)}deg`],
                    }),
                  },
                ],
              },
              {
                top: `${10 + index * 15}%`,
                left: `${5 + (index % 2) * 80}%`,
              },
            ]}
          />
        ))}
      </View>

      {/* Main content */}
      <View style={styles.content}>
        {/* Logo */}
        <Animated.View
          style={[
            styles.logoContainer,
            {
              opacity: fadeAnim,
              transform: [
                { scale: scaleAnim },
                { rotate: logoRotate },
              ],
            },
          ]}
        >
          <View style={styles.logoOuter}>
            <View style={styles.logoInner}>
              <Text style={styles.logoText}>AI</Text>
            </View>
          </View>
        </Animated.View>

        {/* Brand name */}
        <Animated.View
          style={[
            styles.brandContainer,
            {
              opacity: fadeAnim,
              transform: [{ translateY: slideAnim }],
            },
          ]}
        >
          <Text style={styles.brandName}>Aideon AI</Text>
          <Text style={styles.brandSubtitle}>Lite</Text>
        </Animated.View>

        {/* Tagline */}
        <Animated.View
          style={[
            styles.taglineContainer,
            {
              opacity: fadeAnim,
              transform: [{ translateY: slideAnim }],
            },
          ]}
        >
          <Text style={styles.tagline}>Intelligent AI Orchestration</Text>
          <Text style={styles.taglineSubtext}>Powered by Advanced Multi-Model Architecture</Text>
        </Animated.View>

        {/* Loading indicator */}
        <Animated.View
          style={[
            styles.loadingContainer,
            {
              opacity: fadeAnim,
              transform: [{ translateY: slideAnim }],
            },
          ]}
        >
          <View style={styles.loadingBar}>
            <Animated.View
              style={[
                styles.loadingProgress,
                {
                  transform: [
                    {
                      scaleX: logoRotateAnim.interpolate({
                        inputRange: [0, 1],
                        outputRange: [0, 1],
                      }),
                    },
                  ],
                },
              ]}
            />
          </View>
          <Text style={styles.loadingText}>Initializing AI Systems...</Text>
        </Animated.View>
      </View>

      {/* Version info */}
      <Animated.View
        style={[
          styles.versionContainer,
          {
            opacity: fadeAnim,
          },
        ]}
      >
        <Text style={styles.versionText}>Version 2.0.0</Text>
      </Animated.View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.primary[600],
  },
  backgroundElements: {
    ...StyleSheet.absoluteFillObject,
  },
  floatingElement: {
    position: 'absolute',
    width: 20,
    height: 20,
    borderRadius: 10,
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
  },
  content: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: Spacing.xl,
  },
  logoContainer: {
    marginBottom: Spacing['2xl'],
  },
  logoOuter: {
    width: 120,
    height: 120,
    borderRadius: 60,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 2,
    borderColor: 'rgba(255, 255, 255, 0.3)',
  },
  logoInner: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: 'rgba(255, 255, 255, 0.9)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  logoText: {
    fontSize: Typography.fontSize['3xl'],
    fontWeight: Typography.fontWeight.bold,
    color: Colors.primary[600],
    fontFamily: Typography.fontFamily.primary,
  },
  brandContainer: {
    alignItems: 'center',
    marginBottom: Spacing.xl,
  },
  brandName: {
    fontSize: Typography.fontSize['4xl'],
    fontWeight: Typography.fontWeight.bold,
    color: '#ffffff',
    fontFamily: Typography.fontFamily.primary,
    letterSpacing: 2,
  },
  brandSubtitle: {
    fontSize: Typography.fontSize.xl,
    fontWeight: Typography.fontWeight.light,
    color: 'rgba(255, 255, 255, 0.8)',
    fontFamily: Typography.fontFamily.primary,
    letterSpacing: 4,
    marginTop: -Spacing.xs,
  },
  taglineContainer: {
    alignItems: 'center',
    marginBottom: Spacing['3xl'],
  },
  tagline: {
    fontSize: Typography.fontSize.lg,
    fontWeight: Typography.fontWeight.medium,
    color: '#ffffff',
    fontFamily: Typography.fontFamily.primary,
    textAlign: 'center',
    marginBottom: Spacing.xs,
  },
  taglineSubtext: {
    fontSize: Typography.fontSize.sm,
    color: 'rgba(255, 255, 255, 0.7)',
    fontFamily: Typography.fontFamily.primary,
    textAlign: 'center',
  },
  loadingContainer: {
    alignItems: 'center',
    width: '100%',
  },
  loadingBar: {
    width: 200,
    height: 4,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    borderRadius: 2,
    overflow: 'hidden',
    marginBottom: Spacing.md,
  },
  loadingProgress: {
    height: '100%',
    backgroundColor: '#ffffff',
    borderRadius: 2,
  },
  loadingText: {
    fontSize: Typography.fontSize.sm,
    color: 'rgba(255, 255, 255, 0.8)',
    fontFamily: Typography.fontFamily.primary,
  },
  versionContainer: {
    position: 'absolute',
    bottom: Spacing.xl,
    alignSelf: 'center',
  },
  versionText: {
    fontSize: Typography.fontSize.xs,
    color: 'rgba(255, 255, 255, 0.6)',
    fontFamily: Typography.fontFamily.primary,
  },
});

export default SplashScreen;

