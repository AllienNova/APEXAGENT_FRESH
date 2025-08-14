import React, { useState, useRef, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
  Animated,
  TouchableOpacity,
  Alert,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import { useNavigation } from '@react-navigation/native';
import { useDispatch, useSelector } from 'react-redux';

import Button from '../../components/ui/Button';
import Input from '../../components/ui/Input';
import Card from '../../components/ui/Card';
import { Colors, Typography, Spacing, BorderRadius } from '../../constants/theme';
import { RootState } from '../../store';
import { loginUser, biometricLogin } from '../../store/slices/authSlice';

const LoginScreen: React.FC = () => {
  const navigation = useNavigation();
  const dispatch = useDispatch();
  const { isLoading, error, biometricAvailable, biometricEnabled } = useSelector(
    (state: RootState) => state.auth
  );

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);

  const fadeAnim = useRef(new Animated.Value(0)).current;
  const slideAnim = useRef(new Animated.Value(50)).current;

  useEffect(() => {
    Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 800,
        useNativeDriver: true,
      }),
      Animated.timing(slideAnim, {
        toValue: 0,
        duration: 600,
        useNativeDriver: true,
      }),
    ]).start();
  }, []);

  const handleLogin = async () => {
    if (!email.trim() || !password.trim()) {
      Alert.alert('Error', 'Please fill in all fields');
      return;
    }

    try {
      await dispatch(loginUser({
        email: email.trim().toLowerCase(),
        password,
        biometric: rememberMe && biometricAvailable,
      }));
    } catch (error) {
      console.error('Login failed:', error);
    }
  };

  const handleBiometricLogin = async () => {
    try {
      await dispatch(biometricLogin());
    } catch (error) {
      Alert.alert('Biometric Login Failed', 'Please try again or use your password.');
    }
  };

  const handleForgotPassword = () => {
    navigation.navigate('ForgotPassword' as never);
  };

  const handleSignUp = () => {
    navigation.navigate('Register' as never);
  };

  return (
    <SafeAreaView style={styles.container}>
      <LinearGradient
        colors={[Colors.primary[50], Colors.primary[100]]}
        style={StyleSheet.absoluteFill}
      />

      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.keyboardView}
      >
        <ScrollView
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={false}
          keyboardShouldPersistTaps="handled"
        >
          {/* Header */}
          <Animated.View
            style={[
              styles.header,
              {
                opacity: fadeAnim,
                transform: [{ translateY: slideAnim }],
              },
            ]}
          >
            <View style={styles.logoContainer}>
              <LinearGradient
                colors={Colors.gradient.primary}
                style={styles.logo}
              >
                <Text style={styles.logoText}>AI</Text>
              </LinearGradient>
            </View>
            <Text style={styles.title}>Welcome Back</Text>
            <Text style={styles.subtitle}>
              Sign in to continue your AI journey
            </Text>
          </Animated.View>

          {/* Login Form */}
          <Animated.View
            style={[
              styles.formContainer,
              {
                opacity: fadeAnim,
                transform: [{ translateY: slideAnim }],
              },
            ]}
          >
            <Card variant="elevated" style={styles.formCard}>
              <Input
                label="Email Address"
                placeholder="Enter your email"
                value={email}
                onChangeText={setEmail}
                keyboardType="email-address"
                autoCapitalize="none"
                leftIcon="mail-outline"
                error={error && error.includes('email') ? error : undefined}
              />

              <Input
                label="Password"
                placeholder="Enter your password"
                value={password}
                onChangeText={setPassword}
                secureTextEntry
                leftIcon="lock-closed-outline"
                error={error && error.includes('password') ? error : undefined}
              />

              <View style={styles.optionsRow}>
                <TouchableOpacity
                  style={styles.rememberMeContainer}
                  onPress={() => setRememberMe(!rememberMe)}
                >
                  <View style={[styles.checkbox, rememberMe && styles.checkboxChecked]}>
                    {rememberMe && (
                      <Ionicons name="checkmark" size={16} color="#ffffff" />
                    )}
                  </View>
                  <Text style={styles.rememberMeText}>Remember me</Text>
                </TouchableOpacity>

                <TouchableOpacity onPress={handleForgotPassword}>
                  <Text style={styles.forgotPasswordText}>Forgot Password?</Text>
                </TouchableOpacity>
              </View>

              <Button
                title="Sign In"
                onPress={handleLogin}
                variant="gradient"
                loading={isLoading}
                fullWidth
                style={styles.loginButton}
              />

              {/* Biometric Login */}
              {biometricAvailable && biometricEnabled && (
                <View style={styles.biometricContainer}>
                  <View style={styles.divider}>
                    <View style={styles.dividerLine} />
                    <Text style={styles.dividerText}>or</Text>
                    <View style={styles.dividerLine} />
                  </View>

                  <TouchableOpacity
                    style={styles.biometricButton}
                    onPress={handleBiometricLogin}
                  >
                    <LinearGradient
                      colors={['rgba(14, 165, 233, 0.1)', 'rgba(99, 102, 241, 0.1)']}
                      style={styles.biometricGradient}
                    />
                    <Ionicons
                      name="finger-print-outline"
                      size={24}
                      color={Colors.primary[500]}
                    />
                    <Text style={styles.biometricText}>Use Biometric</Text>
                  </TouchableOpacity>
                </View>
              )}
            </Card>
          </Animated.View>

          {/* Social Login */}
          <Animated.View
            style={[
              styles.socialContainer,
              {
                opacity: fadeAnim,
                transform: [{ translateY: slideAnim }],
              },
            ]}
          >
            <View style={styles.divider}>
              <View style={styles.dividerLine} />
              <Text style={styles.dividerText}>or continue with</Text>
              <View style={styles.dividerLine} />
            </View>

            <View style={styles.socialButtons}>
              <TouchableOpacity style={styles.socialButton}>
                <Ionicons name="logo-google" size={24} color="#DB4437" />
              </TouchableOpacity>
              <TouchableOpacity style={styles.socialButton}>
                <Ionicons name="logo-apple" size={24} color="#000000" />
              </TouchableOpacity>
              <TouchableOpacity style={styles.socialButton}>
                <Ionicons name="logo-microsoft" size={24} color="#00A4EF" />
              </TouchableOpacity>
            </View>
          </Animated.View>

          {/* Sign Up Link */}
          <Animated.View
            style={[
              styles.signUpContainer,
              {
                opacity: fadeAnim,
              },
            ]}
          >
            <Text style={styles.signUpText}>
              Don't have an account?{' '}
              <Text style={styles.signUpLink} onPress={handleSignUp}>
                Sign Up
              </Text>
            </Text>
          </Animated.View>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.primary[50],
  },
  keyboardView: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    paddingHorizontal: Spacing.lg,
    paddingVertical: Spacing.xl,
  },
  header: {
    alignItems: 'center',
    marginBottom: Spacing['2xl'],
  },
  logoContainer: {
    marginBottom: Spacing.lg,
  },
  logo: {
    width: 80,
    height: 80,
    borderRadius: 40,
    alignItems: 'center',
    justifyContent: 'center',
  },
  logoText: {
    fontSize: Typography.fontSize['2xl'],
    fontWeight: Typography.fontWeight.bold,
    color: '#ffffff',
    fontFamily: Typography.fontFamily.primary,
  },
  title: {
    fontSize: Typography.fontSize['3xl'],
    fontWeight: Typography.fontWeight.bold,
    color: Colors.light.text.primary,
    fontFamily: Typography.fontFamily.primary,
    marginBottom: Spacing.xs,
  },
  subtitle: {
    fontSize: Typography.fontSize.base,
    color: Colors.light.text.secondary,
    fontFamily: Typography.fontFamily.primary,
    textAlign: 'center',
  },
  formContainer: {
    marginBottom: Spacing.xl,
  },
  formCard: {
    padding: Spacing.xl,
  },
  optionsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: Spacing.lg,
  },
  rememberMeContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  checkbox: {
    width: 20,
    height: 20,
    borderRadius: 4,
    borderWidth: 2,
    borderColor: Colors.gray[300],
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: Spacing.xs,
  },
  checkboxChecked: {
    backgroundColor: Colors.primary[500],
    borderColor: Colors.primary[500],
  },
  rememberMeText: {
    fontSize: Typography.fontSize.sm,
    color: Colors.light.text.secondary,
    fontFamily: Typography.fontFamily.primary,
  },
  forgotPasswordText: {
    fontSize: Typography.fontSize.sm,
    color: Colors.primary[500],
    fontFamily: Typography.fontFamily.primary,
    fontWeight: Typography.fontWeight.medium,
  },
  loginButton: {
    marginBottom: Spacing.lg,
  },
  biometricContainer: {
    alignItems: 'center',
  },
  divider: {
    flexDirection: 'row',
    alignItems: 'center',
    marginVertical: Spacing.lg,
  },
  dividerLine: {
    flex: 1,
    height: 1,
    backgroundColor: Colors.gray[200],
  },
  dividerText: {
    fontSize: Typography.fontSize.sm,
    color: Colors.light.text.tertiary,
    fontFamily: Typography.fontFamily.primary,
    marginHorizontal: Spacing.md,
  },
  biometricButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: Spacing.md,
    paddingHorizontal: Spacing.xl,
    borderRadius: BorderRadius.md,
    borderWidth: 1,
    borderColor: Colors.primary[200],
    overflow: 'hidden',
  },
  biometricGradient: {
    ...StyleSheet.absoluteFillObject,
  },
  biometricText: {
    fontSize: Typography.fontSize.base,
    color: Colors.primary[500],
    fontFamily: Typography.fontFamily.primary,
    fontWeight: Typography.fontWeight.medium,
    marginLeft: Spacing.xs,
  },
  socialContainer: {
    alignItems: 'center',
    marginBottom: Spacing.xl,
  },
  socialButtons: {
    flexDirection: 'row',
    justifyContent: 'center',
    gap: Spacing.md,
  },
  socialButton: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: '#ffffff',
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  signUpContainer: {
    alignItems: 'center',
  },
  signUpText: {
    fontSize: Typography.fontSize.base,
    color: Colors.light.text.secondary,
    fontFamily: Typography.fontFamily.primary,
  },
  signUpLink: {
    color: Colors.primary[500],
    fontWeight: Typography.fontWeight.semibold,
  },
});

export default LoginScreen;

