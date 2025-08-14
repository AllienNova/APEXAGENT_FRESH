"""
Rollback Manager Module for ApexAgent.

This module provides functionality to manage version history and
perform rollbacks to previous versions when needed.
"""

import os
import json
import logging
import shutil
import platform
import subprocess
from typing import Dict, List, Optional, Tuple, Union, Any, Callable
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("rollback_manager")

class RollbackManager:
    """
    Manages version history and rollbacks for ApexAgent.
    
    This class handles tracking version history, creating restore points,
    and rolling back to previous versions when needed.
    """
    
    def __init__(self, 
                 config_path: str = None,
                 installation_path: str = None,
                 progress_callback: Callable = None):
        """
        Initialize the rollback manager.
        
        Args:
            config_path: Path to the configuration file
            installation_path: Path to the ApexAgent installation
            progress_callback: Function to call with progress updates
        """
        self.config_path = config_path or os.path.join(
            os.path.expanduser("~"), ".apexagent", "rollback_config.json"
        )
        self.installation_path = installation_path
        self.progress_callback = progress_callback
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
                
                self.backup_dir = config.get('backup_dir', os.path.join(os.path.expanduser("~"), ".apexagent", "backups"))
                self.installation_path = self.installation_path or config.get('installation_path', self._detect_installation_path())
                self.max_backups = config.get('max_backups', 5)
                self.auto_backup = config.get('auto_backup', True)
                self.backup_user_data = config.get('backup_user_data', True)
                self.version_history_file = config.get('version_history_file', os.path.join(os.path.expanduser("~"), ".apexagent", "version_history.json"))
                
                logger.info(f"Loaded rollback configuration from {self.config_path}")
            else:
                logger.warning(f"Config file not found at {self.config_path}, using defaults")
                self._set_defaults()
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            self._set_defaults()
    
    def _set_defaults(self) -> None:
        """Set default configuration values."""
        self.backup_dir = os.path.join(os.path.expanduser("~"), ".apexagent", "backups")
        self.installation_path = self.installation_path or self._detect_installation_path()
        self.max_backups = 5
        self.auto_backup = True
        self.backup_user_data = True
        self.version_history_file = os.path.join(os.path.expanduser("~"), ".apexagent", "version_history.json")
    
    def _save_config(self) -> None:
        """Save the current configuration to the config file."""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            config = {
                'backup_dir': self.backup_dir,
                'installation_path': self.installation_path,
                'max_backups': self.max_backups,
                'auto_backup': self.auto_backup,
                'backup_user_data': self.backup_user_data,
                'version_history_file': self.version_history_file
            }
            
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            logger.info(f"Saved rollback configuration to {self.config_path}")
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
    
    def _report_progress(self, stage: str, progress: float, message: str) -> None:
        """
        Report progress to the callback function.
        
        Args:
            stage: Current stage of the rollback process
            progress: Progress as a percentage (0-100)
            message: Progress message
        """
        if self.progress_callback:
            try:
                self.progress_callback(stage, progress, message)
            except Exception as e:
                logger.error(f"Error in progress callback: {e}")
        
        logger.info(f"[{stage}] {progress:.1f}%: {message}")
    
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
    
    def get_version_history(self) -> List[Dict[str, Any]]:
        """
        Get the version history.
        
        Returns:
            List[Dict[str, Any]]: Version history
        """
        try:
            if os.path.exists(self.version_history_file):
                with open(self.version_history_file, 'r') as f:
                    history = json.load(f)
                return history
            else:
                logger.warning(f"Version history file not found: {self.version_history_file}")
                return []
        except Exception as e:
            logger.error(f"Error reading version history: {e}")
            return []
    
    def add_version_to_history(self, version: str, update_type: str = "regular", notes: str = None) -> bool:
        """
        Add a version to the version history.
        
        Args:
            version: Version number
            update_type: Type of update (regular, security, recommended)
            notes: Additional notes about the version
            
        Returns:
            bool: True if successful
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.version_history_file), exist_ok=True)
            
            # Load existing history or create new
            history = self.get_version_history()
            
            # Check if version already exists
            for entry in history:
                if entry.get('version') == version:
                    logger.warning(f"Version {version} already exists in history")
                    return False
            
            # Add new version
            history.append({
                'version': version,
                'date': datetime.now().isoformat(),
                'type': update_type,
                'notes': notes,
                'has_backup': False,
                'backup_path': None
            })
            
            # Sort history by date (newest first)
            history.sort(key=lambda x: x.get('date', ''), reverse=True)
            
            # Save history
            with open(self.version_history_file, 'w') as f:
                json.dump(history, f, indent=2)
            
            logger.info(f"Added version {version} to history")
            return True
        except Exception as e:
            logger.error(f"Error adding version to history: {e}")
            return False
    
    def create_restore_point(self, version: str = None, description: str = None) -> Optional[str]:
        """
        Create a restore point for the current installation.
        
        Args:
            version: Version to associate with the restore point (defaults to current)
            description: Description of the restore point
            
        Returns:
            str or None: Path to the backup directory, or None if failed
        """
        self._report_progress("backup", 0, "Creating restore point")
        
        try:
            # Get current version if not specified
            if not version:
                version = self.get_current_version()
            
            # Create backup directory
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"apexagent_{version}_{timestamp}"
            backup_path = os.path.join(self.backup_dir, backup_name)
            
            # Ensure backup directory exists
            os.makedirs(self.backup_dir, exist_ok=True)
            os.makedirs(backup_path, exist_ok=True)
            
            # Save backup metadata
            metadata = {
                'version': version,
                'timestamp': timestamp,
                'description': description or f"Restore point for version {version}",
                'platform': platform.system().lower(),
                'architecture': platform.machine().lower(),
                'installation_path': self.installation_path
            }
            
            with open(os.path.join(backup_path, "backup_metadata.json"), 'w') as f:
                json.dump(metadata, f, indent=2)
            
            # Copy installation files
            self._report_progress("backup", 10, "Copying installation files")
            
            # Determine which files/directories to backup
            # This is platform-specific
            system = platform.system().lower()
            
            if system == "darwin":  # macOS
                # For macOS, copy the entire .app bundle
                if self.installation_path.endswith(".app"):
                    app_name = os.path.basename(self.installation_path)
                    backup_app_path = os.path.join(backup_path, app_name)
                    shutil.copytree(self.installation_path, backup_app_path, symlinks=True)
                else:
                    # Not an app bundle, copy everything
                    for item in os.listdir(self.installation_path):
                        src = os.path.join(self.installation_path, item)
                        dst = os.path.join(backup_path, item)
                        
                        if os.path.isdir(src):
                            shutil.copytree(src, dst, symlinks=True)
                        else:
                            shutil.copy2(src, dst)
            else:
                # For Windows and Linux, copy everything except specific directories
                exclude_dirs = ['logs', 'temp', 'cache']
                
                # If not backing up user data, exclude it
                if not self.backup_user_data:
                    exclude_dirs.append('user_data')
                
                for item in os.listdir(self.installation_path):
                    if item in exclude_dirs:
                        continue
                    
                    src = os.path.join(self.installation_path, item)
                    dst = os.path.join(backup_path, item)
                    
                    try:
                        if os.path.isdir(src):
                            shutil.copytree(src, dst, symlinks=True)
                        else:
                            shutil.copy2(src, dst)
                    except Exception as e:
                        logger.warning(f"Failed to backup {src}: {e}")
            
            # Update version history
            history = self.get_version_history()
            for entry in history:
                if entry.get('version') == version:
                    entry['has_backup'] = True
                    entry['backup_path'] = backup_path
                    break
            
            # Save updated history
            with open(self.version_history_file, 'w') as f:
                json.dump(history, f, indent=2)
            
            # Clean up old backups if needed
            self._cleanup_old_backups()
            
            self._report_progress("backup", 100, f"Restore point created: {backup_path}")
            return backup_path
        
        except Exception as e:
            logger.error(f"Error creating restore point: {e}")
            return None
    
    def _cleanup_old_backups(self) -> None:
        """
        Clean up old backups, keeping only the most recent ones.
        """
        try:
            # Get all backups
            backups = []
            
            if os.path.exists(self.backup_dir):
                for item in os.listdir(self.backup_dir):
                    item_path = os.path.join(self.backup_dir, item)
                    if os.path.isdir(item_path) and item.startswith("apexagent_"):
                        # Get metadata if available
                        metadata_file = os.path.join(item_path, "backup_metadata.json")
                        timestamp = None
                        
                        if os.path.exists(metadata_file):
                            try:
                                with open(metadata_file, 'r') as f:
                                    metadata = json.load(f)
                                timestamp = metadata.get('timestamp')
                            except Exception:
                                pass
                        
                        # If no timestamp in metadata, try to extract from directory name
                        if not timestamp:
                            parts = item.split('_')
                            if len(parts) >= 3:
                                timestamp = parts[-2] + '_' + parts[-1]
                        
                        backups.append((item_path, timestamp or ''))
            
            # Sort backups by timestamp (newest first)
            backups.sort(key=lambda x: x[1], reverse=True)
            
            # Remove old backups
            if len(backups) > self.max_backups:
                for backup_path, _ in backups[self.max_backups:]:
                    try:
                        shutil.rmtree(backup_path)
                        logger.info(f"Removed old backup: {backup_path}")
                    except Exception as e:
                        logger.error(f"Error removing old backup {backup_path}: {e}")
        
        except Exception as e:
            logger.error(f"Error cleaning up old backups: {e}")
    
    def get_available_restore_points(self) -> List[Dict[str, Any]]:
        """
        Get a list of available restore points.
        
        Returns:
            List[Dict[str, Any]]: List of restore points
        """
        restore_points = []
        
        try:
            if os.path.exists(self.backup_dir):
                for item in os.listdir(self.backup_dir):
                    item_path = os.path.join(self.backup_dir, item)
                    if os.path.isdir(item_path) and item.startswith("apexagent_"):
                        metadata_file = os.path.join(item_path, "backup_metadata.json")
                        
                        if os.path.exists(metadata_file):
                            try:
                                with open(metadata_file, 'r') as f:
                                    metadata = json.load(f)
                                
                                restore_points.append({
                                    'path': item_path,
                                    'version': metadata.get('version', 'unknown'),
                                    'timestamp': metadata.get('timestamp', ''),
                                    'description': metadata.get('description', ''),
                                    'platform': metadata.get('platform', ''),
                                    'architecture': metadata.get('architecture', '')
                                })
                            except Exception as e:
                                logger.error(f"Error reading metadata for {item_path}: {e}")
            
            # Sort restore points by timestamp (newest first)
            restore_points.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            return restore_points
        
        except Exception as e:
            logger.error(f"Error getting restore points: {e}")
            return []
    
    def rollback_to_version(self, version: str) -> bool:
        """
        Roll back to a specific version.
        
        Args:
            version: Version to roll back to
            
        Returns:
            bool: True if rollback was successful
        """
        self._report_progress("rollback", 0, f"Rolling back to version {version}")
        
        try:
            # Find backup for the specified version
            restore_points = self.get_available_restore_points()
            backup_path = None
            
            for point in restore_points:
                if point.get('version') == version:
                    backup_path = point.get('path')
                    break
            
            if not backup_path:
                logger.error(f"No backup found for version {version}")
                return False
            
            # Create backup of current version if auto-backup is enabled
            if self.auto_backup:
                self._report_progress("rollback", 10, "Creating backup of current version")
                current_version = self.get_current_version()
                self.create_restore_point(current_version, f"Auto-backup before rollback to {version}")
            
            # Perform rollback
            self._report_progress("rollback", 20, f"Restoring from backup: {backup_path}")
            
            # Check if backup exists
            if not os.path.exists(backup_path):
                logger.error(f"Backup not found: {backup_path}")
                return False
            
            # Check backup metadata
            metadata_file = os.path.join(backup_path, "backup_metadata.json")
            if not os.path.exists(metadata_file):
                logger.error(f"Backup metadata not found: {metadata_file}")
                return False
            
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            # Verify backup is compatible with current system
            system = platform.system().lower()
            if system == "darwin":
                system = "macos"
            
            if metadata.get('platform') != system:
                logger.error(f"Backup platform mismatch: {metadata.get('platform')} vs {system}")
                return False
            
            # Clear installation directory (except specific directories)
            self._report_progress("rollback", 30, "Clearing installation directory")
            
            preserve_dirs = ['logs', 'temp', 'cache']
            
            # If not backing up user data, preserve it during rollback
            if not self.backup_user_data:
                preserve_dirs.append('user_data')
            
            for item in os.listdir(self.installation_path):
                if item in preserve_dirs:
                    continue
                
                path = os.path.join(self.installation_path, item)
                try:
                    if os.path.isdir(path):
                        shutil.rmtree(path)
                    else:
                        os.remove(path)
                except Exception as e:
                    logger.warning(f"Failed to remove {path}: {e}")
            
            # Copy files from backup to installation directory
            self._report_progress("rollback", 50, "Copying files from backup")
            
            # Special handling for macOS .app bundles
            if system == "macos" and self.installation_path.endswith(".app"):
                app_name = os.path.basename(self.installation_path)
                backup_app_path = os.path.join(backup_path, app_name)
                
                if os.path.exists(backup_app_path):
                    # Copy the entire app bundle
                    if os.path.exists(self.installation_path):
                        shutil.rmtree(self.installation_path)
                    shutil.copytree(backup_app_path, self.installation_path, symlinks=True)
                else:
                    # No app bundle in backup, copy contents
                    for item in os.listdir(backup_path):
                        if item == "backup_metadata.json":
                            continue
                        
                        src = os.path.join(backup_path, item)
                        dst = os.path.join(self.installation_path, item)
                        
                        if os.path.isdir(src):
                            if os.path.exists(dst):
                                shutil.rmtree(dst)
                            shutil.copytree(src, dst, symlinks=True)
                        else:
                            shutil.copy2(src, dst)
            else:
                # For Windows and Linux, copy everything except metadata
                for item in os.listdir(backup_path):
                    if item == "backup_metadata.json":
                        continue
                    
                    src = os.path.join(backup_path, item)
                    dst = os.path.join(self.installation_path, item)
                    
                    if os.path.isdir(src):
                        if os.path.exists(dst):
                            shutil.rmtree(dst)
                        shutil.copytree(src, dst, symlinks=True)
                    else:
                        shutil.copy2(src, dst)
            
            self._report_progress("rollback", 80, "Files restored from backup")
            
            # Update version history to mark current version
            history = self.get_version_history()
            for entry in history:
                if entry.get('version') == version:
                    entry['current'] = True
                else:
                    entry['current'] = False
            
            # Save updated history
            with open(self.version_history_file, 'w') as f:
                json.dump(history, f, indent=2)
            
            self._report_progress("rollback", 100, f"Rollback to version {version} complete")
            return True
        
        except Exception as e:
            logger.error(f"Error rolling back to version {version}: {e}")
            return False
    
    def rollback_to_restore_point(self, restore_point_path: str) -> bool:
        """
        Roll back to a specific restore point.
        
        Args:
            restore_point_path: Path to the restore point
            
        Returns:
            bool: True if rollback was successful
        """
        self._report_progress("rollback", 0, f"Rolling back to restore point: {restore_point_path}")
        
        try:
            # Check if restore point exists
            if not os.path.exists(restore_point_path):
                logger.error(f"Restore point not found: {restore_point_path}")
                return False
            
            # Check restore point metadata
            metadata_file = os.path.join(restore_point_path, "backup_metadata.json")
            if not os.path.exists(metadata_file):
                logger.error(f"Restore point metadata not found: {metadata_file}")
                return False
            
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            version = metadata.get('version', 'unknown')
            
            # Create backup of current version if auto-backup is enabled
            if self.auto_backup:
                self._report_progress("rollback", 10, "Creating backup of current version")
                current_version = self.get_current_version()
                self.create_restore_point(current_version, f"Auto-backup before rollback to restore point")
            
            # Perform rollback
            self._report_progress("rollback", 20, f"Restoring from restore point: {restore_point_path}")
            
            # Verify restore point is compatible with current system
            system = platform.system().lower()
            if system == "darwin":
                system = "macos"
            
            if metadata.get('platform') != system:
                logger.error(f"Restore point platform mismatch: {metadata.get('platform')} vs {system}")
                return False
            
            # Clear installation directory (except specific directories)
            self._report_progress("rollback", 30, "Clearing installation directory")
            
            preserve_dirs = ['logs', 'temp', 'cache']
            
            # If not backing up user data, preserve it during rollback
            if not self.backup_user_data:
                preserve_dirs.append('user_data')
            
            for item in os.listdir(self.installation_path):
                if item in preserve_dirs:
                    continue
                
                path = os.path.join(self.installation_path, item)
                try:
                    if os.path.isdir(path):
                        shutil.rmtree(path)
                    else:
                        os.remove(path)
                except Exception as e:
                    logger.warning(f"Failed to remove {path}: {e}")
            
            # Copy files from restore point to installation directory
            self._report_progress("rollback", 50, "Copying files from restore point")
            
            # Special handling for macOS .app bundles
            if system == "macos" and self.installation_path.endswith(".app"):
                app_name = os.path.basename(self.installation_path)
                backup_app_path = os.path.join(restore_point_path, app_name)
                
                if os.path.exists(backup_app_path):
                    # Copy the entire app bundle
                    if os.path.exists(self.installation_path):
                        shutil.rmtree(self.installation_path)
                    shutil.copytree(backup_app_path, self.installation_path, symlinks=True)
                else:
                    # No app bundle in backup, copy contents
                    for item in os.listdir(restore_point_path):
                        if item == "backup_metadata.json":
                            continue
                        
                        src = os.path.join(restore_point_path, item)
                        dst = os.path.join(self.installation_path, item)
                        
                        if os.path.isdir(src):
                            if os.path.exists(dst):
                                shutil.rmtree(dst)
                            shutil.copytree(src, dst, symlinks=True)
                        else:
                            shutil.copy2(src, dst)
            else:
                # For Windows and Linux, copy everything except metadata
                for item in os.listdir(restore_point_path):
                    if item == "backup_metadata.json":
                        continue
                    
                    src = os.path.join(restore_point_path, item)
                    dst = os.path.join(self.installation_path, item)
                    
                    if os.path.isdir(src):
                        if os.path.exists(dst):
                            shutil.rmtree(dst)
                        shutil.copytree(src, dst, symlinks=True)
                    else:
                        shutil.copy2(src, dst)
            
            self._report_progress("rollback", 80, "Files restored from restore point")
            
            # Update version history to mark current version
            history = self.get_version_history()
            for entry in history:
                if entry.get('version') == version:
                    entry['current'] = True
                else:
                    entry['current'] = False
            
            # Save updated history
            with open(self.version_history_file, 'w') as f:
                json.dump(history, f, indent=2)
            
            self._report_progress("rollback", 100, f"Rollback to restore point complete (version {version})")
            return True
        
        except Exception as e:
            logger.error(f"Error rolling back to restore point: {e}")
            return False
    
    def delete_restore_point(self, restore_point_path: str) -> bool:
        """
        Delete a restore point.
        
        Args:
            restore_point_path: Path to the restore point
            
        Returns:
            bool: True if deletion was successful
        """
        try:
            # Check if restore point exists
            if not os.path.exists(restore_point_path):
                logger.error(f"Restore point not found: {restore_point_path}")
                return False
            
            # Get metadata to update version history
            metadata_file = os.path.join(restore_point_path, "backup_metadata.json")
            version = None
            
            if os.path.exists(metadata_file):
                try:
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                    version = metadata.get('version')
                except Exception:
                    pass
            
            # Delete the restore point
            shutil.rmtree(restore_point_path)
            logger.info(f"Deleted restore point: {restore_point_path}")
            
            # Update version history if version was found
            if version:
                history = self.get_version_history()
                for entry in history:
                    if entry.get('version') == version and entry.get('backup_path') == restore_point_path:
                        entry['has_backup'] = False
                        entry['backup_path'] = None
                
                # Save updated history
                with open(self.version_history_file, 'w') as f:
                    json.dump(history, f, indent=2)
            
            return True
        
        except Exception as e:
            logger.error(f"Error deleting restore point: {e}")
            return False
    
    def set_max_backups(self, max_backups: int) -> None:
        """
        Set the maximum number of backups to keep.
        
        Args:
            max_backups: Maximum number of backups
        """
        if max_backups < 1:
            logger.warning(f"Invalid max_backups value: {max_backups}, using 1")
            max_backups = 1
        
        self.max_backups = max_backups
        self._save_config()
        
        # Clean up old backups if needed
        self._cleanup_old_backups()
        
        logger.info(f"Set max_backups to {max_backups}")
    
    def set_auto_backup(self, enabled: bool) -> None:
        """
        Enable or disable automatic backups before updates.
        
        Args:
            enabled: Whether to enable automatic backups
        """
        self.auto_backup = enabled
        self._save_config()
        
        logger.info(f"Set auto_backup to {enabled}")
    
    def set_backup_user_data(self, enabled: bool) -> None:
        """
        Enable or disable backing up user data.
        
        Args:
            enabled: Whether to back up user data
        """
        self.backup_user_data = enabled
        self._save_config()
        
        logger.info(f"Set backup_user_data to {enabled}")


def main():
    """Command-line interface for rollback management."""
    import argparse
    
    parser = argparse.ArgumentParser(description="ApexAgent Rollback Manager")
    
    parser.add_argument("--config", type=str,
                        help="Path to configuration file")
    parser.add_argument("--install-path", type=str,
                        help="Path to ApexAgent installation")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Create restore point command
    create_parser = subparsers.add_parser("create", help="Create a restore point")
    create_parser.add_argument("--version", type=str,
                              help="Version to associate with the restore point")
    create_parser.add_argument("--description", type=str,
                              help="Description of the restore point")
    
    # List restore points command
    list_parser = subparsers.add_parser("list", help="List available restore points")
    
    # Rollback command
    rollback_parser = subparsers.add_parser("rollback", help="Roll back to a previous version")
    rollback_group = rollback_parser.add_mutually_exclusive_group(required=True)
    rollback_group.add_argument("--version", type=str,
                               help="Version to roll back to")
    rollback_group.add_argument("--restore-point", type=str,
                               help="Path to restore point")
    
    # Delete restore point command
    delete_parser = subparsers.add_parser("delete", help="Delete a restore point")
    delete_parser.add_argument("--restore-point", type=str, required=True,
                              help="Path to restore point")
    
    # Configure command
    config_parser = subparsers.add_parser("config", help="Configure rollback manager")
    config_parser.add_argument("--max-backups", type=int,
                              help="Maximum number of backups to keep")
    config_parser.add_argument("--auto-backup", type=str, choices=["enable", "disable"],
                              help="Enable or disable automatic backups")
    config_parser.add_argument("--backup-user-data", type=str, choices=["enable", "disable"],
                              help="Enable or disable backing up user data")
    
    args = parser.parse_args()
    
    # Create rollback manager
    manager = RollbackManager(config_path=args.config, installation_path=args.install_path)
    
    if args.command == "create":
        backup_path = manager.create_restore_point(args.version, args.description)
        
        if backup_path:
            print(f"Restore point created: {backup_path}")
            return 0
        else:
            print("Failed to create restore point")
            return 1
    
    elif args.command == "list":
        restore_points = manager.get_available_restore_points()
        
        if restore_points:
            print(f"Found {len(restore_points)} restore point(s):")
            for i, point in enumerate(restore_points):
                print(f"{i+1}. Version: {point['version']}")
                print(f"   Date: {point['timestamp']}")
                print(f"   Description: {point['description']}")
                print(f"   Path: {point['path']}")
                print()
        else:
            print("No restore points found")
        
        return 0
    
    elif args.command == "rollback":
        if args.version:
            success = manager.rollback_to_version(args.version)
            
            if success:
                print(f"Successfully rolled back to version {args.version}")
                return 0
            else:
                print(f"Failed to roll back to version {args.version}")
                return 1
        
        elif args.restore_point:
            success = manager.rollback_to_restore_point(args.restore_point)
            
            if success:
                print(f"Successfully rolled back to restore point: {args.restore_point}")
                return 0
            else:
                print(f"Failed to roll back to restore point: {args.restore_point}")
                return 1
    
    elif args.command == "delete":
        success = manager.delete_restore_point(args.restore_point)
        
        if success:
            print(f"Restore point deleted: {args.restore_point}")
            return 0
        else:
            print(f"Failed to delete restore point: {args.restore_point}")
            return 1
    
    elif args.command == "config":
        if args.max_backups is not None:
            manager.set_max_backups(args.max_backups)
            print(f"Set maximum backups to {args.max_backups}")
        
        if args.auto_backup:
            enabled = args.auto_backup == "enable"
            manager.set_auto_backup(enabled)
            print(f"{'Enabled' if enabled else 'Disabled'} automatic backups")
        
        if args.backup_user_data:
            enabled = args.backup_user_data == "enable"
            manager.set_backup_user_data(enabled)
            print(f"{'Enabled' if enabled else 'Disabled'} backing up user data")
        
        return 0
    
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
