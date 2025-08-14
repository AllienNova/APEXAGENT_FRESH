# ApexAgent Component Library

## Core Layout Components

### MainLayout
- **Purpose**: Primary application container with three-panel layout
- **Features**:
  - Collapsible sidebar
  - Main content area with tabs
  - Optional context panel
  - Responsive design for all screen sizes
- **State Management**:
  - Sidebar collapsed state
  - Context panel visibility
  - Active tab selection

### Sidebar
- **Purpose**: Navigation and project management
- **Features**:
  - Project list with status indicators
  - System integration services
  - File explorer with local storage indicators
  - User profile and settings access
- **Variants**:
  - Expanded (default)
  - Collapsed (icon-only)

### TabNavigation
- **Purpose**: Switch between different workspaces
- **Features**:
  - Chat/conversation tab
  - Files/explorer tab
  - Console/terminal tab
  - System resources tab
- **Behavior**:
  - Persistent tab state
  - Visual indicators for activity

## Conversation Components

### MessageThread
- **Purpose**: Display conversation between user and agent
- **Features**:
  - Clear visual distinction between user and agent messages
  - System action indicators within messages
  - Code blocks with syntax highlighting
  - File preview capabilities
  - Message timestamps and status indicators

### InputArea
- **Purpose**: Multi-modal input for user messages
- **Features**:
  - Text input with auto-resize
  - Voice input toggle
  - File attachment support
  - Send button with loading state
  - Suggestion chips for common actions

### SystemActionIndicator
- **Purpose**: Show agent actions on the system
- **Features**:
  - Command execution visualization
  - File operation indicators
  - Progress tracking for long-running operations
  - Permission request prompts

## File System Components

### FileExplorer
- **Purpose**: Navigate and manage local files
- **Features**:
  - Tree view of directories and files
  - File status indicators (new, modified, unmodified)
  - Context menu for file operations
  - Search and filter capabilities
  - Path navigation breadcrumbs

### FileTable
- **Purpose**: Tabular view of files with metadata
- **Features**:
  - Sortable columns (name, size, modified date)
  - Status indicators
  - Action buttons for common operations
  - Grouping by directory

### FilePreview
- **Purpose**: Preview file contents
- **Features**:
  - Syntax highlighting for code files
  - Image preview for media files
  - Text preview for documents
  - Download and open options

## System Integration Components

### ActivityMonitor
- **Purpose**: Track and display agent actions
- **Features**:
  - Chronological activity log
  - Filtering by activity type
  - Detailed information on hover
  - Clear visual indicators for different actions

### PermissionManager
- **Purpose**: Control system access permissions
- **Features**:
  - Toggle switches for major permission categories
  - Directory-specific access controls
  - Permission history log
  - Request handling interface

### ResourceMonitor
- **Purpose**: Display system resource usage
- **Features**:
  - CPU, memory, and disk usage visualization
  - Historical usage graphs
  - Process breakdown
  - Alert indicators for high usage

## Project Management Components

### ProjectCard
- **Purpose**: Display project information
- **Features**:
  - Project name and description
  - Status indicator
  - Storage location
  - Last modified date
  - Quick action buttons

### StorageLocationManager
- **Purpose**: Manage project storage locations
- **Features**:
  - Add/remove storage locations
  - Set default location
  - Display available space
  - Connection status indicators

### BackupManager
- **Purpose**: Configure project backups
- **Features**:
  - Backup schedule configuration
  - Location selection
  - Manual backup trigger
  - Restore from backup interface

## Utility Components

### StatusBadge
- **Purpose**: Indicate status of various items
- **Variants**:
  - Success (green)
  - Warning (yellow)
  - Error (red)
  - Info (blue)
  - Neutral (gray)

### ActionButton
- **Purpose**: Consistent button styling
- **Variants**:
  - Primary
  - Secondary
  - Tertiary
  - Danger
  - Icon-only

### Tooltip
- **Purpose**: Provide additional information
- **Features**:
  - Multiple positions
  - Delay on hover
  - Rich content support
  - Keyboard accessibility

### ProgressIndicator
- **Purpose**: Show progress of operations
- **Variants**:
  - Linear
  - Circular
  - Indeterminate
  - Step-based
