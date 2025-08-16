"""
Common utilities for ApexAgent installation across all platforms.

This module provides shared functionality used by all platform-specific installers.
"""

import os
import sys
import shutil
import logging
import subprocess
import platform
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any

# Import configuration
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.config import (
    VERSION, 
    REQUIRED_PYTHON_VERSION, 
    REQUIRED_DEPENDENCIES,
    OPTIONAL_DEPENDENCIES,
    get_system_info,
    is_admin
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(os.path.expanduser("~"), "apexagent_install.log"))
    ]
)
logger = logging.getLogger("apexagent_installer")

def check_python_version() -> bool:
    """
    Check if the current Python version meets the minimum requirements.
    
    Returns:
        bool: True if the Python version is sufficient, False otherwise.
    """
    current_version = sys.version_info[:2]
    if current_version < REQUIRED_PYTHON_VERSION:
        logger.error(
            f"Python version {current_version[0]}.{current_version[1]} is not supported. "
            f"Please use Python {REQUIRED_PYTHON_VERSION[0]}.{REQUIRED_PYTHON_VERSION[1]} or higher."
        )
        return False
    return True

def check_dependencies(dependencies: Dict[str, str] = None) -> Tuple[bool, List[str]]:
    """
    Check if required dependencies are installed and meet version requirements.
    
    Args:
        dependencies: Dictionary of dependencies to check with version constraints.
                     If None, checks REQUIRED_DEPENDENCIES from config.
    
    Returns:
        Tuple containing:
            - bool: True if all dependencies are satisfied, False otherwise.
            - List[str]: List of missing or incompatible dependencies.
    """
    if dependencies is None:
        dependencies = REQUIRED_DEPENDENCIES
    
    missing_or_incompatible = []
    
    try:
        import pkg_resources
        
        for package, version_constraint in dependencies.items():
            try:
                pkg_resources.require(f"{package}{version_constraint}")
            except (pkg_resources.DistributionNotFound, pkg_resources.VersionConflict):
                missing_or_incompatible.append(f"{package}{version_constraint}")
    except ImportError:
        logger.error("pkg_resources module not found. Cannot check dependencies.")
        return False, list(dependencies.keys())
    
    if missing_or_incompatible:
        logger.warning(f"Missing or incompatible dependencies: {', '.join(missing_or_incompatible)}")
        return False, missing_or_incompatible
    
    return True, []

def install_dependencies(dependencies: List[str], upgrade: bool = False) -> bool:
    """
    Install required dependencies using pip.
    
    Args:
        dependencies: List of dependencies to install.
        upgrade: Whether to upgrade existing packages.
    
    Returns:
        bool: True if installation was successful, False otherwise.
    """
    if not dependencies:
        return True
    
    logger.info(f"Installing dependencies: {', '.join(dependencies)}")
    
    cmd = [sys.executable, "-m", "pip", "install"]
    if upgrade:
        cmd.append("--upgrade")
    cmd.extend(dependencies)
    
    try:
        subprocess.check_call(cmd)
        logger.info("Dependencies installed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install dependencies: {e}")
        return False

def create_directory(path: str, overwrite: bool = False) -> bool:
    """
    Create a directory at the specified path.
    
    Args:
        path: Directory path to create.
        overwrite: Whether to remove existing directory if it exists.
    
    Returns:
        bool: True if directory was created or already exists, False otherwise.
    """
    try:
        if os.path.exists(path):
            if not os.path.isdir(path):
                logger.error(f"Path exists but is not a directory: {path}")
                return False
            
            if overwrite:
                logger.info(f"Removing existing directory: {path}")
                shutil.rmtree(path)
            else:
                logger.info(f"Directory already exists: {path}")
                return True
        
        os.makedirs(path, exist_ok=True)
        logger.info(f"Created directory: {path}")
        return True
    except Exception as e:
        logger.error(f"Failed to create directory {path}: {e}")
        return False

def copy_files(source: str, destination: str, patterns: List[str] = None) -> bool:
    """
    Copy files from source to destination, optionally filtering by patterns.
    
    Args:
        source: Source directory.
        destination: Destination directory.
        patterns: List of glob patterns to include.
    
    Returns:
        bool: True if copy was successful, False otherwise.
    """
    try:
        if not os.path.exists(source):
            logger.error(f"Source directory does not exist: {source}")
            return False
        
        if not os.path.exists(destination):
            os.makedirs(destination, exist_ok=True)
        
        if patterns:
            import glob
            for pattern in patterns:
                for file_path in glob.glob(os.path.join(source, pattern)):
                    if os.path.isfile(file_path):
                        shutil.copy2(file_path, destination)
        else:
            if os.path.isfile(source):
                shutil.copy2(source, destination)
            else:
                shutil.copytree(source, destination, dirs_exist_ok=True)
        
        logger.info(f"Copied files from {source} to {destination}")
        return True
    except Exception as e:
        logger.error(f"Failed to copy files from {source} to {destination}: {e}")
        return False

def create_virtual_environment(path: str, system_site_packages: bool = False) -> bool:
    """
    Create a Python virtual environment at the specified path.
    
    Args:
        path: Path where the virtual environment should be created.
        system_site_packages: Whether to give access to system site packages.
    
    Returns:
        bool: True if virtual environment was created successfully, False otherwise.
    """
    try:
        import venv
        
        logger.info(f"Creating virtual environment at {path}")
        venv.create(path, system_site_packages=system_site_packages, with_pip=True)
        logger.info(f"Virtual environment created successfully at {path}")
        return True
    except Exception as e:
        logger.error(f"Failed to create virtual environment at {path}: {e}")
        return False

def create_shortcut(target: str, shortcut_path: str, description: str = "ApexAgent") -> bool:
    """
    Create a shortcut/symlink to the target.
    Platform-specific implementations are in the respective platform modules.
    
    Args:
        target: Target file or directory.
        shortcut_path: Path where the shortcut should be created.
        description: Description of the shortcut (for Windows).
    
    Returns:
        bool: True if shortcut was created successfully, False otherwise.
    """
    system = platform.system().lower()
    
    if system == "windows":
        # Windows implementation will be in windows/utils.py
        logger.info("Creating Windows shortcut - delegating to platform-specific module")
        return False
    else:
        # Unix-like systems (Linux, macOS)
        try:
            if os.path.exists(shortcut_path):
                os.remove(shortcut_path)
            
            os.symlink(target, shortcut_path)
            logger.info(f"Created symlink from {shortcut_path} to {target}")
            return True
        except Exception as e:
            logger.error(f"Failed to create symlink from {shortcut_path} to {target}: {e}")
            return False

def save_installation_info(install_path: str, components: List[str], version: str = VERSION) -> bool:
    """
    Save installation information to a file in the installation directory.
    
    Args:
        install_path: Installation directory.
        components: List of installed components.
        version: Installed version.
    
    Returns:
        bool: True if information was saved successfully, False otherwise.
    """
    info = {
        "version": version,
        "install_path": install_path,
        "install_date": str(datetime.datetime.now()),
        "components": components,
        "system_info": get_system_info()
    }
    
    info_path = os.path.join(install_path, "installation_info.json")
    
    try:
        with open(info_path, "w") as f:
            json.dump(info, f, indent=2)
        
        logger.info(f"Saved installation information to {info_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to save installation information: {e}")
        return False

def verify_installation(install_path: str) -> Tuple[bool, List[str]]:
    """
    Verify that the installation was successful.
    
    Args:
        install_path: Installation directory.
    
    Returns:
        Tuple containing:
            - bool: True if verification passed, False otherwise.
            - List[str]: List of verification failures.
    """
    failures = []
    
    # Check if installation directory exists
    if not os.path.exists(install_path):
        failures.append(f"Installation directory does not exist: {install_path}")
        return False, failures
    
    # Check for essential files
    essential_files = [
        "installation_info.json",
        os.path.join("src", "core", "plugin_system.py"),
        os.path.join("src", "core", "error_handling", "errors.py")
    ]
    
    for file in essential_files:
        file_path = os.path.join(install_path, file)
        if not os.path.exists(file_path):
            failures.append(f"Essential file missing: {file}")
    
    # Check if Python environment is working
    try:
        result = subprocess.run(
            [sys.executable, "-c", "import sys; print('Python is working')"],
            capture_output=True,
            text=True,
            check=True
        )
        if "Python is working" not in result.stdout:
            failures.append("Python environment check failed")
    except Exception as e:
        failures.append(f"Python environment check failed: {e}")
    
    if failures:
        logger.warning(f"Installation verification failed: {', '.join(failures)}")
        return False, failures
    
    logger.info("Installation verification passed")
    return True, []

def collect_analytics(install_path: str, success: bool, errors: List[str] = None) -> None:
    """
    Collect anonymous installation analytics if enabled.
    
    Args:
        install_path: Installation directory.
        success: Whether installation was successful.
        errors: List of errors encountered during installation.
    """
    try:
        info_path = os.path.join(install_path, "installation_info.json")
        if not os.path.exists(info_path):
            return
        
        with open(info_path, "r") as f:
            info = json.load(f)
        
        # Check if analytics are enabled
        if not info.get("analytics_enabled", False):
            return
        
        # In a real implementation, this would send data to an analytics service
        # For now, we just log that analytics would be collected
        logger.info("Installation analytics would be collected (if enabled)")
    except Exception as e:
        logger.error(f"Failed to collect analytics: {e}")

def cleanup_on_failure(install_path: str) -> None:
    """
    Clean up installation files on failure.
    
    Args:
        install_path: Installation directory to clean up.
    """
    try:
        if os.path.exists(install_path):
            logger.info(f"Cleaning up failed installation at {install_path}")
            shutil.rmtree(install_path)
            logger.info(f"Removed directory: {install_path}")
    except Exception as e:
        logger.error(f"Failed to clean up installation directory: {e}")
