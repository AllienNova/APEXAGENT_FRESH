"""
Automation utilities for ApexAgent installation.

This module provides tools for automated and silent installation
across all supported platforms (Windows, macOS, Linux).
"""

import os
import sys
import json
import platform
import logging
import subprocess
import argparse
from typing import Dict, List, Tuple, Optional, Union, Any

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("installation_automation")

class InstallationAutomator:
    """Automates ApexAgent installation across platforms."""
    
    def __init__(self, platform_type: Optional[str] = None):
        """
        Initialize the installation automator.
        
        Args:
            platform_type: Override platform detection (windows, macos, linux)
        """
        self.platform = platform_type or self._detect_platform()
        
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
    
    def generate_config_file(self, 
                            output_path: str,
                            install_path: str,
                            mode: str = "standard",
                            components: List[str] = None,
                            no_shortcut: bool = False,
                            analytics: bool = False) -> bool:
        """
        Generate a configuration file for automated installation.
        
        Args:
            output_path: Path to save the configuration file
            install_path: Target installation path
            mode: Installation mode (standard, minimal, complete, development, custom)
            components: List of components to install (for custom mode)
            no_shortcut: Whether to skip shortcut creation
            analytics: Whether to enable analytics
            
        Returns:
            bool: True if configuration file was generated successfully, False otherwise
        """
        config = {
            "install_path": install_path,
            "mode": mode,
            "components": components or [],
            "no_shortcut": no_shortcut,
            "analytics": analytics,
            "silent": True,
            "platform": self.platform,
            "generated_at": str(datetime.datetime.now()),
            "generated_by": f"ApexAgent Installer Automation v0.1.0 on {platform.node()}"
        }
        
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            logger.info(f"Configuration file generated at {output_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to generate configuration file: {e}")
            return False
    
    def run_silent_installation(self, config_file: str = None, **kwargs) -> bool:
        """
        Run a silent installation using configuration file or parameters.
        
        Args:
            config_file: Path to configuration file (optional)
            **kwargs: Installation parameters (if config_file is not provided)
            
        Returns:
            bool: True if installation was successful, False otherwise
        """
        # Load configuration from file if provided
        if config_file:
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                logger.info(f"Loaded configuration from {config_file}")
            except Exception as e:
                logger.error(f"Failed to load configuration from {config_file}: {e}")
                return False
        else:
            # Use provided parameters
            config = kwargs
            config["silent"] = True
        
        # Validate required parameters
        required_params = ["install_path", "mode"]
        for param in required_params:
            if param not in config:
                logger.error(f"Missing required parameter: {param}")
                return False
        
        # Run platform-specific silent installation
        if self.platform == "windows":
            return self._run_windows_silent_install(config)
        elif self.platform == "macos":
            return self._run_macos_silent_install(config)
        elif self.platform == "linux":
            return self._run_linux_silent_install(config)
        else:
            logger.error(f"Unsupported platform: {self.platform}")
            return False
    
    def _run_windows_silent_install(self, config: Dict[str, Any]) -> bool:
        """
        Run silent installation on Windows.
        
        Args:
            config: Installation configuration
            
        Returns:
            bool: True if installation was successful, False otherwise
        """
        logger.info("Running silent installation on Windows")
        
        # Construct PowerShell command
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "windows", "install.ps1")
        
        # Build arguments
        args = [
            "-InstallPath", f'"{config["install_path"]}"',
            "-Mode", config["mode"],
            "-Silent"
        ]
        
        if config.get("no_shortcut", False):
            args.append("-NoShortcut")
        
        if config.get("analytics", False):
            args.append("-Analytics")
        
        if config["mode"] == "custom" and "components" in config:
            components_str = ",".join(config["components"])
            args.extend(["-Components", f'"{components_str}"'])
        
        # Construct full command
        powershell_cmd = f'powershell.exe -ExecutionPolicy Bypass -File "{script_path}" {" ".join(args)}'
        
        try:
            # Run PowerShell script
            logger.info(f"Executing: {powershell_cmd}")
            result = subprocess.run(powershell_cmd, shell=True, check=True)
            
            if result.returncode == 0:
                logger.info("Windows silent installation completed successfully")
                return True
            else:
                logger.error(f"Windows silent installation failed with exit code {result.returncode}")
                return False
        except subprocess.SubprocessError as e:
            logger.error(f"Failed to run Windows silent installation: {e}")
            return False
    
    def _run_macos_silent_install(self, config: Dict[str, Any]) -> bool:
        """
        Run silent installation on macOS.
        
        Args:
            config: Installation configuration
            
        Returns:
            bool: True if installation was successful, False otherwise
        """
        logger.info("Running silent installation on macOS")
        
        # Construct bash command
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "macos", "install.sh")
        
        # Build arguments
        args = [
            "--install-path", config["install_path"],
            "--mode", config["mode"],
            "--silent"
        ]
        
        if config.get("no_shortcut", False):
            args.append("--no-shortcut")
        
        if config.get("analytics", False):
            args.append("--analytics")
        
        if config["mode"] == "custom" and "components" in config:
            components_str = ",".join(config["components"])
            args.extend(["--components", components_str])
        
        # Check if script is executable
        if not os.access(script_path, os.X_OK):
            logger.info(f"Making script executable: {script_path}")
            os.chmod(script_path, 0o755)
        
        try:
            # Run bash script
            logger.info(f"Executing: {script_path} {' '.join(args)}")
            result = subprocess.run([script_path] + args, check=True)
            
            if result.returncode == 0:
                logger.info("macOS silent installation completed successfully")
                return True
            else:
                logger.error(f"macOS silent installation failed with exit code {result.returncode}")
                return False
        except subprocess.SubprocessError as e:
            logger.error(f"Failed to run macOS silent installation: {e}")
            return False
    
    def _run_linux_silent_install(self, config: Dict[str, Any]) -> bool:
        """
        Run silent installation on Linux.
        
        Args:
            config: Installation configuration
            
        Returns:
            bool: True if installation was successful, False otherwise
        """
        logger.info("Running silent installation on Linux")
        
        # Construct bash command
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "linux", "install.sh")
        
        # Build arguments
        args = [
            "--install-path", config["install_path"],
            "--mode", config["mode"],
            "--silent"
        ]
        
        if config.get("no_shortcut", False):
            args.append("--no-shortcut")
        
        if config.get("analytics", False):
            args.append("--analytics")
        
        if config["mode"] == "custom" and "components" in config:
            components_str = ",".join(config["components"])
            args.extend(["--components", components_str])
        
        # Check if script is executable
        if not os.access(script_path, os.X_OK):
            logger.info(f"Making script executable: {script_path}")
            os.chmod(script_path, 0o755)
        
        try:
            # Run bash script
            logger.info(f"Executing: {script_path} {' '.join(args)}")
            
            # Check if sudo is needed
            if not config["install_path"].startswith(os.path.expanduser("~")) and os.geteuid() != 0:
                logger.info("Installation requires sudo privileges")
                cmd = ["sudo"] + [script_path] + args
            else:
                cmd = [script_path] + args
            
            result = subprocess.run(cmd, check=True)
            
            if result.returncode == 0:
                logger.info("Linux silent installation completed successfully")
                return True
            else:
                logger.error(f"Linux silent installation failed with exit code {result.returncode}")
                return False
        except subprocess.SubprocessError as e:
            logger.error(f"Failed to run Linux silent installation: {e}")
            return False
    
    def generate_ci_config(self, output_dir: str, platform: str = None) -> bool:
        """
        Generate CI/CD configuration files for automated installation.
        
        Args:
            output_dir: Directory to save configuration files
            platform: Target platform (windows, macos, linux, all)
            
        Returns:
            bool: True if configuration files were generated successfully, False otherwise
        """
        platforms = ["windows", "macos", "linux"] if platform == "all" or not platform else [platform or self.platform]
        
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            for plat in platforms:
                if plat == "windows":
                    self._generate_windows_ci_config(output_dir)
                elif plat == "macos":
                    self._generate_macos_ci_config(output_dir)
                elif plat == "linux":
                    self._generate_linux_ci_config(output_dir)
            
            # Generate GitHub Actions workflow for all platforms
            self._generate_github_actions_workflow(output_dir)
            
            logger.info(f"CI/CD configuration files generated in {output_dir}")
            return True
        except Exception as e:
            logger.error(f"Failed to generate CI/CD configuration files: {e}")
            return False
    
    def _generate_windows_ci_config(self, output_dir: str) -> None:
        """
        Generate Windows CI/CD configuration.
        
        Args:
            output_dir: Directory to save configuration file
        """
        config = {
            "install_path": "C:\\Program Files\\ApexAgent",
            "mode": "standard",
            "components": [],
            "no_shortcut": True,
            "analytics": False,
            "silent": True,
            "platform": "windows"
        }
        
        with open(os.path.join(output_dir, "windows_ci_config.json"), 'w') as f:
            json.dump(config, f, indent=2)
        
        # Generate batch script for Windows CI
        batch_script = """@echo off
REM ApexAgent Windows CI Installation Script

echo Installing ApexAgent...
powershell.exe -ExecutionPolicy Bypass -File "%~dp0..\\windows\\install.ps1" -InstallPath "C:\\Program Files\\ApexAgent" -Mode standard -Silent -NoShortcut

if %ERRORLEVEL% NEQ 0 (
    echo Installation failed with error code %ERRORLEVEL%
    exit /b %ERRORLEVEL%
)

echo Installation completed successfully
exit /b 0
"""
        
        with open(os.path.join(output_dir, "windows_ci_install.bat"), 'w') as f:
            f.write(batch_script)
    
    def _generate_macos_ci_config(self, output_dir: str) -> None:
        """
        Generate macOS CI/CD configuration.
        
        Args:
            output_dir: Directory to save configuration file
        """
        config = {
            "install_path": "/Applications/ApexAgent",
            "mode": "standard",
            "components": [],
            "no_shortcut": True,
            "analytics": False,
            "silent": True,
            "platform": "macos"
        }
        
        with open(os.path.join(output_dir, "macos_ci_config.json"), 'w') as f:
            json.dump(config, f, indent=2)
        
        # Generate shell script for macOS CI
        shell_script = """#!/bin/bash
# ApexAgent macOS CI Installation Script

echo "Installing ApexAgent..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"$SCRIPT_DIR/../macos/install.sh" --install-path "/Applications/ApexAgent" --mode standard --silent --no-shortcut

if [ $? -ne 0 ]; then
    echo "Installation failed with error code $?"
    exit 1
fi

echo "Installation completed successfully"
exit 0
"""
        
        with open(os.path.join(output_dir, "macos_ci_install.sh"), 'w') as f:
            f.write(shell_script)
        
        # Make script executable
        os.chmod(os.path.join(output_dir, "macos_ci_install.sh"), 0o755)
    
    def _generate_linux_ci_config(self, output_dir: str) -> None:
        """
        Generate Linux CI/CD configuration.
        
        Args:
            output_dir: Directory to save configuration file
        """
        config = {
            "install_path": "/opt/apexagent",
            "mode": "standard",
            "components": [],
            "no_shortcut": True,
            "analytics": False,
            "silent": True,
            "platform": "linux"
        }
        
        with open(os.path.join(output_dir, "linux_ci_config.json"), 'w') as f:
            json.dump(config, f, indent=2)
        
        # Generate shell script for Linux CI
        shell_script = """#!/bin/bash
# ApexAgent Linux CI Installation Script

echo "Installing ApexAgent..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
sudo "$SCRIPT_DIR/../linux/install.sh" --install-path "/opt/apexagent" --mode standard --silent --no-shortcut

if [ $? -ne 0 ]; then
    echo "Installation failed with error code $?"
    exit 1
fi

echo "Installation completed successfully"
exit 0
"""
        
        with open(os.path.join(output_dir, "linux_ci_install.sh"), 'w') as f:
            f.write(shell_script)
        
        # Make script executable
        os.chmod(os.path.join(output_dir, "linux_ci_install.sh"), 0o755)
    
    def _generate_github_actions_workflow(self, output_dir: str) -> None:
        """
        Generate GitHub Actions workflow for all platforms.
        
        Args:
            output_dir: Directory to save workflow file
        """
        workflow = """name: ApexAgent CI Installation

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
  workflow_dispatch:

jobs:
  install-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install ApexAgent
        run: |
          ./src/installation/ci/windows_ci_install.bat
      - name: Verify Installation
        run: |
          if (Test-Path "C:\\Program Files\\ApexAgent\\bin\\apexagent.exe") {
            Write-Host "Installation verified successfully"
          } else {
            Write-Host "Installation verification failed"
            exit 1
          }

  install-macos:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install ApexAgent
        run: |
          chmod +x ./src/installation/ci/macos_ci_install.sh
          ./src/installation/ci/macos_ci_install.sh
      - name: Verify Installation
        run: |
          if [ -d "/Applications/ApexAgent.app" ]; then
            echo "Installation verified successfully"
          else
            echo "Installation verification failed"
            exit 1
          fi

  install-linux:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install ApexAgent
        run: |
          chmod +x ./src/installation/ci/linux_ci_install.sh
          ./src/installation/ci/linux_ci_install.sh
      - name: Verify Installation
        run: |
          if [ -d "/opt/apexagent" ]; then
            echo "Installation verified successfully"
          else
            echo "Installation verification failed"
            exit 1
          fi
"""
        
        # Create .github/workflows directory
        workflows_dir = os.path.join(output_dir, ".github", "workflows")
        os.makedirs(workflows_dir, exist_ok=True)
        
        with open(os.path.join(workflows_dir, "installation.yml"), 'w') as f:
            f.write(workflow)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="ApexAgent Installation Automation")
    
    parser.add_argument("--generate-config", action="store_true",
                        help="Generate configuration file for silent installation")
    parser.add_argument("--run-silent", action="store_true",
                        help="Run silent installation")
    parser.add_argument("--generate-ci", action="store_true",
                        help="Generate CI/CD configuration files")
    
    parser.add_argument("--config-file", type=str,
                        help="Path to configuration file")
    parser.add_argument("--output-path", type=str,
                        help="Output path for generated files")
    
    parser.add_argument("--install-path", type=str,
                        help="Installation path")
    parser.add_argument("--mode", type=str, choices=["standard", "minimal", "complete", "development", "custom"],
                        default="standard", help="Installation mode")
    parser.add_argument("--components", type=str,
                        help="Comma-separated list of components for custom mode")
    parser.add_argument("--no-shortcut", action="store_true",
                        help="Skip shortcut creation")
    parser.add_argument("--analytics", action="store_true",
                        help="Enable analytics")
    parser.add_argument("--platform", type=str, choices=["windows", "macos", "linux", "all"],
                        help="Target platform for CI/CD configuration")
    
    return parser.parse_args()


if __name__ == "__main__":
    # Parse command line arguments
    args = parse_args()
    
    # Create automator
    automator = InstallationAutomator()
    
    if args.generate_config:
        if not args.output_path:
            print("Error: --output-path is required for --generate-config")
            sys.exit(1)
        
        if not args.install_path:
            print("Error: --install-path is required for --generate-config")
            sys.exit(1)
        
        components = args.components.split(",") if args.components else []
        
        success = automator.generate_config_file(
            args.output_path,
            args.install_path,
            args.mode,
            components,
            args.no_shortcut,
            args.analytics
        )
        
        sys.exit(0 if success else 1)
    
    elif args.run_silent:
        if args.config_file:
            success = automator.run_silent_installation(config_file=args.config_file)
        elif args.install_path:
            components = args.components.split(",") if args.components else []
            
            success = automator.run_silent_installation(
                install_path=args.install_path,
                mode=args.mode,
                components=components,
                no_shortcut=args.no_shortcut,
                analytics=args.analytics
            )
        else:
            print("Error: Either --config-file or --install-path is required for --run-silent")
            sys.exit(1)
        
        sys.exit(0 if success else 1)
    
    elif args.generate_ci:
        if not args.output_path:
            print("Error: --output-path is required for --generate-ci")
            sys.exit(1)
        
        success = automator.generate_ci_config(args.output_path, args.platform)
        
        sys.exit(0 if success else 1)
    
    else:
        print("Error: One of --generate-config, --run-silent, or --generate-ci is required")
        sys.exit(1)
