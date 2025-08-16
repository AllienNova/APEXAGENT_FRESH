#!/usr/bin/env python3
"""
Installation Manager for ApexAgent

This module provides the core functionality for installing ApexAgent across
different platforms (Windows, macOS, Linux) with robust error handling,
dependency resolution, and configuration management.
"""

import os
import sys
import platform
import logging
import shutil
import subprocess
import json
import hashlib
import tempfile
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any
from enum import Enum
import pkg_resources

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("installation.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("installation_manager")

class PlatformType(Enum):
    """Enumeration of supported platforms."""
    WINDOWS = "windows"
    MACOS = "macos"
    LINUX = "linux"
    UNKNOWN = "unknown"

class InstallationStatus(Enum):
    """Enumeration of installation status codes."""
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"
    IN_PROGRESS = "in_progress"
    NOT_STARTED = "not_started"

class InstallationError(Exception):
    """Base exception for installation errors."""
    pass

class DependencyError(InstallationError):
    """Exception raised for dependency resolution errors."""
    pass

class ConfigurationError(InstallationError):
    """Exception raised for configuration errors."""
    pass

class PermissionError(InstallationError):
    """Exception raised for permission-related errors."""
    pass

class VerificationError(InstallationError):
    """Exception raised for verification errors."""
    pass

class InstallationManager:
    """
    Manages the installation process for ApexAgent across different platforms.
    
    This class handles platform detection, dependency resolution, configuration
    generation, and installation verification.
    """
    
    def __init__(self, config_path: Optional[str] = None, 
                 install_dir: Optional[str] = None,
                 verbose: bool = False):
        """
        Initialize the Installation Manager.
        
        Args:
            config_path: Path to the configuration file
            install_dir: Target installation directory
            verbose: Enable verbose logging
        """
        self.config_path = config_path
        self.install_dir = install_dir
        self.verbose = verbose
        self.platform = self._detect_platform()
        self.config = self._load_config()
        self.status = InstallationStatus.NOT_STARTED
        self.dependencies = []
        self.installed_components = []
        
        if verbose:
            logger.setLevel(logging.DEBUG)
        
        logger.info(f"Installation Manager initialized for platform: {self.platform.value}")
        logger.debug(f"Configuration loaded from: {config_path}")
        logger.debug(f"Installation directory: {install_dir}")
    
    def _detect_platform(self) -> PlatformType:
        """
        Detect the current platform.
        
        Returns:
            PlatformType: The detected platform
        """
        system = platform.system().lower()
        
        if system == "windows":
            return PlatformType.WINDOWS
        elif system == "darwin":
            return PlatformType.MACOS
        elif system == "linux":
            return PlatformType.LINUX
        else:
            logger.warning(f"Unknown platform detected: {system}")
            return PlatformType.UNKNOWN
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load the installation configuration.
        
        Returns:
            Dict: The loaded configuration
        
        Raises:
            ConfigurationError: If the configuration cannot be loaded
        """
        if not self.config_path:
            # Use default configuration path based on platform
            if self.platform == PlatformType.WINDOWS:
                self.config_path = os.path.join(os.environ.get("APPDATA", ""), 
                                               "ApexAgent", "config", "installation.json")
            elif self.platform == PlatformType.MACOS:
                self.config_path = os.path.join(os.path.expanduser("~"), 
                                               "Library", "Application Support", 
                                               "ApexAgent", "config", "installation.json")
            else:  # Linux or unknown
                self.config_path = os.path.join(os.path.expanduser("~"), 
                                               ".config", "ApexAgent", "installation.json")
        
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                logger.debug(f"Configuration loaded successfully from {self.config_path}")
                return config
            else:
                logger.info(f"Configuration file not found at {self.config_path}, using defaults")
                return self._get_default_config()
        except Exception as e:
            logger.error(f"Failed to load configuration: {str(e)}")
            raise ConfigurationError(f"Failed to load configuration: {str(e)}")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """
        Get the default configuration.
        
        Returns:
            Dict: The default configuration
        """
        # Default configuration with platform-specific settings
        default_config = {
            "version": "1.0.0",
            "components": [
                {
                    "name": "core",
                    "required": True,
                    "version": "1.0.0",
                    "dependencies": []
                },
                {
                    "name": "plugins",
                    "required": True,
                    "version": "1.0.0",
                    "dependencies": ["core"]
                },
                {
                    "name": "ui",
                    "required": True,
                    "version": "1.0.0",
                    "dependencies": ["core"]
                },
                {
                    "name": "dr_tardis",
                    "required": False,
                    "version": "1.0.0",
                    "dependencies": ["core", "plugins", "ui"]
                }
            ],
            "dependencies": {
                "python": ">=3.8",
                "packages": [
                    "requests>=2.25.0",
                    "pynacl>=1.4.0",
                    "cryptography>=3.4.0"
                ]
            },
            "platforms": {
                "windows": {
                    "install_dir": os.path.join(os.environ.get("PROGRAMFILES", "C:\\Program Files"), "ApexAgent"),
                    "data_dir": os.path.join(os.environ.get("APPDATA", ""), "ApexAgent"),
                    "dependencies": {
                        "packages": ["pywin32>=300"]
                    }
                },
                "macos": {
                    "install_dir": "/Applications/ApexAgent.app",
                    "data_dir": os.path.join(os.path.expanduser("~"), "Library", "Application Support", "ApexAgent"),
                    "dependencies": {}
                },
                "linux": {
                    "install_dir": "/opt/ApexAgent",
                    "data_dir": os.path.join(os.path.expanduser("~"), ".ApexAgent"),
                    "dependencies": {}
                }
            }
        }
        
        return default_config
    
    def set_install_directory(self, install_dir: str) -> None:
        """
        Set the installation directory.
        
        Args:
            install_dir: The installation directory path
        """
        self.install_dir = install_dir
        logger.info(f"Installation directory set to: {install_dir}")
    
    def check_system_requirements(self) -> bool:
        """
        Check if the system meets the minimum requirements.
        
        Returns:
            bool: True if requirements are met, False otherwise
        """
        logger.info("Checking system requirements...")
        
        # Check Python version
        python_req = self.config.get("dependencies", {}).get("python", ">=3.6")
        python_version = platform.python_version()
        
        if not self._check_version_requirement(python_version, python_req):
            logger.error(f"Python version requirement not met: {python_req}, found {python_version}")
            return False
        
        # Check disk space
        if self.install_dir:
            required_space = self.config.get("system_requirements", {}).get("disk_space_mb", 500)
            available_space = self._get_available_disk_space(self.install_dir)
            
            if available_space < required_space:
                logger.error(f"Insufficient disk space: {available_space}MB available, {required_space}MB required")
                return False
        
        # Check memory
        required_memory = self.config.get("system_requirements", {}).get("memory_mb", 1024)
        available_memory = self._get_available_memory()
        
        if available_memory < required_memory:
            logger.warning(f"Low memory: {available_memory}MB available, {required_memory}MB recommended")
        
        logger.info("System requirements check passed")
        return True
    
    def _check_version_requirement(self, version: str, requirement: str) -> bool:
        """
        Check if a version meets a requirement.
        
        Args:
            version: The version to check
            requirement: The version requirement (e.g., ">=3.6")
            
        Returns:
            bool: True if the requirement is met, False otherwise
        """
        try:
            return pkg_resources.parse_version(version) in pkg_resources.Requirement.parse(f"dummy{requirement}")
        except Exception as e:
            logger.error(f"Error checking version requirement: {str(e)}")
            return False
    
    def _get_available_disk_space(self, path: str) -> int:
        """
        Get available disk space in MB.
        
        Args:
            path: The path to check
            
        Returns:
            int: Available disk space in MB
        """
        try:
            if self.platform == PlatformType.WINDOWS:
                import ctypes
                free_bytes = ctypes.c_ulonglong(0)
                ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                    ctypes.c_wchar_p(path), None, None, ctypes.pointer(free_bytes))
                return free_bytes.value // (1024 * 1024)
            else:
                stat = os.statvfs(path)
                return (stat.f_bavail * stat.f_frsize) // (1024 * 1024)
        except Exception as e:
            logger.error(f"Error checking disk space: {str(e)}")
            return 0
    
    def _get_available_memory(self) -> int:
        """
        Get available system memory in MB.
        
        Returns:
            int: Available memory in MB
        """
        try:
            if self.platform == PlatformType.WINDOWS:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                stat = ctypes.c_ulonglong(0)
                kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
                return stat.ullAvailPhys // (1024 * 1024)
            elif self.platform == PlatformType.MACOS or self.platform == PlatformType.LINUX:
                # Use psutil if available, otherwise fallback to subprocess
                try:
                    import psutil
                    return psutil.virtual_memory().available // (1024 * 1024)
                except ImportError:
                    if self.platform == PlatformType.MACOS:
                        cmd = ["sysctl", "-n", "hw.memsize"]
                    else:  # Linux
                        cmd = ["free", "-m"]
                    
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    if result.returncode == 0:
                        if self.platform == PlatformType.MACOS:
                            return int(result.stdout.strip()) // (1024 * 1024)
                        else:  # Linux
                            lines = result.stdout.strip().split('\n')
                            if len(lines) >= 2:
                                parts = lines[1].split()
                                if len(parts) >= 7:
                                    return int(parts[6])
            
            # Fallback
            return 1024  # Assume 1GB if we can't determine
        except Exception as e:
            logger.error(f"Error checking memory: {str(e)}")
            return 1024  # Fallback to 1GB
    
    def check_dependencies(self) -> bool:
        """
        Check if all required dependencies are available.
        
        Returns:
            bool: True if all dependencies are available, False otherwise
        """
        logger.info("Checking dependencies...")
        
        # Get platform-specific dependencies
        platform_deps = self.config.get("platforms", {}).get(
            self.platform.value, {}).get("dependencies", {})
        
        # Merge with common dependencies
        all_deps = self.config.get("dependencies", {}).copy()
        for key, value in platform_deps.items():
            if key in all_deps and isinstance(all_deps[key], list) and isinstance(value, list):
                all_deps[key] = all_deps[key] + value
            else:
                all_deps[key] = value
        
        # Check Python package dependencies
        packages = all_deps.get("packages", [])
        missing_packages = []
        
        for package_req in packages:
            package_name = package_req.split(">=")[0].split("==")[0].split("<")[0].strip()
            try:
                pkg_resources.get_distribution(package_name)
                logger.debug(f"Package dependency satisfied: {package_req}")
            except pkg_resources.DistributionNotFound:
                logger.warning(f"Missing package dependency: {package_req}")
                missing_packages.append(package_req)
        
        # Store dependencies for later installation
        self.dependencies = missing_packages
        
        if missing_packages:
            logger.warning(f"Missing dependencies: {', '.join(missing_packages)}")
            return False
        
        logger.info("All dependencies satisfied")
        return True
    
    def install_dependencies(self) -> bool:
        """
        Install missing dependencies.
        
        Returns:
            bool: True if all dependencies were installed successfully, False otherwise
        """
        if not self.dependencies:
            logger.info("No dependencies to install")
            return True
        
        logger.info(f"Installing {len(self.dependencies)} dependencies...")
        
        try:
            # Use pip to install dependencies
            for package in self.dependencies:
                logger.info(f"Installing {package}...")
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", package],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode != 0:
                    logger.error(f"Failed to install {package}: {result.stderr}")
                    return False
                
                logger.info(f"Successfully installed {package}")
            
            logger.info("All dependencies installed successfully")
            return True
        except Exception as e:
            logger.error(f"Error installing dependencies: {str(e)}")
            return False
    
    def prepare_installation(self) -> bool:
        """
        Prepare for installation by creating directories and validating permissions.
        
        Returns:
            bool: True if preparation was successful, False otherwise
        """
        logger.info("Preparing for installation...")
        
        # Determine installation directory if not specified
        if not self.install_dir:
            platform_config = self.config.get("platforms", {}).get(self.platform.value, {})
            self.install_dir = platform_config.get("install_dir")
            
            if not self.install_dir:
                logger.error("Installation directory not specified and no default available")
                return False
        
        logger.info(f"Installation directory: {self.install_dir}")
        
        # Check if directory exists and create if necessary
        try:
            if not os.path.exists(self.install_dir):
                os.makedirs(self.install_dir)
                logger.info(f"Created installation directory: {self.install_dir}")
            
            # Check write permissions
            test_file = os.path.join(self.install_dir, ".write_test")
            try:
                with open(test_file, 'w') as f:
                    f.write("test")
                os.remove(test_file)
            except Exception as e:
                logger.error(f"No write permission to installation directory: {str(e)}")
                return False
            
            # Create component directories
            for component in self.config.get("components", []):
                component_dir = os.path.join(self.install_dir, component["name"])
                if not os.path.exists(component_dir):
                    os.makedirs(component_dir)
                    logger.debug(f"Created component directory: {component_dir}")
            
            logger.info("Installation preparation completed successfully")
            return True
        except Exception as e:
            logger.error(f"Error preparing installation: {str(e)}")
            return False
    
    def download_components(self) -> bool:
        """
        Download installation components.
        
        Returns:
            bool: True if all components were downloaded successfully, False otherwise
        """
        logger.info("Downloading components...")
        
        # Get download URLs from configuration
        download_base_url = self.config.get("download", {}).get("base_url")
        if not download_base_url:
            logger.error("Download base URL not specified in configuration")
            return False
        
        # Create temporary directory for downloads
        temp_dir = tempfile.mkdtemp()
        logger.debug(f"Created temporary directory for downloads: {temp_dir}")
        
        try:
            # Download each component
            for component in self.config.get("components", []):
                component_name = component["name"]
                component_version = component["version"]
                component_url = f"{download_base_url}/{component_name}-{component_version}-{self.platform.value}.zip"
                component_file = os.path.join(temp_dir, f"{component_name}.zip")
                
                logger.info(f"Downloading {component_name} from {component_url}...")
                
                try:
                    urllib.request.urlretrieve(component_url, component_file)
                    
                    # Verify download
                    if not os.path.exists(component_file) or os.path.getsize(component_file) == 0:
                        logger.error(f"Failed to download {component_name}")
                        return False
                    
                    logger.info(f"Successfully downloaded {component_name}")
                except Exception as e:
                    logger.error(f"Error downloading {component_name}: {str(e)}")
                    return False
            
            logger.info("All components downloaded successfully")
            return True
        except Exception as e:
            logger.error(f"Error downloading components: {str(e)}")
            return False
        finally:
            # Clean up temporary directory
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def install_components(self) -> bool:
        """
        Install all components.
        
        Returns:
            bool: True if all components were installed successfully, False otherwise
        """
        logger.info("Installing components...")
        
        # Get component installation order based on dependencies
        components = self.config.get("components", [])
        installation_order = self._get_installation_order(components)
        
        if not installation_order:
            logger.error("Failed to determine component installation order")
            return False
        
        # Install each component in order
        for component_name in installation_order:
            component = next((c for c in components if c["name"] == component_name), None)
            if not component:
                logger.error(f"Component not found: {component_name}")
                continue
            
            logger.info(f"Installing component: {component_name}")
            
            # Install component
            if not self._install_component(component):
                if component.get("required", True):
                    logger.error(f"Failed to install required component: {component_name}")
                    return False
                else:
                    logger.warning(f"Failed to install optional component: {component_name}")
            else:
                self.installed_components.append(component_name)
                logger.info(f"Successfully installed component: {component_name}")
        
        logger.info("All components installed successfully")
        return True
    
    def _get_installation_order(self, components: List[Dict[str, Any]]) -> List[str]:
        """
        Determine the installation order based on component dependencies.
        
        Args:
            components: List of component configurations
            
        Returns:
            List[str]: Ordered list of component names
        """
        # Build dependency graph
        graph = {}
        for component in components:
            name = component["name"]
            dependencies = component.get("dependencies", [])
            graph[name] = dependencies
        
        # Topological sort
        visited = set()
        temp_visited = set()
        order = []
        
        def visit(node):
            if node in temp_visited:
                logger.error(f"Circular dependency detected: {node}")
                return False
            
            if node in visited:
                return True
            
            temp_visited.add(node)
            
            for dependency in graph.get(node, []):
                if dependency not in graph:
                    logger.error(f"Dependency not found: {dependency}")
                    return False
                
                if not visit(dependency):
                    return False
            
            temp_visited.remove(node)
            visited.add(node)
            order.append(node)
            return True
        
        # Visit each node
        for node in graph:
            if node not in visited:
                if not visit(node):
                    return []
        
        # Reverse to get installation order
        return list(reversed(order))
    
    def _install_component(self, component: Dict[str, Any]) -> bool:
        """
        Install a single component.
        
        Args:
            component: Component configuration
            
        Returns:
            bool: True if installation was successful, False otherwise
        """
        component_name = component["name"]
        component_dir = os.path.join(self.install_dir, component_name)
        
        try:
            # Create component directory if it doesn't exist
            if not os.path.exists(component_dir):
                os.makedirs(component_dir)
            
            # Extract component files
            # In a real implementation, this would extract the downloaded component archive
            # For this example, we'll simulate by creating a placeholder file
            placeholder_file = os.path.join(component_dir, "installed.txt")
            with open(placeholder_file, 'w') as f:
                f.write(f"Component {component_name} installed at {datetime.datetime.now()}")
            
            # Run post-installation script if available
            post_install_script = component.get("post_install")
            if post_install_script:
                logger.info(f"Running post-installation script for {component_name}")
                # In a real implementation, this would execute the post-installation script
            
            return True
        except Exception as e:
            logger.error(f"Error installing component {component_name}: {str(e)}")
            return False
    
    def configure_installation(self) -> bool:
        """
        Configure the installation.
        
        Returns:
            bool: True if configuration was successful, False otherwise
        """
        logger.info("Configuring installation...")
        
        try:
            # Create configuration directory
            platform_config = self.config.get("platforms", {}).get(self.platform.value, {})
            data_dir = platform_config.get("data_dir")
            
            if not data_dir:
                logger.error("Data directory not specified in configuration")
                return False
            
            config_dir = os.path.join(data_dir, "config")
            if not os.path.exists(config_dir):
                os.makedirs(config_dir)
                logger.debug(f"Created configuration directory: {config_dir}")
            
            # Create default configuration file
            config_file = os.path.join(config_dir, "config.json")
            default_config = {
                "installation": {
                    "path": self.install_dir,
                    "version": self.config.get("version"),
                    "platform": self.platform.value,
                    "components": self.installed_components,
                    "install_date": datetime.datetime.now().isoformat()
                },
                "settings": {
                    "auto_update": True,
                    "telemetry": True,
                    "log_level": "info"
                }
            }
            
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            
            logger.info(f"Created configuration file: {config_file}")
            
            # Create data directories
            for dir_name in ["logs", "data", "plugins", "cache"]:
                dir_path = os.path.join(data_dir, dir_name)
                if not os.path.exists(dir_path):
                    os.makedirs(dir_path)
                    logger.debug(f"Created directory: {dir_path}")
            
            logger.info("Installation configured successfully")
            return True
        except Exception as e:
            logger.error(f"Error configuring installation: {str(e)}")
            return False
    
    def verify_installation(self) -> bool:
        """
        Verify the installation.
        
        Returns:
            bool: True if verification was successful, False otherwise
        """
        logger.info("Verifying installation...")
        
        try:
            # Check if all required components are installed
            for component in self.config.get("components", []):
                if component.get("required", True) and component["name"] not in self.installed_components:
                    logger.error(f"Required component not installed: {component['name']}")
                    return False
            
            # Check if installation directory exists and has content
            if not os.path.exists(self.install_dir) or not os.listdir(self.install_dir):
                logger.error(f"Installation directory empty or not found: {self.install_dir}")
                return False
            
            # Check if configuration file exists
            platform_config = self.config.get("platforms", {}).get(self.platform.value, {})
            data_dir = platform_config.get("data_dir")
            config_file = os.path.join(data_dir, "config", "config.json")
            
            if not os.path.exists(config_file):
                logger.error(f"Configuration file not found: {config_file}")
                return False
            
            # Verify component installations
            for component_name in self.installed_components:
                component_dir = os.path.join(self.install_dir, component_name)
                if not os.path.exists(component_dir) or not os.listdir(component_dir):
                    logger.error(f"Component directory empty or not found: {component_dir}")
                    return False
            
            logger.info("Installation verified successfully")
            return True
        except Exception as e:
            logger.error(f"Error verifying installation: {str(e)}")
            return False
    
    def run_installation(self) -> InstallationStatus:
        """
        Run the complete installation process.
        
        Returns:
            InstallationStatus: The final installation status
        """
        logger.info("Starting installation process...")
        self.status = InstallationStatus.IN_PROGRESS
        
        # Check system requirements
        if not self.check_system_requirements():
            logger.error("System requirements check failed")
            self.status = InstallationStatus.FAILED
            return self.status
        
        # Check and install dependencies
        if not self.check_dependencies():
            logger.info("Installing missing dependencies...")
            if not self.install_dependencies():
                logger.error("Failed to install dependencies")
                self.status = InstallationStatus.FAILED
                return self.status
        
        # Prepare installation
        if not self.prepare_installation():
            logger.error("Installation preparation failed")
            self.status = InstallationStatus.FAILED
            return self.status
        
        # Download components
        if not self.download_components():
            logger.error("Component download failed")
            self.status = InstallationStatus.FAILED
            return self.status
        
        # Install components
        if not self.install_components():
            logger.error("Component installation failed")
            self.status = InstallationStatus.FAILED
            return self.status
        
        # Configure installation
        if not self.configure_installation():
            logger.error("Installation configuration failed")
            self.status = InstallationStatus.PARTIAL
            return self.status
        
        # Verify installation
        if not self.verify_installation():
            logger.error("Installation verification failed")
            self.status = InstallationStatus.PARTIAL
            return self.status
        
        logger.info("Installation completed successfully")
        self.status = InstallationStatus.SUCCESS
        return self.status
    
    def get_installation_status(self) -> Dict[str, Any]:
        """
        Get the current installation status.
        
        Returns:
            Dict: Installation status information
        """
        return {
            "status": self.status.value,
            "platform": self.platform.value,
            "install_dir": self.install_dir,
            "components": self.installed_components,
            "dependencies": self.dependencies
        }
    
    def cleanup(self) -> None:
        """
        Clean up temporary files and resources.
        """
        logger.info("Cleaning up installation resources...")
        
        # In a real implementation, this would clean up temporary files and resources
        
        logger.info("Cleanup completed")


def main():
    """
    Main entry point for the installation manager.
    """
    import argparse
    import datetime
    
    parser = argparse.ArgumentParser(description="ApexAgent Installation Manager")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--install-dir", help="Installation directory")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    args = parser.parse_args()
    
    # Create installation manager
    manager = InstallationManager(
        config_path=args.config,
        install_dir=args.install_dir,
        verbose=args.verbose
    )
    
    # Run installation
    status = manager.run_installation()
    
    # Print status
    print(f"Installation status: {status.value}")
    
    # Clean up
    manager.cleanup()
    
    # Exit with appropriate code
    if status == InstallationStatus.SUCCESS:
        sys.exit(0)
    elif status == InstallationStatus.PARTIAL:
        sys.exit(1)
    else:
        sys.exit(2)


if __name__ == "__main__":
    main()
