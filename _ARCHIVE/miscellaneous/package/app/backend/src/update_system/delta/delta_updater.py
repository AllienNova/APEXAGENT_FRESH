"""
Delta Update Module for ApexAgent.

This module provides functionality to create and apply delta updates,
which are more bandwidth-efficient than full updates.
"""

import os
import json
import logging
import tempfile
import platform
import subprocess
from typing import Dict, List, Optional, Tuple, Union, Any, Callable
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("delta_updater")

class DeltaUpdater:
    """
    Creates and applies delta updates for ApexAgent.
    
    This class handles the creation of delta update packages and
    applying them to an existing installation.
    """
    
    def __init__(self, 
                 config_path: str = None,
                 installation_path: str = None,
                 progress_callback: Callable = None):
        """
        Initialize the delta updater.
        
        Args:
            config_path: Path to the configuration file
            installation_path: Path to the ApexAgent installation
            progress_callback: Function to call with progress updates
        """
        self.config_path = config_path or os.path.join(
            os.path.expanduser("~"), ".apexagent", "delta_config.json"
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
                
                self.delta_url = config.get('delta_url', 'https://updates.apexagent.example.com/api/v1/delta')
                self.temp_dir = config.get('temp_dir', tempfile.gettempdir())
                self.installation_path = self.installation_path or config.get('installation_path', self._detect_installation_path())
                self.verify_signatures = config.get('verify_signatures', True)
                self.public_key_path = config.get('public_key_path', os.path.join(self.installation_path, 'security', 'update_public_key.pem'))
                self.proxy = config.get('proxy', None)
                self.timeout = config.get('timeout', 300)  # 5 minutes
                self.max_retries = config.get('max_retries', 3)
                self.retry_delay = config.get('retry_delay', 5)  # 5 seconds
                self.delta_algorithm = config.get('delta_algorithm', 'bsdiff')
                
                logger.info(f"Loaded delta updater configuration from {self.config_path}")
            else:
                logger.warning(f"Config file not found at {self.config_path}, using defaults")
                self._set_defaults()
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            self._set_defaults()
    
    def _set_defaults(self) -> None:
        """Set default configuration values."""
        self.delta_url = 'https://updates.apexagent.example.com/api/v1/delta'
        self.temp_dir = tempfile.gettempdir()
        self.installation_path = self.installation_path or self._detect_installation_path()
        self.verify_signatures = True
        self.public_key_path = os.path.join(self.installation_path, 'security', 'update_public_key.pem')
        self.proxy = None
        self.timeout = 300  # 5 minutes
        self.max_retries = 3
        self.retry_delay = 5  # 5 seconds
        self.delta_algorithm = 'bsdiff'  # bsdiff, xdelta, custom
    
    def _save_config(self) -> None:
        """Save the current configuration to the config file."""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            config = {
                'delta_url': self.delta_url,
                'temp_dir': self.temp_dir,
                'installation_path': self.installation_path,
                'verify_signatures': self.verify_signatures,
                'public_key_path': self.public_key_path,
                'proxy': self.proxy,
                'timeout': self.timeout,
                'max_retries': self.max_retries,
                'retry_delay': self.retry_delay,
                'delta_algorithm': self.delta_algorithm
            }
            
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            logger.info(f"Saved delta updater configuration to {self.config_path}")
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
            stage: Current stage of the delta update process
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
    
    def is_delta_update_available(self, target_version: str) -> bool:
        """
        Check if a delta update is available for the target version.
        
        Args:
            target_version: Target version to update to
            
        Returns:
            bool: True if delta update is available
        """
        current_version = self.get_current_version()
        
        if current_version == "unknown":
            logger.warning("Current version unknown, delta update not available")
            return False
        
        # Check if delta update is available from server
        import requests
        
        try:
            # Prepare request parameters
            params = {
                'from_version': current_version,
                'to_version': target_version,
                'platform': platform.system().lower(),
                'architecture': platform.machine().lower()
            }
            
            # Prepare proxy configuration if needed
            proxies = None
            if self.proxy:
                proxies = {
                    'http': self.proxy,
                    'https': self.proxy
                }
            
            # Make request to delta update server
            response = requests.head(
                self.delta_url,
                params=params,
                proxies=proxies,
                timeout=self.timeout
            )
            
            # Check if delta update is available
            return response.status_code == 200
        
        except Exception as e:
            logger.error(f"Error checking for delta update: {e}")
            return False
    
    def download_delta_update(self, target_version: str) -> Optional[str]:
        """
        Download a delta update package.
        
        Args:
            target_version: Target version to update to
            
        Returns:
            str or None: Path to the downloaded delta package, or None if download failed
        """
        current_version = self.get_current_version()
        
        if current_version == "unknown":
            logger.error("Current version unknown, cannot download delta update")
            return None
        
        self._report_progress("download", 0, f"Downloading delta update from {current_version} to {target_version}")
        
        # Create temporary directory for download
        download_dir = os.path.join(self.temp_dir, f"apexagent_delta_{current_version}_to_{target_version}")
        os.makedirs(download_dir, exist_ok=True)
        
        # Determine package filename and path
        package_filename = f"apexagent_delta_{current_version}_to_{target_version}.bin"
        package_path = os.path.join(download_dir, package_filename)
        
        # Check if package already exists
        if os.path.exists(package_path):
            logger.info(f"Delta package already exists at {package_path}")
            return package_path
        
        # Download the package
        import requests
        import time
        
        # Prepare request parameters
        params = {
            'from_version': current_version,
            'to_version': target_version,
            'platform': platform.system().lower(),
            'architecture': platform.machine().lower()
        }
        
        # Prepare proxy configuration if needed
        proxies = None
        if self.proxy:
            proxies = {
                'http': self.proxy,
                'https': self.proxy
            }
        
        retries = 0
        while retries <= self.max_retries:
            try:
                # Download with progress reporting
                with requests.get(
                    self.delta_url,
                    params=params,
                    proxies=proxies,
                    timeout=self.timeout,
                    stream=True
                ) as response:
                    # Check if request was successful
                    if response.status_code != 200:
                        logger.error(f"Failed to download delta update: HTTP {response.status_code}")
                        return None
                    
                    # Get content length if available
                    content_length = response.headers.get('Content-Length')
                    total_size = int(content_length) if content_length else None
                    
                    # Download the file
                    with open(package_path, 'wb') as out_file:
                        downloaded = 0
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                out_file.write(chunk)
                                downloaded += len(chunk)
                                
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
                    return None
    
    def verify_delta_package(self, package_path: str, metadata: Dict[str, Any]) -> bool:
        """
        Verify the integrity and authenticity of a delta update package.
        
        Args:
            package_path: Path to the delta update package
            metadata: Update metadata
            
        Returns:
            bool: True if verification passed
        """
        self._report_progress("verify", 0, "Verifying delta update package")
        
        # Check if file exists
        if not os.path.exists(package_path):
            logger.error(f"Package file not found: {package_path}")
            return False
        
        # Verify file size
        expected_size = metadata.get('delta_size')
        if expected_size:
            actual_size = os.path.getsize(package_path)
            if actual_size != expected_size:
                logger.error(f"Size mismatch: expected {expected_size}, got {actual_size}")
                return False
            
            self._report_progress("verify", 20, "Size verification passed")
        
        # Verify checksum
        checksum_type = metadata.get('delta_checksum_type', 'sha256')
        expected_checksum = metadata.get('delta_checksum')
        
        if expected_checksum:
            try:
                import hashlib
                
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
            signature = metadata.get('delta_signature')
            
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
    
    def apply_delta_update(self, package_path: str, target_version: str) -> bool:
        """
        Apply a delta update to the current installation.
        
        Args:
            package_path: Path to the delta update package
            target_version: Target version to update to
            
        Returns:
            bool: True if update was successful
        """
        self._report_progress("apply", 0, f"Applying delta update to version {target_version}")
        
        # Create temporary directory for update
        update_dir = os.path.join(os.path.dirname(package_path), "update_files")
        os.makedirs(update_dir, exist_ok=True)
        
        try:
            # Determine which delta algorithm to use
            if self.delta_algorithm == 'bsdiff':
                success = self._apply_bsdiff_delta(package_path, update_dir)
            elif self.delta_algorithm == 'xdelta':
                success = self._apply_xdelta_delta(package_path, update_dir)
            elif self.delta_algorithm == 'custom':
                success = self._apply_custom_delta(package_path, update_dir)
            else:
                logger.error(f"Unsupported delta algorithm: {self.delta_algorithm}")
                return False
            
            if not success:
                logger.error("Failed to apply delta update")
                return False
            
            # Apply the updated files to the installation
            self._report_progress("apply", 60, "Applying updated files to installation")
            
            # Copy files from update_dir to installation_path
            for root, dirs, files in os.walk(update_dir):
                rel_path = os.path.relpath(root, update_dir)
                target_dir = os.path.join(self.installation_path, rel_path)
                
                # Create target directory if it doesn't exist
                os.makedirs(target_dir, exist_ok=True)
                
                # Copy files
                for file in files:
                    src_file = os.path.join(root, file)
                    dst_file = os.path.join(target_dir, file)
                    
                    # Make sure the destination directory exists
                    os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                    
                    # Copy the file
                    import shutil
                    shutil.copy2(src_file, dst_file)
            
            # Update version file
            version_file = os.path.join(self.installation_path, "version.txt")
            with open(version_file, 'w') as f:
                f.write(target_version)
            
            self._report_progress("apply", 100, f"Delta update to version {target_version} complete")
            return True
        
        except Exception as e:
            logger.error(f"Error applying delta update: {e}")
            return False
        finally:
            # Clean up temporary files
            import shutil
            if os.path.exists(update_dir):
                shutil.rmtree(update_dir)
    
    def _apply_bsdiff_delta(self, package_path: str, update_dir: str) -> bool:
        """
        Apply a delta update using the bsdiff algorithm.
        
        Args:
            package_path: Path to the delta update package
            update_dir: Directory to extract updated files to
            
        Returns:
            bool: True if update was successful
        """
        self._report_progress("apply", 10, "Applying bsdiff delta update")
        
        try:
            # Check if bsdiff/bspatch is available
            try:
                import bsdiff4
                has_bsdiff4 = True
            except ImportError:
                has_bsdiff4 = False
                logger.warning("bsdiff4 Python module not available, will try command-line tools")
            
            # Extract delta package
            self._report_progress("apply", 20, "Extracting delta package")
            
            import tarfile
            with tarfile.open(package_path, 'r') as tar:
                tar.extractall(update_dir)
            
            # Read delta manifest
            manifest_path = os.path.join(update_dir, "delta_manifest.json")
            if not os.path.exists(manifest_path):
                logger.error(f"Delta manifest not found: {manifest_path}")
                return False
            
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
            
            # Process each file in the manifest
            self._report_progress("apply", 30, "Processing delta files")
            
            total_files = len(manifest.get('files', []))
            processed_files = 0
            
            for file_entry in manifest.get('files', []):
                file_path = file_entry.get('path')
                action = file_entry.get('action')
                
                if not file_path:
                    continue
                
                # Handle different actions
                if action == 'add':
                    # New file, just copy from the package
                    src_path = os.path.join(update_dir, "new", file_path)
                    dst_path = os.path.join(update_dir, "output", file_path)
                    
                    # Make sure the destination directory exists
                    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                    
                    # Copy the file
                    import shutil
                    shutil.copy2(src_path, dst_path)
                
                elif action == 'remove':
                    # File to be removed, do nothing here
                    # The file will not be copied to the output directory
                    pass
                
                elif action == 'patch':
                    # File to be patched
                    patch_path = os.path.join(update_dir, "patches", file_path + ".patch")
                    src_path = os.path.join(self.installation_path, file_path)
                    dst_path = os.path.join(update_dir, "output", file_path)
                    
                    # Make sure the destination directory exists
                    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                    
                    # Apply patch
                    if has_bsdiff4:
                        # Use bsdiff4 Python module
                        bsdiff4.file_patch(src_path, dst_path, patch_path)
                    else:
                        # Use command-line bspatch
                        subprocess.run(
                            ["bspatch", src_path, dst_path, patch_path],
                            check=True
                        )
                
                # Update progress
                processed_files += 1
                progress = 30 + (processed_files / total_files) * 30
                self._report_progress("apply", progress, f"Processed {processed_files}/{total_files} files")
            
            # Move output files to update_dir root
            output_dir = os.path.join(update_dir, "output")
            if os.path.exists(output_dir):
                for item in os.listdir(output_dir):
                    src = os.path.join(output_dir, item)
                    dst = os.path.join(update_dir, item)
                    
                    if os.path.exists(dst):
                        if os.path.isdir(dst):
                            import shutil
                            shutil.rmtree(dst)
                        else:
                            os.remove(dst)
                    
                    import shutil
                    if os.path.isdir(src):
                        shutil.copytree(src, dst)
                    else:
                        shutil.copy2(src, dst)
            
            return True
        
        except Exception as e:
            logger.error(f"Error applying bsdiff delta: {e}")
            return False
    
    def _apply_xdelta_delta(self, package_path: str, update_dir: str) -> bool:
        """
        Apply a delta update using the xdelta algorithm.
        
        Args:
            package_path: Path to the delta update package
            update_dir: Directory to extract updated files to
            
        Returns:
            bool: True if update was successful
        """
        self._report_progress("apply", 10, "Applying xdelta delta update")
        
        try:
            # Extract delta package
            self._report_progress("apply", 20, "Extracting delta package")
            
            import tarfile
            with tarfile.open(package_path, 'r') as tar:
                tar.extractall(update_dir)
            
            # Read delta manifest
            manifest_path = os.path.join(update_dir, "delta_manifest.json")
            if not os.path.exists(manifest_path):
                logger.error(f"Delta manifest not found: {manifest_path}")
                return False
            
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
            
            # Process each file in the manifest
            self._report_progress("apply", 30, "Processing delta files")
            
            total_files = len(manifest.get('files', []))
            processed_files = 0
            
            for file_entry in manifest.get('files', []):
                file_path = file_entry.get('path')
                action = file_entry.get('action')
                
                if not file_path:
                    continue
                
                # Handle different actions
                if action == 'add':
                    # New file, just copy from the package
                    src_path = os.path.join(update_dir, "new", file_path)
                    dst_path = os.path.join(update_dir, "output", file_path)
                    
                    # Make sure the destination directory exists
                    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                    
                    # Copy the file
                    import shutil
                    shutil.copy2(src_path, dst_path)
                
                elif action == 'remove':
                    # File to be removed, do nothing here
                    # The file will not be copied to the output directory
                    pass
                
                elif action == 'patch':
                    # File to be patched
                    patch_path = os.path.join(update_dir, "patches", file_path + ".vcdiff")
                    src_path = os.path.join(self.installation_path, file_path)
                    dst_path = os.path.join(update_dir, "output", file_path)
                    
                    # Make sure the destination directory exists
                    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                    
                    # Apply patch using xdelta3
                    subprocess.run(
                        ["xdelta3", "-d", "-s", src_path, patch_path, dst_path],
                        check=True
                    )
                
                # Update progress
                processed_files += 1
                progress = 30 + (processed_files / total_files) * 30
                self._report_progress("apply", progress, f"Processed {processed_files}/{total_files} files")
            
            # Move output files to update_dir root
            output_dir = os.path.join(update_dir, "output")
            if os.path.exists(output_dir):
                for item in os.listdir(output_dir):
                    src = os.path.join(output_dir, item)
                    dst = os.path.join(update_dir, item)
                    
                    if os.path.exists(dst):
                        if os.path.isdir(dst):
                            import shutil
                            shutil.rmtree(dst)
                        else:
                            os.remove(dst)
                    
                    import shutil
                    if os.path.isdir(src):
                        shutil.copytree(src, dst)
                    else:
                        shutil.copy2(src, dst)
            
            return True
        
        except Exception as e:
            logger.error(f"Error applying xdelta delta: {e}")
            return False
    
    def _apply_custom_delta(self, package_path: str, update_dir: str) -> bool:
        """
        Apply a delta update using a custom algorithm.
        
        Args:
            package_path: Path to the delta update package
            update_dir: Directory to extract updated files to
            
        Returns:
            bool: True if update was successful
        """
        self._report_progress("apply", 10, "Applying custom delta update")
        
        try:
            # Extract delta package
            self._report_progress("apply", 20, "Extracting delta package")
            
            import tarfile
            with tarfile.open(package_path, 'r') as tar:
                tar.extractall(update_dir)
            
            # Check for custom delta application script
            script_path = os.path.join(update_dir, "apply_delta.py")
            if not os.path.exists(script_path):
                logger.error(f"Custom delta application script not found: {script_path}")
                return False
            
            # Run the custom delta application script
            self._report_progress("apply", 30, "Running custom delta application script")
            
            result = subprocess.run(
                [sys.executable, script_path, self.installation_path, update_dir],
                check=True,
                capture_output=True,
                text=True
            )
            
            logger.info(f"Custom delta application script output: {result.stdout}")
            
            if result.returncode != 0:
                logger.error(f"Custom delta application script failed: {result.stderr}")
                return False
            
            return True
        
        except Exception as e:
            logger.error(f"Error applying custom delta: {e}")
            return False
    
    def create_delta_package(self, old_version_dir: str, new_version_dir: str, output_path: str) -> bool:
        """
        Create a delta update package between two versions.
        
        Args:
            old_version_dir: Directory containing the old version
            new_version_dir: Directory containing the new version
            output_path: Path to save the delta package
            
        Returns:
            bool: True if package creation was successful
        """
        self._report_progress("create", 0, "Creating delta update package")
        
        try:
            # Create temporary directory for delta files
            delta_dir = os.path.join(self.temp_dir, "delta_creation")
            os.makedirs(delta_dir, exist_ok=True)
            
            # Create directories for new files and patches
            new_dir = os.path.join(delta_dir, "new")
            patches_dir = os.path.join(delta_dir, "patches")
            os.makedirs(new_dir, exist_ok=True)
            os.makedirs(patches_dir, exist_ok=True)
            
            # Scan directories and compare files
            self._report_progress("create", 10, "Scanning directories")
            
            old_files = {}
            for root, _, files in os.walk(old_version_dir):
                rel_path = os.path.relpath(root, old_version_dir)
                for file in files:
                    file_path = os.path.join(rel_path, file)
                    if file_path.startswith('./'):
                        file_path = file_path[2:]
                    old_files[file_path] = os.path.join(root, file)
            
            new_files = {}
            for root, _, files in os.walk(new_version_dir):
                rel_path = os.path.relpath(root, new_version_dir)
                for file in files:
                    file_path = os.path.join(rel_path, file)
                    if file_path.startswith('./'):
                        file_path = file_path[2:]
                    new_files[file_path] = os.path.join(root, file)
            
            # Create manifest
            manifest = {
                'files': [],
                'created_at': datetime.now().isoformat(),
                'delta_algorithm': self.delta_algorithm
            }
            
            # Process files
            self._report_progress("create", 20, "Processing files")
            
            total_files = len(set(list(old_files.keys()) + list(new_files.keys())))
            processed_files = 0
            
            # Find added, removed, and modified files
            for file_path in set(new_files.keys()):
                if file_path not in old_files:
                    # Added file
                    manifest['files'].append({
                        'path': file_path,
                        'action': 'add'
                    })
                    
                    # Copy new file
                    dst_dir = os.path.join(new_dir, os.path.dirname(file_path))
                    os.makedirs(dst_dir, exist_ok=True)
                    
                    import shutil
                    shutil.copy2(new_files[file_path], os.path.join(new_dir, file_path))
                else:
                    # Check if file was modified
                    import filecmp
                    if not filecmp.cmp(old_files[file_path], new_files[file_path], shallow=False):
                        # Modified file
                        manifest['files'].append({
                            'path': file_path,
                            'action': 'patch'
                        })
                        
                        # Create patch
                        patch_dir = os.path.join(patches_dir, os.path.dirname(file_path))
                        os.makedirs(patch_dir, exist_ok=True)
                        
                        if self.delta_algorithm == 'bsdiff':
                            # Use bsdiff
                            try:
                                import bsdiff4
                                bsdiff4.file_diff(
                                    old_files[file_path],
                                    new_files[file_path],
                                    os.path.join(patches_dir, file_path + ".patch")
                                )
                            except ImportError:
                                # Use command-line bsdiff
                                subprocess.run(
                                    ["bsdiff", old_files[file_path], new_files[file_path], os.path.join(patches_dir, file_path + ".patch")],
                                    check=True
                                )
                        elif self.delta_algorithm == 'xdelta':
                            # Use xdelta3
                            subprocess.run(
                                ["xdelta3", "-e", "-s", old_files[file_path], new_files[file_path], os.path.join(patches_dir, file_path + ".vcdiff")],
                                check=True
                            )
                        elif self.delta_algorithm == 'custom':
                            # Use custom delta algorithm
                            # This would be implemented by the user
                            pass
                
                processed_files += 1
                progress = 20 + (processed_files / total_files) * 30
                self._report_progress("create", progress, f"Processed {processed_files}/{total_files} files")
            
            # Find removed files
            for file_path in set(old_files.keys()):
                if file_path not in new_files:
                    # Removed file
                    manifest['files'].append({
                        'path': file_path,
                        'action': 'remove'
                    })
                    
                    processed_files += 1
                    progress = 20 + (processed_files / total_files) * 30
                    self._report_progress("create", progress, f"Processed {processed_files}/{total_files} files")
            
            # Save manifest
            with open(os.path.join(delta_dir, "delta_manifest.json"), 'w') as f:
                json.dump(manifest, f, indent=2)
            
            # Create delta package
            self._report_progress("create", 60, "Creating delta package")
            
            import tarfile
            with tarfile.open(output_path, 'w:gz') as tar:
                tar.add(delta_dir, arcname=".")
            
            self._report_progress("create", 100, f"Delta package created: {output_path}")
            return True
        
        except Exception as e:
            logger.error(f"Error creating delta package: {e}")
            return False
        finally:
            # Clean up temporary files
            import shutil
            if os.path.exists(delta_dir):
                shutil.rmtree(delta_dir)


def main():
    """Command-line interface for delta updates."""
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(description="ApexAgent Delta Updater")
    
    parser.add_argument("--config", type=str,
                        help="Path to configuration file")
    parser.add_argument("--install-path", type=str,
                        help="Path to ApexAgent installation")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Check command
    check_parser = subparsers.add_parser("check", help="Check if delta update is available")
    check_parser.add_argument("--target-version", type=str, required=True,
                             help="Target version to update to")
    
    # Apply command
    apply_parser = subparsers.add_parser("apply", help="Apply a delta update")
    apply_parser.add_argument("--package", type=str, required=True,
                             help="Path to delta update package")
    apply_parser.add_argument("--target-version", type=str, required=True,
                             help="Target version to update to")
    apply_parser.add_argument("--metadata-file", type=str,
                             help="Path to update metadata JSON file")
    
    # Create command
    create_parser = subparsers.add_parser("create", help="Create a delta update package")
    create_parser.add_argument("--old-version-dir", type=str, required=True,
                              help="Directory containing the old version")
    create_parser.add_argument("--new-version-dir", type=str, required=True,
                              help="Directory containing the new version")
    create_parser.add_argument("--output", type=str, required=True,
                              help="Path to save the delta package")
    create_parser.add_argument("--algorithm", type=str, choices=["bsdiff", "xdelta", "custom"],
                              default="bsdiff", help="Delta algorithm to use")
    
    args = parser.parse_args()
    
    # Create delta updater
    updater = DeltaUpdater(config_path=args.config, installation_path=args.install_path)
    
    if args.command == "check":
        available = updater.is_delta_update_available(args.target_version)
        
        if available:
            print(f"Delta update to version {args.target_version} is available")
            return 0
        else:
            print(f"No delta update available to version {args.target_version}")
            return 1
    
    elif args.command == "apply":
        # Load metadata if provided
        metadata = {}
        if args.metadata_file:
            try:
                with open(args.metadata_file, 'r') as f:
                    metadata = json.load(f)
            except Exception as e:
                print(f"Error loading metadata: {e}")
                return 1
        
        # Verify package if metadata is available
        if metadata:
            if not updater.verify_delta_package(args.package, metadata):
                print("Delta package verification failed")
                return 1
        
        # Apply delta update
        success = updater.apply_delta_update(args.package, args.target_version)
        
        if success:
            print(f"Delta update to version {args.target_version} applied successfully")
            return 0
        else:
            print("Failed to apply delta update")
            return 1
    
    elif args.command == "create":
        # Set delta algorithm
        updater.delta_algorithm = args.algorithm
        
        # Create delta package
        success = updater.create_delta_package(args.old_version_dir, args.new_version_dir, args.output)
        
        if success:
            print(f"Delta package created successfully: {args.output}")
            return 0
        else:
            print("Failed to create delta package")
            return 1
    
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
