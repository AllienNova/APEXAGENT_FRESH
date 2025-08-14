import React, { useState } from 'react';
import {
  TextInput,
  View,
  Text,
  StyleSheet,
  ViewStyle,
  TextStyle,
  TouchableOpacity,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { Colors, Typography, BorderRadius, Spacing } from '../../constants/theme';

interface InputProps {
  label?: string;
  placeholder?: string;
  value: string;
  onChangeText: (text: string) => void;
  secureTextEntry?: boolean;
  keyboardType?: 'default' | 'email-address' | 'numeric' | 'phone-pad';
  autoCapitalize?: 'none' | 'sentences' | 'words' | 'characters';
  error?: string;
  disabled?: boolean;
  multiline?: boolean;
  numberOfLines?: number;
  leftIcon?: string;
  rightIcon?: string;
  onRightIconPress?: () => void;
  style?: ViewStyle;
  inputStyle?: TextStyle;
  autoFocus?: boolean;
  maxLength?: number;
}

const Input: React.FC<InputProps> = ({
  label,
  placeholder,
  value,
  onChangeText,
  secureTextEntry = false,
  keyboardType = 'default',
  autoCapitalize = 'sentences',
  error,
  disabled = false,
  multiline = false,
  numberOfLines = 1,
  leftIcon,
  rightIcon,
  onRightIconPress,
  style,
  inputStyle,
  autoFocus = false,
  maxLength,
}) => {
  const [isFocused, setIsFocused] = useState(false);
  const [isPasswordVisible, setIsPasswordVisible] = useState(!secureTextEntry);

  const getContainerStyle = (): ViewStyle => ({
    borderWidth: 2,
    borderColor: error
      ? Colors.error
      : isFocused
      ? Colors.primary[500]
      : Colors.gray[200],
    borderRadius: BorderRadius.md,
    backgroundColor: disabled ? Colors.gray[50] : Colors.light.background,
    flexDirection: 'row',
    alignItems: multiline ? 'flex-start' : 'center',
    paddingHorizontal: Spacing.md,
    paddingVertical: multiline ? Spacing.md : 0,
    minHeight: multiline ? 80 : 48,
  });

  const getInputStyle = (): TextStyle => ({
    flex: 1,
    fontFamily: Typography.fontFamily.primary,
    fontSize: Typography.fontSize.base,
    color: disabled ? Colors.gray[400] : Colors.light.text.primary,
    paddingVertical: multiline ? 0 : Spacing.sm,
    textAlignVertical: multiline ? 'top' : 'center',
  });

  const handleRightIconPress = () => {
    if (secureTextEntry) {
      setIsPasswordVisible(!isPasswordVisible);
    } else if (onRightIconPress) {
      onRightIconPress();
    }
  };

  return (
    <View style={[styles.container, style]}>
      {label && (
        <Text style={[styles.label, error && { color: Colors.error }]}>
          {label}
        </Text>
      )}
      
      <View style={getContainerStyle()}>
        {leftIcon && (
          <View style={styles.iconContainer}>
            <Ionicons
              name={leftIcon as any}
              size={20}
              color={isFocused ? Colors.primary[500] : Colors.gray[400]}
            />
          </View>
        )}
        
        <TextInput
          style={[getInputStyle(), inputStyle]}
          placeholder={placeholder}
          placeholderTextColor={Colors.gray[400]}
          value={value}
          onChangeText={onChangeText}
          secureTextEntry={secureTextEntry && !isPasswordVisible}
          keyboardType={keyboardType}
          autoCapitalize={autoCapitalize}
          editable={!disabled}
          multiline={multiline}
          numberOfLines={numberOfLines}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          autoFocus={autoFocus}
          maxLength={maxLength}
        />
        
        {(rightIcon || secureTextEntry) && (
          <TouchableOpacity
            style={styles.iconContainer}
            onPress={handleRightIconPress}
            disabled={!secureTextEntry && !onRightIconPress}
          >
            <Ionicons
              name={
                secureTextEntry
                  ? isPasswordVisible
                    ? 'eye-off-outline'
                    : 'eye-outline'
                  : (rightIcon as any)
              }
              size={20}
              color={isFocused ? Colors.primary[500] : Colors.gray[400]}
            />
          </TouchableOpacity>
        )}
      </View>
      
      {error && (
        <Text style={styles.errorText}>{error}</Text>
      )}
      
      {maxLength && (
        <Text style={styles.characterCount}>
          {value.length}/{maxLength}
        </Text>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    marginBottom: Spacing.md,
  },
  label: {
    fontFamily: Typography.fontFamily.primary,
    fontSize: Typography.fontSize.sm,
    fontWeight: Typography.fontWeight.medium,
    color: Colors.light.text.secondary,
    marginBottom: Spacing.xs,
  },
  iconContainer: {
    marginHorizontal: Spacing.xs,
    alignItems: 'center',
    justifyContent: 'center',
  },
  errorText: {
    fontFamily: Typography.fontFamily.primary,
    fontSize: Typography.fontSize.sm,
    color: Colors.error,
    marginTop: Spacing.xs,
  },
  characterCount: {
    fontFamily: Typography.fontFamily.primary,
    fontSize: Typography.fontSize.xs,
    color: Colors.gray[400],
    textAlign: 'right',
    marginTop: Spacing.xs,
  },
});

export default Input;

