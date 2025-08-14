"""
Update Scheduling Module for ApexAgent.

This module provides functionality to schedule updates and manage
update timing preferences.
"""

import os
import json
import time
import logging
import threading
import platform
from typing import Dict, List, Optional, Tuple, Union, Any, Callable
from datetime import datetime, timedelta

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("update_scheduler")

class UpdateScheduler:
    """
    Schedules updates for ApexAgent.
    
    This class handles scheduling updates, managing update timing preferences,
    and ensuring updates occur at appropriate times.
    """
    
    def __init__(self, 
                 config_path: str = None,
                 callback: Callable = None):
        """
        Initialize the update scheduler.
        
        Args:
            config_path: Path to the configuration file
            callback: Function to call when an update is scheduled
        """
        self.config_path = config_path or os.path.join(
            os.path.expanduser("~"), ".apexagent", "scheduler_config.json"
        )
        self.callback = callback
        self._load_config()
        self._scheduler_thread = None
        self._stop_event = threading.Event()
    
    def _load_config(self) -> None:
        """
        Load configuration from the config file.
        
        If the config file doesn't exist, default values are used.
        """
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                
                self.check_frequency = config.get('check_frequency', 24)  # hours
                self.auto_install = config.get('auto_install', False)
                self.quiet_hours_enabled = config.get('quiet_hours_enabled', False)
                self.quiet_hours_start = config.get('quiet_hours_start', 22)  # 10 PM
                self.quiet_hours_end = config.get('quiet_hours_end', 8)  # 8 AM
                self.update_day = config.get('update_day', None)  # None = any day
                self.update_time = config.get('update_time', None)  # None = any time
                self.last_check_time = config.get('last_check_time')
                self.next_check_time = config.get('next_check_time')
                self.scheduled_updates = config.get('scheduled_updates', [])
                self.update_types = config.get('update_types', ['security', 'recommended', 'regular'])
                
                logger.info(f"Loaded scheduler configuration from {self.config_path}")
            else:
                logger.warning(f"Config file not found at {self.config_path}, using defaults")
                self._set_defaults()
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            self._set_defaults()
    
    def _set_defaults(self) -> None:
        """Set default configuration values."""
        self.check_frequency = 24  # hours
        self.auto_install = False
        self.quiet_hours_enabled = False
        self.quiet_hours_start = 22  # 10 PM
        self.quiet_hours_end = 8  # 8 AM
        self.update_day = None  # None = any day
        self.update_time = None  # None = any time
        self.last_check_time = None
        self.next_check_time = None
        self.scheduled_updates = []
        self.update_types = ['security', 'recommended', 'regular']
    
    def _save_config(self) -> None:
        """Save the current configuration to the config file."""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            config = {
                'check_frequency': self.check_frequency,
                'auto_install': self.auto_install,
                'quiet_hours_enabled': self.quiet_hours_enabled,
                'quiet_hours_start': self.quiet_hours_start,
                'quiet_hours_end': self.quiet_hours_end,
                'update_day': self.update_day,
                'update_time': self.update_time,
                'last_check_time': self.last_check_time,
                'next_check_time': self.next_check_time,
                'scheduled_updates': self.scheduled_updates,
                'update_types': self.update_types
            }
            
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            logger.info(f"Saved scheduler configuration to {self.config_path}")
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
    
    def is_update_day(self) -> bool:
        """
        Check if today is a configured update day.
        
        Returns:
            bool: True if today is an update day
        """
        if self.update_day is None:
            return True
        
        # Get current day of week (0 = Monday, 6 = Sunday)
        current_day = datetime.now().weekday()
        
        # Convert to same format as update_day (0 = Monday, 6 = Sunday)
        return current_day == self.update_day
    
    def is_update_time(self) -> bool:
        """
        Check if current time is within the configured update time.
        
        Returns:
            bool: True if current time is an update time
        """
        if self.update_time is None:
            return True
        
        current_hour = datetime.now().hour
        return current_hour == self.update_time
    
    def should_check_for_updates(self) -> bool:
        """
        Check if it's time to check for updates.
        
        Returns:
            bool: True if it's time to check for updates
        """
        # If no last check time, should check
        if not self.last_check_time:
            return True
        
        # Parse last check time
        try:
            last_check = datetime.fromisoformat(self.last_check_time)
        except (ValueError, TypeError):
            return True
        
        # Check if enough time has passed
        now = datetime.now()
        time_since_last_check = now - last_check
        hours_since_last_check = time_since_last_check.total_seconds() / 3600
        
        return hours_since_last_check >= self.check_frequency
    
    def update_last_check_time(self) -> None:
        """Update the last check time to now."""
        self.last_check_time = datetime.now().isoformat()
        self._calculate_next_check_time()
        self._save_config()
    
    def _calculate_next_check_time(self) -> None:
        """Calculate the next check time based on check frequency."""
        if self.last_check_time:
            try:
                last_check = datetime.fromisoformat(self.last_check_time)
                next_check = last_check + timedelta(hours=self.check_frequency)
                self.next_check_time = next_check.isoformat()
            except (ValueError, TypeError):
                self.next_check_time = None
        else:
            self.next_check_time = None
    
    def schedule_update(self, update_metadata: Dict[str, Any], install_time: str = None) -> bool:
        """
        Schedule an update for installation.
        
        Args:
            update_metadata: Update metadata
            install_time: ISO format datetime for installation (None for immediate)
            
        Returns:
            bool: True if update was scheduled
        """
        try:
            # Check if update is already scheduled
            update_version = update_metadata.get('version')
            
            for scheduled in self.scheduled_updates:
                if scheduled.get('version') == update_version:
                    logger.warning(f"Update {update_version} is already scheduled")
                    return False
            
            # Create scheduled update entry
            scheduled_update = {
                'version': update_version,
                'metadata': update_metadata,
                'scheduled_time': install_time or datetime.now().isoformat(),
                'scheduled_at': datetime.now().isoformat(),
                'status': 'scheduled'
            }
            
            # Add to scheduled updates
            self.scheduled_updates.append(scheduled_update)
            self._save_config()
            
            logger.info(f"Scheduled update {update_version} for {scheduled_update['scheduled_time']}")
            return True
        except Exception as e:
            logger.error(f"Error scheduling update: {e}")
            return False
    
    def cancel_scheduled_update(self, version: str) -> bool:
        """
        Cancel a scheduled update.
        
        Args:
            version: Version of the update to cancel
            
        Returns:
            bool: True if update was cancelled
        """
        try:
            # Find the scheduled update
            for i, scheduled in enumerate(self.scheduled_updates):
                if scheduled.get('version') == version:
                    # Remove from scheduled updates
                    del self.scheduled_updates[i]
                    self._save_config()
                    
                    logger.info(f"Cancelled scheduled update {version}")
                    return True
            
            logger.warning(f"No scheduled update found for version {version}")
            return False
        except Exception as e:
            logger.error(f"Error cancelling update: {e}")
            return False
    
    def get_scheduled_updates(self) -> List[Dict[str, Any]]:
        """
        Get all scheduled updates.
        
        Returns:
            List[Dict[str, Any]]: List of scheduled updates
        """
        return self.scheduled_updates
    
    def get_pending_updates(self) -> List[Dict[str, Any]]:
        """
        Get updates that are scheduled and pending installation.
        
        Returns:
            List[Dict[str, Any]]: List of pending updates
        """
        now = datetime.now()
        pending = []
        
        for scheduled in self.scheduled_updates:
            if scheduled.get('status') != 'scheduled':
                continue
            
            try:
                scheduled_time = datetime.fromisoformat(scheduled.get('scheduled_time'))
                if scheduled_time <= now:
                    pending.append(scheduled)
            except (ValueError, TypeError):
                # If scheduled_time is invalid, consider it pending
                pending.append(scheduled)
        
        return pending
    
    def mark_update_complete(self, version: str, success: bool) -> bool:
        """
        Mark a scheduled update as complete.
        
        Args:
            version: Version of the update
            success: Whether the update was successful
            
        Returns:
            bool: True if update was marked
        """
        try:
            # Find the scheduled update
            for scheduled in self.scheduled_updates:
                if scheduled.get('version') == version:
                    # Update status
                    scheduled['status'] = 'completed' if success else 'failed'
                    scheduled['completed_at'] = datetime.now().isoformat()
                    scheduled['success'] = success
                    self._save_config()
                    
                    logger.info(f"Marked update {version} as {'completed' if success else 'failed'}")
                    return True
            
            logger.warning(f"No scheduled update found for version {version}")
            return False
        except Exception as e:
            logger.error(f"Error marking update: {e}")
            return False
    
    def set_check_frequency(self, hours: int) -> None:
        """
        Set the update check frequency.
        
        Args:
            hours: Hours between update checks
        """
        if hours < 1:
            logger.warning(f"Invalid check frequency: {hours}, using 1")
            hours = 1
        
        self.check_frequency = hours
        self._calculate_next_check_time()
        self._save_config()
        
        logger.info(f"Set check frequency to {hours} hours")
    
    def set_auto_install(self, enabled: bool) -> None:
        """
        Enable or disable automatic installation of updates.
        
        Args:
            enabled: Whether to enable automatic installation
        """
        self.auto_install = enabled
        self._save_config()
        
        logger.info(f"Set auto_install to {enabled}")
    
    def set_quiet_hours(self, enabled: bool, start_hour: int = None, end_hour: int = None) -> None:
        """
        Configure quiet hours for updates.
        
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
    
    def set_update_day(self, day: int) -> None:
        """
        Set the day of the week for updates.
        
        Args:
            day: Day of the week (0 = Monday, 6 = Sunday, None = any day)
        """
        if day is not None and not (0 <= day <= 6):
            logger.warning(f"Invalid update day: {day}")
            return
        
        self.update_day = day
        self._save_config()
        
        if day is not None:
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            logger.info(f"Set update day to {days[day]}")
        else:
            logger.info("Update day set to any day")
    
    def set_update_time(self, hour: int) -> None:
        """
        Set the hour of the day for updates.
        
        Args:
            hour: Hour of the day (0-23, None = any time)
        """
        if hour is not None and not (0 <= hour <= 23):
            logger.warning(f"Invalid update time: {hour}")
            return
        
        self.update_time = hour
        self._save_config()
        
        if hour is not None:
            logger.info(f"Set update time to {hour}:00")
        else:
            logger.info("Update time set to any time")
    
    def set_update_types(self, types: List[str]) -> None:
        """
        Set the types of updates to install automatically.
        
        Args:
            types: List of update types (security, recommended, regular)
        """
        valid_types = ['security', 'recommended', 'regular']
        self.update_types = [t for t in types if t in valid_types]
        self._save_config()
        
        logger.info(f"Set update types to {self.update_types}")
    
    def start_scheduler(self) -> None:
        """Start the scheduler thread."""
        if self._scheduler_thread and self._scheduler_thread.is_alive():
            logger.warning("Scheduler is already running")
            return
        
        self._stop_event.clear()
        self._scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self._scheduler_thread.start()
        
        logger.info("Scheduler started")
    
    def stop_scheduler(self) -> None:
        """Stop the scheduler thread."""
        if not self._scheduler_thread or not self._scheduler_thread.is_alive():
            logger.warning("Scheduler is not running")
            return
        
        self._stop_event.set()
        self._scheduler_thread.join(timeout=5.0)
        
        logger.info("Scheduler stopped")
    
    def _scheduler_loop(self) -> None:
        """Main scheduler loop."""
        while not self._stop_event.is_set():
            try:
                # Check if it's time to check for updates
                if self.should_check_for_updates():
                    logger.info("Checking for updates")
                    self.update_last_check_time()
                    
                    # Notify callback if provided
                    if self.callback:
                        try:
                            self.callback('check', None)
                        except Exception as e:
                            logger.error(f"Error in callback: {e}")
                
                # Check for pending updates
                pending_updates = self.get_pending_updates()
                
                for update in pending_updates:
                    # Check if it's an appropriate time to install
                    if self.is_during_quiet_hours():
                        logger.info("During quiet hours, skipping update installation")
                        continue
                    
                    if not self.is_update_day():
                        logger.info("Not an update day, skipping update installation")
                        continue
                    
                    if not self.is_update_time():
                        logger.info("Not an update time, skipping update installation")
                        continue
                    
                    # Check if update type is allowed
                    update_type = update.get('metadata', {}).get('type', 'regular')
                    if update_type not in self.update_types:
                        logger.info(f"Update type {update_type} not in allowed types {self.update_types}")
                        continue
                    
                    # Notify callback if provided
                    if self.callback:
                        try:
                            self.callback('install', update)
                        except Exception as e:
                            logger.error(f"Error in callback: {e}")
                
                # Sleep for a while before checking again
                # Use a short sleep and check for stop event to allow quick shutdown
                for _ in range(60):  # Check every minute
                    if self._stop_event.is_set():
                        break
                    time.sleep(1)
            
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                time.sleep(60)  # Sleep for a minute before retrying


def main():
    """Command-line interface for update scheduling."""
    import argparse
    
    parser = argparse.ArgumentParser(description="ApexAgent Update Scheduler")
    
    parser.add_argument("--config", type=str,
                        help="Path to configuration file")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Schedule command
    schedule_parser = subparsers.add_parser("schedule", help="Schedule an update")
    schedule_parser.add_argument("--metadata-file", type=str, required=True,
                                help="Path to update metadata JSON file")
    schedule_parser.add_argument("--time", type=str,
                                help="ISO format datetime for installation (None for immediate)")
    
    # Cancel command
    cancel_parser = subparsers.add_parser("cancel", help="Cancel a scheduled update")
    cancel_parser.add_argument("--version", type=str, required=True,
                              help="Version of the update to cancel")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List scheduled updates")
    
    # Configure command
    config_parser = subparsers.add_parser("config", help="Configure scheduler")
    config_parser.add_argument("--check-frequency", type=int,
                              help="Hours between update checks")
    config_parser.add_argument("--auto-install", type=str, choices=["enable", "disable"],
                              help="Enable or disable automatic installation")
    
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
    
    # Update day command
    day_parser = subparsers.add_parser("update-day", help="Set update day")
    day_parser.add_argument("--day", type=int, choices=range(7),
                           help="Day of the week (0 = Monday, 6 = Sunday)")
    day_parser.add_argument("--any", action="store_true",
                           help="Allow updates on any day")
    
    # Update time command
    time_parser = subparsers.add_parser("update-time", help="Set update time")
    time_parser.add_argument("--hour", type=int, choices=range(24),
                            help="Hour of the day (0-23)")
    time_parser.add_argument("--any", action="store_true",
                            help="Allow updates at any time")
    
    # Update types command
    types_parser = subparsers.add_parser("update-types", help="Set update types")
    types_parser.add_argument("--types", type=str, nargs="+", choices=["security", "recommended", "regular"],
                             help="Types of updates to install automatically")
    
    args = parser.parse_args()
    
    # Create scheduler
    scheduler = UpdateScheduler(config_path=args.config)
    
    if args.command == "schedule":
        try:
            with open(args.metadata_file, 'r') as f:
                update_metadata = json.load(f)
            
            success = scheduler.schedule_update(update_metadata, args.time)
            
            if success:
                print(f"Update {update_metadata.get('version')} scheduled")
                return 0
            else:
                print("Failed to schedule update")
                return 1
        except Exception as e:
            print(f"Error: {e}")
            return 1
    
    elif args.command == "cancel":
        success = scheduler.cancel_scheduled_update(args.version)
        
        if success:
            print(f"Update {args.version} cancelled")
            return 0
        else:
            print(f"Failed to cancel update {args.version}")
            return 1
    
    elif args.command == "list":
        scheduled_updates = scheduler.get_scheduled_updates()
        
        if scheduled_updates:
            print(f"Found {len(scheduled_updates)} scheduled update(s):")
            for i, update in enumerate(scheduled_updates):
                print(f"{i+1}. Version: {update.get('version')}")
                print(f"   Scheduled for: {update.get('scheduled_time')}")
                print(f"   Status: {update.get('status')}")
                print(f"   Type: {update.get('metadata', {}).get('type', 'regular')}")
                print()
        else:
            print("No scheduled updates found")
        
        return 0
    
    elif args.command == "config":
        if args.check_frequency is not None:
            scheduler.set_check_frequency(args.check_frequency)
            print(f"Check frequency set to {args.check_frequency} hours")
        
        if args.auto_install:
            enabled = args.auto_install == "enable"
            scheduler.set_auto_install(enabled)
            print(f"Auto-install {'enabled' if enabled else 'disabled'}")
        
        return 0
    
    elif args.command == "quiet-hours":
        if args.enable:
            enabled = True
        elif args.disable:
            enabled = False
        else:
            enabled = scheduler.quiet_hours_enabled
        
        scheduler.set_quiet_hours(enabled, args.start, args.end)
        
        if enabled:
            print(f"Quiet hours enabled: {scheduler.quiet_hours_start}:00 - {scheduler.quiet_hours_end}:00")
        else:
            print("Quiet hours disabled")
        
        return 0
    
    elif args.command == "update-day":
        if args.any:
            scheduler.set_update_day(None)
            print("Update day set to any day")
        elif args.day is not None:
            scheduler.set_update_day(args.day)
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            print(f"Update day set to {days[args.day]}")
        else:
            print("No change to update day")
        
        return 0
    
    elif args.command == "update-time":
        if args.any:
            scheduler.set_update_time(None)
            print("Update time set to any time")
        elif args.hour is not None:
            scheduler.set_update_time(args.hour)
            print(f"Update time set to {args.hour}:00")
        else:
            print("No change to update time")
        
        return 0
    
    elif args.command == "update-types":
        if args.types:
            scheduler.set_update_types(args.types)
            print(f"Update types set to {args.types}")
        else:
            print(f"Current update types: {scheduler.update_types}")
        
        return 0
    
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
