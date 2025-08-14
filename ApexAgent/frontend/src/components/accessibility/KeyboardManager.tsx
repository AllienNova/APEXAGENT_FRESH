// src/components/accessibility/KeyboardManager.tsx
import React, { createContext, useContext, useEffect, useState } from 'react';

// Keyboard shortcut action types
export enum KeyboardActionType {
  NEW_CHAT = 'new_chat',
  SAVE_CHAT = 'save_chat',
  CLEAR_CHAT = 'clear_chat',
  FOCUS_INPUT = 'focus_input',
  TOGGLE_SIDEBAR = 'toggle_sidebar',
  TOGGLE_SETTINGS = 'toggle_settings',
  TOGGLE_THEME = 'toggle_theme',
  NAVIGATE_NEXT_TAB = 'navigate_next_tab',
  NAVIGATE_PREV_TAB = 'navigate_prev_tab',
  SEARCH = 'search',
  HELP = 'help',
  STOP_GENERATION = 'stop_generation',
  REGENERATE = 'regenerate',
  COPY_LAST_RESPONSE = 'copy_last_response',
  TOGGLE_DR_TARDIS = 'toggle_dr_tardis'
}

// Keyboard shortcut interface
export interface KeyboardShortcut {
  id: KeyboardActionType;
  keys: string; // Format: "Ctrl+K" or "Shift+Alt+P"
  description: string;
  global?: boolean; // If true, works anywhere in the app
  disabled?: boolean;
  action: () => void;
}

// Keyboard context interface
interface KeyboardContextType {
  shortcuts: KeyboardShortcut[];
  updateShortcut: (id: KeyboardActionType, keys: string) => void;
  enableShortcut: (id: KeyboardActionType) => void;
  disableShortcut: (id: KeyboardActionType) => void;
  resetToDefaults: () => void;
  isEnabled: boolean;
  setIsEnabled: (enabled: boolean) => void;
}

// Create keyboard context
const KeyboardContext = createContext<KeyboardContextType | undefined>(undefined);

// Default shortcuts
const getDefaultShortcuts = (handlers: Record<KeyboardActionType, () => void>): KeyboardShortcut[] => [
  {
    id: KeyboardActionType.NEW_CHAT,
    keys: 'Ctrl+N',
    description: 'Create a new chat',
    action: handlers.new_chat
  },
  {
    id: KeyboardActionType.SAVE_CHAT,
    keys: 'Ctrl+S',
    description: 'Save current chat',
    action: handlers.save_chat
  },
  {
    id: KeyboardActionType.CLEAR_CHAT,
    keys: 'Ctrl+L',
    description: 'Clear current chat',
    action: handlers.clear_chat
  },
  {
    id: KeyboardActionType.FOCUS_INPUT,
    keys: 'Ctrl+/',
    description: 'Focus on input field',
    global: true,
    action: handlers.focus_input
  },
  {
    id: KeyboardActionType.TOGGLE_SIDEBAR,
    keys: 'Ctrl+B',
    description: 'Toggle sidebar',
    global: true,
    action: handlers.toggle_sidebar
  },
  {
    id: KeyboardActionType.TOGGLE_SETTINGS,
    keys: 'Ctrl+,',
    description: 'Open settings',
    global: true,
    action: handlers.toggle_settings
  },
  {
    id: KeyboardActionType.TOGGLE_THEME,
    keys: 'Ctrl+Shift+T',
    description: 'Toggle between light and dark theme',
    global: true,
    action: handlers.toggle_theme
  },
  {
    id: KeyboardActionType.NAVIGATE_NEXT_TAB,
    keys: 'Ctrl+Tab',
    description: 'Navigate to next tab',
    action: handlers.navigate_next_tab
  },
  {
    id: KeyboardActionType.NAVIGATE_PREV_TAB,
    keys: 'Ctrl+Shift+Tab',
    description: 'Navigate to previous tab',
    action: handlers.navigate_prev_tab
  },
  {
    id: KeyboardActionType.SEARCH,
    keys: 'Ctrl+F',
    description: 'Search in current view',
    action: handlers.search
  },
  {
    id: KeyboardActionType.HELP,
    keys: 'F1',
    description: 'Show help',
    global: true,
    action: handlers.help
  },
  {
    id: KeyboardActionType.STOP_GENERATION,
    keys: 'Escape',
    description: 'Stop current generation',
    action: handlers.stop_generation
  },
  {
    id: KeyboardActionType.REGENERATE,
    keys: 'Ctrl+R',
    description: 'Regenerate last response',
    action: handlers.regenerate
  },
  {
    id: KeyboardActionType.COPY_LAST_RESPONSE,
    keys: 'Ctrl+Shift+C',
    description: 'Copy last response to clipboard',
    action: handlers.copy_last_response
  },
  {
    id: KeyboardActionType.TOGGLE_DR_TARDIS,
    keys: 'Ctrl+D',
    description: 'Toggle Dr. Tardis interface',
    global: true,
    action: handlers.toggle_dr_tardis
  }
];

// Parse key combination string to event properties
const parseKeyCombination = (combination: string): { key: string; ctrlKey: boolean; shiftKey: boolean; altKey: boolean; metaKey: boolean } => {
  const parts = combination.split('+');
  const key = parts[parts.length - 1].toLowerCase();
  
  return {
    key,
    ctrlKey: parts.includes('Ctrl') || parts.includes('Control'),
    shiftKey: parts.includes('Shift'),
    altKey: parts.includes('Alt'),
    metaKey: parts.includes('Meta') || parts.includes('Command')
  };
};

// Check if keyboard event matches shortcut
const matchesShortcut = (event: KeyboardEvent, shortcut: KeyboardShortcut): boolean => {
  const { key, ctrlKey, shiftKey, altKey, metaKey } = parseKeyCombination(shortcut.keys);
  
  return (
    event.key.toLowerCase() === key &&
    event.ctrlKey === ctrlKey &&
    event.shiftKey === shiftKey &&
    event.altKey === altKey &&
    event.metaKey === metaKey
  );
};

// Keyboard provider component
export const KeyboardProvider: React.FC<{
  children: React.ReactNode;
  handlers: Record<KeyboardActionType, () => void>;
}> = ({ children, handlers }) => {
  const [isEnabled, setIsEnabled] = useState(true);
  const [shortcuts, setShortcuts] = useState<KeyboardShortcut[]>(() => getDefaultShortcuts(handlers));

  // Update a shortcut
  const updateShortcut = (id: KeyboardActionType, keys: string) => {
    setShortcuts(prev =>
      prev.map(shortcut =>
        shortcut.id === id ? { ...shortcut, keys } : shortcut
      )
    );
  };

  // Enable a shortcut
  const enableShortcut = (id: KeyboardActionType) => {
    setShortcuts(prev =>
      prev.map(shortcut =>
        shortcut.id === id ? { ...shortcut, disabled: false } : shortcut
      )
    );
  };

  // Disable a shortcut
  const disableShortcut = (id: KeyboardActionType) => {
    setShortcuts(prev =>
      prev.map(shortcut =>
        shortcut.id === id ? { ...shortcut, disabled: true } : shortcut
      )
    );
  };

  // Reset shortcuts to defaults
  const resetToDefaults = () => {
    setShortcuts(getDefaultShortcuts(handlers));
  };

  // Handle keyboard events
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (!isEnabled) return;
      
      // Skip if user is typing in an input, textarea, or contentEditable element
      if (
        event.target instanceof HTMLInputElement ||
        event.target instanceof HTMLTextAreaElement ||
        (event.target instanceof HTMLElement && event.target.isContentEditable)
      ) {
        // Allow global shortcuts even when typing
        const matchingGlobalShortcut = shortcuts.find(
          shortcut => !shortcut.disabled && shortcut.global && matchesShortcut(event, shortcut)
        );
        
        if (!matchingGlobalShortcut) return;
      }
      
      // Find matching shortcut
      const matchingShortcut = shortcuts.find(
        shortcut => !shortcut.disabled && matchesShortcut(event, shortcut)
      );
      
      if (matchingShortcut) {
        event.preventDefault();
        matchingShortcut.action();
      }
    };
    
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isEnabled, shortcuts]);

  return (
    <KeyboardContext.Provider
      value={{
        shortcuts,
        updateShortcut,
        enableShortcut,
        disableShortcut,
        resetToDefaults,
        isEnabled,
        setIsEnabled
      }}
    >
      {children}
    </KeyboardContext.Provider>
  );
};

// Hook for using keyboard shortcuts
export const useKeyboard = () => {
  const context = useContext(KeyboardContext);
  if (!context) {
    throw new Error('useKeyboard must be used within a KeyboardProvider');
  }
  return context;
};

// Keyboard shortcuts help dialog component
export const KeyboardShortcutsHelp: React.FC<{ isOpen: boolean; onClose: () => void }> = ({
  isOpen,
  onClose
}) => {
  const { shortcuts, isEnabled } = useKeyboard();
  
  if (!isOpen) return null;
  
  // Group shortcuts by category
  const categories = {
    'Navigation': shortcuts.filter(s => 
      [KeyboardActionType.TOGGLE_SIDEBAR, KeyboardActionType.NAVIGATE_NEXT_TAB, KeyboardActionType.NAVIGATE_PREV_TAB].includes(s.id)
    ),
    'Chat': shortcuts.filter(s => 
      [KeyboardActionType.NEW_CHAT, KeyboardActionType.SAVE_CHAT, KeyboardActionType.CLEAR_CHAT, KeyboardActionType.FOCUS_INPUT].includes(s.id)
    ),
    'Generation': shortcuts.filter(s => 
      [KeyboardActionType.STOP_GENERATION, KeyboardActionType.REGENERATE, KeyboardActionType.COPY_LAST_RESPONSE].includes(s.id)
    ),
    'Interface': shortcuts.filter(s => 
      [KeyboardActionType.TOGGLE_SETTINGS, KeyboardActionType.TOGGLE_THEME, KeyboardActionType.SEARCH, KeyboardActionType.HELP, KeyboardActionType.TOGGLE_DR_TARDIS].includes(s.id)
    )
  };
  
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" role="dialog" aria-modal="true" aria-labelledby="keyboard-shortcuts-title">
      <div className="bg-background rounded-lg shadow-xl max-w-2xl w-full max-h-[80vh] overflow-auto">
        <div className="p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 id="keyboard-shortcuts-title" className="text-xl font-bold">Keyboard Shortcuts</h2>
            <button
              onClick={onClose}
              className="text-muted-foreground hover:text-foreground"
              aria-label="Close dialog"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
              </svg>
            </button>
          </div>
          
          {!isEnabled && (
            <div className="mb-4 p-3 bg-amber-100 dark:bg-amber-900/20 text-amber-800 dark:text-amber-200 rounded-md">
              Keyboard shortcuts are currently disabled. Enable them in Settings.
            </div>
          )}
          
          <div className="space-y-6">
            {Object.entries(categories).map(([category, categoryShortcuts]) => (
              <div key={category}>
                <h3 className="text-lg font-medium mb-2">{category}</h3>
                <div className="bg-card rounded-md border border-border overflow-hidden">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-border">
                        <th className="text-left p-3 text-sm font-medium">Action</th>
                        <th className="text-right p-3 text-sm font-medium">Shortcut</th>
                      </tr>
                    </thead>
                    <tbody>
                      {categoryShortcuts.map(shortcut => (
                        <tr key={shortcut.id} className="border-b border-border last:border-0">
                          <td className="p-3 text-sm">
                            {shortcut.description}
                            {shortcut.disabled && (
                              <span className="ml-2 text-xs text-muted-foreground">(Disabled)</span>
                            )}
                          </td>
                          <td className="p-3 text-right">
                            <kbd className="px-2 py-1 bg-muted rounded text-xs font-mono">
                              {shortcut.keys}
                            </kbd>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            ))}
          </div>
          
          <div className="mt-6 text-sm text-muted-foreground">
            You can customize these shortcuts in the Settings panel under the Keyboard tab.
          </div>
        </div>
      </div>
    </div>
  );
};

// Example usage component
export const KeyboardExample: React.FC = () => {
  const [showHelp, setShowHelp] = useState(false);
  
  // Mock handlers for demonstration
  const handlers: Record<KeyboardActionType, () => void> = {
    new_chat: () => console.log('New chat'),
    save_chat: () => console.log('Save chat'),
    clear_chat: () => console.log('Clear chat'),
    focus_input: () => console.log('Focus input'),
    toggle_sidebar: () => console.log('Toggle sidebar'),
    toggle_settings: () => console.log('Toggle settings'),
    toggle_theme: () => console.log('Toggle theme'),
    navigate_next_tab: () => console.log('Next tab'),
    navigate_prev_tab: () => console.log('Previous tab'),
    search: () => console.log('Search'),
    help: () => setShowHelp(true),
    stop_generation: () => console.log('Stop generation'),
    regenerate: () => console.log('Regenerate'),
    copy_last_response: () => console.log('Copy response'),
    toggle_dr_tardis: () => console.log('Toggle Dr. Tardis')
  };
  
  return (
    <KeyboardProvider handlers={handlers}>
      <div className="p-6">
        <h2 className="text-xl font-semibold mb-4">Keyboard Shortcuts Example</h2>
        <p className="mb-4">Press <kbd className="px-2 py-1 bg-muted rounded text-xs font-mono">F1</kbd> to view all available shortcuts.</p>
        
        <button
          onClick={() => setShowHelp(true)}
          className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
        >
          Show Keyboard Shortcuts
        </button>
        
        <KeyboardShortcutsHelp isOpen={showHelp} onClose={() => setShowHelp(false)} />
      </div>
    </KeyboardProvider>
  );
};

export default KeyboardProvider;
