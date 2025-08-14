#!/usr/bin/env python3
"""
Test suite for the Deployment System components.

This module provides comprehensive tests for the installation, containerization,
and cloud deployment components of the ApexAgent deployment system.
"""

import os
import sys
import unittest
import tempfile
import shutil
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import modules to test
from deployment.installers.installation_manager import (
    InstallationManager, InstallationConfig, InstallationStatus, 
    PlatformType, InstallationMode
)
from deployment.containers.docker_manager import (
    DockerManager, ContainerConfig, ContainerStatus, 
    NetworkConfig, VolumeConfig
)
from deployment.cloud.cloud_deployment_manager import (
    CloudDeploymentManager, CloudProvider, DeploymentConfig,
    DeploymentStatus, ResourceType
)

class TestInstallationManager(unittest.TestCase):
    """Test cases for the InstallationManager class."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = InstallationConfig(
            app_name="TestApp",
            version="1.0.0",
            install_dir=self.temp_dir,
            platform=PlatformType.LINUX,
            mode=InstallationMode.USER,
            auto_update=True
        )
        self.manager = InstallationManager(self.config)
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    @patch('deployment.installers.installation_manager.os.path.exists')
    @patch('deployment.installers.installation_manager.os.makedirs')
    @patch('deployment.installers.installation_manager.shutil.copy')
    def test_install_application(self, mock_copy, mock_makedirs, mock_exists):
        """Test installing the application."""
        mock_exists.return_value = False
        
        # Create a mock source directory with files
        source_dir = os.path.join(self.temp_dir, "source")
        os.makedirs(source_dir)
        with open(os.path.join(source_dir, "test_file.txt"), "w") as f:
            f.write("Test content")
        
        result = self.manager.install_application(source_dir)
        
        self.assertTrue(result)
        mock_makedirs.assert_called()
        mock_copy.assert_called()
    
    @patch('deployment.installers.installation_manager.os.path.exists')
    @patch('deployment.installers.installation_manager.shutil.rmtree')
    def test_uninstall_application(self, mock_rmtree, mock_exists):
        """Test uninstalling the application."""
        mock_exists.return_value = True
        
        result = self.manager.uninstall_application()
        
        self.assertTrue(result)
        mock_rmtree.assert_called_with(self.temp_dir)
    
    @patch('deployment.installers.installation_manager.requests.get')
    def test_check_for_updates(self, mock_get):
        """Test checking for updates."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "latest_version": "1.1.0",
            "download_url": "https://example.com/download/1.1.0"
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        has_update, version = self.manager.check_for_updates("https://example.com/api/updates")
        
        self.assertTrue(has_update)
        self.assertEqual(version, "1.1.0")
    
    @patch('deployment.installers.installation_manager.requests.get')
    @patch('deployment.installers.installation_manager.os.path.exists')
    @patch('deployment.installers.installation_manager.os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    def test_download_update(self, mock_file, mock_makedirs, mock_exists, mock_get):
        """Test downloading an update."""
        mock_exists.return_value = False
        mock_response = MagicMock()
        mock_response.iter_content.return_value = [b"test content"]
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        result = self.manager.download_update("https://example.com/download/1.1.0")
        
        self.assertTrue(result)
        mock_file.assert_called()
        mock_get.assert_called_with("https://example.com/download/1.1.0", stream=True)
    
    def test_get_installation_status(self):
        """Test getting installation status."""
        with patch('deployment.installers.installation_manager.os.path.exists') as mock_exists:
            # Test when app is installed
            mock_exists.return_value = True
            status = self.manager.get_installation_status()
            self.assertEqual(status, InstallationStatus.INSTALLED)
            
            # Test when app is not installed
            mock_exists.return_value = False
            status = self.manager.get_installation_status()
            self.assertEqual(status, InstallationStatus.NOT_INSTALLED)

class TestDockerManager(unittest.TestCase):
    """Test cases for the DockerManager class."""
    
    def setUp(self):
        """Set up test environment."""
        self.config = ContainerConfig(
            image_name="test-image",
            tag="latest",
            container_name="test-container",
            ports={8080: 8080},
            environment={"ENV_VAR": "value"},
            volumes={"/host/path": "/container/path"}
        )
        self.manager = DockerManager()
    
    @patch('deployment.containers.docker_manager.subprocess.run')
    def test_build_image(self, mock_run):
        """Test building a Docker image."""
        mock_run.return_value = MagicMock(returncode=0)
        
        result = self.manager.build_image("test-image", "latest", "/path/to/dockerfile")
        
        self.assertTrue(result)
        mock_run.assert_called()
    
    @patch('deployment.containers.docker_manager.subprocess.run')
    def test_run_container(self, mock_run):
        """Test running a Docker container."""
        mock_run.return_value = MagicMock(returncode=0)
        
        result = self.manager.run_container(self.config)
        
        self.assertTrue(result)
        mock_run.assert_called()
    
    @patch('deployment.containers.docker_manager.subprocess.run')
    def test_stop_container(self, mock_run):
        """Test stopping a Docker container."""
        mock_run.return_value = MagicMock(returncode=0)
        
        result = self.manager.stop_container("test-container")
        
        self.assertTrue(result)
        mock_run.assert_called_with(
            ["docker", "stop", "test-container"],
            capture_output=True,
            text=True
        )
    
    @patch('deployment.containers.docker_manager.subprocess.run')
    def test_remove_container(self, mock_run):
        """Test removing a Docker container."""
        mock_run.return_value = MagicMock(returncode=0)
        
        result = self.manager.remove_container("test-container")
        
        self.assertTrue(result)
        mock_run.assert_called_with(
            ["docker", "rm", "test-container"],
            capture_output=True,
            text=True
        )
    
    @patch('deployment.containers.docker_manager.subprocess.run')
    def test_get_container_status(self, mock_run):
        """Test getting container status."""
        # Test running container
        mock_run.return_value = MagicMock(returncode=0, stdout="running")
        status = self.manager.get_container_status("test-container")
        self.assertEqual(status, ContainerStatus.RUNNING)
        
        # Test stopped container
        mock_run.return_value = MagicMock(returncode=0, stdout="exited")
        status = self.manager.get_container_status("test-container")
        self.assertEqual(status, ContainerStatus.STOPPED)
        
        # Test non-existent container
        mock_run.return_value = MagicMock(returncode=1)
        status = self.manager.get_container_status("test-container")
        self.assertEqual(status, ContainerStatus.NOT_FOUND)

class TestCloudDeploymentManager(unittest.TestCase):
    """Test cases for the CloudDeploymentManager class."""
    
    def setUp(self):
        """Set up test environment."""
        self.config = DeploymentConfig(
            app_name="TestApp",
            version="1.0.0",
            provider=CloudProvider.AWS,
            region="us-west-2",
            resources=[
                ResourceType.COMPUTE,
                ResourceType.DATABASE,
                ResourceType.STORAGE
            ],
            instance_type="t2.micro",
            auto_scaling=True,
            min_instances=1,
            max_instances=3
        )
        self.manager = CloudDeploymentManager(self.config)
    
    @patch('deployment.cloud.cloud_deployment_manager.boto3.client')
    def test_deploy_application(self, mock_boto_client):
        """Test deploying an application to the cloud."""
        mock_client = MagicMock()
        mock_boto_client.return_value = mock_client
        
        mock_client.create_stack.return_value = {
            'StackId': 'test-stack-id'
        }
        
        result = self.manager.deploy_application()
        
        self.assertTrue(result)
        mock_client.create_stack.assert_called()
    
    @patch('deployment.cloud.cloud_deployment_manager.boto3.client')
    def test_update_deployment(self, mock_boto_client):
        """Test updating a cloud deployment."""
        mock_client = MagicMock()
        mock_boto_client.return_value = mock_client
        
        mock_client.update_stack.return_value = {
            'StackId': 'test-stack-id'
        }
        
        result = self.manager.update_deployment()
        
        self.assertTrue(result)
        mock_client.update_stack.assert_called()
    
    @patch('deployment.cloud.cloud_deployment_manager.boto3.client')
    def test_terminate_deployment(self, mock_boto_client):
        """Test terminating a cloud deployment."""
        mock_client = MagicMock()
        mock_boto_client.return_value = mock_client
        
        result = self.manager.terminate_deployment()
        
        self.assertTrue(result)
        mock_client.delete_stack.assert_called()
    
    @patch('deployment.cloud.cloud_deployment_manager.boto3.client')
    def test_get_deployment_status(self, mock_boto_client):
        """Test getting deployment status."""
        mock_client = MagicMock()
        mock_boto_client.return_value = mock_client
        
        # Test active deployment
        mock_client.describe_stacks.return_value = {
            'Stacks': [{
                'StackStatus': 'CREATE_COMPLETE'
            }]
        }
        status = self.manager.get_deployment_status()
        self.assertEqual(status, DeploymentStatus.ACTIVE)
        
        # Test updating deployment
        mock_client.describe_stacks.return_value = {
            'Stacks': [{
                'StackStatus': 'UPDATE_IN_PROGRESS'
            }]
        }
        status = self.manager.get_deployment_status()
        self.assertEqual(status, DeploymentStatus.UPDATING)
        
        # Test failed deployment
        mock_client.describe_stacks.return_value = {
            'Stacks': [{
                'StackStatus': 'CREATE_FAILED'
            }]
        }
        status = self.manager.get_deployment_status()
        self.assertEqual(status, DeploymentStatus.FAILED)
        
        # Test non-existent deployment
        mock_client.describe_stacks.side_effect = Exception("Stack does not exist")
        status = self.manager.get_deployment_status()
        self.assertEqual(status, DeploymentStatus.NOT_DEPLOYED)

if __name__ == '__main__':
    unittest.main()
