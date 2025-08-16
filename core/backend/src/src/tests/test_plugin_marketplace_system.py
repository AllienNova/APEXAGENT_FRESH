#!/usr/bin/env python3
"""
Test suite for the Plugin Marketplace System.

This module provides comprehensive tests for the plugin marketplace system
components of the ApexAgent system.
"""

import os
import sys
import unittest
import tempfile
import json
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
import threading
import time
import datetime
import hashlib
import uuid

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import modules to test
from plugin_marketplace.plugin_marketplace_system import (
    PluginMarketplaceSystem, PluginMarketplaceConfig, Plugin, PluginVersion,
    PluginCategory, PluginRating, PluginReview, PluginInstallation,
    PluginRepository, PluginValidator, PluginSandbox, PluginAnalytics,
    PluginDependency, PluginPermission, PluginManifest, PluginStore
)

class TestPluginMarketplaceSystem(unittest.TestCase):
    """Test cases for the PluginMarketplaceSystem class."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = PluginMarketplaceConfig(
            enabled=True,
            data_directory=self.temp_dir,
            auto_update_enabled=True,
            sandbox_enabled=True,
            analytics_enabled=True,
            repository_url="https://plugins.example.com",
            api_key="test-api-key"
        )
        self.marketplace = PluginMarketplaceSystem.get_instance()
        self.marketplace.initialize(self.config)
    
    def tearDown(self):
        """Clean up test environment."""
        self.marketplace.shutdown()
    
    def test_singleton_pattern(self):
        """Test that the marketplace system follows the singleton pattern."""
        instance1 = PluginMarketplaceSystem.get_instance()
        instance2 = PluginMarketplaceSystem.get_instance()
        self.assertIs(instance1, instance2)
    
    def test_register_plugin(self):
        """Test registering a plugin."""
        # Create a plugin
        plugin = Plugin(
            plugin_id="test-plugin",
            name="Test Plugin",
            description="A test plugin",
            author="Test Author",
            version=PluginVersion(1, 0, 0),
            category=PluginCategory.PRODUCTIVITY
        )
        
        # Register the plugin
        self.marketplace.register_plugin(plugin)
        
        # Verify plugin was registered
        registered_plugin = self.marketplace.get_plugin("test-plugin")
        self.assertEqual(registered_plugin, plugin)
    
    def test_get_plugins_by_category(self):
        """Test getting plugins by category."""
        # Register plugins for different categories
        plugin1 = Plugin(
            plugin_id="productivity-plugin",
            name="Productivity Plugin",
            category=PluginCategory.PRODUCTIVITY
        )
        plugin2 = Plugin(
            plugin_id="analytics-plugin",
            name="Analytics Plugin",
            category=PluginCategory.ANALYTICS
        )
        plugin3 = Plugin(
            plugin_id="security-plugin",
            name="Security Plugin",
            category=PluginCategory.SECURITY
        )
        
        self.marketplace.register_plugin(plugin1)
        self.marketplace.register_plugin(plugin2)
        self.marketplace.register_plugin(plugin3)
        
        # Get productivity plugins
        productivity_plugins = self.marketplace.get_plugins_by_category(PluginCategory.PRODUCTIVITY)
        self.assertEqual(len(productivity_plugins), 1)
        self.assertIn(plugin1, productivity_plugins)
        
        # Get security plugins
        security_plugins = self.marketplace.get_plugins_by_category(PluginCategory.SECURITY)
        self.assertEqual(len(security_plugins), 1)
        self.assertIn(plugin3, security_plugins)
    
    def test_install_plugin(self):
        """Test installing a plugin."""
        # Create a plugin
        plugin = Plugin(
            plugin_id="test-plugin",
            name="Test Plugin",
            version=PluginVersion(1, 0, 0)
        )
        
        # Mock plugin validator
        with patch.object(self.marketplace, '_validate_plugin') as mock_validate:
            mock_validate.return_value = True
            
            # Mock plugin repository
            with patch.object(self.marketplace, '_download_plugin') as mock_download:
                mock_download.return_value = "/path/to/plugin.zip"
                
                # Mock plugin sandbox
                with patch.object(self.marketplace, '_extract_plugin') as mock_extract:
                    mock_extract.return_value = "/path/to/extracted"
                    
                    # Install plugin
                    installation = self.marketplace.install_plugin(plugin.plugin_id)
                    
                    # Verify installation
                    self.assertEqual(installation.plugin_id, plugin.plugin_id)
                    self.assertEqual(installation.status, "installed")
                    
                    # Verify methods were called
                    mock_validate.assert_called_once()
                    mock_download.assert_called_once()
                    mock_extract.assert_called_once()
    
    def test_uninstall_plugin(self):
        """Test uninstalling a plugin."""
        # Create a plugin installation
        installation = PluginInstallation(
            plugin_id="test-plugin",
            version=PluginVersion(1, 0, 0),
            install_path="/path/to/plugin",
            status="installed"
        )
        
        # Add installation to marketplace
        self.marketplace._installations["test-plugin"] = installation
        
        # Uninstall plugin
        with patch('os.path.exists') as mock_exists:
            mock_exists.return_value = True
            
            with patch('shutil.rmtree') as mock_rmtree:
                result = self.marketplace.uninstall_plugin("test-plugin")
                
                # Verify uninstallation
                self.assertTrue(result)
                self.assertNotIn("test-plugin", self.marketplace._installations)
                mock_rmtree.assert_called_once_with("/path/to/plugin")
    
    def test_update_plugin(self):
        """Test updating a plugin."""
        # Create a plugin installation
        installation = PluginInstallation(
            plugin_id="test-plugin",
            version=PluginVersion(1, 0, 0),
            install_path="/path/to/plugin",
            status="installed"
        )
        
        # Add installation to marketplace
        self.marketplace._installations["test-plugin"] = installation
        
        # Create updated plugin
        updated_plugin = Plugin(
            plugin_id="test-plugin",
            name="Test Plugin",
            version=PluginVersion(1, 1, 0)  # New version
        )
        
        # Mock plugin repository
        with patch.object(self.marketplace, '_get_latest_plugin_version') as mock_get_version:
            mock_get_version.return_value = updated_plugin
            
            # Mock plugin validator
            with patch.object(self.marketplace, '_validate_plugin') as mock_validate:
                mock_validate.return_value = True
                
                # Mock plugin repository
                with patch.object(self.marketplace, '_download_plugin') as mock_download:
                    mock_download.return_value = "/path/to/plugin_new.zip"
                    
                    # Mock plugin sandbox
                    with patch.object(self.marketplace, '_extract_plugin') as mock_extract:
                        mock_extract.return_value = "/path/to/extracted_new"
                        
                        # Update plugin
                        updated_installation = self.marketplace.update_plugin("test-plugin")
                        
                        # Verify update
                        self.assertEqual(updated_installation.plugin_id, "test-plugin")
                        self.assertEqual(updated_installation.version, PluginVersion(1, 1, 0))
                        self.assertEqual(updated_installation.status, "installed")
    
    def test_search_plugins(self):
        """Test searching for plugins."""
        # Register plugins
        plugin1 = Plugin(
            plugin_id="productivity-plugin",
            name="Productivity Plugin",
            description="Boost your productivity",
            category=PluginCategory.PRODUCTIVITY
        )
        plugin2 = Plugin(
            plugin_id="analytics-plugin",
            name="Analytics Plugin",
            description="Analyze your data",
            category=PluginCategory.ANALYTICS
        )
        plugin3 = Plugin(
            plugin_id="security-plugin",
            name="Security Plugin",
            description="Secure your system",
            category=PluginCategory.SECURITY
        )
        
        self.marketplace.register_plugin(plugin1)
        self.marketplace.register_plugin(plugin2)
        self.marketplace.register_plugin(plugin3)
        
        # Search by name
        results1 = self.marketplace.search_plugins("Productivity")
        self.assertEqual(len(results1), 1)
        self.assertIn(plugin1, results1)
        
        # Search by description
        results2 = self.marketplace.search_plugins("data")
        self.assertEqual(len(results2), 1)
        self.assertIn(plugin2, results2)
        
        # Search by category
        results3 = self.marketplace.search_plugins("security")
        self.assertEqual(len(results3), 1)
        self.assertIn(plugin3, results3)
    
    def test_get_plugin_ratings(self):
        """Test getting plugin ratings."""
        # Create plugin
        plugin_id = "test-plugin"
        
        # Create ratings
        rating1 = PluginRating(
            plugin_id=plugin_id,
            user_id="user1",
            rating=5,
            review=PluginReview(
                text="Great plugin!",
                timestamp=datetime.datetime(2023, 1, 1, 12, 0)
            )
        )
        
        rating2 = PluginRating(
            plugin_id=plugin_id,
            user_id="user2",
            rating=4,
            review=PluginReview(
                text="Good plugin",
                timestamp=datetime.datetime(2023, 1, 2, 12, 0)
            )
        )
        
        # Add ratings to marketplace
        self.marketplace._ratings.setdefault(plugin_id, []).append(rating1)
        self.marketplace._ratings.setdefault(plugin_id, []).append(rating2)
        
        # Get ratings
        ratings = self.marketplace.get_plugin_ratings(plugin_id)
        
        # Verify ratings
        self.assertEqual(len(ratings), 2)
        self.assertIn(rating1, ratings)
        self.assertIn(rating2, ratings)
    
    def test_get_plugin_average_rating(self):
        """Test getting plugin average rating."""
        # Create plugin
        plugin_id = "test-plugin"
        
        # Create ratings
        rating1 = PluginRating(
            plugin_id=plugin_id,
            user_id="user1",
            rating=5
        )
        
        rating2 = PluginRating(
            plugin_id=plugin_id,
            user_id="user2",
            rating=4
        )
        
        rating3 = PluginRating(
            plugin_id=plugin_id,
            user_id="user3",
            rating=3
        )
        
        # Add ratings to marketplace
        self.marketplace._ratings.setdefault(plugin_id, []).append(rating1)
        self.marketplace._ratings.setdefault(plugin_id, []).append(rating2)
        self.marketplace._ratings.setdefault(plugin_id, []).append(rating3)
        
        # Get average rating
        avg_rating = self.marketplace.get_plugin_average_rating(plugin_id)
        
        # Verify average rating
        self.assertEqual(avg_rating, 4.0)
    
    def test_add_plugin_rating(self):
        """Test adding a plugin rating."""
        # Create plugin
        plugin_id = "test-plugin"
        
        # Add rating
        rating = self.marketplace.add_plugin_rating(
            plugin_id=plugin_id,
            user_id="user1",
            rating=5,
            review_text="Great plugin!"
        )
        
        # Verify rating was added
        self.assertEqual(rating.plugin_id, plugin_id)
        self.assertEqual(rating.user_id, "user1")
        self.assertEqual(rating.rating, 5)
        self.assertEqual(rating.review.text, "Great plugin!")
        
        # Verify rating is in marketplace
        ratings = self.marketplace.get_plugin_ratings(plugin_id)
        self.assertEqual(len(ratings), 1)
        self.assertEqual(ratings[0], rating)
    
    @patch('plugin_marketplace.plugin_marketplace_system.os.path.exists')
    @patch('plugin_marketplace.plugin_marketplace_system.os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    def test_export_plugin_data(self, mock_file, mock_makedirs, mock_exists):
        """Test exporting plugin data."""
        # Mock path exists
        mock_exists.return_value = False
        
        # Create plugin
        plugin = Plugin(
            plugin_id="test-plugin",
            name="Test Plugin",
            description="A test plugin",
            author="Test Author",
            version=PluginVersion(1, 0, 0),
            category=PluginCategory.PRODUCTIVITY
        )
        
        # Register plugin
        self.marketplace.register_plugin(plugin)
        
        # Export plugin data
        export_path = self.marketplace.export_plugin_data(
            plugin_id="test-plugin",
            format="json",
            output_path=os.path.join(self.temp_dir, "plugin_data.json")
        )
        
        # Verify export
        mock_makedirs.assert_called_once()
        mock_file.assert_called_once()
        self.assertTrue(export_path.endswith("plugin_data.json"))
    
    @patch('plugin_marketplace.plugin_marketplace_system.os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    def test_import_plugin_data(self, mock_file, mock_exists):
        """Test importing plugin data."""
        # Mock path exists
        mock_exists.return_value = True
        
        # Mock file content
        plugin_data = {
            "plugin_id": "test-plugin",
            "name": "Test Plugin",
            "description": "A test plugin",
            "author": "Test Author",
            "version": "1.0.0",
            "category": "productivity"
        }
        mock_file.return_value.__enter__.return_value.read.return_value = json.dumps(plugin_data)
        
        # Import plugin data
        plugin = self.marketplace.import_plugin_data(
            format="json",
            input_path=os.path.join(self.temp_dir, "plugin_data.json")
        )
        
        # Verify import
        self.assertEqual(plugin.plugin_id, "test-plugin")
        self.assertEqual(plugin.name, "Test Plugin")
        self.assertEqual(plugin.description, "A test plugin")
        self.assertEqual(plugin.author, "Test Author")
        self.assertEqual(plugin.version, PluginVersion(1, 0, 0))
        self.assertEqual(plugin.category, PluginCategory.PRODUCTIVITY)

class TestPlugin(unittest.TestCase):
    """Test cases for the Plugin class."""
    
    def test_plugin_creation(self):
        """Test creating a plugin."""
        plugin = Plugin(
            plugin_id="test-plugin",
            name="Test Plugin",
            description="A test plugin",
            author="Test Author",
            version=PluginVersion(1, 0, 0),
            category=PluginCategory.PRODUCTIVITY,
            tags=["test", "example"],
            icon_url="https://example.com/icon.png",
            homepage_url="https://example.com/plugin",
            repository_url="https://github.com/example/plugin",
            license="MIT",
            dependencies=[
                PluginDependency(
                    plugin_id="dependency-plugin",
                    min_version=PluginVersion(1, 0, 0)
                )
            ],
            permissions=[
                PluginPermission.FILE_SYSTEM,
                PluginPermission.NETWORK
            ]
        )
        
        self.assertEqual(plugin.plugin_id, "test-plugin")
        self.assertEqual(plugin.name, "Test Plugin")
        self.assertEqual(plugin.description, "A test plugin")
        self.assertEqual(plugin.author, "Test Author")
        self.assertEqual(plugin.version, PluginVersion(1, 0, 0))
        self.assertEqual(plugin.category, PluginCategory.PRODUCTIVITY)
        self.assertEqual(plugin.tags, ["test", "example"])
        self.assertEqual(plugin.icon_url, "https://example.com/icon.png")
        self.assertEqual(plugin.homepage_url, "https://example.com/plugin")
        self.assertEqual(plugin.repository_url, "https://github.com/example/plugin")
        self.assertEqual(plugin.license, "MIT")
        self.assertEqual(len(plugin.dependencies), 1)
        self.assertEqual(plugin.dependencies[0].plugin_id, "dependency-plugin")
        self.assertEqual(len(plugin.permissions), 2)
        self.assertIn(PluginPermission.FILE_SYSTEM, plugin.permissions)
        self.assertIn(PluginPermission.NETWORK, plugin.permissions)
    
    def test_to_dict(self):
        """Test converting plugin to dictionary."""
        plugin = Plugin(
            plugin_id="test-plugin",
            name="Test Plugin",
            description="A test plugin",
            author="Test Author",
            version=PluginVersion(1, 0, 0),
            category=PluginCategory.PRODUCTIVITY,
            tags=["test", "example"],
            permissions=[PluginPermission.FILE_SYSTEM]
        )
        
        plugin_dict = plugin.to_dict()
        
        self.assertEqual(plugin_dict["plugin_id"], "test-plugin")
        self.assertEqual(plugin_dict["name"], "Test Plugin")
        self.assertEqual(plugin_dict["description"], "A test plugin")
        self.assertEqual(plugin_dict["author"], "Test Author")
        self.assertEqual(plugin_dict["version"], "1.0.0")
        self.assertEqual(plugin_dict["category"], "productivity")
        self.assertEqual(plugin_dict["tags"], ["test", "example"])
        self.assertEqual(plugin_dict["permissions"], ["file_system"])
    
    def test_from_dict(self):
        """Test creating plugin from dictionary."""
        plugin_dict = {
            "plugin_id": "test-plugin",
            "name": "Test Plugin",
            "description": "A test plugin",
            "author": "Test Author",
            "version": "1.0.0",
            "category": "productivity",
            "tags": ["test", "example"],
            "permissions": ["file_system"]
        }
        
        plugin = Plugin.from_dict(plugin_dict)
        
        self.assertEqual(plugin.plugin_id, "test-plugin")
        self.assertEqual(plugin.name, "Test Plugin")
        self.assertEqual(plugin.description, "A test plugin")
        self.assertEqual(plugin.author, "Test Author")
        self.assertEqual(plugin.version, PluginVersion(1, 0, 0))
        self.assertEqual(plugin.category, PluginCategory.PRODUCTIVITY)
        self.assertEqual(plugin.tags, ["test", "example"])
        self.assertEqual(len(plugin.permissions), 1)
        self.assertEqual(plugin.permissions[0], PluginPermission.FILE_SYSTEM)
    
    def test_is_compatible_with(self):
        """Test checking if plugin is compatible with system."""
        plugin = Plugin(
            plugin_id="test-plugin",
            name="Test Plugin",
            version=PluginVersion(1, 0, 0),
            min_system_version=PluginVersion(2, 0, 0),
            max_system_version=PluginVersion(3, 0, 0)
        )
        
        # System version too low
        self.assertFalse(plugin.is_compatible_with(PluginVersion(1, 5, 0)))
        
        # System version in range
        self.assertTrue(plugin.is_compatible_with(PluginVersion(2, 5, 0)))
        
        # System version too high
        self.assertFalse(plugin.is_compatible_with(PluginVersion(3, 5, 0)))

class TestPluginVersion(unittest.TestCase):
    """Test cases for the PluginVersion class."""
    
    def test_version_creation(self):
        """Test creating a plugin version."""
        version = PluginVersion(1, 2, 3, "beta")
        
        self.assertEqual(version.major, 1)
        self.assertEqual(version.minor, 2)
        self.assertEqual(version.patch, 3)
        self.assertEqual(version.label, "beta")
    
    def test_version_from_string(self):
        """Test creating version from string."""
        # Simple version
        version1 = PluginVersion.from_string("1.2.3")
        self.assertEqual(version1.major, 1)
        self.assertEqual(version1.minor, 2)
        self.assertEqual(version1.patch, 3)
        self.assertIsNone(version1.label)
        
        # Version with label
        version2 = PluginVersion.from_string("1.2.3-beta")
        self.assertEqual(version2.major, 1)
        self.assertEqual(version2.minor, 2)
        self.assertEqual(version2.patch, 3)
        self.assertEqual(version2.label, "beta")
        
        # Version with only major.minor
        version3 = PluginVersion.from_string("1.2")
        self.assertEqual(version3.major, 1)
        self.assertEqual(version3.minor, 2)
        self.assertEqual(version3.patch, 0)
        self.assertIsNone(version3.label)
    
    def test_version_to_string(self):
        """Test converting version to string."""
        # Simple version
        version1 = PluginVersion(1, 2, 3)
        self.assertEqual(str(version1), "1.2.3")
        
        # Version with label
        version2 = PluginVersion(1, 2, 3, "beta")
        self.assertEqual(str(version2), "1.2.3-beta")
    
    def test_version_comparison(self):
        """Test comparing versions."""
        # Equal versions
        v1 = PluginVersion(1, 2, 3)
        v2 = PluginVersion(1, 2, 3)
        self.assertEqual(v1, v2)
        
        # Different major
        v3 = PluginVersion(2, 2, 3)
        self.assertLess(v1, v3)
        self.assertGreater(v3, v1)
        
        # Different minor
        v4 = PluginVersion(1, 3, 3)
        self.assertLess(v1, v4)
        self.assertGreater(v4, v1)
        
        # Different patch
        v5 = PluginVersion(1, 2, 4)
        self.assertLess(v1, v5)
        self.assertGreater(v5, v1)
        
        # With label (labels are considered less than no label)
        v6 = PluginVersion(1, 2, 3, "beta")
        self.assertGreater(v1, v6)
        self.assertLess(v6, v1)
        
        # Different labels
        v7 = PluginVersion(1, 2, 3, "alpha")
        v8 = PluginVersion(1, 2, 3, "beta")
        self.assertLess(v7, v8)  # alpha < beta
        self.assertGreater(v8, v7)

class TestPluginDependency(unittest.TestCase):
    """Test cases for the PluginDependency class."""
    
    def test_dependency_creation(self):
        """Test creating a plugin dependency."""
        dependency = PluginDependency(
            plugin_id="dependency-plugin",
            min_version=PluginVersion(1, 0, 0),
            max_version=PluginVersion(2, 0, 0),
            optional=False
        )
        
        self.assertEqual(dependency.plugin_id, "dependency-plugin")
        self.assertEqual(dependency.min_version, PluginVersion(1, 0, 0))
        self.assertEqual(dependency.max_version, PluginVersion(2, 0, 0))
        self.assertFalse(dependency.optional)
    
    def test_is_satisfied_by(self):
        """Test checking if dependency is satisfied by a plugin."""
        dependency = PluginDependency(
            plugin_id="dependency-plugin",
            min_version=PluginVersion(1, 0, 0),
            max_version=PluginVersion(2, 0, 0)
        )
        
        # Create plugins with different versions
        plugin1 = Plugin(
            plugin_id="dependency-plugin",
            name="Dependency Plugin",
            version=PluginVersion(0, 9, 0)  # Too low
        )
        
        plugin2 = Plugin(
            plugin_id="dependency-plugin",
            name="Dependency Plugin",
            version=PluginVersion(1, 5, 0)  # In range
        )
        
        plugin3 = Plugin(
            plugin_id="dependency-plugin",
            name="Dependency Plugin",
            version=PluginVersion(2, 1, 0)  # Too high
        )
        
        plugin4 = Plugin(
            plugin_id="other-plugin",
            name="Other Plugin",
            version=PluginVersion(1, 5, 0)  # Wrong ID
        )
        
        # Check satisfaction
        self.assertFalse(dependency.is_satisfied_by(plugin1))
        self.assertTrue(dependency.is_satisfied_by(plugin2))
        self.assertFalse(dependency.is_satisfied_by(plugin3))
        self.assertFalse(dependency.is_satisfied_by(plugin4))
    
    def test_to_dict(self):
        """Test converting dependency to dictionary."""
        dependency = PluginDependency(
            plugin_id="dependency-plugin",
            min_version=PluginVersion(1, 0, 0),
            max_version=PluginVersion(2, 0, 0),
            optional=True
        )
        
        dependency_dict = dependency.to_dict()
        
        self.assertEqual(dependency_dict["plugin_id"], "dependency-plugin")
        self.assertEqual(dependency_dict["min_version"], "1.0.0")
        self.assertEqual(dependency_dict["max_version"], "2.0.0")
        self.assertTrue(dependency_dict["optional"])
    
    def test_from_dict(self):
        """Test creating dependency from dictionary."""
        dependency_dict = {
            "plugin_id": "dependency-plugin",
            "min_version": "1.0.0",
            "max_version": "2.0.0",
            "optional": True
        }
        
        dependency = PluginDependency.from_dict(dependency_dict)
        
        self.assertEqual(dependency.plugin_id, "dependency-plugin")
        self.assertEqual(dependency.min_version, PluginVersion(1, 0, 0))
        self.assertEqual(dependency.max_version, PluginVersion(2, 0, 0))
        self.assertTrue(dependency.optional)

class TestPluginInstallation(unittest.TestCase):
    """Test cases for the PluginInstallation class."""
    
    def test_installation_creation(self):
        """Test creating a plugin installation."""
        installation = PluginInstallation(
            plugin_id="test-plugin",
            version=PluginVersion(1, 0, 0),
            install_path="/path/to/plugin",
            install_date=datetime.datetime(2023, 1, 1, 12, 0),
            status="installed",
            enabled=True
        )
        
        self.assertEqual(installation.plugin_id, "test-plugin")
        self.assertEqual(installation.version, PluginVersion(1, 0, 0))
        self.assertEqual(installation.install_path, "/path/to/plugin")
        self.assertEqual(installation.install_date, datetime.datetime(2023, 1, 1, 12, 0))
        self.assertEqual(installation.status, "installed")
        self.assertTrue(installation.enabled)
    
    def test_to_dict(self):
        """Test converting installation to dictionary."""
        installation = PluginInstallation(
            plugin_id="test-plugin",
            version=PluginVersion(1, 0, 0),
            install_path="/path/to/plugin",
            install_date=datetime.datetime(2023, 1, 1, 12, 0),
            status="installed",
            enabled=True
        )
        
        installation_dict = installation.to_dict()
        
        self.assertEqual(installation_dict["plugin_id"], "test-plugin")
        self.assertEqual(installation_dict["version"], "1.0.0")
        self.assertEqual(installation_dict["install_path"], "/path/to/plugin")
        self.assertEqual(installation_dict["install_date"], "2023-01-01T12:00:00")
        self.assertEqual(installation_dict["status"], "installed")
        self.assertTrue(installation_dict["enabled"])
    
    def test_from_dict(self):
        """Test creating installation from dictionary."""
        installation_dict = {
            "plugin_id": "test-plugin",
            "version": "1.0.0",
            "install_path": "/path/to/plugin",
            "install_date": "2023-01-01T12:00:00",
            "status": "installed",
            "enabled": True
        }
        
        installation = PluginInstallation.from_dict(installation_dict)
        
        self.assertEqual(installation.plugin_id, "test-plugin")
        self.assertEqual(installation.version, PluginVersion(1, 0, 0))
        self.assertEqual(installation.install_path, "/path/to/plugin")
        self.assertEqual(installation.install_date.year, 2023)
        self.assertEqual(installation.install_date.month, 1)
        self.assertEqual(installation.install_date.day, 1)
        self.assertEqual(installation.status, "installed")
        self.assertTrue(installation.enabled)

class TestPluginRating(unittest.TestCase):
    """Test cases for the PluginRating class."""
    
    def test_rating_creation(self):
        """Test creating a plugin rating."""
        rating = PluginRating(
            plugin_id="test-plugin",
            user_id="user123",
            rating=5,
            review=PluginReview(
                text="Great plugin!",
                timestamp=datetime.datetime(2023, 1, 1, 12, 0)
            )
        )
        
        self.assertEqual(rating.plugin_id, "test-plugin")
        self.assertEqual(rating.user_id, "user123")
        self.assertEqual(rating.rating, 5)
        self.assertEqual(rating.review.text, "Great plugin!")
        self.assertEqual(rating.review.timestamp, datetime.datetime(2023, 1, 1, 12, 0))
    
    def test_to_dict(self):
        """Test converting rating to dictionary."""
        rating = PluginRating(
            plugin_id="test-plugin",
            user_id="user123",
            rating=5,
            review=PluginReview(
                text="Great plugin!",
                timestamp=datetime.datetime(2023, 1, 1, 12, 0)
            )
        )
        
        rating_dict = rating.to_dict()
        
        self.assertEqual(rating_dict["plugin_id"], "test-plugin")
        self.assertEqual(rating_dict["user_id"], "user123")
        self.assertEqual(rating_dict["rating"], 5)
        self.assertEqual(rating_dict["review"]["text"], "Great plugin!")
        self.assertEqual(rating_dict["review"]["timestamp"], "2023-01-01T12:00:00")
    
    def test_from_dict(self):
        """Test creating rating from dictionary."""
        rating_dict = {
            "plugin_id": "test-plugin",
            "user_id": "user123",
            "rating": 5,
            "review": {
                "text": "Great plugin!",
                "timestamp": "2023-01-01T12:00:00"
            }
        }
        
        rating = PluginRating.from_dict(rating_dict)
        
        self.assertEqual(rating.plugin_id, "test-plugin")
        self.assertEqual(rating.user_id, "user123")
        self.assertEqual(rating.rating, 5)
        self.assertEqual(rating.review.text, "Great plugin!")
        self.assertEqual(rating.review.timestamp.year, 2023)
        self.assertEqual(rating.review.timestamp.month, 1)
        self.assertEqual(rating.review.timestamp.day, 1)

class TestPluginRepository(unittest.TestCase):
    """Test cases for the PluginRepository class."""
    
    def setUp(self):
        """Set up test environment."""
        self.config = PluginMarketplaceConfig(
            repository_url="https://plugins.example.com",
            api_key="test-api-key"
        )
        self.repository = PluginRepository(self.config)
    
    @patch('plugin_marketplace.plugin_marketplace_system.requests.get')
    def test_get_plugin_metadata(self, mock_get):
        """Test getting plugin metadata from repository."""
        # Mock API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "plugin_id": "test-plugin",
            "name": "Test Plugin",
            "version": "1.0.0",
            "category": "productivity"
        }
        mock_get.return_value = mock_response
        
        # Get plugin metadata
        plugin = self.repository.get_plugin_metadata("test-plugin")
        
        # Verify plugin
        self.assertEqual(plugin.plugin_id, "test-plugin")
        self.assertEqual(plugin.name, "Test Plugin")
        self.assertEqual(plugin.version, PluginVersion(1, 0, 0))
        self.assertEqual(plugin.category, PluginCategory.PRODUCTIVITY)
        mock_get.assert_called_once()
    
    @patch('plugin_marketplace.plugin_marketplace_system.requests.get')
    def test_get_plugin_metadata_error(self, mock_get):
        """Test handling error when getting plugin metadata."""
        # Mock API error
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        # Get plugin metadata
        plugin = self.repository.get_plugin_metadata("nonexistent-plugin")
        
        # Verify no plugin returned
        self.assertIsNone(plugin)
        mock_get.assert_called_once()
    
    @patch('plugin_marketplace.plugin_marketplace_system.requests.get')
    def test_get_latest_plugin_version(self, mock_get):
        """Test getting latest plugin version from repository."""
        # Mock API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "plugin_id": "test-plugin",
            "name": "Test Plugin",
            "version": "1.1.0",  # Latest version
            "category": "productivity"
        }
        mock_get.return_value = mock_response
        
        # Get latest version
        plugin = self.repository.get_latest_plugin_version("test-plugin")
        
        # Verify plugin
        self.assertEqual(plugin.plugin_id, "test-plugin")
        self.assertEqual(plugin.version, PluginVersion(1, 1, 0))
        mock_get.assert_called_once()
    
    @patch('plugin_marketplace.plugin_marketplace_system.requests.get')
    @patch('plugin_marketplace.plugin_marketplace_system.os.path.exists')
    @patch('plugin_marketplace.plugin_marketplace_system.os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    def test_download_plugin(self, mock_file, mock_makedirs, mock_exists, mock_get):
        """Test downloading a plugin from repository."""
        # Mock path exists
        mock_exists.return_value = False
        
        # Mock API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"plugin data"
        mock_get.return_value = mock_response
        
        # Download plugin
        download_path = self.repository.download_plugin(
            plugin_id="test-plugin",
            version=PluginVersion(1, 0, 0),
            destination_dir="/tmp"
        )
        
        # Verify download
        mock_makedirs.assert_called_once()
        mock_file.assert_called_once()
        mock_file().write.assert_called_once_with(b"plugin data")
        self.assertTrue(download_path.endswith("test-plugin-1.0.0.zip"))
    
    @patch('plugin_marketplace.plugin_marketplace_system.requests.get')
    def test_search_plugins(self, mock_get):
        """Test searching for plugins in repository."""
        # Mock API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [
                {
                    "plugin_id": "productivity-plugin",
                    "name": "Productivity Plugin",
                    "version": "1.0.0",
                    "category": "productivity"
                },
                {
                    "plugin_id": "productivity-tools",
                    "name": "Productivity Tools",
                    "version": "1.0.0",
                    "category": "productivity"
                }
            ]
        }
        mock_get.return_value = mock_response
        
        # Search plugins
        results = self.repository.search_plugins("productivity")
        
        # Verify results
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].plugin_id, "productivity-plugin")
        self.assertEqual(results[1].plugin_id, "productivity-tools")
        mock_get.assert_called_once()
    
    @patch('plugin_marketplace.plugin_marketplace_system.requests.get')
    def test_get_featured_plugins(self, mock_get):
        """Test getting featured plugins from repository."""
        # Mock API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "featured": [
                {
                    "plugin_id": "featured-plugin-1",
                    "name": "Featured Plugin 1",
                    "version": "1.0.0",
                    "category": "productivity"
                },
                {
                    "plugin_id": "featured-plugin-2",
                    "name": "Featured Plugin 2",
                    "version": "1.0.0",
                    "category": "analytics"
                }
            ]
        }
        mock_get.return_value = mock_response
        
        # Get featured plugins
        featured = self.repository.get_featured_plugins()
        
        # Verify featured plugins
        self.assertEqual(len(featured), 2)
        self.assertEqual(featured[0].plugin_id, "featured-plugin-1")
        self.assertEqual(featured[1].plugin_id, "featured-plugin-2")
        mock_get.assert_called_once()

class TestPluginValidator(unittest.TestCase):
    """Test cases for the PluginValidator class."""
    
    def setUp(self):
        """Set up test environment."""
        self.config = PluginMarketplaceConfig()
        self.validator = PluginValidator(self.config)
    
    @patch('plugin_marketplace.plugin_marketplace_system.zipfile.ZipFile')
    def test_validate_plugin_package(self, mock_zipfile):
        """Test validating a plugin package."""
        # Mock manifest file in zip
        manifest_content = json.dumps({
            "plugin_id": "test-plugin",
            "name": "Test Plugin",
            "version": "1.0.0",
            "entry_point": "main.py"
        })
        
        mock_zip = MagicMock()
        mock_zip.namelist.return_value = ["manifest.json", "main.py"]
        mock_zip.read.return_value = manifest_content.encode()
        mock_zipfile.return_value.__enter__.return_value = mock_zip
        
        # Validate package
        result, manifest = self.validator.validate_plugin_package("/path/to/plugin.zip")
        
        # Verify validation
        self.assertTrue(result)
        self.assertEqual(manifest.plugin_id, "test-plugin")
        self.assertEqual(manifest.name, "Test Plugin")
        self.assertEqual(manifest.version, PluginVersion(1, 0, 0))
        self.assertEqual(manifest.entry_point, "main.py")
    
    @patch('plugin_marketplace.plugin_marketplace_system.zipfile.ZipFile')
    def test_validate_plugin_package_missing_manifest(self, mock_zipfile):
        """Test validating a plugin package with missing manifest."""
        # Mock zip without manifest
        mock_zip = MagicMock()
        mock_zip.namelist.return_value = ["main.py"]
        mock_zipfile.return_value.__enter__.return_value = mock_zip
        
        # Validate package
        result, manifest = self.validator.validate_plugin_package("/path/to/plugin.zip")
        
        # Verify validation
        self.assertFalse(result)
        self.assertIsNone(manifest)
    
    @patch('plugin_marketplace.plugin_marketplace_system.zipfile.ZipFile')
    def test_validate_plugin_package_missing_entry_point(self, mock_zipfile):
        """Test validating a plugin package with missing entry point."""
        # Mock manifest file in zip
        manifest_content = json.dumps({
            "plugin_id": "test-plugin",
            "name": "Test Plugin",
            "version": "1.0.0",
            "entry_point": "main.py"
        })
        
        mock_zip = MagicMock()
        mock_zip.namelist.return_value = ["manifest.json"]  # No main.py
        mock_zip.read.return_value = manifest_content.encode()
        mock_zipfile.return_value.__enter__.return_value = mock_zip
        
        # Validate package
        result, manifest = self.validator.validate_plugin_package("/path/to/plugin.zip")
        
        # Verify validation
        self.assertFalse(result)
        self.assertIsNotNone(manifest)
    
    def test_validate_plugin_permissions(self):
        """Test validating plugin permissions."""
        # Create plugin with permissions
        plugin = Plugin(
            plugin_id="test-plugin",
            name="Test Plugin",
            permissions=[
                PluginPermission.FILE_SYSTEM,
                PluginPermission.NETWORK
            ]
        )
        
        # Validate with all permissions allowed
        allowed_permissions = [
            PluginPermission.FILE_SYSTEM,
            PluginPermission.NETWORK,
            PluginPermission.USER_DATA
        ]
        
        result1 = self.validator.validate_plugin_permissions(plugin, allowed_permissions)
        self.assertTrue(result1)
        
        # Validate with some permissions not allowed
        allowed_permissions = [
            PluginPermission.NETWORK
        ]
        
        result2 = self.validator.validate_plugin_permissions(plugin, allowed_permissions)
        self.assertFalse(result2)
    
    def test_validate_plugin_dependencies(self):
        """Test validating plugin dependencies."""
        # Create plugin with dependencies
        plugin = Plugin(
            plugin_id="test-plugin",
            name="Test Plugin",
            dependencies=[
                PluginDependency(
                    plugin_id="required-plugin",
                    min_version=PluginVersion(1, 0, 0)
                ),
                PluginDependency(
                    plugin_id="optional-plugin",
                    min_version=PluginVersion(1, 0, 0),
                    optional=True
                )
            ]
        )
        
        # Create installed plugins
        installed_plugins = {
            "required-plugin": Plugin(
                plugin_id="required-plugin",
                name="Required Plugin",
                version=PluginVersion(1, 5, 0)  # Satisfies dependency
            )
        }
        
        # Validate dependencies
        result, missing = self.validator.validate_plugin_dependencies(plugin, installed_plugins)
        
        # Verify validation
        self.assertTrue(result)  # Optional dependency can be missing
        self.assertEqual(len(missing), 1)
        self.assertEqual(missing[0].plugin_id, "optional-plugin")
        
        # Test with missing required dependency
        installed_plugins = {}
        
        result, missing = self.validator.validate_plugin_dependencies(plugin, installed_plugins)
        
        # Verify validation
        self.assertFalse(result)
        self.assertEqual(len(missing), 2)

class TestPluginSandbox(unittest.TestCase):
    """Test cases for the PluginSandbox class."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = PluginMarketplaceConfig(
            sandbox_enabled=True,
            data_directory=self.temp_dir
        )
        self.sandbox = PluginSandbox(self.config)
    
    @patch('plugin_marketplace.plugin_marketplace_system.zipfile.ZipFile')
    @patch('plugin_marketplace.plugin_marketplace_system.os.path.exists')
    @patch('plugin_marketplace.plugin_marketplace_system.os.makedirs')
    def test_extract_plugin(self, mock_makedirs, mock_exists, mock_zipfile):
        """Test extracting a plugin package."""
        # Mock path exists
        mock_exists.return_value = False
        
        # Mock zip extraction
        mock_zip = MagicMock()
        mock_zipfile.return_value.__enter__.return_value = mock_zip
        
        # Extract plugin
        extract_path = self.sandbox.extract_plugin(
            plugin_id="test-plugin",
            version=PluginVersion(1, 0, 0),
            package_path="/path/to/plugin.zip"
        )
        
        # Verify extraction
        mock_makedirs.assert_called_once()
        mock_zip.extractall.assert_called_once()
        self.assertTrue(extract_path.endswith("test-plugin-1.0.0"))
    
    @patch('plugin_marketplace.plugin_marketplace_system.importlib.util.spec_from_file_location')
    @patch('plugin_marketplace.plugin_marketplace_system.importlib.util.module_from_spec')
    def test_load_plugin_module(self, mock_module_from_spec, mock_spec_from_file):
        """Test loading a plugin module."""
        # Mock module loading
        mock_spec = MagicMock()
        mock_module = MagicMock()
        
        mock_spec_from_file.return_value = mock_spec
        mock_module_from_spec.return_value = mock_module
        
        # Create manifest
        manifest = PluginManifest(
            plugin_id="test-plugin",
            name="Test Plugin",
            version=PluginVersion(1, 0, 0),
            entry_point="main.py"
        )
        
        # Load module
        module = self.sandbox.load_plugin_module(
            manifest=manifest,
            plugin_path="/path/to/plugin"
        )
        
        # Verify module loading
        self.assertEqual(module, mock_module)
        mock_spec.loader.exec_module.assert_called_once_with(mock_module)
    
    def test_create_sandbox_environment(self):
        """Test creating a sandbox environment for a plugin."""
        # Create sandbox environment
        env = self.sandbox.create_sandbox_environment(
            plugin_id="test-plugin",
            permissions=[PluginPermission.FILE_SYSTEM]
        )
        
        # Verify environment
        self.assertIsInstance(env, dict)
        self.assertIn("plugin_id", env)
        self.assertEqual(env["plugin_id"], "test-plugin")
        self.assertIn("permissions", env)
        self.assertIn(PluginPermission.FILE_SYSTEM, env["permissions"])
    
    def test_run_plugin_in_sandbox(self):
        """Test running a plugin in sandbox."""
        # Create mock module with initialize function
        mock_module = MagicMock()
        mock_module.initialize = MagicMock(return_value=True)
        
        # Create manifest
        manifest = PluginManifest(
            plugin_id="test-plugin",
            name="Test Plugin",
            version=PluginVersion(1, 0, 0),
            entry_point="main.py"
        )
        
        # Run plugin
        with patch.object(self.sandbox, 'load_plugin_module') as mock_load:
            mock_load.return_value = mock_module
            
            result = self.sandbox.run_plugin_in_sandbox(
                manifest=manifest,
                plugin_path="/path/to/plugin"
            )
            
            # Verify plugin execution
            self.assertTrue(result)
            mock_module.initialize.assert_called_once()

class TestPluginAnalytics(unittest.TestCase):
    """Test cases for the PluginAnalytics class."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = PluginMarketplaceConfig(
            analytics_enabled=True,
            data_directory=self.temp_dir
        )
        self.analytics = PluginAnalytics(self.config)
    
    def test_track_plugin_installation(self):
        """Test tracking plugin installation."""
        # Track installation
        self.analytics.track_plugin_installation(
            plugin_id="test-plugin",
            version=PluginVersion(1, 0, 0),
            user_id="user123"
        )
        
        # Verify tracking
        installations = self.analytics.get_plugin_installations("test-plugin")
        self.assertEqual(len(installations), 1)
        self.assertEqual(installations[0]["plugin_id"], "test-plugin")
        self.assertEqual(installations[0]["version"], "1.0.0")
        self.assertEqual(installations[0]["user_id"], "user123")
    
    def test_track_plugin_usage(self):
        """Test tracking plugin usage."""
        # Track usage
        self.analytics.track_plugin_usage(
            plugin_id="test-plugin",
            version=PluginVersion(1, 0, 0),
            user_id="user123",
            feature="test-feature",
            duration=60
        )
        
        # Verify tracking
        usage = self.analytics.get_plugin_usage("test-plugin")
        self.assertEqual(len(usage), 1)
        self.assertEqual(usage[0]["plugin_id"], "test-plugin")
        self.assertEqual(usage[0]["version"], "1.0.0")
        self.assertEqual(usage[0]["user_id"], "user123")
        self.assertEqual(usage[0]["feature"], "test-feature")
        self.assertEqual(usage[0]["duration"], 60)
    
    def test_track_plugin_error(self):
        """Test tracking plugin error."""
        # Track error
        self.analytics.track_plugin_error(
            plugin_id="test-plugin",
            version=PluginVersion(1, 0, 0),
            user_id="user123",
            error_type="RuntimeError",
            error_message="Test error message",
            stack_trace="Test stack trace"
        )
        
        # Verify tracking
        errors = self.analytics.get_plugin_errors("test-plugin")
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]["plugin_id"], "test-plugin")
        self.assertEqual(errors[0]["version"], "1.0.0")
        self.assertEqual(errors[0]["user_id"], "user123")
        self.assertEqual(errors[0]["error_type"], "RuntimeError")
        self.assertEqual(errors[0]["error_message"], "Test error message")
    
    def test_get_plugin_usage_stats(self):
        """Test getting plugin usage statistics."""
        # Track multiple usage events
        self.analytics.track_plugin_usage(
            plugin_id="test-plugin",
            version=PluginVersion(1, 0, 0),
            user_id="user1",
            feature="feature1",
            duration=60
        )
        
        self.analytics.track_plugin_usage(
            plugin_id="test-plugin",
            version=PluginVersion(1, 0, 0),
            user_id="user2",
            feature="feature1",
            duration=30
        )
        
        self.analytics.track_plugin_usage(
            plugin_id="test-plugin",
            version=PluginVersion(1, 0, 0),
            user_id="user1",
            feature="feature2",
            duration=45
        )
        
        # Get usage stats
        stats = self.analytics.get_plugin_usage_stats("test-plugin")
        
        # Verify stats
        self.assertEqual(stats["total_users"], 2)
        self.assertEqual(stats["total_usage_count"], 3)
        self.assertEqual(stats["total_usage_duration"], 135)
        self.assertEqual(stats["avg_usage_duration"], 45)
        self.assertEqual(len(stats["feature_usage"]), 2)
        self.assertEqual(stats["feature_usage"]["feature1"], 2)
        self.assertEqual(stats["feature_usage"]["feature2"], 1)
    
    @patch('plugin_marketplace.plugin_marketplace_system.os.path.exists')
    @patch('plugin_marketplace.plugin_marketplace_system.os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    def test_export_analytics_data(self, mock_file, mock_makedirs, mock_exists):
        """Test exporting analytics data."""
        # Mock path exists
        mock_exists.return_value = False
        
        # Track some data
        self.analytics.track_plugin_installation(
            plugin_id="test-plugin",
            version=PluginVersion(1, 0, 0),
            user_id="user123"
        )
        
        # Export data
        export_path = self.analytics.export_analytics_data(
            plugin_id="test-plugin",
            format="json",
            output_path=os.path.join(self.temp_dir, "analytics.json")
        )
        
        # Verify export
        mock_makedirs.assert_called_once()
        mock_file.assert_called_once()
        self.assertTrue(export_path.endswith("analytics.json"))

class TestPluginManifest(unittest.TestCase):
    """Test cases for the PluginManifest class."""
    
    def test_manifest_creation(self):
        """Test creating a plugin manifest."""
        manifest = PluginManifest(
            plugin_id="test-plugin",
            name="Test Plugin",
            description="A test plugin",
            author="Test Author",
            version=PluginVersion(1, 0, 0),
            entry_point="main.py",
            min_system_version=PluginVersion(1, 0, 0),
            permissions=[PluginPermission.FILE_SYSTEM],
            dependencies=[
                PluginDependency(
                    plugin_id="dependency-plugin",
                    min_version=PluginVersion(1, 0, 0)
                )
            ]
        )
        
        self.assertEqual(manifest.plugin_id, "test-plugin")
        self.assertEqual(manifest.name, "Test Plugin")
        self.assertEqual(manifest.description, "A test plugin")
        self.assertEqual(manifest.author, "Test Author")
        self.assertEqual(manifest.version, PluginVersion(1, 0, 0))
        self.assertEqual(manifest.entry_point, "main.py")
        self.assertEqual(manifest.min_system_version, PluginVersion(1, 0, 0))
        self.assertEqual(len(manifest.permissions), 1)
        self.assertEqual(manifest.permissions[0], PluginPermission.FILE_SYSTEM)
        self.assertEqual(len(manifest.dependencies), 1)
        self.assertEqual(manifest.dependencies[0].plugin_id, "dependency-plugin")
    
    def test_to_dict(self):
        """Test converting manifest to dictionary."""
        manifest = PluginManifest(
            plugin_id="test-plugin",
            name="Test Plugin",
            version=PluginVersion(1, 0, 0),
            entry_point="main.py"
        )
        
        manifest_dict = manifest.to_dict()
        
        self.assertEqual(manifest_dict["plugin_id"], "test-plugin")
        self.assertEqual(manifest_dict["name"], "Test Plugin")
        self.assertEqual(manifest_dict["version"], "1.0.0")
        self.assertEqual(manifest_dict["entry_point"], "main.py")
    
    def test_from_dict(self):
        """Test creating manifest from dictionary."""
        manifest_dict = {
            "plugin_id": "test-plugin",
            "name": "Test Plugin",
            "version": "1.0.0",
            "entry_point": "main.py",
            "permissions": ["file_system"]
        }
        
        manifest = PluginManifest.from_dict(manifest_dict)
        
        self.assertEqual(manifest.plugin_id, "test-plugin")
        self.assertEqual(manifest.name, "Test Plugin")
        self.assertEqual(manifest.version, PluginVersion(1, 0, 0))
        self.assertEqual(manifest.entry_point, "main.py")
        self.assertEqual(len(manifest.permissions), 1)
        self.assertEqual(manifest.permissions[0], PluginPermission.FILE_SYSTEM)
    
    @patch('builtins.open', new_callable=mock_open)
    def test_save_to_file(self, mock_file):
        """Test saving manifest to file."""
        manifest = PluginManifest(
            plugin_id="test-plugin",
            name="Test Plugin",
            version=PluginVersion(1, 0, 0),
            entry_point="main.py"
        )
        
        # Save manifest
        manifest.save_to_file("/path/to/manifest.json")
        
        # Verify save
        mock_file.assert_called_once_with("/path/to/manifest.json", "w")
        mock_file().write.assert_called_once()
    
    @patch('builtins.open', new_callable=mock_open)
    def test_load_from_file(self, mock_file):
        """Test loading manifest from file."""
        # Mock file content
        manifest_content = json.dumps({
            "plugin_id": "test-plugin",
            "name": "Test Plugin",
            "version": "1.0.0",
            "entry_point": "main.py"
        })
        mock_file.return_value.__enter__.return_value.read.return_value = manifest_content
        
        # Load manifest
        manifest = PluginManifest.load_from_file("/path/to/manifest.json")
        
        # Verify load
        self.assertEqual(manifest.plugin_id, "test-plugin")
        self.assertEqual(manifest.name, "Test Plugin")
        self.assertEqual(manifest.version, PluginVersion(1, 0, 0))
        self.assertEqual(manifest.entry_point, "main.py")
        mock_file.assert_called_once_with("/path/to/manifest.json", "r")

class TestPluginStore(unittest.TestCase):
    """Test cases for the PluginStore class."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = PluginMarketplaceConfig(
            data_directory=self.temp_dir
        )
        self.store = PluginStore(self.config)
    
    def test_add_plugin(self):
        """Test adding a plugin to the store."""
        # Create plugin
        plugin = Plugin(
            plugin_id="test-plugin",
            name="Test Plugin",
            version=PluginVersion(1, 0, 0)
        )
        
        # Add plugin
        self.store.add_plugin(plugin)
        
        # Verify plugin was added
        stored_plugin = self.store.get_plugin("test-plugin")
        self.assertEqual(stored_plugin, plugin)
    
    def test_update_plugin(self):
        """Test updating a plugin in the store."""
        # Create and add plugin
        plugin = Plugin(
            plugin_id="test-plugin",
            name="Test Plugin",
            version=PluginVersion(1, 0, 0)
        )
        self.store.add_plugin(plugin)
        
        # Create updated plugin
        updated_plugin = Plugin(
            plugin_id="test-plugin",
            name="Test Plugin Updated",
            version=PluginVersion(1, 1, 0)
        )
        
        # Update plugin
        self.store.update_plugin(updated_plugin)
        
        # Verify plugin was updated
        stored_plugin = self.store.get_plugin("test-plugin")
        self.assertEqual(stored_plugin.name, "Test Plugin Updated")
        self.assertEqual(stored_plugin.version, PluginVersion(1, 1, 0))
    
    def test_remove_plugin(self):
        """Test removing a plugin from the store."""
        # Create and add plugin
        plugin = Plugin(
            plugin_id="test-plugin",
            name="Test Plugin",
            version=PluginVersion(1, 0, 0)
        )
        self.store.add_plugin(plugin)
        
        # Remove plugin
        self.store.remove_plugin("test-plugin")
        
        # Verify plugin was removed
        stored_plugin = self.store.get_plugin("test-plugin")
        self.assertIsNone(stored_plugin)
    
    def test_get_all_plugins(self):
        """Test getting all plugins from the store."""
        # Create and add plugins
        plugin1 = Plugin(
            plugin_id="plugin1",
            name="Plugin 1",
            version=PluginVersion(1, 0, 0)
        )
        
        plugin2 = Plugin(
            plugin_id="plugin2",
            name="Plugin 2",
            version=PluginVersion(1, 0, 0)
        )
        
        self.store.add_plugin(plugin1)
        self.store.add_plugin(plugin2)
        
        # Get all plugins
        plugins = self.store.get_all_plugins()
        
        # Verify plugins
        self.assertEqual(len(plugins), 2)
        self.assertIn(plugin1, plugins)
        self.assertIn(plugin2, plugins)
    
    def test_get_plugins_by_category(self):
        """Test getting plugins by category."""
        # Create and add plugins
        plugin1 = Plugin(
            plugin_id="plugin1",
            name="Plugin 1",
            category=PluginCategory.PRODUCTIVITY
        )
        
        plugin2 = Plugin(
            plugin_id="plugin2",
            name="Plugin 2",
            category=PluginCategory.ANALYTICS
        )
        
        plugin3 = Plugin(
            plugin_id="plugin3",
            name="Plugin 3",
            category=PluginCategory.PRODUCTIVITY
        )
        
        self.store.add_plugin(plugin1)
        self.store.add_plugin(plugin2)
        self.store.add_plugin(plugin3)
        
        # Get plugins by category
        productivity_plugins = self.store.get_plugins_by_category(PluginCategory.PRODUCTIVITY)
        
        # Verify plugins
        self.assertEqual(len(productivity_plugins), 2)
        self.assertIn(plugin1, productivity_plugins)
        self.assertIn(plugin3, productivity_plugins)
    
    @patch('plugin_marketplace.plugin_marketplace_system.os.path.exists')
    @patch('plugin_marketplace.plugin_marketplace_system.os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    def test_save(self, mock_file, mock_makedirs, mock_exists):
        """Test saving the store to disk."""
        # Mock path exists
        mock_exists.return_value = False
        
        # Create and add plugin
        plugin = Plugin(
            plugin_id="test-plugin",
            name="Test Plugin",
            version=PluginVersion(1, 0, 0)
        )
        self.store.add_plugin(plugin)
        
        # Save store
        self.store.save()
        
        # Verify save
        mock_makedirs.assert_called_once()
        mock_file.assert_called_once()
        mock_file().write.assert_called_once()
    
    @patch('plugin_marketplace.plugin_marketplace_system.os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    def test_load(self, mock_file, mock_exists):
        """Test loading the store from disk."""
        # Mock path exists
        mock_exists.return_value = True
        
        # Mock file content
        store_content = json.dumps({
            "plugins": [
                {
                    "plugin_id": "test-plugin",
                    "name": "Test Plugin",
                    "version": "1.0.0"
                }
            ]
        })
        mock_file.return_value.__enter__.return_value.read.return_value = store_content
        
        # Load store
        self.store.load()
        
        # Verify load
        stored_plugin = self.store.get_plugin("test-plugin")
        self.assertIsNotNone(stored_plugin)
        self.assertEqual(stored_plugin.plugin_id, "test-plugin")
        self.assertEqual(stored_plugin.name, "Test Plugin")
        self.assertEqual(stored_plugin.version, PluginVersion(1, 0, 0))
        mock_file.assert_called_once()

if __name__ == '__main__':
    unittest.main()
