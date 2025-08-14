export const Colors = {
  // Brand Colors - Aideon AI Lite
  primary: {
    50: '#f0f9ff',
    100: '#e0f2fe',
    200: '#bae6fd',
    300: '#7dd3fc',
    400: '#38bdf8',
    500: '#0ea5e9', // Main brand blue
    600: '#0284c7',
    700: '#0369a1',
    800: '#075985',
    900: '#0c4a6e',
  },
  
  secondary: {
    50: '#fdf4ff',
    100: '#fae8ff',
    200: '#f5d0fe',
    300: '#f0abfc',
    400: '#e879f9',
    500: '#d946ef', // Accent purple
    600: '#c026d3',
    700: '#a21caf',
    800: '#86198f',
    900: '#701a75',
  },

  // AI-themed gradients
  gradient: {
    primary: ['#0ea5e9', '#3b82f6', '#6366f1'],
    secondary: ['#d946ef', '#f59e0b', '#ef4444'],
    neural: ['#06b6d4', '#8b5cf6', '#ec4899'],
    success: ['#10b981', '#059669'],
    warning: ['#f59e0b', '#d97706'],
    error: ['#ef4444', '#dc2626'],
  },

  // Neutral colors
  gray: {
    50: '#f9fafb',
    100: '#f3f4f6',
    200: '#e5e7eb',
    300: '#d1d5db',
    400: '#9ca3af',
    500: '#6b7280',
    600: '#4b5563',
    700: '#374151',
    800: '#1f2937',
    900: '#111827',
  },

  // Semantic colors
  success: '#10b981',
  warning: '#f59e0b',
  error: '#ef4444',
  info: '#3b82f6',

  // Dark mode colors
  dark: {
    background: '#0f0f23',
    surface: '#1a1a2e',
    card: '#16213e',
    border: '#2a2a3e',
    text: {
      primary: '#ffffff',
      secondary: '#a1a1aa',
      tertiary: '#71717a',
    },
  },

  // Light mode colors
  light: {
    background: '#ffffff',
    surface: '#f8fafc',
    card: '#ffffff',
    border: '#e2e8f0',
    text: {
      primary: '#1e293b',
      secondary: '#475569',
      tertiary: '#64748b',
    },
  },
};

export const Typography = {
  fontFamily: {
    primary: 'Inter',
    secondary: 'SF Pro Display',
    mono: 'SF Mono',
  },
  
  fontSize: {
    xs: 12,
    sm: 14,
    base: 16,
    lg: 18,
    xl: 20,
    '2xl': 24,
    '3xl': 30,
    '4xl': 36,
    '5xl': 48,
    '6xl': 60,
  },

  fontWeight: {
    light: '300',
    normal: '400',
    medium: '500',
    semibold: '600',
    bold: '700',
    extrabold: '800',
  },

  lineHeight: {
    tight: 1.25,
    snug: 1.375,
    normal: 1.5,
    relaxed: 1.625,
    loose: 2,
  },
};

export const Spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  '2xl': 48,
  '3xl': 64,
  '4xl': 80,
  '5xl': 96,
};

export const BorderRadius = {
  none: 0,
  sm: 4,
  md: 8,
  lg: 12,
  xl: 16,
  '2xl': 24,
  full: 9999,
};

export const Shadows = {
  sm: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 1,
  },
  md: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 4,
  },
  lg: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.15,
    shadowRadius: 16,
    elevation: 8,
  },
  xl: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 12 },
    shadowOpacity: 0.2,
    shadowRadius: 24,
    elevation: 12,
  },
};

export const Animation = {
  timing: {
    fast: 150,
    normal: 250,
    slow: 350,
  },
  easing: {
    linear: 'linear',
    ease: 'ease',
    easeIn: 'ease-in',
    easeOut: 'ease-out',
    easeInOut: 'ease-in-out',
  },
};

export const Layout = {
  screen: {
    padding: Spacing.md,
    paddingHorizontal: Spacing.md,
    paddingVertical: Spacing.lg,
  },
  card: {
    padding: Spacing.md,
    margin: Spacing.sm,
    borderRadius: BorderRadius.lg,
  },
  button: {
    height: 48,
    borderRadius: BorderRadius.md,
    paddingHorizontal: Spacing.lg,
  },
  input: {
    height: 48,
    borderRadius: BorderRadius.md,
    paddingHorizontal: Spacing.md,
  },
};

export const Theme = {
  light: {
    colors: {
      ...Colors,
      background: Colors.light.background,
      surface: Colors.light.surface,
      card: Colors.light.card,
      border: Colors.light.border,
      text: Colors.light.text,
    },
    ...Typography,
    spacing: Spacing,
    borderRadius: BorderRadius,
    shadows: Shadows,
    animation: Animation,
    layout: Layout,
  },
  dark: {
    colors: {
      ...Colors,
      background: Colors.dark.background,
      surface: Colors.dark.surface,
      card: Colors.dark.card,
      border: Colors.dark.border,
      text: Colors.dark.text,
    },
    ...Typography,
    spacing: Spacing,
    borderRadius: BorderRadius,
    shadows: Shadows,
    animation: Animation,
    layout: Layout,
  },
};

export default Theme;

