"""
Update Checker Module for ApexAgent.

This module provides functionality to check for available updates from
the update server, compare versions, and retrieve update metadata.
"""

import os
import json
import time
import logging
import requests
import platform
import threading
from typing import Dict, List, Optional, Tuple, Union, Any
from datetime import datetime, timedelta

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("update_checker")

class UpdateChecker:
    """
    Checks for available updates for ApexAgent.
    
    This class handles communication with the update server,
    version comparison, and update metadata retrieval.
    """
    
    def __init__(self, 
                 config_path: str = None,
                 update_url: str = None,
                 check_interval: int = 86400,  # Default: once per day
                 auto_check: bool = True):
        """
        Initialize the update checker.
        
        Args:
            config_path: Path to the configuration file
            update_url: URL of the update server (overrides config)
            check_interval: Interval between update checks in seconds
            auto_check: Whether to automatically check for updates
        """
        self.config_path = config_path or os.path.join(
            os.path.expanduser("~"), ".apexagent", "update_config.json"
        )
        self._load_config()
        
        # Override config with parameters if provided
        if update_url:
            self.update_url = update_url
        
        self.check_interval = check_interval
        self.auto_check = auto_check
        self.last_check_time = None
        self.available_updates = []
        self.update_thread = None
        self.stop_thread = False
        
        # Start automatic update checking if enabled
        if self.auto_check:
            self.start_auto_check()
    
    def _load_config(self) -> None:
        """
        Load configuration from the config file.
        
        If the config file doesn't exist, default values are used.
        """
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                
                self.update_url = config.get('update_url', 'https://updates.apexagent.example.com/api/v1/updates')
                self.current_version = config.get('current_version', '0.1.0')
                self.channel = config.get('channel', 'stable')
                self.platform = config.get('platform', self._detect_platform())
                self.architecture = config.get('architecture', self._detect_architecture())
                self.last_check_time = config.get('last_check_time')
                self.check_interval = config.get('check_interval', 86400)
                self.auto_check = config.get('auto_check', True)
                self.proxy = config.get('proxy', None)
                self.timeout = config.get('timeout', 30)
                self.installation_path = config.get('installation_path', self._detect_installation_path())
                self.update_history = config.get('update_history', [])
                
                logger.info(f"Loaded update configuration from {self.config_path}")
            else:
                logger.warning(f"Config file not found at {self.config_path}, using defaults")
                self._set_defaults()
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            self._set_defaults()
    
    def _set_defaults(self) -> None:
        """Set default configuration values."""
        self.update_url = 'https://updates.apexagent.example.com/api/v1/updates'
        self.current_version = '0.1.0'
        self.channel = 'stable'
        self.platform = self._detect_platform()
        self.architecture = self._detect_architecture()
        self.proxy = None
        self.timeout = 30
        self.installation_path = self._detect_installation_path()
        self.update_history = []
    
    def _save_config(self) -> None:
        """Save the current configuration to the config file."""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            config = {
                'update_url': self.update_url,
                'current_version': self.current_version,
                'channel': self.channel,
                'platform': self.platform,
                'architecture': self.architecture,
                'last_check_time': self.last_check_time,
                'check_interval': self.check_interval,
                'auto_check': self.auto_check,
                'proxy': self.proxy,
                'timeout': self.timeout,
                'installation_path': self.installation_path,
                'update_history': self.update_history
            }
            
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            logger.info(f"Saved update configuration to {self.config_path}")
        except Exception as e:
            logger.error(f"Error saving config: {e}")
    
    def _detect_platform(self) -> str:
        """
        Detect the current platform.
        
        Returns:
            str: Platform identifier (windows, macos, linux)
        """
        system = platform.system().lower()
        if system == "darwin":
            return "macos"
        elif system == "windows":
            return "windows"
        elif system == "linux":
            return "linux"
        else:
            logger.warning(f"Unknown platform: {system}, defaulting to linux")
            return "linux"
    
    def _detect_architecture(self) -> str:
        """
        Detect the current architecture.
        
        Returns:
            str: Architecture identifier (x86_64, arm64, etc.)
        """
        arch = platform.machine().lower()
        if arch in ["x86_64", "amd64"]:
            return "x86_64"
        elif arch in ["arm64", "aarch64"]:
            return "arm64"
        elif arch in ["i386", "i686", "x86"]:
            return "x86"
        else:
            logger.warning(f"Unknown architecture: {arch}, defaulting to x86_64")
            return "x86_64"
    
    def _detect_installation_path(self) -> str:
        """
        Detect the ApexAgent installation path.
        
        Returns:
            str: Installation path
        """
        # Try to find installation path based on platform
        if self.platform == "windows":
            # Check common Windows installation locations
            potential_paths = [
                os.path.join(os.environ.get("ProgramFiles", "C:\\Program Files"), "ApexAgent"),
                os.path.join(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"), "ApexAgent"),
                os.path.join(os.environ.get("LOCALAPPDATA", ""), "ApexAgent")
            ]
        elif self.platform == "macos":
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
        if self.platform == "windows":
            return os.path.join(os.environ.get("ProgramFiles", "C:\\Program Files"), "ApexAgent")
        elif self.platform == "macos":
            return "/Applications/ApexAgent.app"
        else:  # Linux
            return "/opt/apexagent"
    
    def start_auto_check(self) -> None:
        """Start automatic update checking in a background thread."""
        if self.update_thread is not None and self.update_thread.is_alive():
            logger.warning("Update checking thread is already running")
            return
        
        self.stop_thread = False
        self.update_thread = threading.Thread(target=self._auto_check_loop, daemon=True)
        self.update_thread.start()
        logger.info("Started automatic update checking")
    
    def stop_auto_check(self) -> None:
        """Stop automatic update checking."""
        if self.update_thread is None or not self.update_thread.is_alive():
            logger.warning("No update checking thread is running")
            return
        
        self.stop_thread = True
        self.update_thread.join(timeout=2.0)
        if self.update_thread.is_alive():
            logger.warning("Update checking thread did not stop gracefully")
        else:
            logger.info("Stopped automatic update checking")
    
    def _auto_check_loop(self) -> None:
        """Background thread for automatic update checking."""
        while not self.stop_thread:
            try:
                # Check if it's time to check for updates
                if self.last_check_time is None or (
                    datetime.now() - datetime.fromisoformat(self.last_check_time)
                ).total_seconds() >= self.check_interval:
                    logger.info("Performing automatic update check")
                    self.check_for_updates()
                
                # Sleep for a while before checking again
                # Use small sleep intervals to allow for graceful shutdown
                for _ in range(min(600, self.check_interval // 10)):
                    if self.stop_thread:
                        break
                    time.sleep(10)
            except Exception as e:
                logger.error(f"Error in automatic update check: {e}")
                # Sleep for a while before retrying
                time.sleep(300)  # 5 minutes
    
    def check_for_updates(self) -> List[Dict[str, Any]]:
        """
        Check for available updates.
        
        Returns:
            List[Dict]: List of available updates with metadata
        """
        try:
            logger.info(f"Checking for updates from {self.update_url}")
            
            # Prepare request parameters
            params = {
                'current_version': self.current_version,
                'platform': self.platform,
                'architecture': self.architecture,
                'channel': self.channel
            }
            
            # Prepare proxy configuration if needed
            proxies = None
            if self.proxy:
                proxies = {
                    'http': self.proxy,
                    'https': self.proxy
                }
            
            # Make request to update server
            response = requests.get(
                self.update_url,
                params=params,
                proxies=proxies,
                timeout=self.timeout
            )
            
            # Check if request was successful
            if response.status_code == 200:
                data = response.json()
                
                # Update last check time
                self.last_check_time = datetime.now().isoformat()
                self._save_config()
                
                # Process available updates
                if 'updates' in data and isinstance(data['updates'], list):
                    self.available_updates = data['updates']
                    
                    # Filter updates that are newer than current version
                    newer_updates = [
                        update for update in self.available_updates
                        if self.compare_versions(update['version'], self.current_version) > 0
                    ]
                    
                    if newer_updates:
                        logger.info(f"Found {len(newer_updates)} new update(s)")
                        for update in newer_updates:
                            logger.info(f"Available update: {update['version']} ({update['type']})")
                    else:
                        logger.info("No new updates available")
                    
                    return newer_updates
                else:
                    logger.warning("Invalid response format from update server")
                    return []
            else:
                logger.error(f"Failed to check for updates: HTTP {response.status_code}")
                return []
        except requests.RequestException as e:
            logger.error(f"Network error checking for updates: {e}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response from update server: {e}")
            return []
        except Exception as e:
            logger.error(f"Error checking for updates: {e}")
            return []
    
    def get_latest_update(self) -> Optional[Dict[str, Any]]:
        """
        Get the latest available update.
        
        Returns:
            Dict or None: Latest update metadata or None if no updates available
        """
        if not self.available_updates:
            self.check_for_updates()
        
        if not self.available_updates:
            return None
        
        # Find the update with the highest version number
        latest_update = max(
            self.available_updates,
            key=lambda u: self.parse_version(u['version'])
        )
        
        return latest_update
    
    def get_update_by_version(self, version: str) -> Optional[Dict[str, Any]]:
        """
        Get update metadata for a specific version.
        
        Args:
            version: Version string to look for
            
        Returns:
            Dict or None: Update metadata or None if not found
        """
        if not self.available_updates:
            self.check_for_updates()
        
        for update in self.available_updates:
            if update['version'] == version:
                return update
        
        return None
    
    def parse_version(self, version_str: str) -> Tuple[int, ...]:
        """
        Parse a version string into a tuple of integers for comparison.
        
        Args:
            version_str: Version string (e.g., "1.2.3")
            
        Returns:
            Tuple[int, ...]: Parsed version as a tuple of integers
        """
        # Handle pre-release versions (e.g., "1.2.3-beta.1")
        if '-' in version_str:
            version_part, pre_release = version_str.split('-', 1)
            
            # Parse the version part
            version_tuple = tuple(map(int, version_part.split('.')))
            
            # For pre-release versions, add a 0 component to make them sort before
            # the corresponding release version
            return version_tuple + (0,)
        else:
            # Parse regular version
            return tuple(map(int, version_str.split('.')))
    
    def compare_versions(self, version_a: str, version_b: str) -> int:
        """
        Compare two version strings.
        
        Args:
            version_a: First version string
            version_b: Second version string
            
        Returns:
            int: 1 if version_a > version_b, -1 if version_a < version_b, 0 if equal
        """
        parsed_a = self.parse_version(version_a)
        parsed_b = self.parse_version(version_b)
        
        if parsed_a > parsed_b:
            return 1
        elif parsed_a < parsed_b:
            return -1
        else:
            return 0
    
    def get_update_metadata(self, version: str = None) -> Dict[str, Any]:
        """
        Get detailed metadata for an update.
        
        Args:
            version: Version to get metadata for (default: latest)
            
        Returns:
            Dict: Update metadata
        """
        try:
            # If no version specified, use latest
            if version is None:
                update = self.get_latest_update()
                if update is None:
                    logger.warning("No updates available")
                    return {}
                version = update['version']
            
            # Prepare request parameters
            params = {
                'version': version,
                'platform': self.platform,
                'architecture': self.architecture
            }
            
            # Prepare proxy configuration if needed
            proxies = None
            if self.proxy:
                proxies = {
                    'http': self.proxy,
                    'https': self.proxy
                }
            
            # Make request to update server
            metadata_url = f"{self.update_url}/{version}/metadata"
            response = requests.get(
                metadata_url,
                params=params,
                proxies=proxies,
                timeout=self.timeout
            )
            
            # Check if request was successful
            if response.status_code == 200:
                metadata = response.json()
                logger.info(f"Retrieved metadata for version {version}")
                return metadata
            else:
                logger.error(f"Failed to get update metadata: HTTP {response.status_code}")
                return {}
        except requests.RequestException as e:
            logger.error(f"Network error getting update metadata: {e}")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response for update metadata: {e}")
            return {}
        except Exception as e:
            logger.error(f"Error getting update metadata: {e}")
            return {}
    
    def set_channel(self, channel: str) -> None:
        """
        Set the update channel.
        
        Args:
            channel: Channel name (stable, beta, dev)
        """
        if channel not in ['stable', 'beta', 'dev']:
            logger.warning(f"Invalid channel: {channel}, must be one of: stable, beta, dev")
            return
        
        self.channel = channel
        self._save_config()
        logger.info(f"Update channel set to: {channel}")
        
        # Clear cached updates and check for updates on the new channel
        self.available_updates = []
        self.check_for_updates()
    
    def set_check_interval(self, interval: int) -> None:
        """
        Set the interval between update checks.
        
        Args:
            interval: Interval in seconds
        """
        if interval < 3600:  # Minimum 1 hour
            logger.warning(f"Check interval too short: {interval}, setting to 3600 seconds (1 hour)")
            interval = 3600
        
        self.check_interval = interval
        self._save_config()
        logger.info(f"Update check interval set to: {interval} seconds")
    
    def set_auto_check(self, enabled: bool) -> None:
        """
        Enable or disable automatic update checking.
        
        Args:
            enabled: Whether to enable automatic checking
        """
        self.auto_check = enabled
        self._save_config()
        
        if enabled:
            logger.info("Automatic update checking enabled")
            self.start_auto_check()
        else:
            logger.info("Automatic update checking disabled")
            self.stop_auto_check()
    
    def set_proxy(self, proxy: str) -> None:
        """
        Set proxy for update checking.
        
        Args:
            proxy: Proxy URL (e.g., "http://proxy.example.com:8080")
        """
        self.proxy = proxy
        self._save_config()
        logger.info(f"Update proxy set to: {proxy}")
    
    def add_update_to_history(self, version: str, status: str, timestamp: str = None) -> None:
        """
        Add an update to the history.
        
        Args:
            version: Update version
            status: Update status (success, failed, rolled_back)
            timestamp: ISO format timestamp (default: current time)
        """
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        
        history_entry = {
            'version': version,
            'status': status,
            'timestamp': timestamp
        }
        
        self.update_history.append(history_entry)
        self._save_config()
        logger.info(f"Added update to history: {version} ({status})")
    
    def get_update_history(self) -> List[Dict[str, str]]:
        """
        Get the update history.
        
        Returns:
            List[Dict]: List of update history entries
        """
        return self.update_history


def main():
    """Command-line interface for update checking."""
    import argparse
    
    parser = argparse.ArgumentParser(description="ApexAgent Update Checker")
    
    parser.add_argument("--config", type=str,
                        help="Path to configuration file")
    parser.add_argument("--url", type=str,
                        help="URL of the update server")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Check command
    check_parser = subparsers.add_parser("check", help="Check for updates")
    
    # Latest command
    latest_parser = subparsers.add_parser("latest", help="Get latest update")
    
    # Metadata command
    metadata_parser = subparsers.add_parser("metadata", help="Get update metadata")
    metadata_parser.add_argument("--version", type=str,
                                help="Version to get metadata for")
    
    # Channel command
    channel_parser = subparsers.add_parser("channel", help="Set update channel")
    channel_parser.add_argument("channel", type=str, choices=["stable", "beta", "dev"],
                               help="Channel name")
    
    # Auto command
    auto_parser = subparsers.add_parser("auto", help="Configure automatic update checking")
    auto_parser.add_argument("--enable", action="store_true",
                            help="Enable automatic update checking")
    auto_parser.add_argument("--disable", action="store_true",
                            help="Disable automatic update checking")
    auto_parser.add_argument("--interval", type=int,
                            help="Interval between checks in seconds")
    
    args = parser.parse_args()
    
    # Create update checker
    checker = UpdateChecker(config_path=args.config, update_url=args.url, auto_check=False)
    
    if args.command == "check":
        updates = checker.check_for_updates()
        if updates:
            print(f"Found {len(updates)} update(s):")
            for update in updates:
                print(f"- {update['version']} ({update['type']}): {update.get('description', 'No description')}")
        else:
            print("No updates available")
    
    elif args.command == "latest":
        latest = checker.get_latest_update()
        if latest:
            print(f"Latest update: {latest['version']} ({latest['type']})")
            print(f"Description: {latest.get('description', 'No description')}")
            print(f"Release date: {latest.get('release_date', 'Unknown')}")
        else:
            print("No updates available")
    
    elif args.command == "metadata":
        metadata = checker.get_update_metadata(args.version)
        if metadata:
            print(json.dumps(metadata, indent=2))
        else:
            print("Failed to retrieve update metadata")
    
    elif args.command == "channel":
        checker.set_channel(args.channel)
        print(f"Update channel set to: {args.channel}")
    
    elif args.command == "auto":
        if args.enable:
            checker.set_auto_check(True)
            print("Automatic update checking enabled")
        elif args.disable:
            checker.set_auto_check(False)
            print("Automatic update checking disabled")
        
        if args.interval:
            checker.set_check_interval(args.interval)
            print(f"Update check interval set to: {args.interval} seconds")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
