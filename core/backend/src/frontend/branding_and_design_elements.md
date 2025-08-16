# ApexAgent Branding and Design Elements

This document outlines the key branding and design elements extracted from the provided UI mockups and implementation plan for the ApexAgent desktop application.

## Brand Identity

### Logo and Icon
- Primary logo: Blue square/rounded rectangle with "A" in white
- Icon: Zap/lightning bolt icon in blue (from Lucide icon set)
- Accent colors: Blue as primary brand color

### Typography
- Font family: Sans-serif (system font stack)
- Headings: Light to medium weight
- Body text: Regular weight
- Size hierarchy:
  - Large headings: 1.5rem-2rem
  - Section headings: 1rem-1.25rem
  - Body text: 0.875rem
  - Small text/captions: 0.75rem

## Color System

### Primary Color Palette
- **Blue**: 
  - Primary: #3B82F6 (blue-500)
  - Light: #EFF6FF (blue-50)
  - Dark: #1E40AF (blue-800)

### Theme Options
- **Light Theme** (Default):
  - Background: #F9FAFB (gray-50)
  - Card/Surface: #FFFFFF (white)
  - Text Primary: #1F2937 (gray-800)
  - Text Secondary: #6B7280 (gray-500)
  - Border: #F3F4F6 (gray-100)
  - Input Background: #F9FAFB (gray-50)

- **Dark Theme**:
  - Background: #111827 (gray-900)
  - Card/Surface: #1F2937 (gray-800)
  - Text Primary: #F9FAFB (gray-100)
  - Text Secondary: #9CA3AF (gray-400)
  - Border: #374151 (gray-700)
  - Input Background: #374151 (gray-700)

- **Accent Theme Options**:
  - Blue theme
  - Green theme
  - Purple theme

### Semantic Colors
- Success: #10B981 (green-500)
- Warning: #F59E0B (yellow-500)
- Error: #EF4444 (red-500)
- Info: #3B82F6 (blue-500)

## Layout System

### Core Layout Structure
- Three-panel layout:
  1. Left sidebar (collapsible): 16rem width (64px when collapsed)
  2. Main content area (flexible)
  3. Right context panel (collapsible): 20rem width

### Navigation System
- Vertical sidebar navigation with icons and labels
- Icon-only mode when sidebar is collapsed
- Active state: Blue background with white icon or text
- Hover state: Light gray background

### Spacing System
- Base unit: 0.25rem (4px)
- Common spacing values:
  - Extra small: 0.5rem (8px)
  - Small: 1rem (16px)
  - Medium: 1.5rem (24px)
  - Large: 2rem (32px)
  - Extra large: 3rem (48px)

## UI Components

### Cards and Containers
- Rounded corners: 0.375rem (6px) to 0.5rem (8px)
- Light shadow: shadow-sm
- Border: 1px solid border color
- Padding: 1rem-1.5rem

### Buttons
- Primary: Blue background, white text
- Secondary: Gray/transparent background, current text color
- Rounded: 0.375rem (standard) or pill/full rounded for actions
- Sizes:
  - Small: 0.75rem text, 0.5rem vertical padding
  - Medium: 0.875rem text, 0.625rem vertical padding
  - Large: 1rem text, 0.75rem vertical padding

### Input Fields
- Rounded corners: 0.375rem or full rounded (pill)
- Border: 1px solid border color
- Background: Light gray in light mode, dark gray in dark mode
- Focus state: Blue border/ring

### Icons
- Icon library: Lucide React
- Standard sizes:
  - Small: 14px-16px
  - Medium: 18px-20px
  - Large: 24px
- Common icons:
  - Navigation: MessageSquare, Code, Activity, Layers, FileText, Brain, Compass
  - Actions: Send, Plus, Search, Settings, ChevronRight/Left
  - System: Terminal, HardDrive, Shield, Globe, Database
  - Status: CheckCircle, AlertTriangle, AlertCircle

## UI Patterns

### Conversation Interface
- Clear distinction between user and agent messages
- User messages: Right-aligned, blue background
- Agent messages: Left-aligned, white/dark background with border
- Timestamp separators between message groups
- Input field at bottom with send button and attachments

### System Integration Features
- File system navigation with tree view
- Activity monitoring with timestamped entries
- Permission management with status indicators
- Resource monitoring with visual graphs
- Terminal/console integration

### Status Indicators
- Green dot: Active/Available
- Yellow dot: Warning/Limited
- Red dot: Error/Unavailable
- Progress bars for ongoing operations

### Notifications and Alerts
- Toast-style notifications in bottom right
- Subtle animation for appearance
- Icon + title + description format
- Action buttons when applicable

## Responsive Behavior
- Collapsible panels for space efficiency
- Icon-only navigation when space is limited
- Responsive card layouts (grid to single column)
- Minimum width considerations for desktop application

## Accessibility Considerations
- Color contrast compliance
- Focus indicators for keyboard navigation
- Text size and readability
- Icon + text combinations for clarity

## Animation and Transitions
- Subtle transitions for panel resizing (200-300ms)
- Fade-in for notifications and alerts
- Micro-interactions for status changes
- Progress indicators for ongoing operations
