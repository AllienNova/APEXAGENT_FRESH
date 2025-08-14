import React from 'react';
import {
  View,
  StyleSheet,
  ViewStyle,
  TouchableOpacity,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Colors, BorderRadius, Spacing, Shadows } from '../../constants/theme';

interface CardProps {
  children: React.ReactNode;
  variant?: 'default' | 'elevated' | 'outlined' | 'gradient';
  onPress?: () => void;
  style?: ViewStyle;
  padding?: number;
  margin?: number;
  borderRadius?: number;
  disabled?: boolean;
}

const Card: React.FC<CardProps> = ({
  children,
  variant = 'default',
  onPress,
  style,
  padding = Spacing.md,
  margin = 0,
  borderRadius = BorderRadius.lg,
  disabled = false,
}) => {
  const getCardStyle = (): ViewStyle => {
    const baseStyle: ViewStyle = {
      borderRadius,
      padding,
      margin,
    };

    const variantStyles = {
      default: {
        backgroundColor: Colors.light.card,
        ...Shadows.sm,
      },
      elevated: {
        backgroundColor: Colors.light.card,
        ...Shadows.lg,
      },
      outlined: {
        backgroundColor: Colors.light.card,
        borderWidth: 1,
        borderColor: Colors.gray[200],
      },
      gradient: {
        backgroundColor: 'transparent',
        ...Shadows.md,
      },
    };

    return {
      ...baseStyle,
      ...variantStyles[variant],
      ...(disabled && { opacity: 0.6 }),
    };
  };

  const renderCard = () => {
    if (variant === 'gradient') {
      return (
        <View style={[getCardStyle(), style]}>
          <LinearGradient
            colors={['rgba(14, 165, 233, 0.1)', 'rgba(99, 102, 241, 0.1)']}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 1 }}
            style={[StyleSheet.absoluteFill, { borderRadius }]}
          />
          {children}
        </View>
      );
    }

    return (
      <View style={[getCardStyle(), style]}>
        {children}
      </View>
    );
  };

  if (onPress) {
    return (
      <TouchableOpacity
        onPress={onPress}
        disabled={disabled}
        activeOpacity={0.8}
        style={{ borderRadius }}
      >
        {renderCard()}
      </TouchableOpacity>
    );
  }

  return renderCard();
};

export default Card;

