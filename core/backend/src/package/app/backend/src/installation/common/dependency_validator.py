"""
Dependency validation module for ApexAgent installation.

This module provides comprehensive dependency checking and validation
across all supported platforms (Windows, macOS, Linux).
"""

import os
import sys
import platform
import subprocess
import logging
from typing import Dict, List, Tuple, Optional, Union, Any

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("dependency_validator")

class DependencyValidator:
    """Validates system dependencies for ApexAgent installation."""
    
    def __init__(self, platform_type: Optional[str] = None):
        """
        Initialize the dependency validator.
        
        Args:
            platform_type: Override platform detection (windows, macos, linux)
        """
        self.platform = platform_type or self._detect_platform()
        self.python_version = sys.version_info
        
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
    
    def check_python_version(self, min_version: Tuple[int, int] = (3, 8)) -> bool:
        """
        Check if the current Python version meets the minimum requirements.
        
        Args:
            min_version: Minimum required Python version as (major, minor)
            
        Returns:
            bool: True if Python version is sufficient, False otherwise
        """
        current_version = (self.python_version.major, self.python_version.minor)
        if current_version < min_version:
            logger.error(
                f"Python version {current_version[0]}.{current_version[1]} is not supported. "
                f"Please use Python {min_version[0]}.{min_version[1]} or higher."
            )
            return False
        
        logger.info(f"Python version check passed: {current_version[0]}.{current_version[1]}")
        return True
    
    def check_pip_version(self, min_version: str = "21.0.0") -> bool:
        """
        Check if pip is installed and meets the minimum version requirement.
        
        Args:
            min_version: Minimum required pip version
            
        Returns:
            bool: True if pip version is sufficient, False otherwise
        """
        try:
            import pkg_resources
            pip_version = pkg_resources.get_distribution("pip").version
            
            # Compare versions
            if pkg_resources.parse_version(pip_version) < pkg_resources.parse_version(min_version):
                logger.warning(
                    f"pip version {pip_version} is below recommended version {min_version}. "
                    f"Consider upgrading pip using 'python -m pip install --upgrade pip'."
                )
                return False
            
            logger.info(f"pip version check passed: {pip_version}")
            return True
        except (pkg_resources.DistributionNotFound, ImportError):
            logger.error("pip is not installed or not accessible.")
            return False
    
    def check_dependencies(self, dependencies: Dict[str, str]) -> Tuple[bool, List[str]]:
        """
        Check if required dependencies are installed and meet version requirements.
        
        Args:
            dependencies: Dictionary of dependencies with version constraints
            
        Returns:
            Tuple containing:
                - bool: True if all dependencies are satisfied, False otherwise
                - List[str]: List of missing or incompatible dependencies
        """
        missing_or_incompatible = []
        
        try:
            import pkg_resources
            
            for package, version_constraint in dependencies.items():
                try:
                    pkg_resources.require(f"{package}{version_constraint}")
                    logger.info(f"Dependency check passed: {package}{version_constraint}")
                except (pkg_resources.DistributionNotFound, pkg_resources.VersionConflict):
                    missing_or_incompatible.append(f"{package}{version_constraint}")
                    logger.warning(f"Dependency check failed: {package}{version_constraint}")
        except ImportError:
            logger.error("pkg_resources module not found. Cannot check dependencies.")
            return False, list(dependencies.keys())
        
        if missing_or_incompatible:
            logger.warning(f"Missing or incompatible dependencies: {', '.join(missing_or_incompatible)}")
            return False, missing_or_incompatible
        
        logger.info("All dependencies check passed")
        return True, []
    
    def check_system_requirements(self) -> Tuple[bool, List[str]]:
        """
        Check platform-specific system requirements.
        
        Returns:
            Tuple containing:
                - bool: True if all system requirements are met, False otherwise
                - List[str]: List of unmet requirements
        """
        unmet_requirements = []
        
        # Check disk space
        free_space = self._get_free_disk_space()
        required_space = 500 * 1024 * 1024  # 500 MB in bytes
        
        if free_space < required_space:
            unmet_requirements.append(
                f"Insufficient disk space. Required: 500 MB, Available: {free_space // (1024 * 1024)} MB"
            )
            logger.error(f"Disk space check failed. Available: {free_space // (1024 * 1024)} MB")
        else:
            logger.info(f"Disk space check passed. Available: {free_space // (1024 * 1024)} MB")
        
        # Platform-specific checks
        if self.platform == "windows":
            windows_reqs = self._check_windows_requirements()
            unmet_requirements.extend(windows_reqs)
        elif self.platform == "macos":
            macos_reqs = self._check_macos_requirements()
            unmet_requirements.extend(macos_reqs)
        elif self.platform == "linux":
            linux_reqs = self._check_linux_requirements()
            unmet_requirements.extend(linux_reqs)
        
        if unmet_requirements:
            logger.warning(f"System requirements check failed: {', '.join(unmet_requirements)}")
            return False, unmet_requirements
        
        logger.info("All system requirements check passed")
        return True, []
    
    def _get_free_disk_space(self) -> int:
        """
        Get free disk space in bytes for the current directory.
        
        Returns:
            int: Free disk space in bytes
        """
        if self.platform == "windows":
            import ctypes
            free_bytes = ctypes.c_ulonglong(0)
            ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                ctypes.c_wchar_p(os.getcwd()),
                None, None,
                ctypes.pointer(free_bytes)
            )
            return free_bytes.value
        else:
            # Unix-like systems
            st = os.statvfs(os.getcwd())
            return st.f_bavail * st.f_frsize
    
    def _check_windows_requirements(self) -> List[str]:
        """
        Check Windows-specific requirements.
        
        Returns:
            List[str]: List of unmet requirements
        """
        unmet_requirements = []
        
        # Check PowerShell version
        try:
            result = subprocess.run(
                ["powershell", "-Command", "$PSVersionTable.PSVersion.ToString()"],
                capture_output=True,
                text=True,
                check=True
            )
            ps_version = result.stdout.strip()
            
            # Parse version
            version_parts = ps_version.split('.')
            if len(version_parts) >= 2:
                major = int(version_parts[0])
                minor = int(version_parts[1])
                
                if major < 5 or (major == 5 and minor < 1):
                    unmet_requirements.append(
                        f"PowerShell version {ps_version} is not supported. Please use PowerShell 5.1 or higher."
                    )
                    logger.error(f"PowerShell version check failed: {ps_version}")
                else:
                    logger.info(f"PowerShell version check passed: {ps_version}")
        except (subprocess.SubprocessError, ValueError):
            unmet_requirements.append("Could not determine PowerShell version.")
            logger.error("Failed to check PowerShell version")
        
        # Check .NET Framework version
        try:
            result = subprocess.run(
                ["powershell", "-Command", "Get-ChildItem 'HKLM:\\SOFTWARE\\Microsoft\\NET Framework Setup\\NDP' -Recurse | Get-ItemProperty -Name Version -ErrorAction SilentlyContinue | Where-Object { $_.PSChildName -match '^v4' } | Select-Object -ExpandProperty Version"],
                capture_output=True,
                text=True,
                check=True
            )
            
            if result.stdout.strip():
                net_version = result.stdout.strip()
                logger.info(f".NET Framework version check passed: {net_version}")
            else:
                unmet_requirements.append(".NET Framework 4.5 or higher is required.")
                logger.error(".NET Framework version check failed")
        except subprocess.SubprocessError:
            logger.warning("Could not determine .NET Framework version")
        
        return unmet_requirements
    
    def _check_macos_requirements(self) -> List[str]:
        """
        Check macOS-specific requirements.
        
        Returns:
            List[str]: List of unmet requirements
        """
        unmet_requirements = []
        
        # Check macOS version
        try:
            result = subprocess.run(
                ["sw_vers", "-productVersion"],
                capture_output=True,
                text=True,
                check=True
            )
            os_version = result.stdout.strip()
            
            # Parse version
            version_parts = os_version.split('.')
            if len(version_parts) >= 2:
                major = int(version_parts[0])
                minor = int(version_parts[1]) if len(version_parts) > 1 else 0
                
                # macOS 10.15 (Catalina) or higher is required
                if (major < 10) or (major == 10 and minor < 15):
                    unmet_requirements.append(
                        f"macOS version {os_version} is not supported. Please use macOS 10.15 (Catalina) or higher."
                    )
                    logger.error(f"macOS version check failed: {os_version}")
                else:
                    logger.info(f"macOS version check passed: {os_version}")
        except (subprocess.SubprocessError, ValueError):
            unmet_requirements.append("Could not determine macOS version.")
            logger.error("Failed to check macOS version")
        
        # Check if Xcode Command Line Tools are installed
        try:
            result = subprocess.run(
                ["xcode-select", "-p"],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                unmet_requirements.append("Xcode Command Line Tools are not installed.")
                logger.error("Xcode Command Line Tools check failed")
            else:
                logger.info("Xcode Command Line Tools check passed")
        except subprocess.SubprocessError:
            logger.warning("Could not check for Xcode Command Line Tools")
        
        return unmet_requirements
    
    def _check_linux_requirements(self) -> List[str]:
        """
        Check Linux-specific requirements.
        
        Returns:
            List[str]: List of unmet requirements
        """
        unmet_requirements = []
        
        # Detect Linux distribution
        distro, version = self._detect_linux_distro()
        logger.info(f"Detected Linux distribution: {distro} {version}")
        
        # Check for required system packages
        required_packages = {
            "debian": ["build-essential", "libssl-dev", "libffi-dev"],
            "ubuntu": ["build-essential", "libssl-dev", "libffi-dev"],
            "fedora": ["gcc", "openssl-devel", "libffi-devel"],
            "centos": ["gcc", "openssl-devel", "libffi-devel"],
            "rhel": ["gcc", "openssl-devel", "libffi-devel"],
            "arch": ["base-devel"],
            "manjaro": ["base-devel"],
            "opensuse": ["gcc", "libopenssl-devel", "libffi-devel"],
            "suse": ["gcc", "libopenssl-devel", "libffi-devel"]
        }
        
        if distro in required_packages:
            missing_packages = self._check_linux_packages(distro, required_packages[distro])
            if missing_packages:
                unmet_requirements.append(f"Missing required system packages: {', '.join(missing_packages)}")
                logger.error(f"System packages check failed. Missing: {', '.join(missing_packages)}")
            else:
                logger.info("System packages check passed")
        else:
            logger.warning(f"Unsupported Linux distribution: {distro}. Skipping package check.")
        
        return unmet_requirements
    
    def _detect_linux_distro(self) -> Tuple[str, str]:
        """
        Detect Linux distribution and version.
        
        Returns:
            Tuple containing:
                - str: Distribution name
                - str: Distribution version
        """
        distro = "unknown"
        version = "unknown"
        
        # Check /etc/os-release first (most modern distributions)
        if os.path.exists("/etc/os-release"):
            try:
                with open("/etc/os-release", "r") as f:
                    lines = f.readlines()
                
                for line in lines:
                    if line.startswith("ID="):
                        distro = line.split("=")[1].strip().strip('"').lower()
                    elif line.startswith("VERSION_ID="):
                        version = line.split("=")[1].strip().strip('"')
            except Exception as e:
                logger.error(f"Error reading /etc/os-release: {e}")
        
        # Fallbacks for older distributions
        if distro == "unknown":
            if os.path.exists("/etc/debian_version"):
                distro = "debian"
                try:
                    with open("/etc/debian_version", "r") as f:
                        version = f.read().strip()
                except Exception:
                    pass
            elif os.path.exists("/etc/redhat-release"):
                distro = "redhat"
                try:
                    with open("/etc/redhat-release", "r") as f:
                        release_info = f.read().strip()
                        # Extract version from release info
                        import re
                        version_match = re.search(r'release\s+(\d+\.\d+)', release_info)
                        if version_match:
                            version = version_match.group(1)
                except Exception:
                    pass
        
        return distro, version
    
    def _check_linux_packages(self, distro: str, packages: List[str]) -> List[str]:
        """
        Check if required Linux packages are installed.
        
        Args:
            distro: Linux distribution name
            packages: List of required packages
            
        Returns:
            List[str]: List of missing packages
        """
        missing_packages = []
        
        # Different package managers for different distributions
        if distro in ["debian", "ubuntu"]:
            for package in packages:
                try:
                    result = subprocess.run(
                        ["dpkg", "-s", package],
                        capture_output=True,
                        text=True
                    )
                    if result.returncode != 0:
                        missing_packages.append(package)
                except subprocess.SubprocessError:
                    missing_packages.append(package)
        
        elif distro in ["fedora", "centos", "rhel"]:
            for package in packages:
                try:
                    # Try dnf first (newer), then yum
                    if os.path.exists("/usr/bin/dnf"):
                        result = subprocess.run(
                            ["dnf", "list", "installed", package],
                            capture_output=True,
                            text=True
                        )
                    else:
                        result = subprocess.run(
                            ["yum", "list", "installed", package],
                            capture_output=True,
                            text=True
                        )
                    
                    if result.returncode != 0:
                        missing_packages.append(package)
                except subprocess.SubprocessError:
                    missing_packages.append(package)
        
        elif distro in ["arch", "manjaro"]:
            for package in packages:
                try:
                    result = subprocess.run(
                        ["pacman", "-Q", package],
                        capture_output=True,
                        text=True
                    )
                    if result.returncode != 0:
                        missing_packages.append(package)
                except subprocess.SubprocessError:
                    missing_packages.append(package)
        
        elif distro in ["opensuse", "suse"]:
            for package in packages:
                try:
                    result = subprocess.run(
                        ["rpm", "-q", package],
                        capture_output=True,
                        text=True
                    )
                    if result.returncode != 0:
                        missing_packages.append(package)
                except subprocess.SubprocessError:
                    missing_packages.append(package)
        
        return missing_packages
    
    def check_all(self, dependencies: Dict[str, str], min_python_version: Tuple[int, int] = (3, 8)) -> Tuple[bool, List[str]]:
        """
        Run all validation checks.
        
        Args:
            dependencies: Dictionary of dependencies with version constraints
            min_python_version: Minimum required Python version
            
        Returns:
            Tuple containing:
                - bool: True if all checks pass, False otherwise
                - List[str]: List of validation failures
        """
        failures = []
        
        # Check Python version
        if not self.check_python_version(min_python_version):
            failures.append(f"Python version must be {min_python_version[0]}.{min_python_version[1]} or higher")
        
        # Check pip version
        if not self.check_pip_version():
            failures.append("pip version is insufficient or not installed")
        
        # Check dependencies
        deps_ok, missing_deps = self.check_dependencies(dependencies)
        if not deps_ok:
            failures.append(f"Missing dependencies: {', '.join(missing_deps)}")
        
        # Check system requirements
        sys_ok, unmet_reqs = self.check_system_requirements()
        if not sys_ok:
            failures.extend(unmet_reqs)
        
        return len(failures) == 0, failures


class ConfigValidator:
    """Validates configuration settings for ApexAgent installation."""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize the configuration validator.
        
        Args:
            config_file: Path to configuration file (optional)
        """
        self.config = {}
        if config_file and os.path.exists(config_file):
            self.load_config(config_file)
    
    def load_config(self, config_file: str) -> bool:
        """
        Load configuration from file.
        
        Args:
            config_file: Path to configuration file
            
        Returns:
            bool: True if configuration was loaded successfully, False otherwise
        """
        try:
            import json
            with open(config_file, 'r') as f:
                self.config = json.load(f)
            logger.info(f"Configuration loaded from {config_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to load configuration from {config_file}: {e}")
            return False
    
    def validate_install_path(self, install_path: str) -> bool:
        """
        Validate installation path.
        
        Args:
            install_path: Path to validate
            
        Returns:
            bool: True if path is valid, False otherwise
        """
        # Check if path is absolute
        if not os.path.isabs(install_path):
            logger.error(f"Installation path must be absolute: {install_path}")
            return False
        
        # Check if path exists and is writable
        if os.path.exists(install_path):
            if not os.access(install_path, os.W_OK):
                logger.error(f"Installation path is not writable: {install_path}")
                return False
            
            # Check if path is a directory
            if not os.path.isdir(install_path):
                logger.error(f"Installation path exists but is not a directory: {install_path}")
                return False
        else:
            # Check if parent directory exists and is writable
            parent_dir = os.path.dirname(install_path)
            if not os.path.exists(parent_dir):
                logger.error(f"Parent directory does not exist: {parent_dir}")
                return False
            
            if not os.access(parent_dir, os.W_OK):
                logger.error(f"Parent directory is not writable: {parent_dir}")
                return False
        
        logger.info(f"Installation path validation passed: {install_path}")
        return True
    
    def validate_installation_mode(self, mode: str) -> bool:
        """
        Validate installation mode.
        
        Args:
            mode: Installation mode to validate
            
        Returns:
            bool: True if mode is valid, False otherwise
        """
        valid_modes = ["standard", "minimal", "complete", "development", "custom"]
        
        if mode not in valid_modes:
            logger.error(f"Invalid installation mode: {mode}. Must be one of: {', '.join(valid_modes)}")
            return False
        
        logger.info(f"Installation mode validation passed: {mode}")
        return True
    
    def validate_components(self, components: List[str], mode: str) -> bool:
        """
        Validate component selection.
        
        Args:
            components: List of components to validate
            mode: Installation mode
            
        Returns:
            bool: True if components are valid, False otherwise
        """
        # Components are only required for custom mode
        if mode != "custom":
            return True
        
        if not components:
            logger.error("Component list cannot be empty for custom installation mode")
            return False
        
        # Define valid components
        valid_components = [
            "core", "llm_providers", "tools", "ui", "examples",
            "openai", "anthropic", "gemini", "ollama",
            "file_tools", "shell_tools", "web_tools", "knowledge_tools",
            "web_ui", "desktop_ui", "cli"
        ]
        
        # Check if all components are valid
        invalid_components = [c for c in components if c not in valid_components]
        if invalid_components:
            logger.error(f"Invalid components: {', '.join(invalid_components)}")
            return False
        
        # Check if core component is included (required)
        if "core" not in components:
            logger.warning("Core component is not included but is required. It will be added automatically.")
        
        logger.info(f"Component validation passed: {', '.join(components)}")
        return True
    
    def validate_analytics_settings(self, analytics_enabled: bool) -> bool:
        """
        Validate analytics settings.
        
        Args:
            analytics_enabled: Whether analytics are enabled
            
        Returns:
            bool: True if settings are valid, False otherwise
        """
        # Simple validation for now, could be expanded in the future
        logger.info(f"Analytics settings validation passed: {'enabled' if analytics_enabled else 'disabled'}")
        return True
    
    def validate_all(self, install_path: str, mode: str, components: List[str] = None, analytics_enabled: bool = False) -> Tuple[bool, List[str]]:
        """
        Run all configuration validation checks.
        
        Args:
            install_path: Installation path
            mode: Installation mode
            components: List of components (for custom mode)
            analytics_enabled: Whether analytics are enabled
            
        Returns:
            Tuple containing:
                - bool: True if all checks pass, False otherwise
                - List[str]: List of validation failures
        """
        failures = []
        
        # Validate installation path
        if not self.validate_install_path(install_path):
            failures.append(f"Invalid installation path: {install_path}")
        
        # Validate installation mode
        if not self.validate_installation_mode(mode):
            failures.append(f"Invalid installation mode: {mode}")
        
        # Validate components if mode is custom
        if mode == "custom" and not self.validate_components(components or [], mode):
            failures.append("Invalid component selection")
        
        # Validate analytics settings
        if not self.validate_analytics_settings(analytics_enabled):
            failures.append("Invalid analytics settings")
        
        return len(failures) == 0, failures


# Helper function to run all validations
def validate_installation(
    install_path: str,
    mode: str,
    components: List[str] = None,
    analytics_enabled: bool = False,
    dependencies: Dict[str, str] = None,
    min_python_version: Tuple[int, int] = (3, 8)
) -> Tuple[bool, List[str]]:
    """
    Run all installation validations.
    
    Args:
        install_path: Installation path
        mode: Installation mode
        components: List of components (for custom mode)
        analytics_enabled: Whether analytics are enabled
        dependencies: Dictionary of dependencies with version constraints
        min_python_version: Minimum required Python version
        
    Returns:
        Tuple containing:
            - bool: True if all validations pass, False otherwise
            - List[str]: List of validation failures
    """
    failures = []
    
    # Validate configuration
    config_validator = ConfigValidator()
    config_ok, config_failures = config_validator.validate_all(
        install_path, mode, components, analytics_enabled
    )
    
    if not config_ok:
        failures.extend(config_failures)
    
    # Validate dependencies and system requirements
    if dependencies:
        dependency_validator = DependencyValidator()
        deps_ok, deps_failures = dependency_validator.check_all(
            dependencies, min_python_version
        )
        
        if not deps_ok:
            failures.extend(deps_failures)
    
    return len(failures) == 0, failures


if __name__ == "__main__":
    # Example usage
    print("ApexAgent Dependency Validator")
    print("-----------------------------")
    
    # Example dependencies
    example_deps = {
        "requests": ">=2.25.0",
        "numpy": ">=1.19.0",
        "pandas": ">=1.2.0"
    }
    
    # Run validation
    validator = DependencyValidator()
    all_ok, failures = validator.check_all(example_deps)
    
    if all_ok:
        print("All validation checks passed!")
    else:
        print("Validation failed:")
        for failure in failures:
            print(f"- {failure}")
