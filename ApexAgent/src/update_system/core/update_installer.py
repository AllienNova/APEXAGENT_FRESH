"""
Update Installer Module for ApexAgent.

This module provides functionality to download and install updates,
verify their integrity, and manage the installation process.
"""

import os
import json
import time
import shutil
import hashlib
import logging
import tempfile
import platform
import subprocess
import urllib.request
from typing import Dict, List, Optional, Tuple, Union, Any, Callable
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("update_installer")

class UpdateInstaller:
    """
    Installs ApexAgent updates.
    
    This class handles downloading update packages, verifying their integrity,
    and installing them on the system.
    """
    
    def __init__(self, 
                 config_path: str = None,
                 installation_path: str = None,
                 progress_callback: Callable = None):
        """
        Initialize the update installer.
        
        Args:
            config_path: Path to the configuration file
            installation_path: Path to the ApexAgent installation
            progress_callback: Function to call with progress updates
        """
        self.config_path = config_path or os.path.join(
            os.path.expanduser("~"), ".apexagent", "installer_config.json"
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
                
                self.download_url = config.get('download_url', 'https://updates.apexagent.example.com/api/v1/downloads')
                self.temp_dir = config.get('temp_dir', tempfile.gettempdir())
                self.installation_path = self.installation_path or config.get('installation_path', self._detect_installation_path())
                self.backup_dir = config.get('backup_dir', os.path.join(self.temp_dir, 'apexagent_backups'))
                self.verify_signatures = config.get('verify_signatures', True)
                self.public_key_path = config.get('public_key_path', os.path.join(self.installation_path, 'security', 'update_public_key.pem'))
                self.proxy = config.get('proxy', None)
                self.timeout = config.get('timeout', 300)  # 5 minutes
                self.max_retries = config.get('max_retries', 3)
                self.retry_delay = config.get('retry_delay', 5)  # 5 seconds
                
                logger.info(f"Loaded installer configuration from {self.config_path}")
            else:
                logger.warning(f"Config file not found at {self.config_path}, using defaults")
                self._set_defaults()
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            self._set_defaults()
    
    def _set_defaults(self) -> None:
        """Set default configuration values."""
        self.download_url = 'https://updates.apexagent.example.com/api/v1/downloads'
        self.temp_dir = tempfile.gettempdir()
        self.installation_path = self.installation_path or self._detect_installation_path()
        self.backup_dir = os.path.join(self.temp_dir, 'apexagent_backups')
        self.verify_signatures = True
        self.public_key_path = os.path.join(self.installation_path, 'security', 'update_public_key.pem')
        self.proxy = None
        self.timeout = 300  # 5 minutes
        self.max_retries = 3
        self.retry_delay = 5  # 5 seconds
    
    def _save_config(self) -> None:
        """Save the current configuration to the config file."""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            config = {
                'download_url': self.download_url,
                'temp_dir': self.temp_dir,
                'installation_path': self.installation_path,
                'backup_dir': self.backup_dir,
                'verify_signatures': self.verify_signatures,
                'public_key_path': self.public_key_path,
                'proxy': self.proxy,
                'timeout': self.timeout,
                'max_retries': self.max_retries,
                'retry_delay': self.retry_delay
            }
            
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            logger.info(f"Saved installer configuration to {self.config_path}")
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
            stage: Current stage of the update process
            progress: Progress as a percentage (0-100)
            message: Progress message
        """
        if self.progress_callback:
            try:
                self.progress_callback(stage, progress, message)
            except Exception as e:
                logger.error(f"Error in progress callback: {e}")
        
        logger.info(f"[{stage}] {progress:.1f}%: {message}")
    
    def download_update(self, update_metadata: Dict[str, Any]) -> str:
        """
        Download an update package.
        
        Args:
            update_metadata: Update metadata
            
        Returns:
            str: Path to the downloaded package
        
        Raises:
            ValueError: If update metadata is invalid
            IOError: If download fails
        """
        if not update_metadata or 'version' not in update_metadata:
            raise ValueError("Invalid update metadata")
        
        version = update_metadata['version']
        platform_type = update_metadata.get('platform', platform.system().lower())
        architecture = update_metadata.get('architecture', platform.machine().lower())
        
        # Normalize platform and architecture
        if platform_type == "darwin":
            platform_type = "macos"
        
        if architecture in ["x86_64", "amd64"]:
            architecture = "x86_64"
        elif architecture in ["arm64", "aarch64"]:
            architecture = "arm64"
        
        # Get download URL from metadata or construct it
        download_url = update_metadata.get('download_url')
        if not download_url:
            download_url = f"{self.download_url}/{version}/{platform_type}/{architecture}"
        
        # Create temporary directory for download
        download_dir = os.path.join(self.temp_dir, f"apexagent_update_{version}")
        os.makedirs(download_dir, exist_ok=True)
        
        # Determine package filename and path
        package_filename = update_metadata.get('filename', f"apexagent_{version}_{platform_type}_{architecture}.zip")
        package_path = os.path.join(download_dir, package_filename)
        
        # Check if package already exists
        if os.path.exists(package_path):
            logger.info(f"Update package already exists at {package_path}")
            return package_path
        
        # Download the package
        self._report_progress("download", 0, f"Downloading update {version}")
        
        retries = 0
        while retries <= self.max_retries:
            try:
                # Setup proxy handler if needed
                handlers = []
                if self.proxy:
                    proxy_handler = urllib.request.ProxyHandler({
                        'http': self.proxy,
                        'https': self.proxy
                    })
                    handlers.append(proxy_handler)
                
                # Create opener with handlers
                opener = urllib.request.build_opener(*handlers)
                
                # Download with progress reporting
                with opener.open(download_url, timeout=self.timeout) as response:
                    # Get content length if available
                    content_length = response.headers.get('Content-Length')
                    total_size = int(content_length) if content_length else None
                    
                    # Download the file
                    with open(package_path, 'wb') as out_file:
                        downloaded = 0
                        block_size = 8192
                        
                        while True:
                            buffer = response.read(block_size)
                            if not buffer:
                                break
                            
                            out_file.write(buffer)
                            downloaded += len(buffer)
                            
                            if total_size:
                                progress = (downloaded / total_size) * 100
                                self._report_progress("download", progress, f"Downloaded {downloaded}/{total_size} bytes")
                
                # Download successful
                self._report_progress("download", 100, f"Download complete: {package_path}")
                return package_path
            
            except Exception as e:
                retries += 1
                if retries <= self.max_retries:
                    logger.warning(f"Download attempt {retries} failed: {e}. Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"Download failed after {retries} attempts: {e}")
                    raise IOError(f"Failed to download update: {e}")
    
    def verify_package(self, package_path: str, update_metadata: Dict[str, Any]) -> bool:
        """
        Verify the integrity and authenticity of an update package.
        
        Args:
            package_path: Path to the update package
            update_metadata: Update metadata
            
        Returns:
            bool: True if verification passed
        """
        self._report_progress("verify", 0, "Verifying update package")
        
        # Check if file exists
        if not os.path.exists(package_path):
            logger.error(f"Package file not found: {package_path}")
            return False
        
        # Verify file size
        expected_size = update_metadata.get('size')
        if expected_size:
            actual_size = os.path.getsize(package_path)
            if actual_size != expected_size:
                logger.error(f"Size mismatch: expected {expected_size}, got {actual_size}")
                return False
            
            self._report_progress("verify", 20, "Size verification passed")
        
        # Verify checksum
        checksum_type = update_metadata.get('checksum_type', 'sha256')
        expected_checksum = update_metadata.get('checksum')
        
        if expected_checksum:
            try:
                if checksum_type == 'md5':
                    hasher = hashlib.md5()
                elif checksum_type == 'sha1':
                    hasher = hashlib.sha1()
                else:  # Default to sha256
                    hasher = hashlib.sha256()
                
                with open(package_path, 'rb') as f:
                    # Read and update hash in chunks
                    for chunk in iter(lambda: f.read(4096), b""):
                        hasher.update(chunk)
                
                actual_checksum = hasher.hexdigest()
                
                if actual_checksum != expected_checksum:
                    logger.error(f"Checksum mismatch: expected {expected_checksum}, got {actual_checksum}")
                    return False
                
                self._report_progress("verify", 50, "Checksum verification passed")
            except Exception as e:
                logger.error(f"Checksum verification failed: {e}")
                return False
        
        # Verify signature if enabled
        if self.verify_signatures:
            signature = update_metadata.get('signature')
            
            if signature:
                try:
                    # Check if public key exists
                    if not os.path.exists(self.public_key_path):
                        logger.error(f"Public key not found: {self.public_key_path}")
                        return False
                    
                    # Verify signature
                    # This is a simplified example; in a real implementation,
                    # you would use proper cryptographic libraries
                    from cryptography.hazmat.primitives import hashes
                    from cryptography.hazmat.primitives.asymmetric import padding
                    from cryptography.hazmat.primitives.serialization import load_pem_public_key
                    
                    with open(self.public_key_path, 'rb') as key_file:
                        public_key = load_pem_public_key(key_file.read())
                    
                    with open(package_path, 'rb') as f:
                        file_data = f.read()
                    
                    # Decode signature from base64
                    import base64
                    signature_bytes = base64.b64decode(signature)
                    
                    # Verify signature
                    public_key.verify(
                        signature_bytes,
                        file_data,
                        padding.PKCS1v15(),
                        hashes.SHA256()
                    )
                    
                    self._report_progress("verify", 80, "Signature verification passed")
                except ImportError:
                    logger.warning("Cryptography library not available, skipping signature verification")
                except Exception as e:
                    logger.error(f"Signature verification failed: {e}")
                    return False
        
        self._report_progress("verify", 100, "Package verification complete")
        return True
    
    def backup_current_installation(self) -> str:
        """
        Create a backup of the current installation.
        
        Returns:
            str: Path to the backup directory
        
        Raises:
            IOError: If backup fails
        """
        self._report_progress("backup", 0, "Creating backup of current installation")
        
        # Ensure backup directory exists
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # Create timestamped backup directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(self.backup_dir, f"apexagent_backup_{timestamp}")
        os.makedirs(backup_path, exist_ok=True)
        
        try:
            # Get current version
            version_file = os.path.join(self.installation_path, "version.txt")
            current_version = "unknown"
            if os.path.exists(version_file):
                with open(version_file, 'r') as f:
                    current_version = f.read().strip()
            
            # Save backup metadata
            metadata = {
                'timestamp': timestamp,
                'version': current_version,
                'installation_path': self.installation_path,
                'platform': platform.system().lower(),
                'architecture': platform.machine().lower()
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
            
            self._report_progress("backup", 100, f"Backup complete: {backup_path}")
            return backup_path
        
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            raise IOError(f"Failed to create backup: {e}")
    
    def extract_package(self, package_path: str) -> str:
        """
        Extract the update package.
        
        Args:
            package_path: Path to the update package
            
        Returns:
            str: Path to the extracted directory
        
        Raises:
            IOError: If extraction fails
        """
        self._report_progress("extract", 0, "Extracting update package")
        
        # Determine extraction directory
        extract_dir = os.path.join(os.path.dirname(package_path), "extracted")
        os.makedirs(extract_dir, exist_ok=True)
        
        try:
            # Determine package type and extract accordingly
            if package_path.endswith('.zip'):
                import zipfile
                with zipfile.ZipFile(package_path, 'r') as zip_ref:
                    total_files = len(zip_ref.namelist())
                    for i, member in enumerate(zip_ref.namelist()):
                        zip_ref.extract(member, extract_dir)
                        progress = ((i + 1) / total_files) * 100
                        if i % 10 == 0 or i == total_files - 1:
                            self._report_progress("extract", progress, f"Extracted {i+1}/{total_files} files")
            
            elif package_path.endswith('.tar.gz') or package_path.endswith('.tgz'):
                import tarfile
                with tarfile.open(package_path, 'r:gz') as tar_ref:
                    total_files = len(tar_ref.getmembers())
                    for i, member in enumerate(tar_ref.getmembers()):
                        tar_ref.extract(member, extract_dir)
                        progress = ((i + 1) / total_files) * 100
                        if i % 10 == 0 or i == total_files - 1:
                            self._report_progress("extract", progress, f"Extracted {i+1}/{total_files} files")
            
            else:
                raise ValueError(f"Unsupported package format: {package_path}")
            
            self._report_progress("extract", 100, "Extraction complete")
            return extract_dir
        
        except Exception as e:
            logger.error(f"Extraction failed: {e}")
            raise IOError(f"Failed to extract update package: {e}")
    
    def install_update(self, extract_dir: str, update_metadata: Dict[str, Any]) -> bool:
        """
        Install the extracted update.
        
        Args:
            extract_dir: Path to the extracted update
            update_metadata: Update metadata
            
        Returns:
            bool: True if installation was successful
        
        Raises:
            IOError: If installation fails
        """
        self._report_progress("install", 0, "Installing update")
        
        try:
            # Check if there's an install script
            install_script = None
            system = platform.system().lower()
            
            if system == "windows":
                install_script = os.path.join(extract_dir, "install.ps1")
                if not os.path.exists(install_script):
                    install_script = os.path.join(extract_dir, "install.bat")
            else:  # macOS or Linux
                install_script = os.path.join(extract_dir, "install.sh")
            
            # If there's an install script, run it
            if install_script and os.path.exists(install_script):
                self._report_progress("install", 10, "Running install script")
                
                # Make script executable on Unix-like systems
                if system != "windows":
                    os.chmod(install_script, 0o755)
                
                # Prepare command
                if system == "windows":
                    if install_script.endswith(".ps1"):
                        cmd = ["powershell", "-ExecutionPolicy", "Bypass", "-File", install_script]
                    else:
                        cmd = [install_script]
                else:
                    cmd = [install_script]
                
                # Add installation path as argument
                cmd.append(self.installation_path)
                
                # Run the script
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                # Monitor the process
                while process.poll() is None:
                    time.sleep(0.5)
                
                # Check result
                if process.returncode != 0:
                    stdout, stderr = process.communicate()
                    logger.error(f"Install script failed with code {process.returncode}")
                    logger.error(f"Stdout: {stdout}")
                    logger.error(f"Stderr: {stderr}")
                    raise IOError(f"Install script failed with code {process.returncode}")
                
                self._report_progress("install", 90, "Install script completed successfully")
            
            else:
                # No install script, perform manual installation
                self._report_progress("install", 10, "Performing manual installation")
                
                # Copy files from extract_dir to installation_path
                for item in os.listdir(extract_dir):
                    src = os.path.join(extract_dir, item)
                    dst = os.path.join(self.installation_path, item)
                    
                    if os.path.isdir(src):
                        # If directory exists, merge contents
                        if os.path.exists(dst):
                            # Copy files recursively, overwriting existing files
                            for root, dirs, files in os.walk(src):
                                rel_path = os.path.relpath(root, src)
                                dst_dir = os.path.join(dst, rel_path)
                                os.makedirs(dst_dir, exist_ok=True)
                                
                                for file in files:
                                    src_file = os.path.join(root, file)
                                    dst_file = os.path.join(dst_dir, file)
                                    shutil.copy2(src_file, dst_file)
                        else:
                            # Directory doesn't exist, copy it entirely
                            shutil.copytree(src, dst)
                    else:
                        # Copy file, overwriting if it exists
                        shutil.copy2(src, dst)
                
                self._report_progress("install", 80, "Files copied to installation directory")
                
                # Update version file
                version = update_metadata.get('version', 'unknown')
                version_file = os.path.join(self.installation_path, "version.txt")
                
                with open(version_file, 'w') as f:
                    f.write(version)
                
                self._report_progress("install", 90, f"Version file updated to {version}")
            
            # Run post-install verification
            self._report_progress("install", 95, "Running post-install verification")
            
            # Check if the installation is valid
            if not self._verify_installation():
                raise IOError("Post-install verification failed")
            
            self._report_progress("install", 100, "Installation complete")
            return True
        
        except Exception as e:
            logger.error(f"Installation failed: {e}")
            raise IOError(f"Failed to install update: {e}")
    
    def _verify_installation(self) -> bool:
        """
        Verify that the installation is valid.
        
        Returns:
            bool: True if verification passed
        """
        # Check if essential files exist
        essential_files = ["version.txt"]
        
        for file in essential_files:
            file_path = os.path.join(self.installation_path, file)
            if not os.path.exists(file_path):
                logger.error(f"Essential file missing: {file}")
                return False
        
        # Additional platform-specific checks could be added here
        
        return True
    
    def restore_backup(self, backup_path: str) -> bool:
        """
        Restore from a backup.
        
        Args:
            backup_path: Path to the backup directory
            
        Returns:
            bool: True if restoration was successful
        """
        self._report_progress("restore", 0, "Restoring from backup")
        
        try:
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
            self._report_progress("restore", 20, "Clearing installation directory")
            
            preserve_dirs = ['logs', 'temp', 'cache', 'user_data']
            
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
            self._report_progress("restore", 40, "Copying files from backup")
            
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
            
            self._report_progress("restore", 80, "Files restored from backup")
            
            # Verify restoration
            if not self._verify_installation():
                logger.error("Restoration verification failed")
                return False
            
            self._report_progress("restore", 100, "Restoration complete")
            return True
        
        except Exception as e:
            logger.error(f"Restoration failed: {e}")
            return False
    
    def cleanup(self, package_path: str = None, extract_dir: str = None) -> None:
        """
        Clean up temporary files.
        
        Args:
            package_path: Path to the update package
            extract_dir: Path to the extracted update
        """
        self._report_progress("cleanup", 0, "Cleaning up temporary files")
        
        try:
            # Remove package file if specified
            if package_path and os.path.exists(package_path):
                os.remove(package_path)
                logger.info(f"Removed package file: {package_path}")
            
            # Remove extraction directory if specified
            if extract_dir and os.path.exists(extract_dir):
                shutil.rmtree(extract_dir)
                logger.info(f"Removed extraction directory: {extract_dir}")
            
            # Clean up old backups (keep last 3)
            if os.path.exists(self.backup_dir):
                backups = []
                
                for item in os.listdir(self.backup_dir):
                    item_path = os.path.join(self.backup_dir, item)
                    if os.path.isdir(item_path) and item.startswith("apexagent_backup_"):
                        backups.append((item_path, os.path.getmtime(item_path)))
                
                # Sort backups by modification time (newest first)
                backups.sort(key=lambda x: x[1], reverse=True)
                
                # Remove old backups
                for backup_path, _ in backups[3:]:
                    shutil.rmtree(backup_path)
                    logger.info(f"Removed old backup: {backup_path}")
            
            self._report_progress("cleanup", 100, "Cleanup complete")
        
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
    
    def perform_update(self, update_metadata: Dict[str, Any]) -> bool:
        """
        Perform the complete update process.
        
        Args:
            update_metadata: Update metadata
            
        Returns:
            bool: True if update was successful
        """
        package_path = None
        extract_dir = None
        backup_path = None
        success = False
        
        try:
            # Download update package
            package_path = self.download_update(update_metadata)
            
            # Verify package
            if not self.verify_package(package_path, update_metadata):
                logger.error("Package verification failed")
                return False
            
            # Backup current installation
            backup_path = self.backup_current_installation()
            
            # Extract package
            extract_dir = self.extract_package(package_path)
            
            # Install update
            success = self.install_update(extract_dir, update_metadata)
            
            # Clean up
            self.cleanup(package_path, extract_dir)
            
            return success
        
        except Exception as e:
            logger.error(f"Update failed: {e}")
            
            # Attempt to restore from backup if available
            if backup_path and os.path.exists(backup_path):
                logger.info("Attempting to restore from backup")
                if self.restore_backup(backup_path):
                    logger.info("Successfully restored from backup")
                else:
                    logger.error("Failed to restore from backup")
            
            # Clean up
            self.cleanup(package_path, extract_dir)
            
            return False


def main():
    """Command-line interface for update installation."""
    import argparse
    
    parser = argparse.ArgumentParser(description="ApexAgent Update Installer")
    
    parser.add_argument("--config", type=str,
                        help="Path to configuration file")
    parser.add_argument("--install-path", type=str,
                        help="Path to ApexAgent installation")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Install command
    install_parser = subparsers.add_parser("install", help="Install an update")
    install_parser.add_argument("--metadata-file", type=str, required=True,
                               help="Path to update metadata JSON file")
    
    # Restore command
    restore_parser = subparsers.add_parser("restore", help="Restore from backup")
    restore_parser.add_argument("--backup-path", type=str, required=True,
                               help="Path to backup directory")
    
    # List backups command
    list_backups_parser = subparsers.add_parser("list-backups", help="List available backups")
    
    args = parser.parse_args()
    
    # Create update installer
    installer = UpdateInstaller(config_path=args.config, installation_path=args.install_path)
    
    if args.command == "install":
        try:
            with open(args.metadata_file, 'r') as f:
                update_metadata = json.load(f)
            
            success = installer.perform_update(update_metadata)
            
            if success:
                print("Update installed successfully")
                return 0
            else:
                print("Update installation failed")
                return 1
        except Exception as e:
            print(f"Error: {e}")
            return 1
    
    elif args.command == "restore":
        success = installer.restore_backup(args.backup_path)
        
        if success:
            print("Restoration completed successfully")
            return 0
        else:
            print("Restoration failed")
            return 1
    
    elif args.command == "list-backups":
        backup_dir = installer.backup_dir
        
        if not os.path.exists(backup_dir):
            print(f"No backups found (backup directory does not exist: {backup_dir})")
            return 0
        
        backups = []
        
        for item in os.listdir(backup_dir):
            item_path = os.path.join(backup_dir, item)
            if os.path.isdir(item_path) and item.startswith("apexagent_backup_"):
                metadata_file = os.path.join(item_path, "backup_metadata.json")
                
                if os.path.exists(metadata_file):
                    try:
                        with open(metadata_file, 'r') as f:
                            metadata = json.load(f)
                        
                        backups.append({
                            'path': item_path,
                            'timestamp': metadata.get('timestamp'),
                            'version': metadata.get('version', 'unknown'),
                            'size': sum(os.path.getsize(os.path.join(dirpath, filename))
                                       for dirpath, _, filenames in os.walk(item_path)
                                       for filename in filenames)
                        })
                    except Exception as e:
                        print(f"Error reading backup metadata: {e}")
                        backups.append({
                            'path': item_path,
                            'timestamp': 'unknown',
                            'version': 'unknown',
                            'size': 0
                        })
        
        # Sort backups by timestamp (newest first)
        backups.sort(key=lambda x: x['timestamp'] if x['timestamp'] != 'unknown' else '', reverse=True)
        
        if backups:
            print(f"Found {len(backups)} backup(s):")
            for i, backup in enumerate(backups):
                size_mb = backup['size'] / (1024 * 1024)
                print(f"{i+1}. {backup['timestamp']} - Version: {backup['version']} - Size: {size_mb:.2f} MB")
                print(f"   Path: {backup['path']}")
        else:
            print("No backups found")
        
        return 0
    
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
