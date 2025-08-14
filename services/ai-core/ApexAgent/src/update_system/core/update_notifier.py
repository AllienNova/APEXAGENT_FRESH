"""
Update Notifier Module for ApexAgent.

This module provides functionality to notify users about available updates
and display update information in a user-friendly manner.
"""

import os
import json
import logging
import platform
import threading
import webbrowser
from typing import Dict, List, Optional, Tuple, Union, Any, Callable
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("update_notifier")

class UpdateNotifier:
    """
    Notifies users about available ApexAgent updates.
    
    This class handles user notifications for available updates,
    displays update information, and manages user preferences for notifications.
    """
    
    def __init__(self, 
                 config_path: str = None,
                 quiet_mode: bool = False,
                 notification_callback: Callable = None):
        """
        Initialize the update notifier.
        
        Args:
            config_path: Path to the configuration file
            quiet_mode: Whether to suppress notifications
            notification_callback: Function to call for custom notification handling
        """
        self.config_path = config_path or os.path.join(
            os.path.expanduser("~"), ".apexagent", "notification_config.json"
        )
        self.quiet_mode = quiet_mode
        self.notification_callback = notification_callback
        self._load_config()
    
    def _load_config(self) -> None:
        """
        Load configuration from the config file.
        
        If the config file doesn't exist, default values are used.
        """
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                
                self.notification_level = config.get('notification_level', 'recommended')
                self.quiet_hours_enabled = config.get('quiet_hours_enabled', False)
                self.quiet_hours_start = config.get('quiet_hours_start', 22)  # 10 PM
                self.quiet_hours_end = config.get('quiet_hours_end', 8)  # 8 AM
                self.last_notification_time = config.get('last_notification_time')
                self.dismissed_updates = config.get('dismissed_updates', [])
                self.notification_style = config.get('notification_style', 'standard')
                
                logger.info(f"Loaded notification configuration from {self.config_path}")
            else:
                logger.warning(f"Config file not found at {self.config_path}, using defaults")
                self._set_defaults()
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            self._set_defaults()
    
    def _set_defaults(self) -> None:
        """Set default configuration values."""
        self.notification_level = 'recommended'  # all, recommended, security, none
        self.quiet_hours_enabled = False
        self.quiet_hours_start = 22  # 10 PM
        self.quiet_hours_end = 8  # 8 AM
        self.last_notification_time = None
        self.dismissed_updates = []
        self.notification_style = 'standard'  # standard, minimal, detailed
    
    def _save_config(self) -> None:
        """Save the current configuration to the config file."""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            config = {
                'notification_level': self.notification_level,
                'quiet_hours_enabled': self.quiet_hours_enabled,
                'quiet_hours_start': self.quiet_hours_start,
                'quiet_hours_end': self.quiet_hours_end,
                'last_notification_time': self.last_notification_time,
                'dismissed_updates': self.dismissed_updates,
                'notification_style': self.notification_style
            }
            
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            logger.info(f"Saved notification configuration to {self.config_path}")
        except Exception as e:
            logger.error(f"Error saving config: {e}")
    
    def is_during_quiet_hours(self) -> bool:
        """
        Check if current time is during configured quiet hours.
        
        Returns:
            bool: True if current time is during quiet hours
        """
        if not self.quiet_hours_enabled:
            return False
        
        current_hour = datetime.now().hour
        
        # Handle case where quiet hours span midnight
        if self.quiet_hours_start > self.quiet_hours_end:
            return current_hour >= self.quiet_hours_start or current_hour < self.quiet_hours_end
        else:
            return self.quiet_hours_start <= current_hour < self.quiet_hours_end
    
    def should_notify_for_update(self, update: Dict[str, Any]) -> bool:
        """
        Determine if a notification should be shown for an update.
        
        Args:
            update: Update metadata
            
        Returns:
            bool: True if notification should be shown
        """
        # Check if in quiet mode
        if self.quiet_mode:
            return False
        
        # Check if during quiet hours
        if self.is_during_quiet_hours():
            return False
        
        # Check if update has been dismissed
        if update['version'] in self.dismissed_updates:
            return False
        
        # Check notification level
        update_type = update.get('type', 'regular')
        
        if self.notification_level == 'none':
            return False
        elif self.notification_level == 'security' and update_type != 'security':
            return False
        elif self.notification_level == 'recommended' and update_type not in ['security', 'recommended']:
            return False
        
        return True
    
    def notify_update(self, update: Dict[str, Any]) -> bool:
        """
        Show notification for an available update.
        
        Args:
            update: Update metadata
            
        Returns:
            bool: True if notification was shown
        """
        if not self.should_notify_for_update(update):
            logger.info(f"Skipping notification for update {update['version']}")
            return False
        
        # Record notification time
        self.last_notification_time = datetime.now().isoformat()
        self._save_config()
        
        # Use custom notification callback if provided
        if self.notification_callback:
            try:
                self.notification_callback(update)
                logger.info(f"Showed notification for update {update['version']} using callback")
                return True
            except Exception as e:
                logger.error(f"Error in notification callback: {e}")
                # Fall back to platform-specific notification
        
        # Platform-specific notification
        try:
            system = platform.system().lower()
            
            if system == "windows":
                self._show_windows_notification(update)
            elif system == "darwin":  # macOS
                self._show_macos_notification(update)
            elif system == "linux":
                self._show_linux_notification(update)
            else:
                logger.warning(f"Unsupported platform for notifications: {system}")
                return False
            
            logger.info(f"Showed notification for update {update['version']}")
            return True
        except Exception as e:
            logger.error(f"Error showing notification: {e}")
            return False
    
    def _show_windows_notification(self, update: Dict[str, Any]) -> None:
        """
        Show a notification on Windows.
        
        Args:
            update: Update metadata
        """
        try:
            # Try to use Windows toast notifications
            from win10toast import ToastNotifier
            
            toaster = ToastNotifier()
            title = f"ApexAgent Update {update['version']} Available"
            
            if self.notification_style == 'minimal':
                message = "A new update is available."
            elif self.notification_style == 'detailed':
                message = f"Type: {update.get('type', 'regular')}\n"
                message += f"Description: {update.get('description', 'No description')}\n"
                message += f"Release Date: {update.get('release_date', 'Unknown')}"
            else:  # standard
                message = f"{update.get('description', 'A new update is available.')}"
            
            toaster.show_toast(
                title,
                message,
                icon_path=None,
                duration=10,
                threaded=True
            )
        except ImportError:
            # Fall back to a simple message box
            try:
                import ctypes
                
                title = f"ApexAgent Update {update['version']} Available"
                message = f"{update.get('description', 'A new update is available.')}"
                
                ctypes.windll.user32.MessageBoxW(0, message, title, 0)
            except Exception as e:
                logger.error(f"Failed to show Windows notification: {e}")
                self._show_console_notification(update)
    
    def _show_macos_notification(self, update: Dict[str, Any]) -> None:
        """
        Show a notification on macOS.
        
        Args:
            update: Update metadata
        """
        try:
            # Use osascript to show a notification
            import subprocess
            
            title = f"ApexAgent Update {update['version']} Available"
            
            if self.notification_style == 'minimal':
                message = "A new update is available."
            elif self.notification_style == 'detailed':
                message = f"Type: {update.get('type', 'regular')} - "
                message += f"Description: {update.get('description', 'No description')} - "
                message += f"Release Date: {update.get('release_date', 'Unknown')}"
            else:  # standard
                message = f"{update.get('description', 'A new update is available.')}"
            
            # Escape double quotes in the message
            message = message.replace('"', '\\"')
            
            script = f'display notification "{message}" with title "{title}"'
            subprocess.run(["osascript", "-e", script], check=True)
        except Exception as e:
            logger.error(f"Failed to show macOS notification: {e}")
            self._show_console_notification(update)
    
    def _show_linux_notification(self, update: Dict[str, Any]) -> None:
        """
        Show a notification on Linux.
        
        Args:
            update: Update metadata
        """
        try:
            # Try to use notify-send
            import subprocess
            
            title = f"ApexAgent Update {update['version']} Available"
            
            if self.notification_style == 'minimal':
                message = "A new update is available."
            elif self.notification_style == 'detailed':
                message = f"Type: {update.get('type', 'regular')}\n"
                message += f"Description: {update.get('description', 'No description')}\n"
                message += f"Release Date: {update.get('release_date', 'Unknown')}"
            else:  # standard
                message = f"{update.get('description', 'A new update is available.')}"
            
            subprocess.run(["notify-send", title, message], check=True)
        except Exception as e:
            logger.error(f"Failed to show Linux notification: {e}")
            self._show_console_notification(update)
    
    def _show_console_notification(self, update: Dict[str, Any]) -> None:
        """
        Show a notification in the console (fallback method).
        
        Args:
            update: Update metadata
        """
        print("\n" + "=" * 60)
        print(f"ApexAgent Update {update['version']} Available")
        print("-" * 60)
        print(f"Type: {update.get('type', 'regular')}")
        print(f"Description: {update.get('description', 'No description')}")
        print(f"Release Date: {update.get('release_date', 'Unknown')}")
        print("=" * 60 + "\n")
    
    def dismiss_update(self, version: str) -> None:
        """
        Dismiss an update to prevent further notifications.
        
        Args:
            version: Update version to dismiss
        """
        if version not in self.dismissed_updates:
            self.dismissed_updates.append(version)
            self._save_config()
            logger.info(f"Dismissed update {version}")
    
    def undismiss_update(self, version: str) -> None:
        """
        Remove an update from the dismissed list.
        
        Args:
            version: Update version to undismiss
        """
        if version in self.dismissed_updates:
            self.dismissed_updates.remove(version)
            self._save_config()
            logger.info(f"Undismissed update {version}")
    
    def set_notification_level(self, level: str) -> None:
        """
        Set the notification level.
        
        Args:
            level: Notification level (all, recommended, security, none)
        """
        if level not in ['all', 'recommended', 'security', 'none']:
            logger.warning(f"Invalid notification level: {level}")
            return
        
        self.notification_level = level
        self._save_config()
        logger.info(f"Notification level set to: {level}")
    
    def set_quiet_hours(self, enabled: bool, start_hour: int = None, end_hour: int = None) -> None:
        """
        Configure quiet hours for notifications.
        
        Args:
            enabled: Whether to enable quiet hours
            start_hour: Start hour (0-23)
            end_hour: End hour (0-23)
        """
        self.quiet_hours_enabled = enabled
        
        if start_hour is not None:
            if 0 <= start_hour <= 23:
                self.quiet_hours_start = start_hour
            else:
                logger.warning(f"Invalid start hour: {start_hour}")
        
        if end_hour is not None:
            if 0 <= end_hour <= 23:
                self.quiet_hours_end = end_hour
            else:
                logger.warning(f"Invalid end hour: {end_hour}")
        
        self._save_config()
        
        if enabled:
            logger.info(f"Quiet hours enabled: {self.quiet_hours_start}:00 - {self.quiet_hours_end}:00")
        else:
            logger.info("Quiet hours disabled")
    
    def set_notification_style(self, style: str) -> None:
        """
        Set the notification style.
        
        Args:
            style: Notification style (standard, minimal, detailed)
        """
        if style not in ['standard', 'minimal', 'detailed']:
            logger.warning(f"Invalid notification style: {style}")
            return
        
        self.notification_style = style
        self._save_config()
        logger.info(f"Notification style set to: {style}")
    
    def show_release_notes(self, update: Dict[str, Any]) -> bool:
        """
        Show release notes for an update.
        
        Args:
            update: Update metadata
            
        Returns:
            bool: True if release notes were shown
        """
        release_notes_url = update.get('release_notes_url')
        
        if not release_notes_url:
            logger.warning(f"No release notes URL for update {update['version']}")
            return False
        
        try:
            webbrowser.open(release_notes_url)
            logger.info(f"Opened release notes for update {update['version']}")
            return True
        except Exception as e:
            logger.error(f"Failed to open release notes: {e}")
            return False


def main():
    """Command-line interface for update notifications."""
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description="ApexAgent Update Notifier")
    
    parser.add_argument("--config", type=str,
                        help="Path to configuration file")
    parser.add_argument("--quiet", action="store_true",
                        help="Enable quiet mode")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Notify command
    notify_parser = subparsers.add_parser("notify", help="Show update notification")
    notify_parser.add_argument("--update-file", type=str, required=True,
                              help="Path to update metadata JSON file")
    
    # Dismiss command
    dismiss_parser = subparsers.add_parser("dismiss", help="Dismiss an update")
    dismiss_parser.add_argument("version", type=str,
                               help="Update version to dismiss")
    
    # Undismiss command
    undismiss_parser = subparsers.add_parser("undismiss", help="Undismiss an update")
    undismiss_parser.add_argument("version", type=str,
                                 help="Update version to undismiss")
    
    # Level command
    level_parser = subparsers.add_parser("level", help="Set notification level")
    level_parser.add_argument("level", type=str, choices=["all", "recommended", "security", "none"],
                             help="Notification level")
    
    # Quiet hours command
    quiet_parser = subparsers.add_parser("quiet-hours", help="Configure quiet hours")
    quiet_parser.add_argument("--enable", action="store_true",
                             help="Enable quiet hours")
    quiet_parser.add_argument("--disable", action="store_true",
                             help="Disable quiet hours")
    quiet_parser.add_argument("--start", type=int,
                             help="Start hour (0-23)")
    quiet_parser.add_argument("--end", type=int,
                             help="End hour (0-23)")
    
    # Style command
    style_parser = subparsers.add_parser("style", help="Set notification style")
    style_parser.add_argument("style", type=str, choices=["standard", "minimal", "detailed"],
                             help="Notification style")
    
    args = parser.parse_args()
    
    # Create update notifier
    notifier = UpdateNotifier(config_path=args.config, quiet_mode=args.quiet)
    
    if args.command == "notify":
        try:
            with open(args.update_file, 'r') as f:
                update = json.load(f)
            
            notifier.notify_update(update)
        except Exception as e:
            print(f"Error: {e}")
    
    elif args.command == "dismiss":
        notifier.dismiss_update(args.version)
        print(f"Dismissed update {args.version}")
    
    elif args.command == "undismiss":
        notifier.undismiss_update(args.version)
        print(f"Undismissed update {args.version}")
    
    elif args.command == "level":
        notifier.set_notification_level(args.level)
        print(f"Notification level set to: {args.level}")
    
    elif args.command == "quiet-hours":
        if args.enable:
            enabled = True
        elif args.disable:
            enabled = False
        else:
            enabled = notifier.quiet_hours_enabled
        
        notifier.set_quiet_hours(enabled, args.start, args.end)
        
        if enabled:
            print(f"Quiet hours enabled: {notifier.quiet_hours_start}:00 - {notifier.quiet_hours_end}:00")
        else:
            print("Quiet hours disabled")
    
    elif args.command == "style":
        notifier.set_notification_style(args.style)
        print(f"Notification style set to: {args.style}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
