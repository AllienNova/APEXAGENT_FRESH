#!/usr/bin/env python3
"""
Plugin Marketplace and Ecosystem Framework for ApexAgent

This module provides a comprehensive framework for managing plugins,
including discovery, installation, updates, security, and potentially
monetization, creating a robust ecosystem around ApexAgent.
"""

import os
import sys
import json
import uuid
import logging
import threading
import time
import shutil
import zipfile
import hashlib
import requests
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union, Callable, Set, TypeVar
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
import queue
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("plugin_marketplace.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("plugin_marketplace")

# Type variables for generic functions
T = TypeVar("T")

class PluginStatus(Enum):
    """Enumeration of plugin statuses."""
    INSTALLED = "installed"
    ENABLED = "enabled"
    DISABLED = "disabled"
    UNINSTALLED = "uninstalled"
    UPDATE_AVAILABLE = "update_available"
    ERROR = "error"
    PENDING_INSTALL = "pending_install"
    PENDING_UNINSTALL = "pending_uninstall"

class PluginSourceType(Enum):
    """Enumeration of plugin source types."""
    LOCAL = "local"
    REMOTE_REPOSITORY = "remote_repository"
    DIRECT_URL = "direct_url"

class PluginPermission(Enum):
    """Enumeration of potential plugin permissions."""
    FILE_READ = "file_read"
    FILE_WRITE = "file_write"
    NETWORK_ACCESS = "network_access"
    SYSTEM_INFO = "system_info"
    EXECUTE_CODE = "execute_code"
    MODIFY_SETTINGS = "modify_settings"
    ACCESS_USER_DATA = "access_user_data"
    CUSTOM = "custom"

@dataclass
class PluginMarketplaceConfig:
    """Configuration for the plugin marketplace system."""
    enabled: bool = True
    plugin_directory: str = "plugins"
    repository_urls: List[str] = field(default_factory=list)
    allow_local_install: bool = True
    allow_direct_url_install: bool = True
    auto_update_check: bool = True
    update_check_interval: int = 86400  # seconds (1 day)
    security_sandboxing: bool = True
    require_signatures: bool = False
    trusted_publishers: List[str] = field(default_factory=list)
    cache_directory: str = "plugin_cache"
    max_cache_size: int = 1024 * 1024 * 100  # 100 MB
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the configuration to a dictionary."""
        return {
            "enabled": self.enabled,
            "plugin_directory": self.plugin_directory,
            "repository_urls": self.repository_urls,
            "allow_local_install": self.allow_local_install,
            "allow_direct_url_install": self.allow_direct_url_install,
            "auto_update_check": self.auto_update_check,
            "update_check_interval": self.update_check_interval,
            "security_sandboxing": self.security_sandboxing,
            "require_signatures": self.require_signatures,
            "trusted_publishers": self.trusted_publishers,
            "cache_directory": self.cache_directory,
            "max_cache_size": self.max_cache_size
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PluginMarketplaceConfig":
        """Create a configuration from a dictionary."""
        return cls(
            enabled=data.get("enabled", True),
            plugin_directory=data.get("plugin_directory", "plugins"),
            repository_urls=data.get("repository_urls", []),
            allow_local_install=data.get("allow_local_install", True),
            allow_direct_url_install=data.get("allow_direct_url_install", True),
            auto_update_check=data.get("auto_update_check", True),
            update_check_interval=data.get("update_check_interval", 86400),
            security_sandboxing=data.get("security_sandboxing", True),
            require_signatures=data.get("require_signatures", False),
            trusted_publishers=data.get("trusted_publishers", []),
            cache_directory=data.get("cache_directory", "plugin_cache"),
            max_cache_size=data.get("max_cache_size", 1024 * 1024 * 100)
        )

@dataclass
class PluginDependency:
    """Represents a plugin dependency."""
    plugin_id: str
    min_version: Optional[str] = None
    max_version: Optional[str] = None
    required: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "plugin_id": self.plugin_id,
            "min_version": self.min_version,
            "max_version": self.max_version,
            "required": self.required
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PluginDependency":
        """Create from dictionary."""
        return cls(
            plugin_id=data["plugin_id"],
            min_version=data.get("min_version"),
            max_version=data.get("max_version"),
            required=data.get("required", True)
        )

@dataclass
class PluginMetadata:
    """Metadata for a plugin."""
    plugin_id: str
    name: str
    version: str
    description: str
    author: str
    author_email: Optional[str] = None
    url: Optional[str] = None
    license: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    dependencies: List[PluginDependency] = field(default_factory=list)
    permissions: List[PluginPermission] = field(default_factory=list)
    entry_point: str = "main.py"  # Relative path within the plugin package
    icon_url: Optional[str] = None
    min_app_version: Optional[str] = None
    max_app_version: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    # Fields populated by the marketplace/repository
    download_url: Optional[str] = None
    signature: Optional[str] = None
    checksum: Optional[str] = None
    size: Optional[int] = None
    rating: Optional[float] = None
    download_count: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "plugin_id": self.plugin_id,
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "author_email": self.author_email,
            "url": self.url,
            "license": self.license,
            "tags": self.tags,
            "dependencies": [dep.to_dict() for dep in self.dependencies],
            "permissions": [perm.value for perm in self.permissions],
            "entry_point": self.entry_point,
            "icon_url": self.icon_url,
            "min_app_version": self.min_app_version,
            "max_app_version": self.max_app_version,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "download_url": self.download_url,
            "signature": self.signature,
            "checksum": self.checksum,
            "size": self.size,
            "rating": self.rating,
            "download_count": self.download_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PluginMetadata":
        """Create from dictionary."""
        return cls(
            plugin_id=data["plugin_id"],
            name=data["name"],
            version=data["version"],
            description=data["description"],
            author=data["author"],
            author_email=data.get("author_email"),
            url=data.get("url"),
            license=data.get("license"),
            tags=data.get("tags", []),
            dependencies=[PluginDependency.from_dict(dep) for dep in data.get("dependencies", [])],
            permissions=[PluginPermission(perm) for perm in data.get("permissions", [])],
            entry_point=data.get("entry_point", "main.py"),
            icon_url=data.get("icon_url"),
            min_app_version=data.get("min_app_version"),
            max_app_version=data.get("max_app_version"),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
            updated_at=datetime.fromisoformat(data.get("updated_at", datetime.now().isoformat())),
            download_url=data.get("download_url"),
            signature=data.get("signature"),
            checksum=data.get("checksum"),
            size=data.get("size"),
            rating=data.get("rating"),
            download_count=data.get("download_count")
        )
    
    @classmethod
    def from_manifest(cls, manifest_path: Path) -> "PluginMetadata":
        """Load metadata from a manifest file (e.g., plugin.json)."""
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return cls.from_dict(data)
        except Exception as e:
            logger.error(f"Failed to load plugin manifest from {manifest_path}: {str(e)}")
            raise

@dataclass
class InstalledPlugin:
    """Represents an installed plugin."""
    metadata: PluginMetadata
    install_path: Path
    status: PluginStatus
    installed_at: datetime
    last_enabled_at: Optional[datetime] = None
    last_disabled_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "metadata": self.metadata.to_dict(),
            "install_path": str(self.install_path),
            "status": self.status.value,
            "installed_at": self.installed_at.isoformat(),
            "last_enabled_at": self.last_enabled_at.isoformat() if self.last_enabled_at else None,
            "last_disabled_at": self.last_disabled_at.isoformat() if self.last_disabled_at else None,
            "error_message": self.error_message
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "InstalledPlugin":
        """Create from dictionary."""
        return cls(
            metadata=PluginMetadata.from_dict(data["metadata"]),
            install_path=Path(data["install_path"]),
            status=PluginStatus(data["status"]),
            installed_at=datetime.fromisoformat(data["installed_at"]),
            last_enabled_at=datetime.fromisoformat(data["last_enabled_at"]) if data.get("last_enabled_at") else None,
            last_disabled_at=datetime.fromisoformat(data["last_disabled_at"]) if data.get("last_disabled_at") else None,
            error_message=data.get("error_message")
        )

class PluginRepository:
    """Manages plugin repositories."""
    
    def __init__(self, config: PluginMarketplaceConfig):
        """Initialize the plugin repository manager."""
        self.config = config
        self.repositories: Dict[str, List[PluginMetadata]] = {}
        self._lock = threading.RLock()
        self._load_repositories()
    
    def _load_repositories(self) -> None:
        """Load plugin metadata from configured repositories."""
        with self._lock:
            self.repositories = {}
            for repo_url in self.config.repository_urls:
                try:
                    response = requests.get(repo_url, timeout=10)
                    response.raise_for_status()
                    repo_data = response.json()
                    
                    plugins = []
                    for plugin_data in repo_data.get("plugins", []):
                        try:
                            plugins.append(PluginMetadata.from_dict(plugin_data))
                        except Exception as e:
                            logger.error(f"Failed to parse plugin metadata from {repo_url}: {str(e)}")
                    
                    self.repositories[repo_url] = plugins
                    logger.info(f"Loaded {len(plugins)} plugins from repository: {repo_url}")
                except Exception as e:
                    logger.error(f"Failed to load repository {repo_url}: {str(e)}")
    
    def refresh_repositories(self) -> None:
        """Refresh plugin metadata from repositories."""
        self._load_repositories()
    
    def search_plugins(self, query: str, tags: Optional[List[str]] = None) -> List[PluginMetadata]:
        """Search for plugins across all repositories."""
        with self._lock:
            results = []
            query = query.lower()
            
            for repo_url, plugins in self.repositories.items():
                for plugin in plugins:
                    # Check query match
                    if (query in plugin.name.lower() or 
                        query in plugin.description.lower() or 
                        query in plugin.author.lower() or 
                        any(query in tag.lower() for tag in plugin.tags)):
                        
                        # Check tags match
                        if tags and not any(tag in plugin.tags for tag in tags):
                            continue
                        
                        results.append(plugin)
            
            # Remove duplicates (based on plugin_id and version)
            unique_results = {}
            for plugin in results:
                key = (plugin.plugin_id, plugin.version)
                if key not in unique_results:
                    unique_results[key] = plugin
            
            return list(unique_results.values())
    
    def get_plugin_metadata(self, plugin_id: str, version: Optional[str] = None) -> Optional[PluginMetadata]:
        """Get metadata for a specific plugin, optionally a specific version."""
        with self._lock:
            best_match: Optional[PluginMetadata] = None
            
            for repo_url, plugins in self.repositories.items():
                for plugin in plugins:
                    if plugin.plugin_id == plugin_id:
                        if version is None:
                            # Find the latest version
                            if best_match is None or self._compare_versions(plugin.version, best_match.version) > 0:
                                best_match = plugin
                        elif plugin.version == version:
                            return plugin
            
            return best_match
    
    def check_for_updates(self, installed_plugins: List[InstalledPlugin]) -> Dict[str, PluginMetadata]:
        """Check for updates for installed plugins."""
        with self._lock:
            updates_available = {}
            
            for installed in installed_plugins:
                latest_metadata = self.get_plugin_metadata(installed.metadata.plugin_id)
                
                if latest_metadata and self._compare_versions(latest_metadata.version, installed.metadata.version) > 0:
                    updates_available[installed.metadata.plugin_id] = latest_metadata
            
            return updates_available
    
    def _compare_versions(self, v1: str, v2: str) -> int:
        """Compare two version strings (e.g., 1.2.3)."""
        # Simple comparison, can be enhanced with proper version parsing
        parts1 = list(map(int, v1.split(".")))
        parts2 = list(map(int, v2.split(".")))
        
        for i in range(max(len(parts1), len(parts2))):
            p1 = parts1[i] if i < len(parts1) else 0
            p2 = parts2[i] if i < len(parts2) else 0
            
            if p1 > p2:
                return 1
            if p1 < p2:
                return -1
        
        return 0

class PluginInstaller:
    """Handles plugin installation, updates, and uninstallation."""
    
    def __init__(self, config: PluginMarketplaceConfig):
        """Initialize the plugin installer."""
        self.config = config
        self.cache_dir = Path(self.config.cache_directory)
        self.plugin_dir = Path(self.config.plugin_directory)
        self._lock = threading.RLock()
        self._ensure_dirs()
    
    def _ensure_dirs(self) -> None:
        """Ensure cache and plugin directories exist."""
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.plugin_dir.mkdir(parents=True, exist_ok=True)
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of a file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def _verify_checksum(self, file_path: Path, expected_checksum: str) -> bool:
        """Verify the checksum of a downloaded file."""
        if not expected_checksum:
            logger.warning(f"No expected checksum provided for {file_path}. Skipping verification.")
            return True
        
        actual_checksum = self._calculate_checksum(file_path)
        return actual_checksum == expected_checksum
    
    def _verify_signature(self, file_path: Path, signature: str, public_key: str) -> bool:
        """Verify the signature of a downloaded file."""
        # Placeholder for signature verification logic
        # Requires a cryptographic library (e.g., cryptography)
        logger.warning("Signature verification is not implemented.")
        return True
    
    def _download_plugin(self, download_url: str, expected_checksum: Optional[str]) -> Optional[Path]:
        """Download a plugin package."""
        try:
            parsed_url = urlparse(download_url)
            filename = Path(parsed_url.path).name
            if not filename:
                filename = f"plugin_{uuid.uuid4()}.zip"
            
            cache_path = self.cache_dir / filename
            
            # Check cache first
            if cache_path.exists() and expected_checksum:
                if self._verify_checksum(cache_path, expected_checksum):
                    logger.info(f"Using cached plugin: {cache_path}")
                    return cache_path
                else:
                    logger.warning(f"Cached file checksum mismatch for {cache_path}. Re-downloading.")
                    cache_path.unlink()
            
            # Download the file
            logger.info(f"Downloading plugin from {download_url} to {cache_path}")
            response = requests.get(download_url, stream=True, timeout=60)
            response.raise_for_status()
            
            with open(cache_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Verify checksum after download
            if expected_checksum and not self._verify_checksum(cache_path, expected_checksum):
                logger.error(f"Checksum verification failed for downloaded file: {cache_path}")
                cache_path.unlink()
                return None
            
            return cache_path
        except Exception as e:
            logger.error(f"Failed to download plugin from {download_url}: {str(e)}")
            return None
    
    def _extract_plugin(self, package_path: Path, install_path: Path) -> bool:
        """Extract a plugin package to the installation directory."""
        try:
            # Ensure install path is clean
            if install_path.exists():
                shutil.rmtree(install_path)
            install_path.mkdir(parents=True)
            
            # Extract zip file
            with zipfile.ZipFile(package_path, "r") as zip_ref:
                zip_ref.extractall(install_path)
            
            logger.info(f"Extracted plugin to {install_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to extract plugin package {package_path}: {str(e)}")
            if install_path.exists():
                shutil.rmtree(install_path)
            return False
    
    def install_plugin(self, metadata: PluginMetadata) -> Optional[InstalledPlugin]:
        """Install a plugin from its metadata."""
        with self._lock:
            if not metadata.download_url:
                logger.error(f"Plugin {metadata.plugin_id} has no download URL.")
                return None
            
            # Download the plugin package
            package_path = self._download_plugin(metadata.download_url, metadata.checksum)
            if not package_path:
                return None
            
            # Verify signature if required
            if self.config.require_signatures:
                if not metadata.signature or not self.config.trusted_publishers:
                    logger.error(f"Signature required but not provided or no trusted publishers configured for {metadata.plugin_id}")
                    return None
                
                # Placeholder for getting publisher public key
                public_key = "" # Get public key based on author/publisher
                if not self._verify_signature(package_path, metadata.signature, public_key):
                    logger.error(f"Signature verification failed for {metadata.plugin_id}")
                    return None
            
            # Determine install path
            install_path = self.plugin_dir / metadata.plugin_id
            
            # Extract the plugin
            if not self._extract_plugin(package_path, install_path):
                return None
            
            # Verify manifest inside the package matches
            manifest_path = install_path / "plugin.json"
            if not manifest_path.exists():
                logger.error(f"Manifest file not found in package for {metadata.plugin_id}")
                shutil.rmtree(install_path)
                return None
            
            try:
                installed_metadata = PluginMetadata.from_manifest(manifest_path)
                if installed_metadata.plugin_id != metadata.plugin_id or installed_metadata.version != metadata.version:
                    logger.error(f"Manifest mismatch for {metadata.plugin_id}. Expected {metadata.version}, found {installed_metadata.version}")
                    shutil.rmtree(install_path)
                    return None
            except Exception as e:
                logger.error(f"Failed to read installed manifest for {metadata.plugin_id}: {str(e)}")
                shutil.rmtree(install_path)
                return None
            
            # Create installed plugin record
            installed_plugin = InstalledPlugin(
                metadata=installed_metadata,
                install_path=install_path,
                status=PluginStatus.INSTALLED,
                installed_at=datetime.now()
            )
            
            logger.info(f"Successfully installed plugin: {metadata.plugin_id} v{metadata.version}")
            return installed_plugin
    
    def uninstall_plugin(self, plugin_id: str) -> bool:
        """Uninstall a plugin."""
        with self._lock:
            install_path = self.plugin_dir / plugin_id
            if not install_path.exists():
                logger.warning(f"Plugin {plugin_id} not found for uninstallation.")
                return True # Already uninstalled
            
            try:
                shutil.rmtree(install_path)
                logger.info(f"Successfully uninstalled plugin: {plugin_id}")
                return True
            except Exception as e:
                logger.error(f"Failed to uninstall plugin {plugin_id}: {str(e)}")
                return False
    
    def update_plugin(self, plugin_id: str, update_metadata: PluginMetadata) -> Optional[InstalledPlugin]:
        """Update an existing plugin."""
        with self._lock:
            logger.info(f"Attempting to update plugin {plugin_id} to version {update_metadata.version}")
            
            # Uninstall the old version (or move it to a backup)
            # For simplicity, we just uninstall here
            if not self.uninstall_plugin(plugin_id):
                logger.error(f"Failed to remove old version of {plugin_id} during update.")
                return None
            
            # Install the new version
            installed_plugin = self.install_plugin(update_metadata)
            if installed_plugin:
                logger.info(f"Successfully updated plugin {plugin_id} to version {update_metadata.version}")
            else:
                logger.error(f"Failed to install new version of {plugin_id} during update.")
            
            return installed_plugin
    
    def cleanup_cache(self) -> None:
        """Clean up the plugin download cache."""
        with self._lock:
            total_size = 0
            files = []
            
            for item in self.cache_dir.iterdir():
                if item.is_file():
                    size = item.stat().st_size
                    total_size += size
                    files.append((item, item.stat().st_mtime))
            
            if total_size > self.config.max_cache_size:
                # Sort files by last modified time (oldest first)
                files.sort(key=lambda x: x[1])
                
                size_to_remove = total_size - self.config.max_cache_size
                removed_size = 0
                
                for file_path, _ in files:
                    if removed_size >= size_to_remove:
                        break
                    
                    try:
                        size = file_path.stat().st_size
                        file_path.unlink()
                        removed_size += size
                        logger.info(f"Removed cached file: {file_path}")
                    except Exception as e:
                        logger.error(f"Failed to remove cached file {file_path}: {str(e)}")
                
                logger.info(f"Cache cleanup complete. Removed {removed_size} bytes.")

class PluginManager:
    """Manages the lifecycle of installed plugins."""
    
    def __init__(self, config: PluginMarketplaceConfig):
        """Initialize the plugin manager."""
        self.config = config
        self.installed_plugins: Dict[str, InstalledPlugin] = {}
        self._lock = threading.RLock()
        self._load_installed_plugins()
    
    def _load_installed_plugins(self) -> None:
        """Load metadata of installed plugins from the plugin directory."""
        with self._lock:
            self.installed_plugins = {}
            plugin_dir = Path(self.config.plugin_directory)
            plugin_dir.mkdir(parents=True, exist_ok=True)
            
            for item in plugin_dir.iterdir():
                if item.is_dir():
                    plugin_id = item.name
                    manifest_path = item / "plugin.json"
                    state_path = item / "plugin_state.json"
                    
                    if manifest_path.exists():
                        try:
                            metadata = PluginMetadata.from_manifest(manifest_path)
                            
                            # Load state if exists
                            status = PluginStatus.INSTALLED
                            installed_at = datetime.fromtimestamp(item.stat().st_ctime)
                            last_enabled_at = None
                            last_disabled_at = None
                            error_message = None
                            
                            if state_path.exists():
                                with open(state_path, "r") as f:
                                    state_data = json.load(f)
                                status = PluginStatus(state_data.get("status", "installed"))
                                installed_at = datetime.fromisoformat(state_data.get("installed_at", installed_at.isoformat()))
                                last_enabled_at = datetime.fromisoformat(state_data["last_enabled_at"]) if state_data.get("last_enabled_at") else None
                                last_disabled_at = datetime.fromisoformat(state_data["last_disabled_at"]) if state_data.get("last_disabled_at") else None
                                error_message = state_data.get("error_message")
                            
                            installed_plugin = InstalledPlugin(
                                metadata=metadata,
                                install_path=item,
                                status=status,
                                installed_at=installed_at,
                                last_enabled_at=last_enabled_at,
                                last_disabled_at=last_disabled_at,
                                error_message=error_message
                            )
                            self.installed_plugins[plugin_id] = installed_plugin
                        except Exception as e:
                            logger.error(f"Failed to load installed plugin {plugin_id}: {str(e)}")
                    else:
                        logger.warning(f"Plugin directory {plugin_id} missing manifest file.")
    
    def _save_plugin_state(self, plugin: InstalledPlugin) -> None:
        """Save the state of a plugin."""
        state_path = plugin.install_path / "plugin_state.json"
        state_data = {
            "status": plugin.status.value,
            "installed_at": plugin.installed_at.isoformat(),
            "last_enabled_at": plugin.last_enabled_at.isoformat() if plugin.last_enabled_at else None,
            "last_disabled_at": plugin.last_disabled_at.isoformat() if plugin.last_disabled_at else None,
            "error_message": plugin.error_message
        }
        try:
            with open(state_path, "w") as f:
                json.dump(state_data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save state for plugin {plugin.metadata.plugin_id}: {str(e)}")
    
    def get_installed_plugins(self) -> List[InstalledPlugin]:
        """Get a list of all installed plugins."""
        with self._lock:
            return list(self.installed_plugins.values())
    
    def get_plugin(self, plugin_id: str) -> Optional[InstalledPlugin]:
        """Get an installed plugin by ID."""
        with self._lock:
            return self.installed_plugins.get(plugin_id)
    
    def add_installed_plugin(self, plugin: InstalledPlugin) -> None:
        """Add a newly installed plugin to the manager."""
        with self._lock:
            self.installed_plugins[plugin.metadata.plugin_id] = plugin
            self._save_plugin_state(plugin)
    
    def remove_installed_plugin(self, plugin_id: str) -> None:
        """Remove an uninstalled plugin from the manager."""
        with self._lock:
            if plugin_id in self.installed_plugins:
                del self.installed_plugins[plugin_id]
    
    def enable_plugin(self, plugin_id: str) -> bool:
        """Enable an installed plugin."""
        with self._lock:
            plugin = self.get_plugin(plugin_id)
            if not plugin:
                logger.error(f"Cannot enable plugin: {plugin_id} not found.")
                return False
            
            if plugin.status == PluginStatus.ENABLED:
                return True
            
            # Placeholder for loading and initializing the plugin
            try:
                # Load plugin code (e.g., import entry point)
                # Call initialization function if exists
                logger.info(f"Enabling plugin: {plugin_id}")
                
                plugin.status = PluginStatus.ENABLED
                plugin.last_enabled_at = datetime.now()
                plugin.error_message = None
                self._save_plugin_state(plugin)
                return True
            except Exception as e:
                logger.error(f"Failed to enable plugin {plugin_id}: {str(e)}")
                plugin.status = PluginStatus.ERROR
                plugin.error_message = str(e)
                self._save_plugin_state(plugin)
                return False
    
    def disable_plugin(self, plugin_id: str) -> bool:
        """Disable an enabled plugin."""
        with self._lock:
            plugin = self.get_plugin(plugin_id)
            if not plugin:
                logger.error(f"Cannot disable plugin: {plugin_id} not found.")
                return False
            
            if plugin.status == PluginStatus.DISABLED:
                return True
            
            # Placeholder for unloading the plugin
            try:
                # Call deinitialization function if exists
                # Unload plugin code
                logger.info(f"Disabling plugin: {plugin_id}")
                
                plugin.status = PluginStatus.DISABLED
                plugin.last_disabled_at = datetime.now()
                self._save_plugin_state(plugin)
                return True
            except Exception as e:
                logger.error(f"Failed to disable plugin {plugin_id}: {str(e)}")
                # Keep status as enabled or move to error?
                return False
    
    def get_enabled_plugins(self) -> List[InstalledPlugin]:
        """Get a list of all enabled plugins."""
        with self._lock:
            return [p for p in self.installed_plugins.values() if p.status == PluginStatus.ENABLED]

class PluginSecurityManager:
    """Handles plugin security aspects like permissions."""
    
    def __init__(self, config: PluginMarketplaceConfig):
        """Initialize the security manager."""
        self.config = config
        self.granted_permissions: Dict[str, Set[PluginPermission]] = {}
        self._lock = threading.RLock()
    
    def check_permission(self, plugin_id: str, permission: PluginPermission) -> bool:
        """Check if a plugin has been granted a specific permission."""
        with self._lock:
            # In a real implementation, this would check against user-granted permissions
            # For now, assume all declared permissions are granted
            plugin = PluginManager(self.config).get_plugin(plugin_id)
            if plugin:
                return permission in plugin.metadata.permissions
            return False
    
    def grant_permission(self, plugin_id: str, permission: PluginPermission) -> None:
        """Grant a permission to a plugin (requires user interaction)."""
        with self._lock:
            if plugin_id not in self.granted_permissions:
                self.granted_permissions[plugin_id] = set()
            self.granted_permissions[plugin_id].add(permission)
            logger.info(f"Permission {permission.value} granted to plugin {plugin_id}")
    
    def revoke_permission(self, plugin_id: str, permission: PluginPermission) -> None:
        """Revoke a permission from a plugin."""
        with self._lock:
            if plugin_id in self.granted_permissions:
                self.granted_permissions[plugin_id].discard(permission)
                logger.info(f"Permission {permission.value} revoked from plugin {plugin_id}")
    
    def get_granted_permissions(self, plugin_id: str) -> Set[PluginPermission]:
        """Get the set of permissions granted to a plugin."""
        with self._lock:
            return self.granted_permissions.get(plugin_id, set())
    
    def sandbox_plugin_execution(self, plugin_id: str, function: Callable, *args, **kwargs) -> Any:
        """Execute a plugin function within a security sandbox."""
        if not self.config.security_sandboxing:
            # Execute directly if sandboxing is disabled
            return function(*args, **kwargs)
        
        # Placeholder for sandboxing logic
        # This is complex and requires careful implementation, potentially using
        # separate processes, restricted environments, or techniques like seccomp.
        logger.warning(f"Sandboxing requested for {plugin_id}, but not fully implemented. Executing directly.")
        
        # Check required permissions before execution
        # Example: If function needs network access, check for NETWORK_ACCESS permission
        # required_permission = PluginPermission.NETWORK_ACCESS
        # if not self.check_permission(plugin_id, required_permission):
        #     raise PermissionError(f"Plugin {plugin_id} does not have permission {required_permission.value}")
        
        try:
            result = function(*args, **kwargs)
            return result
        except Exception as e:
            logger.error(f"Error during sandboxed execution of {plugin_id}: {str(e)}")
            raise

class PluginMarketplaceSystem:
    """Main plugin marketplace system class."""
    
    _instance = None
    
    @classmethod
    def get_instance(cls) -> "PluginMarketplaceSystem":
        """Get the singleton instance."""
        if cls._instance is None:
            cls._instance = PluginMarketplaceSystem()
        return cls._instance
    
    def __init__(self):
        """Initialize the plugin marketplace system."""
        self.config = PluginMarketplaceConfig()
        self.repository = None
        self.installer = None
        self.manager = None
        self.security_manager = None
        self._initialized = False
        self._lock = threading.RLock()
        self._update_thread = None
        self._running = False
    
    def initialize(self, config_path: Optional[str] = None) -> None:
        """Initialize the system with configuration."""
        with self._lock:
            if self._initialized:
                return
            
            if config_path and Path(config_path).exists():
                try:
                    with open(config_path, "r") as f:
                        config_data = json.load(f)
                    self.config = PluginMarketplaceConfig.from_dict(config_data)
                except Exception as e:
                    logger.error(f"Failed to load marketplace config from {config_path}: {str(e)}. Using defaults.")
                    self.config = PluginMarketplaceConfig()
            else:
                logger.warning("Marketplace config file not found. Using defaults.")
                self.config = PluginMarketplaceConfig()
            
            # Initialize components
            self.repository = PluginRepository(self.config)
            self.installer = PluginInstaller(self.config)
            self.manager = PluginManager(self.config)
            self.security_manager = PluginSecurityManager(self.config)
            
            # Start auto-update check thread if enabled
            if self.config.auto_update_check:
                self._running = True
                self._update_thread = threading.Thread(target=self._run_update_checks, daemon=True)
                self._update_thread.start()
            
            self._initialized = True
            logger.info("Plugin Marketplace system initialized")
    
    def shutdown(self) -> None:
        """Shutdown the system."""
        with self._lock:
            if not self._initialized:
                return
            
            self._running = False
            if self._update_thread:
                self._update_thread.join(timeout=5.0)
                self._update_thread = None
            
            self._initialized = False
            logger.info("Plugin Marketplace system shutdown")
    
    def ensure_initialized(self) -> None:
        """Ensure the system is initialized."""
        if not self._initialized:
            self.initialize()
    
    def _run_update_checks(self) -> None:
        """Periodically check for plugin updates."""
        while self._running:
            try:
                logger.info("Running periodic plugin update check...")
                self.check_for_updates()
            except Exception as e:
                logger.error(f"Error during periodic update check: {str(e)}")
            
            # Wait for the next interval
            interval = self.config.update_check_interval
            start_time = time.time()
            while self._running and time.time() - start_time < interval:
                time.sleep(1)
    
    def search_plugins(self, query: str, tags: Optional[List[str]] = None) -> List[PluginMetadata]:
        """Search for available plugins."""
        self.ensure_initialized()
        return self.repository.search_plugins(query, tags)
    
    def get_installed_plugins(self) -> List[InstalledPlugin]:
        """Get a list of installed plugins."""
        self.ensure_initialized()
        return self.manager.get_installed_plugins()
    
    def get_enabled_plugins(self) -> List[InstalledPlugin]:
        """Get a list of enabled plugins."""
        self.ensure_initialized()
        return self.manager.get_enabled_plugins()
    
    def install_plugin(self, plugin_id: str, version: Optional[str] = None) -> bool:
        """Install a plugin by ID and optional version."""
        self.ensure_initialized()
        
        # Check if already installed
        if self.manager.get_plugin(plugin_id):
            logger.warning(f"Plugin {plugin_id} is already installed.")
            return True
        
        # Get metadata from repository
        metadata = self.repository.get_plugin_metadata(plugin_id, version)
        if not metadata:
            logger.error(f"Plugin {plugin_id} (version: {version or 'latest'}) not found in repositories.")
            return False
        
        # Install dependencies first (recursive call)
        for dep in metadata.dependencies:
            if dep.required:
                installed_dep = self.manager.get_plugin(dep.plugin_id)
                if not installed_dep:
                    logger.info(f"Installing required dependency: {dep.plugin_id}")
                    if not self.install_plugin(dep.plugin_id, dep.min_version):
                        logger.error(f"Failed to install required dependency: {dep.plugin_id}")
                        return False
                # Add version check here if needed
        
        # Install the plugin
        installed_plugin = self.installer.install_plugin(metadata)
        if installed_plugin:
            self.manager.add_installed_plugin(installed_plugin)
            return True
        else:
            return False
    
    def uninstall_plugin(self, plugin_id: str) -> bool:
        """Uninstall a plugin."""
        self.ensure_initialized()
        
        # Disable first if enabled
        plugin = self.manager.get_plugin(plugin_id)
        if plugin and plugin.status == PluginStatus.ENABLED:
            self.disable_plugin(plugin_id)
        
        # Uninstall
        if self.installer.uninstall_plugin(plugin_id):
            self.manager.remove_installed_plugin(plugin_id)
            return True
        else:
            return False
    
    def update_plugin(self, plugin_id: str) -> bool:
        """Update a plugin to the latest available version."""
        self.ensure_initialized()
        
        installed_plugin = self.manager.get_plugin(plugin_id)
        if not installed_plugin:
            logger.error(f"Plugin {plugin_id} not installed, cannot update.")
            return False
        
        # Check for updates
        updates = self.repository.check_for_updates([installed_plugin])
        if plugin_id not in updates:
            logger.info(f"Plugin {plugin_id} is already up to date.")
            return True
        
        update_metadata = updates[plugin_id]
        
        # Perform update
        updated_plugin = self.installer.update_plugin(plugin_id, update_metadata)
        if updated_plugin:
            # Update the manager record
            self.manager.add_installed_plugin(updated_plugin)
            return True
        else:
            # Attempt to restore the old version? (Complex)
            logger.error(f"Update failed for {plugin_id}. State might be inconsistent.")
            # Reload installed plugins to reflect actual state
            self.manager._load_installed_plugins()
            return False
    
    def check_for_updates(self) -> Dict[str, PluginMetadata]:
        """Check for updates for all installed plugins."""
        self.ensure_initialized()
        
        installed = self.manager.get_installed_plugins()
        updates = self.repository.check_for_updates(installed)
        
        # Update status for plugins with available updates
        for plugin_id in updates:
            plugin = self.manager.get_plugin(plugin_id)
            if plugin and plugin.status != PluginStatus.UPDATE_AVAILABLE:
                plugin.status = PluginStatus.UPDATE_AVAILABLE
                self.manager._save_plugin_state(plugin)
        
        logger.info(f"Found updates for {len(updates)} plugins.")
        return updates
    
    def enable_plugin(self, plugin_id: str) -> bool:
        """Enable an installed plugin."""
        self.ensure_initialized()
        return self.manager.enable_plugin(plugin_id)
    
    def disable_plugin(self, plugin_id: str) -> bool:
        """Disable an enabled plugin."""
        self.ensure_initialized()
        return self.manager.disable_plugin(plugin_id)
    
    def check_permission(self, plugin_id: str, permission: PluginPermission) -> bool:
        """Check if a plugin has a specific permission."""
        self.ensure_initialized()
        return self.security_manager.check_permission(plugin_id, permission)
    
    def sandbox_plugin_execution(self, plugin_id: str, function: Callable, *args, **kwargs) -> Any:
        """Execute a plugin function within a security sandbox."""
        self.ensure_initialized()
        return self.security_manager.sandbox_plugin_execution(plugin_id, function, *args, **kwargs)

# Global instance for easy access
plugin_marketplace_system = PluginMarketplaceSystem.get_instance()

# --- Helper Functions --- #

def initialize_plugin_system(config_path: Optional[str] = None) -> None:
    """Initialize the plugin marketplace system."""
    plugin_marketplace_system.initialize(config_path)

def shutdown_plugin_system() -> None:
    """Shutdown the plugin marketplace system."""
    plugin_marketplace_system.shutdown()

# Example usage
if __name__ == "__main__":
    # Initialize
    # Create a dummy config for testing
    test_config = {
        "repository_urls": ["https://example.com/plugin_repo.json"], # Replace with a real URL if available
        "plugin_directory": "test_plugins",
        "cache_directory": "test_plugin_cache"
    }
    with open("test_marketplace_config.json", "w") as f:
        json.dump(test_config, f)
    
    initialize_plugin_system("test_marketplace_config.json")
    
    # Search for plugins
    search_results = plugin_marketplace_system.search_plugins("example")
    print(f"Search results for 'example': {len(search_results)}")
    for plugin in search_results:
        print(f"- {plugin.name} v{plugin.version} by {plugin.author}")
    
    # Install a plugin (replace with a valid plugin_id from your repo)
    # plugin_id_to_install = "com.example.sampleplugin"
    # print(f"\nInstalling plugin: {plugin_id_to_install}")
    # success = plugin_marketplace_system.install_plugin(plugin_id_to_install)
    # print(f"Installation successful: {success}")
    
    # List installed plugins
    installed = plugin_marketplace_system.get_installed_plugins()
    print(f"\nInstalled plugins: {len(installed)}")
    for plugin in installed:
        print(f"- {plugin.metadata.name} v{plugin.metadata.version} ({plugin.status.value})")
        # if success:
        #     plugin_marketplace_system.enable_plugin(plugin.metadata.plugin_id)
        #     print(f"  Enabled: {plugin_marketplace_system.get_plugin(plugin.metadata.plugin_id).status == PluginStatus.ENABLED}")
    
    # Check for updates
    # updates = plugin_marketplace_system.check_for_updates()
    # print(f"\nUpdates available: {len(updates)}")
    # for plugin_id, metadata in updates.items():
    #     print(f"- {metadata.name} v{metadata.version}")
    
    # Uninstall a plugin
    # if success:
    #     print(f"\nUninstalling plugin: {plugin_id_to_install}")
    #     uninstalled = plugin_marketplace_system.uninstall_plugin(plugin_id_to_install)
    #     print(f"Uninstallation successful: {uninstalled}")
    
    # Shutdown
    shutdown_plugin_system()
    
    # Clean up test directories
    # shutil.rmtree("test_plugins", ignore_errors=True)
    # shutil.rmtree("test_plugin_cache", ignore_errors=True)
    # os.remove("test_marketplace_config.json")
