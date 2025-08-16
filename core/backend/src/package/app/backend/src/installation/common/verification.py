"""
Installation verification and troubleshooting module for ApexAgent.

This module provides tools to verify successful installation and
troubleshoot common installation issues across all platforms.
"""

import os
import sys
import json
import platform
import logging
import subprocess
import shutil
from typing import Dict, List, Tuple, Optional, Union, Any

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("installation_verification")

class InstallationVerifier:
    """Verifies ApexAgent installation across platforms."""
    
    def __init__(self, install_path: str, platform_type: Optional[str] = None):
        """
        Initialize the installation verifier.
        
        Args:
            install_path: Path where ApexAgent is installed
            platform_type: Override platform detection (windows, macos, linux)
        """
        self.install_path = install_path
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
    
    def verify_installation(self) -> Tuple[bool, List[str]]:
        """
        Verify that the installation was successful.
        
        Returns:
            Tuple containing:
                - bool: True if verification passed, False otherwise
                - List[str]: List of verification failures
        """
        failures = []
        
        # Check if installation directory exists
        if not os.path.exists(self.install_path):
            failures.append(f"Installation directory does not exist: {self.install_path}")
            return False, failures
        
        # Platform-specific verification
        if self.platform == "windows":
            success, platform_failures = self._verify_windows_installation()
        elif self.platform == "macos":
            success, platform_failures = self._verify_macos_installation()
        elif self.platform == "linux":
            success, platform_failures = self._verify_linux_installation()
        else:
            failures.append(f"Unsupported platform: {self.platform}")
            return False, failures
        
        failures.extend(platform_failures)
        
        # Check installation info file
        info_path = self._get_installation_info_path()
        if not os.path.exists(info_path):
            failures.append("Installation information file not found")
        else:
            try:
                with open(info_path, 'r') as f:
                    info = json.load(f)
                
                # Verify version
                if "version" not in info:
                    failures.append("Version information missing in installation info")
                
                # Verify installation path
                if "install_path" not in info:
                    failures.append("Installation path missing in installation info")
                
                logger.info(f"Installation info verified: version {info.get('version', 'unknown')}")
            except Exception as e:
                failures.append(f"Failed to read installation info: {e}")
        
        # Check Python environment
        if not self._verify_python_environment():
            failures.append("Python environment verification failed")
        
        if failures:
            logger.warning(f"Installation verification failed: {', '.join(failures)}")
            return False, failures
        
        logger.info("Installation verification passed")
        return True, []
    
    def _get_installation_info_path(self) -> str:
        """
        Get the path to the installation info file.
        
        Returns:
            str: Path to installation info file
        """
        if self.platform == "macos":
            # For macOS, the info file is in the app bundle
            if self.install_path.endswith(".app"):
                return os.path.join(self.install_path, "Contents", "Resources", "installation_info.json")
            else:
                return os.path.join(self.install_path + ".app", "Contents", "Resources", "installation_info.json")
        else:
            # For Windows and Linux
            return os.path.join(self.install_path, "installation_info.json")
    
    def _verify_windows_installation(self) -> Tuple[bool, List[str]]:
        """
        Verify Windows-specific installation components.
        
        Returns:
            Tuple containing:
                - bool: True if verification passed, False otherwise
                - List[str]: List of verification failures
        """
        failures = []
        
        # Check for essential files
        essential_files = [
            os.path.join("bin", "apexagent.exe"),
            "installation_info.json",
            os.path.join("src", "core", "plugin_system.py"),
            os.path.join("src", "core", "error_handling", "errors.py")
        ]
        
        for file in essential_files:
            file_path = os.path.join(self.install_path, file)
            if not os.path.exists(file_path):
                failures.append(f"Essential file missing: {file}")
        
        # Check registry entries
        try:
            import winreg
            registry_key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\ApexAgent"
            )
            
            # Check registry values
            try:
                install_path, _ = winreg.QueryValueEx(registry_key, "InstallPath")
                if install_path != self.install_path:
                    failures.append(f"Registry install path mismatch: {install_path} vs {self.install_path}")
            except FileNotFoundError:
                failures.append("Registry install path value missing")
            
            try:
                version, _ = winreg.QueryValueEx(registry_key, "Version")
                logger.info(f"Registry version: {version}")
            except FileNotFoundError:
                failures.append("Registry version value missing")
            
            winreg.CloseKey(registry_key)
        except (ImportError, FileNotFoundError):
            failures.append("Registry entries not found")
        except Exception as e:
            failures.append(f"Failed to check registry entries: {e}")
        
        # Check shortcuts
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop", "ApexAgent.lnk")
        start_menu_path = os.path.join(
            os.environ.get("APPDATA", ""),
            "Microsoft", "Windows", "Start Menu", "Programs", "ApexAgent", "ApexAgent.lnk"
        )
        
        if not os.path.exists(desktop_path) and not os.path.exists(start_menu_path):
            logger.warning("No shortcuts found (this may be intentional if --no-shortcut was used)")
        
        return len(failures) == 0, failures
    
    def _verify_macos_installation(self) -> Tuple[bool, List[str]]:
        """
        Verify macOS-specific installation components.
        
        Returns:
            Tuple containing:
                - bool: True if verification passed, False otherwise
                - List[str]: List of verification failures
        """
        failures = []
        
        # Adjust path for .app bundle
        app_path = self.install_path
        if not app_path.endswith(".app"):
            app_path = app_path + ".app"
        
        # Check if application bundle exists
        if not os.path.isdir(app_path):
            failures.append(f"Application bundle does not exist: {app_path}")
            return False, failures
        
        # Check for essential files
        essential_files = [
            os.path.join("Contents", "MacOS", "ApexAgent"),
            os.path.join("Contents", "Info.plist"),
            os.path.join("Contents", "Resources", "installation_info.json"),
            os.path.join("Contents", "Resources", "src", "main.py")
        ]
        
        for file in essential_files:
            file_path = os.path.join(app_path, file)
            if not os.path.exists(file_path):
                failures.append(f"Essential file missing: {file}")
        
        # Check if application is registered in Launch Services
        try:
            result = subprocess.run(
                ["mdfind", f"kMDItemCFBundleIdentifier == 'com.apexagent.app'"],
                capture_output=True,
                text=True,
                check=True
            )
            
            if app_path not in result.stdout:
                logger.warning("Application not found in Launch Services database")
        except subprocess.SubprocessError:
            logger.warning("Could not check Launch Services registration")
        
        # Check for Applications symlink
        applications_symlink = "/Applications/ApexAgent.app"
        if not os.path.exists(applications_symlink) and app_path != applications_symlink:
            logger.warning("No symlink in /Applications (this may be intentional)")
        
        return len(failures) == 0, failures
    
    def _verify_linux_installation(self) -> Tuple[bool, List[str]]:
        """
        Verify Linux-specific installation components.
        
        Returns:
            Tuple containing:
                - bool: True if verification passed, False otherwise
                - List[str]: List of verification failures
        """
        failures = []
        
        # Check for essential files
        essential_files = [
            os.path.join("bin", "apexagent"),
            "installation_info.json",
            os.path.join("src", "main.py"),
            os.path.join("venv", "bin", "python")
        ]
        
        for file in essential_files:
            file_path = os.path.join(self.install_path, file)
            if not os.path.exists(file_path):
                failures.append(f"Essential file missing: {file}")
        
        # Check executable permissions
        executable_files = [
            os.path.join("bin", "apexagent"),
            os.path.join("src", "main.py")
        ]
        
        for file in executable_files:
            file_path = os.path.join(self.install_path, file)
            if os.path.exists(file_path) and not os.access(file_path, os.X_OK):
                failures.append(f"File is not executable: {file}")
        
        # Check for system-wide symlink
        if not self.install_path.startswith(os.path.expanduser("~")):
            symlink_path = "/usr/local/bin/apexagent"
            if not os.path.exists(symlink_path):
                logger.warning("No symlink in /usr/local/bin (this may be intentional)")
        
        # Check desktop entry
        desktop_file = None
        if self.install_path.startswith(os.path.expanduser("~")):
            desktop_file = os.path.join(
                os.path.expanduser("~"),
                ".local", "share", "applications", "apexagent.desktop"
            )
        else:
            desktop_file = "/usr/share/applications/apexagent.desktop"
        
        if not os.path.exists(desktop_file):
            logger.warning("No desktop entry found (this may be intentional if --no-shortcut was used)")
        
        return len(failures) == 0, failures
    
    def _verify_python_environment(self) -> bool:
        """
        Verify Python environment.
        
        Returns:
            bool: True if verification passed, False otherwise
        """
        # Determine Python executable path
        if self.platform == "windows":
            python_path = os.path.join(self.install_path, "venv", "Scripts", "python.exe")
        elif self.platform == "macos":
            if self.install_path.endswith(".app"):
                python_path = os.path.join(self.install_path, "Contents", "Resources", "venv", "bin", "python")
            else:
                python_path = os.path.join(self.install_path + ".app", "Contents", "Resources", "venv", "bin", "python")
        else:  # Linux
            python_path = os.path.join(self.install_path, "venv", "bin", "python")
        
        # Check if Python executable exists
        if not os.path.exists(python_path):
            logger.error(f"Python executable not found: {python_path}")
            return False
        
        # Try to run Python
        try:
            result = subprocess.run(
                [python_path, "-c", "print('Python environment is working')"],
                capture_output=True,
                text=True,
                check=True
            )
            
            if "Python environment is working" not in result.stdout:
                logger.error("Python environment check failed")
                return False
            
            logger.info("Python environment check passed")
            return True
        except subprocess.SubprocessError as e:
            logger.error(f"Failed to run Python: {e}")
            return False
    
    def run_self_test(self) -> Tuple[bool, Dict[str, Any]]:
        """
        Run a self-test of the ApexAgent installation.
        
        Returns:
            Tuple containing:
                - bool: True if self-test passed, False otherwise
                - Dict: Test results and diagnostics
        """
        results = {
            "platform": self.platform,
            "install_path": self.install_path,
            "tests": {},
            "overall_result": False
        }
        
        # Verify installation first
        verification_passed, failures = self.verify_installation()
        results["tests"]["installation_verification"] = {
            "passed": verification_passed,
            "failures": failures
        }
        
        if not verification_passed:
            logger.error("Installation verification failed, skipping further tests")
            return False, results
        
        # Run the application in test mode
        test_passed, test_output = self._run_application_test()
        results["tests"]["application_test"] = {
            "passed": test_passed,
            "output": test_output
        }
        
        # Check dependencies
        deps_passed, deps_results = self._check_dependencies()
        results["tests"]["dependencies"] = {
            "passed": deps_passed,
            "results": deps_results
        }
        
        # Check permissions
        perm_passed, perm_results = self._check_permissions()
        results["tests"]["permissions"] = {
            "passed": perm_passed,
            "results": perm_results
        }
        
        # Overall result
        results["overall_result"] = verification_passed and test_passed and deps_passed and perm_passed
        
        if results["overall_result"]:
            logger.info("Self-test passed successfully")
        else:
            logger.warning("Self-test failed")
        
        return results["overall_result"], results
    
    def _run_application_test(self) -> Tuple[bool, str]:
        """
        Run the application in test mode.
        
        Returns:
            Tuple containing:
                - bool: True if test passed, False otherwise
                - str: Test output
        """
        # Determine executable path
        if self.platform == "windows":
            executable = os.path.join(self.install_path, "bin", "apexagent.exe")
        elif self.platform == "macos":
            if self.install_path.endswith(".app"):
                executable = os.path.join(self.install_path, "Contents", "MacOS", "ApexAgent")
            else:
                executable = os.path.join(self.install_path + ".app", "Contents", "MacOS", "ApexAgent")
        else:  # Linux
            executable = os.path.join(self.install_path, "bin", "apexagent")
        
        # Check if executable exists
        if not os.path.exists(executable):
            logger.error(f"Executable not found: {executable}")
            return False, f"Executable not found: {executable}"
        
        # Run the application in test mode
        try:
            result = subprocess.run(
                [executable, "--test"],
                capture_output=True,
                text=True,
                check=True
            )
            
            logger.info("Application test passed")
            return True, result.stdout
        except subprocess.SubprocessError as e:
            logger.error(f"Application test failed: {e}")
            return False, f"Application test failed: {e}\nStdout: {e.stdout if hasattr(e, 'stdout') else 'N/A'}\nStderr: {e.stderr if hasattr(e, 'stderr') else 'N/A'}"
    
    def _check_dependencies(self) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if all dependencies are properly installed.
        
        Returns:
            Tuple containing:
                - bool: True if all dependencies are properly installed, False otherwise
                - Dict: Dependency check results
        """
        results = {}
        
        # Determine Python executable path
        if self.platform == "windows":
            python_path = os.path.join(self.install_path, "venv", "Scripts", "python.exe")
        elif self.platform == "macos":
            if self.install_path.endswith(".app"):
                python_path = os.path.join(self.install_path, "Contents", "Resources", "venv", "bin", "python")
            else:
                python_path = os.path.join(self.install_path + ".app", "Contents", "Resources", "venv", "bin", "python")
        else:  # Linux
            python_path = os.path.join(self.install_path, "venv", "bin", "python")
        
        # Check if Python executable exists
        if not os.path.exists(python_path):
            logger.error(f"Python executable not found: {python_path}")
            return False, {"error": f"Python executable not found: {python_path}"}
        
        # Get installed packages
        try:
            result = subprocess.run(
                [python_path, "-m", "pip", "list", "--format=json"],
                capture_output=True,
                text=True,
                check=True
            )
            
            packages = json.loads(result.stdout)
            
            # Convert to dictionary for easier lookup
            installed_packages = {pkg["name"].lower(): pkg["version"] for pkg in packages}
            results["installed_packages"] = installed_packages
            
            # Check required packages
            required_packages = {
                "requests": "2.25.0",
                "numpy": "1.19.0",
                "pandas": "1.2.0"
            }
            
            missing_packages = []
            for package, min_version in required_packages.items():
                if package.lower() not in installed_packages:
                    missing_packages.append(package)
            
            results["missing_packages"] = missing_packages
            
            if missing_packages:
                logger.warning(f"Missing required packages: {', '.join(missing_packages)}")
                return False, results
            
            logger.info("All required packages are installed")
            return True, results
        except (subprocess.SubprocessError, json.JSONDecodeError) as e:
            logger.error(f"Failed to check dependencies: {e}")
            return False, {"error": f"Failed to check dependencies: {e}"}
    
    def _check_permissions(self) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if the installation has the correct permissions.
        
        Returns:
            Tuple containing:
                - bool: True if permissions are correct, False otherwise
                - Dict: Permission check results
        """
        results = {
            "directories": {},
            "files": {}
        }
        
        # Skip permission check on Windows
        if self.platform == "windows":
            return True, {"message": "Permission check not applicable on Windows"}
        
        # Adjust path for macOS
        check_path = self.install_path
        if self.platform == "macos" and not check_path.endswith(".app"):
            check_path = check_path + ".app"
        
        # Check if installation directory exists
        if not os.path.exists(check_path):
            logger.error(f"Installation directory does not exist: {check_path}")
            return False, {"error": f"Installation directory does not exist: {check_path}"}
        
        # Check directory permissions
        for root, dirs, files in os.walk(check_path):
            for directory in dirs:
                dir_path = os.path.join(root, directory)
                readable = os.access(dir_path, os.R_OK)
                writable = os.access(dir_path, os.W_OK)
                executable = os.access(dir_path, os.X_OK)
                
                results["directories"][os.path.relpath(dir_path, check_path)] = {
                    "readable": readable,
                    "writable": writable,
                    "executable": executable
                }
                
                if not readable or not executable:
                    logger.warning(f"Directory has incorrect permissions: {dir_path}")
            
            for file in files:
                file_path = os.path.join(root, file)
                readable = os.access(file_path, os.R_OK)
                writable = os.access(file_path, os.W_OK)
                executable = os.access(file_path, os.X_OK)
                
                results["files"][os.path.relpath(file_path, check_path)] = {
                    "readable": readable,
                    "writable": writable,
                    "executable": executable
                }
                
                # Check if executable files have execute permission
                if file.endswith((".py", ".sh")) or file in ["apexagent", "ApexAgent"]:
                    if not executable:
                        logger.warning(f"Executable file missing execute permission: {file_path}")
        
        # Check for any permission issues
        permission_issues = False
        for path, perms in results["directories"].items():
            if not perms["readable"] or not perms["executable"]:
                permission_issues = True
                break
        
        for path, perms in results["files"].items():
            if not perms["readable"]:
                permission_issues = True
                break
            
            # Check executable permission for specific files
            if (path.endswith((".py", ".sh")) or os.path.basename(path) in ["apexagent", "ApexAgent"]) and not perms["executable"]:
                permission_issues = True
                break
        
        if permission_issues:
            logger.warning("Permission issues detected")
            return False, results
        
        logger.info("Permission check passed")
        return True, results


class InstallationTroubleshooter:
    """Troubleshoots common ApexAgent installation issues."""
    
    def __init__(self, install_path: str, platform_type: Optional[str] = None):
        """
        Initialize the installation troubleshooter.
        
        Args:
            install_path: Path where ApexAgent is installed
            platform_type: Override platform detection (windows, macos, linux)
        """
        self.install_path = install_path
        self.platform = platform_type or self._detect_platform()
        self.verifier = InstallationVerifier(install_path, self.platform)
        
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
    
    def diagnose_issues(self) -> Dict[str, Any]:
        """
        Diagnose installation issues.
        
        Returns:
            Dict: Diagnostic results and recommendations
        """
        results = {
            "platform": self.platform,
            "install_path": self.install_path,
            "verification_result": None,
            "issues": [],
            "recommendations": []
        }
        
        # Verify installation
        verification_passed, failures = self.verifier.verify_installation()
        results["verification_result"] = {
            "passed": verification_passed,
            "failures": failures
        }
        
        # Run self-test
        self_test_passed, self_test_results = self.verifier.run_self_test()
        results["self_test_result"] = self_test_results
        
        # Identify issues
        if not verification_passed:
            for failure in failures:
                if "directory does not exist" in failure:
                    results["issues"].append({
                        "type": "missing_directory",
                        "message": failure,
                        "severity": "critical"
                    })
                    results["recommendations"].append(
                        "The installation directory is missing. Please reinstall ApexAgent."
                    )
                elif "file missing" in failure:
                    results["issues"].append({
                        "type": "missing_file",
                        "message": failure,
                        "severity": "critical"
                    })
                    results["recommendations"].append(
                        "Essential files are missing. Please reinstall ApexAgent."
                    )
                elif "registry" in failure.lower():
                    results["issues"].append({
                        "type": "registry_issue",
                        "message": failure,
                        "severity": "warning"
                    })
                    results["recommendations"].append(
                        "Registry entries are missing or incorrect. This may cause issues with uninstallation or updates."
                    )
                else:
                    results["issues"].append({
                        "type": "unknown",
                        "message": failure,
                        "severity": "warning"
                    })
        
        # Check for dependency issues
        if not self_test_passed and "dependencies" in self_test_results["tests"]:
            deps_result = self_test_results["tests"]["dependencies"]
            if not deps_result["passed"] and "missing_packages" in deps_result["results"]:
                missing_packages = deps_result["results"]["missing_packages"]
                if missing_packages:
                    results["issues"].append({
                        "type": "missing_dependencies",
                        "message": f"Missing required packages: {', '.join(missing_packages)}",
                        "severity": "high"
                    })
                    results["recommendations"].append(
                        f"Install missing dependencies using: pip install {' '.join(missing_packages)}"
                    )
        
        # Check for permission issues
        if not self_test_passed and "permissions" in self_test_results["tests"]:
            perm_result = self_test_results["tests"]["permissions"]
            if not perm_result["passed"] and isinstance(perm_result["results"], dict):
                results["issues"].append({
                    "type": "permission_issues",
                    "message": "Some files or directories have incorrect permissions",
                    "severity": "high"
                })
                
                if self.platform == "linux" or self.platform == "macos":
                    results["recommendations"].append(
                        f"Fix permissions using: chmod -R u+rX {self.install_path}"
                    )
        
        # Check for application test issues
        if not self_test_passed and "application_test" in self_test_results["tests"]:
            app_result = self_test_results["tests"]["application_test"]
            if not app_result["passed"]:
                results["issues"].append({
                    "type": "application_test_failed",
                    "message": f"Application test failed: {app_result['output']}",
                    "severity": "high"
                })
                results["recommendations"].append(
                    "The application failed to run in test mode. This may indicate a corrupted installation or missing dependencies."
                )
        
        # Add general recommendations if there are issues
        if results["issues"]:
            results["recommendations"].append(
                "If the issues persist after following the recommendations, please try reinstalling ApexAgent."
            )
            results["recommendations"].append(
                "For further assistance, please check the documentation or contact support."
            )
        
        return results
    
    def fix_common_issues(self) -> Dict[str, Any]:
        """
        Attempt to fix common installation issues.
        
        Returns:
            Dict: Results of fix attempts
        """
        results = {
            "platform": self.platform,
            "install_path": self.install_path,
            "fixed_issues": [],
            "failed_fixes": [],
            "recommendations": []
        }
        
        # Diagnose issues first
        diagnosis = self.diagnose_issues()
        
        # No issues to fix
        if not diagnosis["issues"]:
            results["message"] = "No issues detected, nothing to fix."
            return results
        
        # Try to fix each issue
        for issue in diagnosis["issues"]:
            issue_type = issue["type"]
            
            if issue_type == "permission_issues" and (self.platform == "linux" or self.platform == "macos"):
                # Fix permissions
                try:
                    if self.platform == "macos" and not self.install_path.endswith(".app"):
                        fix_path = self.install_path + ".app"
                    else:
                        fix_path = self.install_path
                    
                    subprocess.run(
                        ["chmod", "-R", "u+rX", fix_path],
                        check=True
                    )
                    
                    # Make executable files executable
                    if self.platform == "linux":
                        executable_files = [
                            os.path.join(fix_path, "bin", "apexagent"),
                            os.path.join(fix_path, "src", "main.py")
                        ]
                    else:  # macOS
                        executable_files = [
                            os.path.join(fix_path, "Contents", "MacOS", "ApexAgent"),
                            os.path.join(fix_path, "Contents", "Resources", "src", "main.py")
                        ]
                    
                    for file in executable_files:
                        if os.path.exists(file):
                            subprocess.run(
                                ["chmod", "+x", file],
                                check=True
                            )
                    
                    results["fixed_issues"].append({
                        "type": issue_type,
                        "message": "Fixed file and directory permissions"
                    })
                except subprocess.SubprocessError as e:
                    results["failed_fixes"].append({
                        "type": issue_type,
                        "message": f"Failed to fix permissions: {e}"
                    })
                    results["recommendations"].append(
                        "Try fixing permissions manually using: sudo chmod -R u+rX " + fix_path
                    )
            
            elif issue_type == "missing_dependencies":
                # Try to fix missing dependencies
                try:
                    # Determine pip path
                    if self.platform == "windows":
                        pip_path = os.path.join(self.install_path, "venv", "Scripts", "pip.exe")
                    elif self.platform == "macos":
                        if self.install_path.endswith(".app"):
                            pip_path = os.path.join(self.install_path, "Contents", "Resources", "venv", "bin", "pip")
                        else:
                            pip_path = os.path.join(self.install_path + ".app", "Contents", "Resources", "venv", "bin", "pip")
                    else:  # Linux
                        pip_path = os.path.join(self.install_path, "venv", "bin", "pip")
                    
                    # Check if pip exists
                    if not os.path.exists(pip_path):
                        results["failed_fixes"].append({
                            "type": issue_type,
                            "message": f"Pip not found at {pip_path}"
                        })
                        continue
                    
                    # Extract missing packages from issue message
                    import re
                    match = re.search(r"Missing required packages: (.*)", issue["message"])
                    if match:
                        packages = [pkg.strip() for pkg in match.group(1).split(",")]
                        
                        # Install missing packages
                        subprocess.run(
                            [pip_path, "install"] + packages,
                            check=True
                        )
                        
                        results["fixed_issues"].append({
                            "type": issue_type,
                            "message": f"Installed missing packages: {', '.join(packages)}"
                        })
                    else:
                        results["failed_fixes"].append({
                            "type": issue_type,
                            "message": "Could not determine missing packages"
                        })
                except subprocess.SubprocessError as e:
                    results["failed_fixes"].append({
                        "type": issue_type,
                        "message": f"Failed to install missing packages: {e}"
                    })
                    results["recommendations"].append(
                        "Try installing dependencies manually using pip"
                    )
            
            elif issue_type == "registry_issue" and self.platform == "windows":
                # Try to fix registry issues
                try:
                    import winreg
                    
                    # Create registry key if it doesn't exist
                    try:
                        registry_key = winreg.CreateKey(
                            winreg.HKEY_LOCAL_MACHINE,
                            r"SOFTWARE\ApexAgent"
                        )
                        
                        # Set registry values
                        winreg.SetValueEx(registry_key, "InstallPath", 0, winreg.REG_SZ, self.install_path)
                        winreg.SetValueEx(registry_key, "Version", 0, winreg.REG_SZ, "0.1.0")
                        winreg.SetValueEx(registry_key, "InstallDate", 0, winreg.REG_SZ, str(datetime.datetime.now().date()))
                        
                        winreg.CloseKey(registry_key)
                        
                        results["fixed_issues"].append({
                            "type": issue_type,
                            "message": "Fixed registry entries"
                        })
                    except Exception as e:
                        results["failed_fixes"].append({
                            "type": issue_type,
                            "message": f"Failed to fix registry entries: {e}"
                        })
                        results["recommendations"].append(
                            "Try running the installer again with administrative privileges"
                        )
                except ImportError:
                    results["failed_fixes"].append({
                        "type": issue_type,
                        "message": "Could not access Windows registry"
                    })
            
            else:
                # Other issues can't be fixed automatically
                results["failed_fixes"].append({
                    "type": issue_type,
                    "message": "This issue cannot be fixed automatically"
                })
        
        # Add general recommendations if there are failed fixes
        if results["failed_fixes"]:
            results["recommendations"].append(
                "Some issues could not be fixed automatically. Consider reinstalling ApexAgent."
            )
            results["recommendations"].append(
                "For further assistance, please check the documentation or contact support."
            )
        
        # Verify fixes
        verification_passed, _ = self.verifier.verify_installation()
        results["verification_after_fixes"] = verification_passed
        
        if verification_passed:
            results["message"] = "All issues have been fixed successfully."
        else:
            results["message"] = "Some issues remain after attempted fixes."
        
        return results
    
    def generate_diagnostic_report(self, output_file: Optional[str] = None) -> str:
        """
        Generate a comprehensive diagnostic report.
        
        Args:
            output_file: Path to save the report (optional)
            
        Returns:
            str: Path to the generated report
        """
        # Collect system information
        system_info = {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "processor": platform.processor(),
            "hostname": platform.node(),
            "username": os.getlogin() if hasattr(os, 'getlogin') else "unknown"
        }
        
        # Collect installation information
        try:
            info_path = self.verifier._get_installation_info_path()
            if os.path.exists(info_path):
                with open(info_path, 'r') as f:
                    installation_info = json.load(f)
            else:
                installation_info = {"error": "Installation info file not found"}
        except Exception as e:
            installation_info = {"error": f"Failed to read installation info: {e}"}
        
        # Run diagnostics
        verification_result, failures = self.verifier.verify_installation()
        self_test_result, self_test_details = self.verifier.run_self_test()
        diagnosis = self.diagnose_issues()
        
        # Compile report
        report = {
            "timestamp": str(datetime.datetime.now()),
            "system_info": system_info,
            "installation_info": installation_info,
            "verification_result": {
                "passed": verification_result,
                "failures": failures
            },
            "self_test_result": self_test_details,
            "diagnosis": diagnosis
        }
        
        # Save report to file if requested
        if output_file:
            try:
                with open(output_file, 'w') as f:
                    json.dump(report, f, indent=2)
                logger.info(f"Diagnostic report saved to {output_file}")
                return output_file
            except Exception as e:
                logger.error(f"Failed to save diagnostic report: {e}")
        
        # Generate default filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"apexagent_diagnostic_{timestamp}.json"
        default_path = os.path.join(os.path.expanduser("~"), default_filename)
        
        try:
            with open(default_path, 'w') as f:
                json.dump(report, f, indent=2)
            logger.info(f"Diagnostic report saved to {default_path}")
            return default_path
        except Exception as e:
            logger.error(f"Failed to save diagnostic report: {e}")
            return json.dumps(report, indent=2)  # Return as string if file saving fails


def main():
    """Command-line interface for installation verification and troubleshooting."""
    parser = argparse.ArgumentParser(description="ApexAgent Installation Verification and Troubleshooting")
    
    parser.add_argument("--install-path", type=str, required=True,
                        help="Path where ApexAgent is installed")
    parser.add_argument("--platform", type=str, choices=["windows", "macos", "linux"],
                        help="Override platform detection")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Verify command
    verify_parser = subparsers.add_parser("verify", help="Verify installation")
    
    # Test command
    test_parser = subparsers.add_parser("test", help="Run self-test")
    
    # Diagnose command
    diagnose_parser = subparsers.add_parser("diagnose", help="Diagnose installation issues")
    
    # Fix command
    fix_parser = subparsers.add_parser("fix", help="Attempt to fix common installation issues")
    
    # Report command
    report_parser = subparsers.add_parser("report", help="Generate diagnostic report")
    report_parser.add_argument("--output", type=str,
                              help="Path to save the report")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Create verifier and troubleshooter
    verifier = InstallationVerifier(args.install_path, args.platform)
    troubleshooter = InstallationTroubleshooter(args.install_path, args.platform)
    
    if args.command == "verify":
        passed, failures = verifier.verify_installation()
        if passed:
            print("Installation verification passed!")
            return 0
        else:
            print("Installation verification failed:")
            for failure in failures:
                print(f"- {failure}")
            return 1
    
    elif args.command == "test":
        passed, results = verifier.run_self_test()
        print(json.dumps(results, indent=2))
        return 0 if passed else 1
    
    elif args.command == "diagnose":
        diagnosis = troubleshooter.diagnose_issues()
        print(json.dumps(diagnosis, indent=2))
        return 0
    
    elif args.command == "fix":
        results = troubleshooter.fix_common_issues()
        print(json.dumps(results, indent=2))
        return 0 if results.get("verification_after_fixes", False) else 1
    
    elif args.command == "report":
        report_path = troubleshooter.generate_diagnostic_report(args.output)
        print(f"Diagnostic report saved to: {report_path}")
        return 0


if __name__ == "__main__":
    import argparse
    import datetime
    sys.exit(main())
