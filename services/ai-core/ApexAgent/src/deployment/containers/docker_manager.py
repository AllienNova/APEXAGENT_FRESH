#!/usr/bin/env python3
"""
Docker Container Manager for ApexAgent

This module provides functionality for managing Docker containers for ApexAgent,
including image building, container creation, orchestration, and monitoring.
"""

import os
import sys
import json
import logging
import subprocess
import tempfile
import time
import shutil
from typing import Dict, List, Optional, Tuple, Union, Any
from enum import Enum
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("docker_manager.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("docker_manager")

class ContainerStatus(Enum):
    """Enumeration of container status codes."""
    RUNNING = "running"
    STOPPED = "stopped"
    FAILED = "failed"
    NOT_FOUND = "not_found"
    UNKNOWN = "unknown"

class DockerError(Exception):
    """Base exception for Docker-related errors."""
    pass

class ImageBuildError(DockerError):
    """Exception raised for image build errors."""
    pass

class ContainerError(DockerError):
    """Exception raised for container operation errors."""
    pass

class NetworkError(DockerError):
    """Exception raised for network-related errors."""
    pass

class VolumeError(DockerError):
    """Exception raised for volume-related errors."""
    pass

class DockerManager:
    """
    Manages Docker containers for ApexAgent.
    
    This class handles Docker image building, container creation,
    orchestration, and monitoring for ApexAgent components.
    """
    
    def __init__(self, config_path: Optional[str] = None, 
                 base_dir: Optional[str] = None,
                 verbose: bool = False):
        """
        Initialize the Docker Manager.
        
        Args:
            config_path: Path to the Docker configuration file
            base_dir: Base directory for Docker resources
            verbose: Enable verbose logging
        """
        self.config_path = config_path
        self.base_dir = base_dir or os.getcwd()
        self.verbose = verbose
        self.config = self._load_config()
        self.containers = {}
        self.networks = {}
        self.volumes = {}
        
        if verbose:
            logger.setLevel(logging.DEBUG)
        
        logger.info("Docker Manager initialized")
        logger.debug(f"Configuration loaded from: {config_path}")
        logger.debug(f"Base directory: {base_dir}")
        
        # Check Docker availability
        if not self._check_docker_available():
            logger.warning("Docker is not available or not running")
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load the Docker configuration.
        
        Returns:
            Dict: The loaded configuration
        
        Raises:
            DockerError: If the configuration cannot be loaded
        """
        if not self.config_path:
            # Use default configuration path
            self.config_path = os.path.join(self.base_dir, "config", "docker_config.json")
        
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
            raise DockerError(f"Failed to load configuration: {str(e)}")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """
        Get the default Docker configuration.
        
        Returns:
            Dict: The default configuration
        """
        default_config = {
            "version": "1.0.0",
            "registry": {
                "url": "docker.io",
                "username": "",
                "password": ""
            },
            "images": {
                "base": "ubuntu:22.04",
                "python": "python:3.11-slim",
                "node": "node:18-alpine"
            },
            "components": [
                {
                    "name": "core",
                    "image": "apexagent/core:latest",
                    "dockerfile": "Dockerfile.core",
                    "ports": [8000],
                    "volumes": ["data", "config"],
                    "environment": {
                        "LOG_LEVEL": "info"
                    },
                    "depends_on": []
                },
                {
                    "name": "ui",
                    "image": "apexagent/ui:latest",
                    "dockerfile": "Dockerfile.ui",
                    "ports": [3000],
                    "volumes": ["config"],
                    "environment": {
                        "API_URL": "http://core:8000",
                        "NODE_ENV": "production"
                    },
                    "depends_on": ["core"]
                },
                {
                    "name": "plugins",
                    "image": "apexagent/plugins:latest",
                    "dockerfile": "Dockerfile.plugins",
                    "ports": [8001],
                    "volumes": ["plugins", "data"],
                    "environment": {
                        "CORE_URL": "http://core:8000",
                        "LOG_LEVEL": "info"
                    },
                    "depends_on": ["core"]
                }
            ],
            "networks": [
                {
                    "name": "apexagent",
                    "driver": "bridge",
                    "subnet": "172.28.0.0/16"
                }
            ],
            "volumes": [
                {
                    "name": "data",
                    "driver": "local",
                    "mount_point": "/data"
                },
                {
                    "name": "config",
                    "driver": "local",
                    "mount_point": "/config"
                },
                {
                    "name": "plugins",
                    "driver": "local",
                    "mount_point": "/plugins"
                }
            ],
            "healthchecks": {
                "interval": 30,
                "timeout": 10,
                "retries": 3
            },
            "resources": {
                "cpu_limit": "1.0",
                "memory_limit": "1G"
            }
        }
        
        return default_config
    
    def _check_docker_available(self) -> bool:
        """
        Check if Docker is available and running.
        
        Returns:
            bool: True if Docker is available, False otherwise
        """
        try:
            result = subprocess.run(
                ["docker", "info"],
                capture_output=True,
                text=True
            )
            
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Error checking Docker availability: {str(e)}")
            return False
    
    def build_image(self, component_name: str, tag: Optional[str] = None,
                   build_args: Optional[Dict[str, str]] = None,
                   no_cache: bool = False) -> bool:
        """
        Build a Docker image for a component.
        
        Args:
            component_name: Name of the component to build
            tag: Optional tag for the image
            build_args: Optional build arguments
            no_cache: Whether to use cache during build
            
        Returns:
            bool: True if the image was built successfully, False otherwise
            
        Raises:
            ImageBuildError: If the image build fails
        """
        logger.info(f"Building image for component: {component_name}")
        
        # Find component configuration
        component = next((c for c in self.config.get("components", []) 
                         if c["name"] == component_name), None)
        
        if not component:
            logger.error(f"Component not found: {component_name}")
            raise ImageBuildError(f"Component not found: {component_name}")
        
        # Get image name and tag
        image_name = tag or component.get("image")
        if not image_name:
            logger.error(f"Image name not specified for component: {component_name}")
            raise ImageBuildError(f"Image name not specified for component: {component_name}")
        
        # Get Dockerfile path
        dockerfile = component.get("dockerfile")
        if not dockerfile:
            logger.error(f"Dockerfile not specified for component: {component_name}")
            raise ImageBuildError(f"Dockerfile not specified for component: {component_name}")
        
        dockerfile_path = os.path.join(self.base_dir, "dockerfiles", dockerfile)
        if not os.path.exists(dockerfile_path):
            logger.error(f"Dockerfile not found: {dockerfile_path}")
            raise ImageBuildError(f"Dockerfile not found: {dockerfile_path}")
        
        # Prepare build command
        cmd = ["docker", "build", "-t", image_name, "-f", dockerfile_path]
        
        # Add build arguments
        if build_args:
            for key, value in build_args.items():
                cmd.extend(["--build-arg", f"{key}={value}"])
        
        # Add no-cache option if specified
        if no_cache:
            cmd.append("--no-cache")
        
        # Add context path
        cmd.append(os.path.join(self.base_dir, "dockerfiles"))
        
        try:
            # Run build command
            logger.debug(f"Running build command: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                logger.error(f"Image build failed: {result.stderr}")
                raise ImageBuildError(f"Image build failed: {result.stderr}")
            
            logger.info(f"Image built successfully: {image_name}")
            return True
        except Exception as e:
            logger.error(f"Error building image: {str(e)}")
            raise ImageBuildError(f"Error building image: {str(e)}")
    
    def build_all_images(self, no_cache: bool = False) -> Dict[str, bool]:
        """
        Build all component images.
        
        Args:
            no_cache: Whether to use cache during build
            
        Returns:
            Dict[str, bool]: Dictionary of component names and build success status
        """
        logger.info("Building all component images")
        
        results = {}
        
        for component in self.config.get("components", []):
            component_name = component["name"]
            try:
                success = self.build_image(component_name, no_cache=no_cache)
                results[component_name] = success
            except Exception as e:
                logger.error(f"Failed to build image for {component_name}: {str(e)}")
                results[component_name] = False
        
        return results
    
    def create_network(self, network_name: Optional[str] = None) -> bool:
        """
        Create a Docker network.
        
        Args:
            network_name: Optional name of the network to create
            
        Returns:
            bool: True if the network was created successfully, False otherwise
            
        Raises:
            NetworkError: If the network creation fails
        """
        # Use default network if not specified
        if not network_name:
            networks = self.config.get("networks", [])
            if not networks:
                logger.error("No networks defined in configuration")
                raise NetworkError("No networks defined in configuration")
            
            network = networks[0]
            network_name = network["name"]
        else:
            network = next((n for n in self.config.get("networks", []) 
                           if n["name"] == network_name), None)
            
            if not network:
                logger.error(f"Network not found in configuration: {network_name}")
                raise NetworkError(f"Network not found in configuration: {network_name}")
        
        logger.info(f"Creating network: {network_name}")
        
        # Check if network already exists
        try:
            result = subprocess.run(
                ["docker", "network", "inspect", network_name],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info(f"Network already exists: {network_name}")
                self.networks[network_name] = network
                return True
        except Exception:
            pass
        
        # Prepare network creation command
        cmd = ["docker", "network", "create", "--driver", network.get("driver", "bridge")]
        
        # Add subnet if specified
        if "subnet" in network:
            cmd.extend(["--subnet", network["subnet"]])
        
        # Add network name
        cmd.append(network_name)
        
        try:
            # Run network creation command
            logger.debug(f"Running network creation command: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                logger.error(f"Network creation failed: {result.stderr}")
                raise NetworkError(f"Network creation failed: {result.stderr}")
            
            logger.info(f"Network created successfully: {network_name}")
            self.networks[network_name] = network
            return True
        except Exception as e:
            logger.error(f"Error creating network: {str(e)}")
            raise NetworkError(f"Error creating network: {str(e)}")
    
    def create_volume(self, volume_name: Optional[str] = None) -> bool:
        """
        Create a Docker volume.
        
        Args:
            volume_name: Optional name of the volume to create
            
        Returns:
            bool: True if the volume was created successfully, False otherwise
            
        Raises:
            VolumeError: If the volume creation fails
        """
        # Use first volume if not specified
        if not volume_name:
            volumes = self.config.get("volumes", [])
            if not volumes:
                logger.error("No volumes defined in configuration")
                raise VolumeError("No volumes defined in configuration")
            
            volume = volumes[0]
            volume_name = volume["name"]
        else:
            volume = next((v for v in self.config.get("volumes", []) 
                          if v["name"] == volume_name), None)
            
            if not volume:
                logger.error(f"Volume not found in configuration: {volume_name}")
                raise VolumeError(f"Volume not found in configuration: {volume_name}")
        
        logger.info(f"Creating volume: {volume_name}")
        
        # Check if volume already exists
        try:
            result = subprocess.run(
                ["docker", "volume", "inspect", volume_name],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info(f"Volume already exists: {volume_name}")
                self.volumes[volume_name] = volume
                return True
        except Exception:
            pass
        
        # Prepare volume creation command
        cmd = ["docker", "volume", "create", "--driver", volume.get("driver", "local")]
        
        # Add volume options if specified
        if "options" in volume:
            for key, value in volume["options"].items():
                cmd.extend(["--opt", f"{key}={value}"])
        
        # Add volume name
        cmd.append(volume_name)
        
        try:
            # Run volume creation command
            logger.debug(f"Running volume creation command: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                logger.error(f"Volume creation failed: {result.stderr}")
                raise VolumeError(f"Volume creation failed: {result.stderr}")
            
            logger.info(f"Volume created successfully: {volume_name}")
            self.volumes[volume_name] = volume
            return True
        except Exception as e:
            logger.error(f"Error creating volume: {str(e)}")
            raise VolumeError(f"Error creating volume: {str(e)}")
    
    def create_all_volumes(self) -> Dict[str, bool]:
        """
        Create all volumes defined in the configuration.
        
        Returns:
            Dict[str, bool]: Dictionary of volume names and creation success status
        """
        logger.info("Creating all volumes")
        
        results = {}
        
        for volume in self.config.get("volumes", []):
            volume_name = volume["name"]
            try:
                success = self.create_volume(volume_name)
                results[volume_name] = success
            except Exception as e:
                logger.error(f"Failed to create volume {volume_name}: {str(e)}")
                results[volume_name] = False
        
        return results
    
    def create_container(self, component_name: str, container_name: Optional[str] = None,
                        environment: Optional[Dict[str, str]] = None,
                        ports: Optional[Dict[int, int]] = None,
                        network: Optional[str] = None) -> str:
        """
        Create a Docker container for a component.
        
        Args:
            component_name: Name of the component
            container_name: Optional name for the container
            environment: Optional environment variables
            ports: Optional port mappings (host:container)
            network: Optional network name
            
        Returns:
            str: Container ID if created successfully
            
        Raises:
            ContainerError: If the container creation fails
        """
        logger.info(f"Creating container for component: {component_name}")
        
        # Find component configuration
        component = next((c for c in self.config.get("components", []) 
                         if c["name"] == component_name), None)
        
        if not component:
            logger.error(f"Component not found: {component_name}")
            raise ContainerError(f"Component not found: {component_name}")
        
        # Get image name
        image_name = component.get("image")
        if not image_name:
            logger.error(f"Image name not specified for component: {component_name}")
            raise ContainerError(f"Image name not specified for component: {component_name}")
        
        # Set container name if not specified
        if not container_name:
            container_name = f"apexagent-{component_name}"
        
        # Prepare container creation command
        cmd = ["docker", "run", "-d", "--name", container_name]
        
        # Add environment variables
        env_vars = component.get("environment", {}).copy()
        if environment:
            env_vars.update(environment)
        
        for key, value in env_vars.items():
            cmd.extend(["-e", f"{key}={value}"])
        
        # Add port mappings
        port_mappings = {}
        component_ports = component.get("ports", [])
        
        if ports:
            for container_port, host_port in ports.items():
                port_mappings[container_port] = host_port
        else:
            # Use default port mappings (same port on host and container)
            for port in component_ports:
                port_mappings[port] = port
        
        for container_port, host_port in port_mappings.items():
            cmd.extend(["-p", f"{host_port}:{container_port}"])
        
        # Add volume mounts
        for volume_name in component.get("volumes", []):
            volume = next((v for v in self.config.get("volumes", []) 
                          if v["name"] == volume_name), None)
            
            if volume:
                mount_point = volume.get("mount_point", f"/{volume_name}")
                cmd.extend(["-v", f"{volume_name}:{mount_point}"])
        
        # Add network
        if not network:
            networks = self.config.get("networks", [])
            if networks:
                network = networks[0]["name"]
        
        if network:
            cmd.extend(["--network", network])
        
        # Add resource limits
        resources = self.config.get("resources", {})
        if "cpu_limit" in resources:
            cmd.extend(["--cpus", resources["cpu_limit"]])
        
        if "memory_limit" in resources:
            cmd.extend(["-m", resources["memory_limit"]])
        
        # Add healthcheck if specified
        healthchecks = self.config.get("healthchecks", {})
        if "command" in component.get("healthcheck", {}):
            healthcheck = component["healthcheck"]
            cmd.extend([
                "--health-cmd", healthcheck["command"],
                "--health-interval", f"{healthcheck.get('interval', healthchecks.get('interval', 30))}s",
                "--health-timeout", f"{healthcheck.get('timeout', healthchecks.get('timeout', 10))}s",
                "--health-retries", str(healthcheck.get("retries", healthchecks.get("retries", 3)))
            ])
        
        # Add restart policy
        cmd.extend(["--restart", "unless-stopped"])
        
        # Add image name
        cmd.append(image_name)
        
        try:
            # Run container creation command
            logger.debug(f"Running container creation command: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                logger.error(f"Container creation failed: {result.stderr}")
                raise ContainerError(f"Container creation failed: {result.stderr}")
            
            container_id = result.stdout.strip()
            logger.info(f"Container created successfully: {container_id}")
            
            # Store container information
            self.containers[component_name] = {
                "id": container_id,
                "name": container_name,
                "image": image_name,
                "ports": port_mappings,
                "network": network,
                "volumes": component.get("volumes", [])
            }
            
            return container_id
        except Exception as e:
            logger.error(f"Error creating container: {str(e)}")
            raise ContainerError(f"Error creating container: {str(e)}")
    
    def start_container(self, component_name: str) -> bool:
        """
        Start a container for a component.
        
        Args:
            component_name: Name of the component
            
        Returns:
            bool: True if the container was started successfully, False otherwise
            
        Raises:
            ContainerError: If the container start fails
        """
        logger.info(f"Starting container for component: {component_name}")
        
        # Check if container exists
        if component_name in self.containers:
            container_id = self.containers[component_name]["id"]
        else:
            # Check if container exists with default name
            container_name = f"apexagent-{component_name}"
            try:
                result = subprocess.run(
                    ["docker", "ps", "-a", "--filter", f"name={container_name}", "--format", "{{.ID}}"],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0 and result.stdout.strip():
                    container_id = result.stdout.strip()
                else:
                    logger.error(f"Container not found for component: {component_name}")
                    raise ContainerError(f"Container not found for component: {component_name}")
            except Exception as e:
                logger.error(f"Error finding container: {str(e)}")
                raise ContainerError(f"Error finding container: {str(e)}")
        
        try:
            # Start container
            result = subprocess.run(
                ["docker", "start", container_id],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                logger.error(f"Container start failed: {result.stderr}")
                raise ContainerError(f"Container start failed: {result.stderr}")
            
            logger.info(f"Container started successfully: {container_id}")
            return True
        except Exception as e:
            logger.error(f"Error starting container: {str(e)}")
            raise ContainerError(f"Error starting container: {str(e)}")
    
    def stop_container(self, component_name: str, timeout: int = 10) -> bool:
        """
        Stop a container for a component.
        
        Args:
            component_name: Name of the component
            timeout: Timeout in seconds before killing the container
            
        Returns:
            bool: True if the container was stopped successfully, False otherwise
            
        Raises:
            ContainerError: If the container stop fails
        """
        logger.info(f"Stopping container for component: {component_name}")
        
        # Check if container exists
        if component_name in self.containers:
            container_id = self.containers[component_name]["id"]
        else:
            # Check if container exists with default name
            container_name = f"apexagent-{component_name}"
            try:
                result = subprocess.run(
                    ["docker", "ps", "-a", "--filter", f"name={container_name}", "--format", "{{.ID}}"],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0 and result.stdout.strip():
                    container_id = result.stdout.strip()
                else:
                    logger.error(f"Container not found for component: {component_name}")
                    raise ContainerError(f"Container not found for component: {component_name}")
            except Exception as e:
                logger.error(f"Error finding container: {str(e)}")
                raise ContainerError(f"Error finding container: {str(e)}")
        
        try:
            # Stop container
            result = subprocess.run(
                ["docker", "stop", "-t", str(timeout), container_id],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                logger.error(f"Container stop failed: {result.stderr}")
                raise ContainerError(f"Container stop failed: {result.stderr}")
            
            logger.info(f"Container stopped successfully: {container_id}")
            return True
        except Exception as e:
            logger.error(f"Error stopping container: {str(e)}")
            raise ContainerError(f"Error stopping container: {str(e)}")
    
    def remove_container(self, component_name: str, force: bool = False) -> bool:
        """
        Remove a container for a component.
        
        Args:
            component_name: Name of the component
            force: Whether to force removal of a running container
            
        Returns:
            bool: True if the container was removed successfully, False otherwise
            
        Raises:
            ContainerError: If the container removal fails
        """
        logger.info(f"Removing container for component: {component_name}")
        
        # Check if container exists
        if component_name in self.containers:
            container_id = self.containers[component_name]["id"]
        else:
            # Check if container exists with default name
            container_name = f"apexagent-{component_name}"
            try:
                result = subprocess.run(
                    ["docker", "ps", "-a", "--filter", f"name={container_name}", "--format", "{{.ID}}"],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0 and result.stdout.strip():
                    container_id = result.stdout.strip()
                else:
                    logger.error(f"Container not found for component: {component_name}")
                    raise ContainerError(f"Container not found for component: {component_name}")
            except Exception as e:
                logger.error(f"Error finding container: {str(e)}")
                raise ContainerError(f"Error finding container: {str(e)}")
        
        try:
            # Prepare removal command
            cmd = ["docker", "rm"]
            
            if force:
                cmd.append("-f")
            
            cmd.append(container_id)
            
            # Remove container
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                logger.error(f"Container removal failed: {result.stderr}")
                raise ContainerError(f"Container removal failed: {result.stderr}")
            
            logger.info(f"Container removed successfully: {container_id}")
            
            # Remove from containers dictionary
            if component_name in self.containers:
                del self.containers[component_name]
            
            return True
        except Exception as e:
            logger.error(f"Error removing container: {str(e)}")
            raise ContainerError(f"Error removing container: {str(e)}")
    
    def get_container_status(self, component_name: str) -> ContainerStatus:
        """
        Get the status of a container for a component.
        
        Args:
            component_name: Name of the component
            
        Returns:
            ContainerStatus: The container status
        """
        logger.debug(f"Getting status for component: {component_name}")
        
        # Check if container exists
        if component_name in self.containers:
            container_id = self.containers[component_name]["id"]
        else:
            # Check if container exists with default name
            container_name = f"apexagent-{component_name}"
            try:
                result = subprocess.run(
                    ["docker", "ps", "-a", "--filter", f"name={container_name}", "--format", "{{.ID}}"],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0 and result.stdout.strip():
                    container_id = result.stdout.strip()
                else:
                    logger.debug(f"Container not found for component: {component_name}")
                    return ContainerStatus.NOT_FOUND
            except Exception as e:
                logger.error(f"Error finding container: {str(e)}")
                return ContainerStatus.UNKNOWN
        
        try:
            # Get container status
            result = subprocess.run(
                ["docker", "inspect", "--format", "{{.State.Status}}", container_id],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                logger.error(f"Failed to get container status: {result.stderr}")
                return ContainerStatus.UNKNOWN
            
            status = result.stdout.strip()
            
            if status == "running":
                return ContainerStatus.RUNNING
            elif status == "exited":
                return ContainerStatus.STOPPED
            else:
                return ContainerStatus.UNKNOWN
        except Exception as e:
            logger.error(f"Error getting container status: {str(e)}")
            return ContainerStatus.UNKNOWN
    
    def get_container_logs(self, component_name: str, tail: Optional[int] = None) -> str:
        """
        Get logs from a container for a component.
        
        Args:
            component_name: Name of the component
            tail: Optional number of lines to retrieve from the end
            
        Returns:
            str: Container logs
            
        Raises:
            ContainerError: If the logs cannot be retrieved
        """
        logger.debug(f"Getting logs for component: {component_name}")
        
        # Check if container exists
        if component_name in self.containers:
            container_id = self.containers[component_name]["id"]
        else:
            # Check if container exists with default name
            container_name = f"apexagent-{component_name}"
            try:
                result = subprocess.run(
                    ["docker", "ps", "-a", "--filter", f"name={container_name}", "--format", "{{.ID}}"],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0 and result.stdout.strip():
                    container_id = result.stdout.strip()
                else:
                    logger.error(f"Container not found for component: {component_name}")
                    raise ContainerError(f"Container not found for component: {component_name}")
            except Exception as e:
                logger.error(f"Error finding container: {str(e)}")
                raise ContainerError(f"Error finding container: {str(e)}")
        
        try:
            # Prepare logs command
            cmd = ["docker", "logs"]
            
            if tail:
                cmd.extend(["--tail", str(tail)])
            
            cmd.append(container_id)
            
            # Get container logs
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                logger.error(f"Failed to get container logs: {result.stderr}")
                raise ContainerError(f"Failed to get container logs: {result.stderr}")
            
            return result.stdout
        except Exception as e:
            logger.error(f"Error getting container logs: {str(e)}")
            raise ContainerError(f"Error getting container logs: {str(e)}")
    
    def deploy_component(self, component_name: str, build: bool = True,
                        force: bool = False) -> bool:
        """
        Deploy a component (build, create, and start).
        
        Args:
            component_name: Name of the component
            build: Whether to build the image
            force: Whether to force removal of existing containers
            
        Returns:
            bool: True if the component was deployed successfully, False otherwise
        """
        logger.info(f"Deploying component: {component_name}")
        
        try:
            # Find component configuration
            component = next((c for c in self.config.get("components", []) 
                             if c["name"] == component_name), None)
            
            if not component:
                logger.error(f"Component not found: {component_name}")
                return False
            
            # Check dependencies
            for dependency in component.get("depends_on", []):
                dep_status = self.get_container_status(dependency)
                if dep_status != ContainerStatus.RUNNING:
                    logger.error(f"Dependency not running: {dependency}")
                    return False
            
            # Build image if requested
            if build:
                self.build_image(component_name)
            
            # Remove existing container if it exists
            status = self.get_container_status(component_name)
            if status != ContainerStatus.NOT_FOUND:
                self.remove_container(component_name, force=force)
            
            # Create and start container
            self.create_container(component_name)
            self.start_container(component_name)
            
            # Verify container is running
            status = self.get_container_status(component_name)
            if status != ContainerStatus.RUNNING:
                logger.error(f"Container not running after deployment: {component_name}")
                return False
            
            logger.info(f"Component deployed successfully: {component_name}")
            return True
        except Exception as e:
            logger.error(f"Error deploying component: {str(e)}")
            return False
    
    def deploy_all(self, build: bool = True, force: bool = False) -> Dict[str, bool]:
        """
        Deploy all components in dependency order.
        
        Args:
            build: Whether to build images
            force: Whether to force removal of existing containers
            
        Returns:
            Dict[str, bool]: Dictionary of component names and deployment success status
        """
        logger.info("Deploying all components")
        
        # Create network and volumes
        try:
            self.create_network()
            self.create_all_volumes()
        except Exception as e:
            logger.error(f"Error creating network or volumes: {str(e)}")
            return {}
        
        # Get components in dependency order
        components = self.config.get("components", [])
        deployment_order = self._get_deployment_order(components)
        
        if not deployment_order:
            logger.error("Failed to determine component deployment order")
            return {}
        
        results = {}
        
        # Deploy each component in order
        for component_name in deployment_order:
            try:
                success = self.deploy_component(component_name, build=build, force=force)
                results[component_name] = success
                
                if not success:
                    logger.error(f"Failed to deploy component: {component_name}")
                    # Continue with other components
            except Exception as e:
                logger.error(f"Error deploying component {component_name}: {str(e)}")
                results[component_name] = False
        
        return results
    
    def _get_deployment_order(self, components: List[Dict[str, Any]]) -> List[str]:
        """
        Determine the deployment order based on component dependencies.
        
        Args:
            components: List of component configurations
            
        Returns:
            List[str]: Ordered list of component names
        """
        # Build dependency graph
        graph = {}
        for component in components:
            name = component["name"]
            dependencies = component.get("depends_on", [])
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
        
        # Reverse to get deployment order
        return list(reversed(order))
    
    def monitor_containers(self, interval: int = 30) -> None:
        """
        Monitor container status at regular intervals.
        
        Args:
            interval: Monitoring interval in seconds
        """
        logger.info(f"Starting container monitoring with interval: {interval}s")
        
        try:
            while True:
                logger.info("Checking container status...")
                
                for component in self.config.get("components", []):
                    component_name = component["name"]
                    status = self.get_container_status(component_name)
                    
                    logger.info(f"Component {component_name}: {status.value}")
                    
                    # Restart failed containers
                    if status == ContainerStatus.STOPPED:
                        logger.warning(f"Container stopped: {component_name}, attempting restart")
                        try:
                            self.start_container(component_name)
                        except Exception as e:
                            logger.error(f"Failed to restart container: {str(e)}")
                
                time.sleep(interval)
        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
        except Exception as e:
            logger.error(f"Error in monitoring: {str(e)}")
    
    def cleanup(self) -> None:
        """
        Clean up resources (containers, networks, volumes).
        """
        logger.info("Cleaning up resources...")
        
        # Stop and remove containers
        for component_name in list(self.containers.keys()):
            try:
                self.remove_container(component_name, force=True)
            except Exception as e:
                logger.error(f"Error removing container {component_name}: {str(e)}")
        
        # Remove networks
        for network_name in list(self.networks.keys()):
            try:
                logger.info(f"Removing network: {network_name}")
                subprocess.run(["docker", "network", "rm", network_name], 
                              capture_output=True, text=True)
            except Exception as e:
                logger.error(f"Error removing network {network_name}: {str(e)}")
        
        # Remove volumes
        for volume_name in list(self.volumes.keys()):
            try:
                logger.info(f"Removing volume: {volume_name}")
                subprocess.run(["docker", "volume", "rm", volume_name], 
                              capture_output=True, text=True)
            except Exception as e:
                logger.error(f"Error removing volume {volume_name}: {str(e)}")
        
        logger.info("Cleanup completed")


def main():
    """
    Main entry point for the Docker Manager.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="ApexAgent Docker Manager")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--base-dir", help="Base directory for Docker resources")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument("--build", action="store_true", help="Build images")
    parser.add_argument("--deploy", action="store_true", help="Deploy containers")
    parser.add_argument("--force", action="store_true", help="Force container removal")
    parser.add_argument("--monitor", action="store_true", help="Monitor containers")
    parser.add_argument("--interval", type=int, default=30, help="Monitoring interval in seconds")
    parser.add_argument("--component", help="Specific component to operate on")
    parser.add_argument("--cleanup", action="store_true", help="Clean up resources")
    args = parser.parse_args()
    
    # Create Docker manager
    manager = DockerManager(
        config_path=args.config,
        base_dir=args.base_dir,
        verbose=args.verbose
    )
    
    try:
        # Process commands
        if args.build:
            if args.component:
                manager.build_image(args.component)
            else:
                manager.build_all_images()
        
        if args.deploy:
            if args.component:
                manager.deploy_component(args.component, build=args.build, force=args.force)
            else:
                manager.deploy_all(build=args.build, force=args.force)
        
        if args.monitor:
            manager.monitor_containers(interval=args.interval)
        
        if args.cleanup:
            manager.cleanup()
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
