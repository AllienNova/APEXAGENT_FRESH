// src/components/notifications/NotificationSystem.tsx
import React, { createContext, useContext, useState, useEffect } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { X, CheckCircle, AlertCircle, AlertTriangle, Info } from 'lucide-react';

// Notification types
export enum NotificationType {
  INFO = 'info',
  SUCCESS = 'success',
  WARNING = 'warning',
  ERROR = 'error'
}

// Notification interface
export interface Notification {
  id: string;
  type: NotificationType;
  title: string;
  message: string;
  duration?: number; // in milliseconds, undefined for persistent
  action?: {
    label: string;
    onClick: () => void;
  };
  createdAt: Date;
}

// Notification context interface
interface NotificationContextType {
  notifications: Notification[];
  addNotification: (notification: Omit<Notification, 'id' | 'createdAt'>) => string;
  removeNotification: (id: string) => void;
  clearAllNotifications: () => void;
}

// Create notification context
const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

// Notification provider component
export const NotificationProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [notifications, setNotifications] = useState<Notification[]>([]);

  // Add a new notification
  const addNotification = (notification: Omit<Notification, 'id' | 'createdAt'>): string => {
    const id = `notification-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    const newNotification: Notification = {
      ...notification,
      id,
      createdAt: new Date()
    };
    
    setNotifications(prev => [...prev, newNotification]);
    
    // Auto-remove non-persistent notifications after their duration
    if (notification.duration) {
      setTimeout(() => {
        removeNotification(id);
      }, notification.duration);
    }
    
    return id;
  };

  // Remove a notification by ID
  const removeNotification = (id: string) => {
    setNotifications(prev => prev.filter(notification => notification.id !== id));
  };

  // Clear all notifications
  const clearAllNotifications = () => {
    setNotifications([]);
  };

  return (
    <NotificationContext.Provider
      value={{
        notifications,
        addNotification,
        removeNotification,
        clearAllNotifications
      }}
    >
      {children}
      <NotificationContainer />
    </NotificationContext.Provider>
  );
};

// Hook for using notifications
export const useNotifications = () => {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotifications must be used within a NotificationProvider');
  }
  return context;
};

// Helper hooks for common notification types
export const useInfoNotification = () => {
  const { addNotification } = useNotifications();
  return (title: string, message: string, options?: { duration?: number; action?: { label: string; onClick: () => void } }) => {
    return addNotification({
      type: NotificationType.INFO,
      title,
      message,
      ...options
    });
  };
};

export const useSuccessNotification = () => {
  const { addNotification } = useNotifications();
  return (title: string, message: string, options?: { duration?: number; action?: { label: string; onClick: () => void } }) => {
    return addNotification({
      type: NotificationType.SUCCESS,
      title,
      message,
      ...options
    });
  };
};

export const useWarningNotification = () => {
  const { addNotification } = useNotifications();
  return (title: string, message: string, options?: { duration?: number; action?: { label: string; onClick: () => void } }) => {
    return addNotification({
      type: NotificationType.WARNING,
      title,
      message,
      ...options
    });
  };
};

export const useErrorNotification = () => {
  const { addNotification } = useNotifications();
  return (title: string, message: string, options?: { duration?: number; action?: { label: string; onClick: () => void } }) => {
    return addNotification({
      type: NotificationType.ERROR,
      title,
      message,
      ...options
    });
  };
};

// Notification container component
const NotificationContainer: React.FC = () => {
  const { notifications, removeNotification } = useNotifications();

  return (
    <div
      aria-live="polite"
      aria-atomic="true"
      className="fixed top-4 right-4 z-50 flex flex-col gap-2 w-full max-w-sm"
    >
      <AnimatePresence>
        {notifications.map(notification => (
          <NotificationItem
            key={notification.id}
            notification={notification}
            onClose={() => removeNotification(notification.id)}
          />
        ))}
      </AnimatePresence>
    </div>
  );
};

// Notification item component
const NotificationItem: React.FC<{
  notification: Notification;
  onClose: () => void;
}> = ({ notification, onClose }) => {
  const { id, type, title, message, action } = notification;

  // Get icon based on notification type
  const getIcon = () => {
    switch (type) {
      case NotificationType.SUCCESS:
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case NotificationType.WARNING:
        return <AlertTriangle className="h-5 w-5 text-amber-500" />;
      case NotificationType.ERROR:
        return <AlertCircle className="h-5 w-5 text-red-500" />;
      case NotificationType.INFO:
      default:
        return <Info className="h-5 w-5 text-blue-500" />;
    }
  };

  // Get background color based on notification type
  const getBackgroundColor = () => {
    switch (type) {
      case NotificationType.SUCCESS:
        return 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800';
      case NotificationType.WARNING:
        return 'bg-amber-50 dark:bg-amber-900/20 border-amber-200 dark:border-amber-800';
      case NotificationType.ERROR:
        return 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800';
      case NotificationType.INFO:
      default:
        return 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800';
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: -20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: -20, scale: 0.95 }}
      transition={{ duration: 0.2 }}
      className={`rounded-lg border shadow-lg ${getBackgroundColor()} p-4 w-full`}
      role="alert"
      aria-labelledby={`notification-${id}-title`}
    >
      <div className="flex items-start">
        <div className="flex-shrink-0">{getIcon()}</div>
        <div className="ml-3 flex-1">
          <h3
            id={`notification-${id}-title`}
            className="text-sm font-medium text-gray-900 dark:text-gray-100"
          >
            {title}
          </h3>
          <div className="mt-1 text-sm text-gray-700 dark:text-gray-300">{message}</div>
          
          {action && (
            <div className="mt-2">
              <button
                onClick={action.onClick}
                className="text-sm font-medium text-primary hover:text-primary/80 focus:outline-none focus:ring-2 focus:ring-primary/50 rounded"
              >
                {action.label}
              </button>
            </div>
          )}
        </div>
        <button
          onClick={onClose}
          className="flex-shrink-0 ml-4 text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-primary/50 rounded"
          aria-label="Close notification"
        >
          <X className="h-5 w-5" />
        </button>
      </div>
    </motion.div>
  );
};

// Example usage component
export const NotificationExample: React.FC = () => {
  const { addNotification } = useNotifications();
  const showInfoNotification = useInfoNotification();
  const showSuccessNotification = useSuccessNotification();
  const showWarningNotification = useWarningNotification();
  const showErrorNotification = useErrorNotification();

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold">Notification Examples</h2>
      
      <div className="flex flex-wrap gap-2">
        <button
          onClick={() =>
            showInfoNotification('Information', 'This is an informational notification.', {
              duration: 5000
            })
          }
          className="px-3 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
        >
          Show Info
        </button>
        
        <button
          onClick={() =>
            showSuccessNotification('Success', 'Operation completed successfully!', {
              duration: 5000
            })
          }
          className="px-3 py-2 bg-green-500 text-white rounded-md hover:bg-green-600"
        >
          Show Success
        </button>
        
        <button
          onClick={() =>
            showWarningNotification('Warning', 'This action might have consequences.', {
              duration: 5000
            })
          }
          className="px-3 py-2 bg-amber-500 text-white rounded-md hover:bg-amber-600"
        >
          Show Warning
        </button>
        
        <button
          onClick={() =>
            showErrorNotification('Error', 'An error occurred while processing your request.', {
              duration: 5000
            })
          }
          className="px-3 py-2 bg-red-500 text-white rounded-md hover:bg-red-600"
        >
          Show Error
        </button>
        
        <button
          onClick={() =>
            addNotification({
              type: NotificationType.INFO,
              title: 'With Action',
              message: 'This notification has an action button.',
              duration: 8000,
              action: {
                label: 'Take Action',
                onClick: () => alert('Action taken!')
              }
            })
          }
          className="px-3 py-2 bg-purple-500 text-white rounded-md hover:bg-purple-600"
        >
          With Action
        </button>
        
        <button
          onClick={() =>
            addNotification({
              type: NotificationType.WARNING,
              title: 'Persistent Notification',
              message: 'This notification will not disappear automatically.',
              action: {
                label: 'Acknowledge',
                onClick: () => alert('Acknowledged!')
              }
            })
          }
          className="px-3 py-2 bg-gray-500 text-white rounded-md hover:bg-gray-600"
        >
          Persistent
        </button>
      </div>
    </div>
  );
};

export default NotificationProvider;
