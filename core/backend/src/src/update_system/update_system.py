"""
Update System Integration Module for ApexAgent.

This module provides the main interface for the update system,
integrating all components into a cohesive system.
"""

import os
import json
import logging
import threading
import platform
from typing import Dict, List, Optional, Tuple, Union, Any, Callable
from datetime import datetime

# Import update system components
from src.update_system.core.update_checker import UpdateChecker
from src.update_system.core.update_notifier import UpdateNotifier
from src.update_system.core.update_installer import UpdateInstaller
from src.update_system.delta.delta_updater import DeltaUpdater
from src.update_system.rollback.rollback_manager import RollbackManager
from src.update_system.scheduling.update_scheduler import UpdateScheduler

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("update_system")

class UpdateSystem:
    """
    Main interface for the ApexAgent update system.
    
    This class integrates all update system components and provides
    a unified interface for managing updates.
    """
    
    def __init__(self, 
                 config_path: str = None,
                 installation_path: str = None,
                 progress_callback: Callable = None,
                 notification_callback: Callable = None):
        """
        Initialize the update system.
        
        Args:
            config_path: Path to the configuration file
            installation_path: Path to the ApexAgent installation
            progress_callback: Function to call with progress updates
            notification_callback: Function to call for custom notifications
        """
        self.config_path = config_path or os.path.join(
            os.path.expanduser("~"), ".apexagent", "update_system_config.json"
        )
        self.installation_path = installation_path or self._detect_installation_path()
        self.progress_callback = progress_callback
        self.notification_callback = notification_callback
        
        # Load configuration
        self._load_config()
        
        # Initialize components
        self._init_components()
        
        logger.info("Update system initialized")
    
    def _load_config(self) -> None:
        """
        Load configuration from the config file.
        
        If the config file doesn't exist, default values are used.
        """
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                
                self.update_server_url = config.get('update_server_url', 'https://updates.apexagent.example.com/api/v1')
                self.check_on_startup = config.get('check_on_startup', True)
                self.use_delta_updates = config.get('use_delta_updates', True)
                self.auto_download = config.get('auto_download', False)
                self.verify_signatures = config.get('verify_signatures', True)
                self.public_key_path = config.get('public_key_path', os.path.join(self.installation_path, 'security', 'update_public_key.pem'))
                
                logger.info(f"Loaded update system configuration from {self.config_path}")
            else:
                logger.warning(f"Config file not found at {self.config_path}, using defaults")
                self._set_defaults()
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            self._set_defaults()
    
    def _set_defaults(self) -> None:
        """Set default configuration values."""
        self.update_server_url = 'https://updates.apexagent.example.com/api/v1'
        self.check_on_startup = True
        self.use_delta_updates = True
        self.auto_download = False
        self.verify_signatures = True
        self.public_key_path = os.path.join(self.installation_path, 'security', 'update_public_key.pem')
    
    def _save_config(self) -> None:
        """Save the current configuration to the config file."""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            config = {
                'update_server_url': self.update_server_url,
                'check_on_startup': self.check_on_startup,
                'use_delta_updates': self.use_delta_updates,
                'auto_download': self.auto_download,
                'verify_signatures': self.verify_signatures,
                'public_key_path': self.public_key_path
            }
            
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            logger.info(f"Saved update system configuration to {self.config_path}")
        except Exception as e:
            logger.error(f"Error saving config: {e}")
    
    def _detect_installation_path(self) -> str:
        """
        Detect the ApexAgent installation path.
        
        Returns:
            str: Installation path
        """
        # Try to find installation path based on platform
        system = platform.system().lower()
        
        if system == "windows":
            # Check common Windows installation locations
            potential_paths = [
                os.path.join(os.environ.get("ProgramFiles", "C:\\Program Files"), "ApexAgent"),
                os.path.join(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"), "ApexAgent"),
                os.path.join(os.environ.get("LOCALAPPDATA", ""), "ApexAgent")
            ]
        elif system == "darwin":  # macOS
            # Check common macOS installation locations
            potential_paths = [
                "/Applications/ApexAgent.app",
                os.path.join(os.path.expanduser("~"), "Applications", "ApexAgent.app")
            ]
        else:  # Linux
            # Check common Linux installation locations
            potential_paths = [
                "/opt/apexagent",
                "/usr/local/apexagent",
                os.path.join(os.path.expanduser("~"), ".local", "share", "apexagent")
            ]
        
        # Check if any of the potential paths exist
        for path in potential_paths:
            if os.path.exists(path):
                return path
        
        # If no path is found, return a default path
        if system == "windows":
            return os.path.join(os.environ.get("ProgramFiles", "C:\\Program Files"), "ApexAgent")
        elif system == "darwin":
            return "/Applications/ApexAgent.app"
        else:  # Linux
            return "/opt/apexagent"
    
    def _init_components(self) -> None:
        """Initialize all update system components."""
        # Create component configuration paths
        config_dir = os.path.dirname(self.config_path)
        
        checker_config = os.path.join(config_dir, "checker_config.json")
        notifier_config = os.path.join(config_dir, "notifier_config.json")
        installer_config = os.path.join(config_dir, "installer_config.json")
        delta_config = os.path.join(config_dir, "delta_config.json")
        rollback_config = os.path.join(config_dir, "rollback_config.json")
        scheduler_config = os.path.join(config_dir, "scheduler_config.json")
        
        # Initialize components
        self.checker = UpdateChecker(
            config_path=checker_config,
            update_server_url=self.update_server_url
        )
        
        self.notifier = UpdateNotifier(
            config_path=notifier_config,
            notification_callback=self.notification_callback
        )
        
        self.installer = UpdateInstaller(
            config_path=installer_config,
            installation_path=self.installation_path,
            progress_callback=self.progress_callback
        )
        
        self.delta_updater = DeltaUpdater(
            config_path=delta_config,
            installation_path=self.installation_path,
            progress_callback=self.progress_callback
        )
        
        self.rollback_manager = RollbackManager(
            config_path=rollback_config,
            installation_path=self.installation_path,
            progress_callback=self.progress_callback
        )
        
        self.scheduler = UpdateScheduler(
            config_path=scheduler_config,
            callback=self._scheduler_callback
        )
    
    def _scheduler_callback(self, action: str, update: Dict[str, Any]) -> None:
        """
        Callback for the scheduler.
        
        Args:
            action: Action to perform ('check' or 'install')
            update: Update metadata (for 'install' action)
        """
        if action == 'check':
            # Check for updates
            self.check_for_updates()
        
        elif action == 'install' and update:
            # Install the update
            self.install_update(update.get('metadata', {}))
    
    def start(self) -> None:
        """Start the update system."""
        # Start the scheduler
        self.scheduler.start_scheduler()
        
        # Check for updates on startup if enabled
        if self.check_on_startup:
            threading.Thread(target=self.check_for_updates, daemon=True).start()
        
        logger.info("Update system started")
    
    def stop(self) -> None:
        """Stop the update system."""
        # Stop the scheduler
        self.scheduler.stop_scheduler()
        
        logger.info("Update system stopped")
    
    def check_for_updates(self) -> Optional[Dict[str, Any]]:
        """
        Check for available updates.
        
        Returns:
            Dict[str, Any] or None: Update metadata if available, None otherwise
        """
        try:
            logger.info("Checking for updates")
            
            # Get current version
            current_version = self.get_current_version()
            
            # Check for updates
            update_info = self.checker.check_for_updates(current_version)
            
            if not update_info:
                logger.info("No updates available")
                return None
            
            # Notify user about available update
            self.notifier.notify_update(update_info)
            
            # Auto-download if enabled
            if self.auto_download:
                threading.Thread(
                    target=self.download_update,
                    args=(update_info,),
                    daemon=True
                ).start()
            
            return update_info
        
        except Exception as e:
            logger.error(f"Error checking for updates: {e}")
            return None
    
    def get_current_version(self) -> str:
        """
        Get the current installed version.
        
        Returns:
            str: Current version
        """
        version_file = os.path.join(self.installation_path, "version.txt")
        
        if os.path.exists(version_file):
            try:
                with open(version_file, 'r') as f:
                    return f.read().strip()
            except Exception as e:
                logger.error(f"Error reading version file: {e}")
                return "unknown"
        else:
            logger.warning(f"Version file not found: {version_file}")
            return "unknown"
    
    def download_update(self, update_metadata: Dict[str, Any]) -> Optional[str]:
        """
        Download an update package.
        
        Args:
            update_metadata: Update metadata
            
        Returns:
            str or None: Path to the downloaded package, or None if download failed
        """
        try:
            logger.info(f"Downloading update {update_metadata.get('version')}")
            
            # Check if delta update is available and enabled
            if self.use_delta_updates and self.delta_updater.is_delta_update_available(update_metadata.get('version')):
                logger.info("Using delta update")
                return self.delta_updater.download_delta_update(update_metadata.get('version'))
            else:
                # Use full update
                logger.info("Using full update")
                return self.installer.download_update(update_metadata)
        
        except Exception as e:
            logger.error(f"Error downloading update: {e}")
            return None
    
    def verify_update(self, package_path: str, update_metadata: Dict[str, Any]) -> bool:
        """
        Verify an update package.
        
        Args:
            package_path: Path to the update package
            update_metadata: Update metadata
            
        Returns:
            bool: True if verification passed
        """
        try:
            logger.info(f"Verifying update package: {package_path}")
            
            # Check if it's a delta update
            if package_path.endswith('.bin'):
                return self.delta_updater.verify_delta_package(package_path, update_metadata)
            else:
                return self.installer.verify_package(package_path, update_metadata)
        
        except Exception as e:
            logger.error(f"Error verifying update: {e}")
            return False
    
    def install_update(self, update_metadata: Dict[str, Any], package_path: str = None) -> bool:
        """
        Install an update.
        
        Args:
            update_metadata: Update metadata
            package_path: Path to the update package (if already downloaded)
            
        Returns:
            bool: True if installation was successful
        """
        try:
            logger.info(f"Installing update {update_metadata.get('version')}")
            
            # Create restore point before update
            self.rollback_manager.create_restore_point(
                self.get_current_version(),
                f"Auto-backup before update to {update_metadata.get('version')}"
            )
            
            # Download the update if not provided
            if not package_path:
                package_path = self.download_update(update_metadata)
                
                if not package_path:
                    logger.error("Failed to download update")
                    return False
            
            # Verify the update
            if not self.verify_update(package_path, update_metadata):
                logger.error("Update verification failed")
                return False
            
            # Install the update
            success = False
            
            # Check if it's a delta update
            if package_path.endswith('.bin'):
                success = self.delta_updater.apply_delta_update(
                    package_path,
                    update_metadata.get('version')
                )
            else:
                success = self.installer.perform_update(update_metadata)
            
            # Update version history
            if success:
                self.rollback_manager.add_version_to_history(
                    update_metadata.get('version'),
                    update_metadata.get('type', 'regular'),
                    update_metadata.get('description')
                )
            
            return success
        
        except Exception as e:
            logger.error(f"Error installing update: {e}")
            return False
    
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
            logger.info(f"Scheduling update {update_metadata.get('version')}")
            return self.scheduler.schedule_update(update_metadata, install_time)
        
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
            logger.info(f"Cancelling scheduled update {version}")
            return self.scheduler.cancel_scheduled_update(version)
        
        except Exception as e:
            logger.error(f"Error cancelling update: {e}")
            return False
    
    def get_scheduled_updates(self) -> List[Dict[str, Any]]:
        """
        Get all scheduled updates.
        
        Returns:
            List[Dict[str, Any]]: List of scheduled updates
        """
        return self.scheduler.get_scheduled_updates()
    
    def rollback_to_version(self, version: str) -> bool:
        """
        Roll back to a specific version.
        
        Args:
            version: Version to roll back to
            
        Returns:
            bool: True if rollback was successful
        """
        try:
            logger.info(f"Rolling back to version {version}")
            return self.rollback_manager.rollback_to_version(version)
        
        except Exception as e:
            logger.error(f"Error rolling back: {e}")
            return False
    
    def get_version_history(self) -> List[Dict[str, Any]]:
        """
        Get the version history.
        
        Returns:
            List[Dict[str, Any]]: Version history
        """
        return self.rollback_manager.get_version_history()
    
    def get_available_restore_points(self) -> List[Dict[str, Any]]:
        """
        Get a list of available restore points.
        
        Returns:
            List[Dict[str, Any]]: List of restore points
        """
        return self.rollback_manager.get_available_restore_points()
    
    def create_restore_point(self, description: str = None) -> Optional[str]:
        """
        Create a restore point for the current installation.
        
        Args:
            description: Description of the restore point
            
        Returns:
            str or None: Path to the backup directory, or None if failed
        """
        try:
            logger.info("Creating restore point")
            return self.rollback_manager.create_restore_point(
                self.get_current_version(),
                description
            )
        
        except Exception as e:
            logger.error(f"Error creating restore point: {e}")
            return None
    
    def set_update_server_url(self, url: str) -> None:
        """
        Set the update server URL.
        
        Args:
            url: Update server URL
        """
        self.update_server_url = url
        self.checker.update_server_url = url
        self._save_config()
        
        logger.info(f"Set update server URL to {url}")
    
    def set_check_on_startup(self, enabled: bool) -> None:
        """
        Enable or disable checking for updates on startup.
        
        Args:
            enabled: Whether to check for updates on startup
        """
        self.check_on_startup = enabled
        self._save_config()
        
        logger.info(f"Set check_on_startup to {enabled}")
    
    def set_use_delta_updates(self, enabled: bool) -> None:
        """
        Enable or disable delta updates.
        
        Args:
            enabled: Whether to use delta updates
        """
        self.use_delta_updates = enabled
        self._save_config()
        
        logger.info(f"Set use_delta_updates to {enabled}")
    
    def set_auto_download(self, enabled: bool) -> None:
        """
        Enable or disable automatic download of updates.
        
        Args:
            enabled: Whether to automatically download updates
        """
        self.auto_download = enabled
        self._save_config()
        
        logger.info(f"Set auto_download to {enabled}")
    
    def set_verify_signatures(self, enabled: bool) -> None:
        """
        Enable or disable signature verification.
        
        Args:
            enabled: Whether to verify signatures
        """
        self.verify_signatures = enabled
        self.installer.verify_signatures = enabled
        self.delta_updater.verify_signatures = enabled
        self._save_config()
        
        logger.info(f"Set verify_signatures to {enabled}")
    
    def set_public_key_path(self, path: str) -> None:
        """
        Set the path to the public key for signature verification.
        
        Args:
            path: Path to the public key
        """
        self.public_key_path = path
        self.installer.public_key_path = path
        self.delta_updater.public_key_path = path
        self._save_config()
        
        logger.info(f"Set public_key_path to {path}")


def main():
    """Command-line interface for the update system."""
    import argparse
    import time
    
    parser = argparse.ArgumentParser(description="ApexAgent Update System")
    
    parser.add_argument("--config", type=str,
                        help="Path to configuration file")
    parser.add_argument("--install-path", type=str,
                        help="Path to ApexAgent installation")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Check command
    check_parser = subparsers.add_parser("check", help="Check for updates")
    
    # Install command
    install_parser = subparsers.add_parser("install", help="Install an update")
    install_parser.add_argument("--metadata-file", type=str, required=True,
                               help="Path to update metadata JSON file")
    install_parser.add_argument("--package", type=str,
                               help="Path to update package (if already downloaded)")
    
    # Schedule command
    schedule_parser = subparsers.add_parser("schedule", help="Schedule an update")
    schedule_parser.add_argument("--metadata-file", type=str, required=True,
                                help="Path to update metadata JSON file")
    schedule_parser.add_argument("--time", type=str,
                                help="ISO format datetime for installation (None for immediate)")
    
    # Rollback command
    rollback_parser = subparsers.add_parser("rollback", help="Roll back to a previous version")
    rollback_parser.add_argument("--version", type=str, required=True,
                                help="Version to roll back to")
    
    # History command
    history_parser = subparsers.add_parser("history", help="Show version history")
    
    # Restore point command
    restore_parser = subparsers.add_parser("restore-point", help="Create a restore point")
    restore_parser.add_argument("--description", type=str,
                               help="Description of the restore point")
    
    # Run command
    run_parser = subparsers.add_parser("run", help="Run the update system")
    run_parser.add_argument("--daemon", action="store_true",
                           help="Run as a daemon")
    
    args = parser.parse_args()
    
    # Create update system
    update_system = UpdateSystem(
        config_path=args.config,
        installation_path=args.install_path
    )
    
    if args.command == "check":
        update_info = update_system.check_for_updates()
        
        if update_info:
            print(f"Update available: {update_info.get('version')}")
            print(f"Type: {update_info.get('type', 'regular')}")
            print(f"Description: {update_info.get('description', 'No description')}")
            return 0
        else:
            print("No updates available")
            return 0
    
    elif args.command == "install":
        try:
            with open(args.metadata_file, 'r') as f:
                update_metadata = json.load(f)
            
            success = update_system.install_update(update_metadata, args.package)
            
            if success:
                print(f"Update {update_metadata.get('version')} installed successfully")
                return 0
            else:
                print("Update installation failed")
                return 1
        except Exception as e:
            print(f"Error: {e}")
            return 1
    
    elif args.command == "schedule":
        try:
            with open(args.metadata_file, 'r') as f:
                update_metadata = json.load(f)
            
            success = update_system.schedule_update(update_metadata, args.time)
            
            if success:
                print(f"Update {update_metadata.get('version')} scheduled")
                return 0
            else:
                print("Failed to schedule update")
                return 1
        except Exception as e:
            print(f"Error: {e}")
            return 1
    
    elif args.command == "rollback":
        success = update_system.rollback_to_version(args.version)
        
        if success:
            print(f"Successfully rolled back to version {args.version}")
            return 0
        else:
            print(f"Failed to roll back to version {args.version}")
            return 1
    
    elif args.command == "history":
        history = update_system.get_version_history()
        
        if history:
            print(f"Version history ({len(history)} entries):")
            for entry in history:
                print(f"Version: {entry.get('version')}")
                print(f"Date: {entry.get('date')}")
                print(f"Type: {entry.get('type', 'regular')}")
                if entry.get('notes'):
                    print(f"Notes: {entry.get('notes')}")
                print(f"Has backup: {entry.get('has_backup', False)}")
                print()
        else:
            print("No version history found")
        
        return 0
    
    elif args.command == "restore-point":
        backup_path = update_system.create_restore_point(args.description)
        
        if backup_path:
            print(f"Restore point created: {backup_path}")
            return 0
        else:
            print("Failed to create restore point")
            return 1
    
    elif args.command == "run":
        try:
            update_system.start()
            
            if args.daemon:
                print("Running as daemon")
                # Keep running
                while True:
                    time.sleep(60)
            else:
                print("Press Ctrl+C to stop")
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    pass
            
            update_system.stop()
            return 0
        except Exception as e:
            print(f"Error: {e}")
            return 1
    
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
