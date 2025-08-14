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
import { registerUser } from '../../store/slices/authSlice';

const RegisterScreen: React.FC = () => {
  const navigation = useNavigation();
  const dispatch = useDispatch();
  const { isLoading, error } = useSelector((state: RootState) => state.auth);

  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
  });
  const [acceptTerms, setAcceptTerms] = useState(false);
  const [enableBiometric, setEnableBiometric] = useState(false);

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

  const updateFormData = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const validateForm = () => {
    if (!formData.name.trim()) {
      Alert.alert('Error', 'Please enter your full name');
      return false;
    }
    if (!formData.email.trim()) {
      Alert.alert('Error', 'Please enter your email address');
      return false;
    }
    if (!/\S+@\S+\.\S+/.test(formData.email)) {
      Alert.alert('Error', 'Please enter a valid email address');
      return false;
    }
    if (formData.password.length < 8) {
      Alert.alert('Error', 'Password must be at least 8 characters long');
      return false;
    }
    if (formData.password !== formData.confirmPassword) {
      Alert.alert('Error', 'Passwords do not match');
      return false;
    }
    if (!acceptTerms) {
      Alert.alert('Error', 'Please accept the Terms of Service and Privacy Policy');
      return false;
    }
    return true;
  };

  const handleRegister = async () => {
    if (!validateForm()) return;

    try {
      await dispatch(registerUser({
        name: formData.name.trim(),
        email: formData.email.trim().toLowerCase(),
        password: formData.password,
        enableBiometric,
      }));
    } catch (error) {
      console.error('Registration failed:', error);
    }
  };

  const handleSignIn = () => {
    navigation.navigate('Login' as never);
  };

  const getPasswordStrength = () => {
    const password = formData.password;
    if (password.length === 0) return { strength: 0, text: '', color: Colors.gray[300] };
    if (password.length < 6) return { strength: 1, text: 'Weak', color: Colors.error };
    if (password.length < 8) return { strength: 2, text: 'Fair', color: Colors.warning };
    if (password.length >= 8 && /(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(password)) {
      return { strength: 4, text: 'Strong', color: Colors.success };
    }
    return { strength: 3, text: 'Good', color: Colors.primary[500] };
  };

  const passwordStrength = getPasswordStrength();

  return (
    <SafeAreaView style={styles.container}>
      <LinearGradient
        colors={[Colors.secondary[50], Colors.primary[50]]}
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
                colors={Colors.gradient.secondary}
                style={styles.logo}
              >
                <Text style={styles.logoText}>AI</Text>
              </LinearGradient>
            </View>
            <Text style={styles.title}>Create Account</Text>
            <Text style={styles.subtitle}>
              Join the future of AI-powered productivity
            </Text>
          </Animated.View>

          {/* Registration Form */}
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
                label="Full Name"
                placeholder="Enter your full name"
                value={formData.name}
                onChangeText={(value) => updateFormData('name', value)}
                leftIcon="person-outline"
                autoCapitalize="words"
              />

              <Input
                label="Email Address"
                placeholder="Enter your email"
                value={formData.email}
                onChangeText={(value) => updateFormData('email', value)}
                keyboardType="email-address"
                autoCapitalize="none"
                leftIcon="mail-outline"
              />

              <Input
                label="Password"
                placeholder="Create a strong password"
                value={formData.password}
                onChangeText={(value) => updateFormData('password', value)}
                secureTextEntry
                leftIcon="lock-closed-outline"
              />

              {/* Password Strength Indicator */}
              {formData.password.length > 0 && (
                <View style={styles.passwordStrengthContainer}>
                  <View style={styles.passwordStrengthBar}>
                    <View
                      style={[
                        styles.passwordStrengthFill,
                        {
                          width: `${(passwordStrength.strength / 4) * 100}%`,
                          backgroundColor: passwordStrength.color,
                        },
                      ]}
                    />
                  </View>
                  <Text style={[styles.passwordStrengthText, { color: passwordStrength.color }]}>
                    {passwordStrength.text}
                  </Text>
                </View>
              )}

              <Input
                label="Confirm Password"
                placeholder="Confirm your password"
                value={formData.confirmPassword}
                onChangeText={(value) => updateFormData('confirmPassword', value)}
                secureTextEntry
                leftIcon="lock-closed-outline"
                error={
                  formData.confirmPassword.length > 0 && 
                  formData.password !== formData.confirmPassword
                    ? 'Passwords do not match'
                    : undefined
                }
              />

              {/* Terms and Conditions */}
              <TouchableOpacity
                style={styles.checkboxRow}
                onPress={() => setAcceptTerms(!acceptTerms)}
              >
                <View style={[styles.checkbox, acceptTerms && styles.checkboxChecked]}>
                  {acceptTerms && (
                    <Ionicons name="checkmark" size={16} color="#ffffff" />
                  )}
                </View>
                <Text style={styles.checkboxText}>
                  I agree to the{' '}
                  <Text style={styles.linkText}>Terms of Service</Text> and{' '}
                  <Text style={styles.linkText}>Privacy Policy</Text>
                </Text>
              </TouchableOpacity>

              {/* Biometric Setup */}
              <TouchableOpacity
                style={styles.checkboxRow}
                onPress={() => setEnableBiometric(!enableBiometric)}
              >
                <View style={[styles.checkbox, enableBiometric && styles.checkboxChecked]}>
                  {enableBiometric && (
                    <Ionicons name="checkmark" size={16} color="#ffffff" />
                  )}
                </View>
                <Text style={styles.checkboxText}>
                  Enable biometric authentication for faster login
                </Text>
              </TouchableOpacity>

              <Button
                title="Create Account"
                onPress={handleRegister}
                variant="gradient"
                loading={isLoading}
                fullWidth
                style={styles.registerButton}
              />
            </Card>
          </Animated.View>

          {/* Social Registration */}
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
              <Text style={styles.dividerText}>or sign up with</Text>
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

          {/* Sign In Link */}
          <Animated.View
            style={[
              styles.signInContainer,
              {
                opacity: fadeAnim,
              },
            ]}
          >
            <Text style={styles.signInText}>
              Already have an account?{' '}
              <Text style={styles.signInLink} onPress={handleSignIn}>
                Sign In
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
    backgroundColor: Colors.secondary[50],
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
    marginBottom: Spacing.xl,
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
    marginBottom: Spacing.lg,
  },
  formCard: {
    padding: Spacing.xl,
  },
  passwordStrengthContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: Spacing.md,
    marginTop: -Spacing.xs,
  },
  passwordStrengthBar: {
    flex: 1,
    height: 4,
    backgroundColor: Colors.gray[200],
    borderRadius: 2,
    marginRight: Spacing.sm,
    overflow: 'hidden',
  },
  passwordStrengthFill: {
    height: '100%',
    borderRadius: 2,
  },
  passwordStrengthText: {
    fontSize: Typography.fontSize.xs,
    fontFamily: Typography.fontFamily.primary,
    fontWeight: Typography.fontWeight.medium,
  },
  checkboxRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: Spacing.md,
  },
  checkbox: {
    width: 20,
    height: 20,
    borderRadius: 4,
    borderWidth: 2,
    borderColor: Colors.gray[300],
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: Spacing.sm,
    marginTop: 2,
  },
  checkboxChecked: {
    backgroundColor: Colors.primary[500],
    borderColor: Colors.primary[500],
  },
  checkboxText: {
    flex: 1,
    fontSize: Typography.fontSize.sm,
    color: Colors.light.text.secondary,
    fontFamily: Typography.fontFamily.primary,
    lineHeight: Typography.lineHeight.relaxed * Typography.fontSize.sm,
  },
  linkText: {
    color: Colors.primary[500],
    fontWeight: Typography.fontWeight.medium,
  },
  registerButton: {
    marginTop: Spacing.md,
  },
  socialContainer: {
    alignItems: 'center',
    marginBottom: Spacing.xl,
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
  signInContainer: {
    alignItems: 'center',
  },
  signInText: {
    fontSize: Typography.fontSize.base,
    color: Colors.light.text.secondary,
    fontFamily: Typography.fontFamily.primary,
  },
  signInLink: {
    color: Colors.primary[500],
    fontWeight: Typography.fontWeight.semibold,
  },
});

export default RegisterScreen;

