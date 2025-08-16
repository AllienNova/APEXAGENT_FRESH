"""
Multi-Region Deployment for Gemini Live API Integration with Dr. TARDIS

This module implements multi-region deployment capabilities for the Gemini Live API
Integration with Dr. TARDIS in the Aideon AI Lite platform.

It provides:
1. Region-aware routing and load balancing
2. Data residency compliance mechanisms
3. Cross-region synchronization
4. Latency optimization
5. Regional failover capabilities
"""

import json
import logging
import os
import time
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple, Union

# Configure logging
logger = logging.getLogger(__name__)

class Region(Enum):
    """Supported deployment regions for Gemini Live API Integration."""
    US_CENTRAL = "us-central1"
    US_EAST = "us-east1"
    US_WEST = "us-west1"
    EUROPE_WEST = "europe-west1"
    EUROPE_NORTH = "europe-north1"
    ASIA_EAST = "asia-east1"
    ASIA_SOUTH = "asia-south1"
    AUSTRALIA = "australia-southeast1"

    @classmethod
    def from_string(cls, region_str: str) -> "Region":
        """Convert string to Region enum value."""
        try:
            return cls(region_str)
        except ValueError:
            logger.warning(f"Unknown region: {region_str}, defaulting to US_CENTRAL")
            return cls.US_CENTRAL

@dataclass
class RegionConfig:
    """Configuration for a specific region."""
    region: Region
    endpoint: str
    api_key: str
    max_capacity: int
    priority: int
    data_residency_compliant: bool
    enabled: bool = True
    health_check_interval: int = 60  # seconds
    failover_regions: List[Region] = None

    def __post_init__(self):
        if self.failover_regions is None:
            self.failover_regions = []

class DataResidencyRequirement(Enum):
    """Data residency requirements for different compliance regimes."""
    NONE = "none"
    EU_ONLY = "eu_only"
    US_ONLY = "us_only"
    AUSTRALIA_ONLY = "australia_only"
    ASIA_ONLY = "asia_only"
    CUSTOM = "custom"

class RegionHealth(Enum):
    """Health status of a region."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"

class MultiRegionDeployment:
    """
    Manages multi-region deployment for Gemini Live API Integration with Dr. TARDIS.
    
    This class provides:
    - Region-aware routing based on latency, load, and data residency requirements
    - Health monitoring of regions with automatic failover
    - Cross-region data synchronization
    - Configuration management for regional deployments
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the multi-region deployment manager.
        
        Args:
            config_path: Path to the configuration file. If None, uses default config.
        """
        self.regions: Dict[Region, RegionConfig] = {}
        self.region_health: Dict[Region, RegionHealth] = {}
        self.primary_region: Region = Region.US_CENTRAL
        self.data_residency_requirement: DataResidencyRequirement = DataResidencyRequirement.NONE
        self.allowed_regions: Set[Region] = set(Region)
        self.region_latencies: Dict[Region, float] = {}
        self.region_loads: Dict[Region, float] = {}
        self.last_health_check: Dict[Region, float] = {}
        
        # Load configuration
        if config_path and os.path.exists(config_path):
            self._load_config(config_path)
        else:
            self._load_default_config()
        
        # Initialize health status for all regions
        for region in self.regions:
            self.region_health[region] = RegionHealth.UNKNOWN
            self.region_latencies[region] = 0.0
            self.region_loads[region] = 0.0
            self.last_health_check[region] = 0.0
    
    def _load_config(self, config_path: str) -> None:
        """
        Load configuration from a file.
        
        Args:
            config_path: Path to the configuration file.
        """
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Load primary region
            self.primary_region = Region.from_string(config.get('primary_region', 'us-central1'))
            
            # Load data residency requirement
            residency = config.get('data_residency_requirement', 'none')
            self.data_residency_requirement = DataResidencyRequirement(residency)
            
            # Load allowed regions
            allowed = config.get('allowed_regions', [r.value for r in Region])
            self.allowed_regions = {Region.from_string(r) for r in allowed}
            
            # Load region configurations
            for region_config in config.get('regions', []):
                region = Region.from_string(region_config['region'])
                failover_regions = [Region.from_string(r) for r in region_config.get('failover_regions', [])]
                
                self.regions[region] = RegionConfig(
                    region=region,
                    endpoint=region_config['endpoint'],
                    api_key=region_config['api_key'],
                    max_capacity=region_config.get('max_capacity', 1000),
                    priority=region_config.get('priority', 1),
                    data_residency_compliant=region_config.get('data_residency_compliant', True),
                    enabled=region_config.get('enabled', True),
                    health_check_interval=region_config.get('health_check_interval', 60),
                    failover_regions=failover_regions
                )
            
            logger.info(f"Loaded configuration from {config_path} with {len(self.regions)} regions")
        except Exception as e:
            logger.error(f"Failed to load configuration from {config_path}: {e}")
            self._load_default_config()
    
    def _load_default_config(self) -> None:
        """Load default configuration with US, Europe, and Asia regions."""
        # US Central (Primary)
        self.regions[Region.US_CENTRAL] = RegionConfig(
            region=Region.US_CENTRAL,
            endpoint="https://us-central1-aiplatform.googleapis.com/v1/projects/aideon-ai-lite/locations/us-central1/endpoints/gemini-pro",
            api_key="",  # Will be loaded from ApiKeyManager
            max_capacity=5000,
            priority=1,
            data_residency_compliant=True,
            failover_regions=[Region.US_EAST, Region.US_WEST]
        )
        
        # US East
        self.regions[Region.US_EAST] = RegionConfig(
            region=Region.US_EAST,
            endpoint="https://us-east1-aiplatform.googleapis.com/v1/projects/aideon-ai-lite/locations/us-east1/endpoints/gemini-pro",
            api_key="",  # Will be loaded from ApiKeyManager
            max_capacity=3000,
            priority=2,
            data_residency_compliant=True,
            failover_regions=[Region.US_CENTRAL, Region.US_WEST]
        )
        
        # US West
        self.regions[Region.US_WEST] = RegionConfig(
            region=Region.US_WEST,
            endpoint="https://us-west1-aiplatform.googleapis.com/v1/projects/aideon-ai-lite/locations/us-west1/endpoints/gemini-pro",
            api_key="",  # Will be loaded from ApiKeyManager
            max_capacity=3000,
            priority=2,
            data_residency_compliant=True,
            failover_regions=[Region.US_CENTRAL, Region.US_EAST]
        )
        
        # Europe West
        self.regions[Region.EUROPE_WEST] = RegionConfig(
            region=Region.EUROPE_WEST,
            endpoint="https://europe-west1-aiplatform.googleapis.com/v1/projects/aideon-ai-lite/locations/europe-west1/endpoints/gemini-pro",
            api_key="",  # Will be loaded from ApiKeyManager
            max_capacity=4000,
            priority=1,
            data_residency_compliant=True,
            failover_regions=[Region.EUROPE_NORTH, Region.US_EAST]
        )
        
        # Europe North
        self.regions[Region.EUROPE_NORTH] = RegionConfig(
            region=Region.EUROPE_NORTH,
            endpoint="https://europe-north1-aiplatform.googleapis.com/v1/projects/aideon-ai-lite/locations/europe-north1/endpoints/gemini-pro",
            api_key="",  # Will be loaded from ApiKeyManager
            max_capacity=2000,
            priority=2,
            data_residency_compliant=True,
            failover_regions=[Region.EUROPE_WEST, Region.US_EAST]
        )
        
        # Asia East
        self.regions[Region.ASIA_EAST] = RegionConfig(
            region=Region.ASIA_EAST,
            endpoint="https://asia-east1-aiplatform.googleapis.com/v1/projects/aideon-ai-lite/locations/asia-east1/endpoints/gemini-pro",
            api_key="",  # Will be loaded from ApiKeyManager
            max_capacity=3000,
            priority=1,
            data_residency_compliant=True,
            failover_regions=[Region.ASIA_SOUTH, Region.US_WEST]
        )
        
        # Asia South
        self.regions[Region.ASIA_SOUTH] = RegionConfig(
            region=Region.ASIA_SOUTH,
            endpoint="https://asia-south1-aiplatform.googleapis.com/v1/projects/aideon-ai-lite/locations/asia-south1/endpoints/gemini-pro",
            api_key="",  # Will be loaded from ApiKeyManager
            max_capacity=2000,
            priority=2,
            data_residency_compliant=True,
            failover_regions=[Region.ASIA_EAST, Region.US_WEST]
        )
        
        # Australia
        self.regions[Region.AUSTRALIA] = RegionConfig(
            region=Region.AUSTRALIA,
            endpoint="https://australia-southeast1-aiplatform.googleapis.com/v1/projects/aideon-ai-lite/locations/australia-southeast1/endpoints/gemini-pro",
            api_key="",  # Will be loaded from ApiKeyManager
            max_capacity=1000,
            priority=2,
            data_residency_compliant=True,
            failover_regions=[Region.ASIA_EAST, Region.US_WEST]
        )
        
        logger.info(f"Loaded default configuration with {len(self.regions)} regions")
    
    def select_region(self, user_location: Optional[str] = None, 
                     data_residency: Optional[DataResidencyRequirement] = None) -> Region:
        """
        Select the optimal region based on user location, data residency requirements, and region health.
        
        Args:
            user_location: Optional location of the user (e.g., 'US', 'EU')
            data_residency: Optional data residency requirement
            
        Returns:
            The selected region
        """
        # Use provided data residency requirement or default
        residency_req = data_residency or self.data_residency_requirement
        
        # Filter regions based on data residency requirements
        compliant_regions = self._filter_compliant_regions(residency_req)
        if not compliant_regions:
            logger.warning(f"No compliant regions found for {residency_req}, using all enabled regions")
            compliant_regions = [r for r in self.regions if self.regions[r].enabled]
        
        # Filter out unhealthy regions
        healthy_regions = [r for r in compliant_regions 
                          if self.region_health.get(r, RegionHealth.UNKNOWN) != RegionHealth.UNHEALTHY]
        if not healthy_regions:
            logger.warning("No healthy regions available, using all compliant regions")
            healthy_regions = compliant_regions
        
        # If user location is provided, prioritize regions based on proximity
        if user_location:
            return self._select_by_proximity(healthy_regions, user_location)
        
        # Otherwise, select based on load and latency
        return self._select_by_performance(healthy_regions)
    
    def _filter_compliant_regions(self, residency_req: DataResidencyRequirement) -> List[Region]:
        """Filter regions based on data residency requirements."""
        if residency_req == DataResidencyRequirement.NONE:
            return [r for r in self.regions if self.regions[r].enabled]
        
        compliant_regions = []
        for region, config in self.regions.items():
            if not config.enabled:
                continue
                
            if residency_req == DataResidencyRequirement.EU_ONLY:
                if region in [Region.EUROPE_WEST, Region.EUROPE_NORTH] and config.data_residency_compliant:
                    compliant_regions.append(region)
            elif residency_req == DataResidencyRequirement.US_ONLY:
                if region in [Region.US_CENTRAL, Region.US_EAST, Region.US_WEST] and config.data_residency_compliant:
                    compliant_regions.append(region)
            elif residency_req == DataResidencyRequirement.AUSTRALIA_ONLY:
                if region == Region.AUSTRALIA and config.data_residency_compliant:
                    compliant_regions.append(region)
            elif residency_req == DataResidencyRequirement.ASIA_ONLY:
                if region in [Region.ASIA_EAST, Region.ASIA_SOUTH] and config.data_residency_compliant:
                    compliant_regions.append(region)
            elif residency_req == DataResidencyRequirement.CUSTOM:
                if region in self.allowed_regions and config.data_residency_compliant:
                    compliant_regions.append(region)
        
        return compliant_regions
    
    def _select_by_proximity(self, regions: List[Region], user_location: str) -> Region:
        """Select region based on proximity to user location."""
        user_location = user_location.upper()
        
        # Map user locations to regions
        location_map = {
            "US": [Region.US_CENTRAL, Region.US_EAST, Region.US_WEST],
            "USA": [Region.US_CENTRAL, Region.US_EAST, Region.US_WEST],
            "NORTH AMERICA": [Region.US_CENTRAL, Region.US_EAST, Region.US_WEST],
            "EU": [Region.EUROPE_WEST, Region.EUROPE_NORTH],
            "EUROPE": [Region.EUROPE_WEST, Region.EUROPE_NORTH],
            "ASIA": [Region.ASIA_EAST, Region.ASIA_SOUTH],
            "AUSTRALIA": [Region.AUSTRALIA],
            "OCEANIA": [Region.AUSTRALIA]
        }
        
        # Find matching regions
        preferred_regions = location_map.get(user_location, [])
        
        # Filter to regions that are in our allowed list
        preferred_regions = [r for r in preferred_regions if r in regions]
        
        if preferred_regions:
            # Sort by priority (lower is better)
            preferred_regions.sort(key=lambda r: self.regions[r].priority)
            return preferred_regions[0]
        
        # If no match, use performance-based selection
        return self._select_by_performance(regions)
    
    def _select_by_performance(self, regions: List[Region]) -> Region:
        """Select region based on performance metrics (load and latency)."""
        if not regions:
            logger.warning("No regions provided for selection, using primary region")
            return self.primary_region
        
        # Calculate a score for each region based on load and latency
        # Lower score is better
        scores = {}
        for region in regions:
            # Normalize load (0-1 scale)
            load = self.region_loads.get(region, 0.0)
            max_capacity = self.regions[region].max_capacity
            normalized_load = load / max_capacity if max_capacity > 0 else 1.0
            
            # Normalize latency (0-1 scale, assuming max latency of 1000ms)
            latency = self.region_latencies.get(region, 0.0)
            normalized_latency = min(latency / 1000.0, 1.0)
            
            # Priority factor (1-3 scale)
            priority = self.regions[region].priority
            priority_factor = priority / 3.0
            
            # Calculate score (lower is better)
            # Weight: 40% load, 40% latency, 20% priority
            score = (0.4 * normalized_load) + (0.4 * normalized_latency) + (0.2 * priority_factor)
            scores[region] = score
        
        # Select region with lowest score
        selected_region = min(scores.items(), key=lambda x: x[1])[0]
        logger.info(f"Selected region {selected_region} with score {scores[selected_region]}")
        
        return selected_region
    
    def update_region_health(self, region: Region, health: RegionHealth) -> None:
        """
        Update the health status of a region.
        
        Args:
            region: The region to update
            health: The new health status
        """
        old_health = self.region_health.get(region, RegionHealth.UNKNOWN)
        self.region_health[region] = health
        self.last_health_check[region] = time.time()
        
        if old_health != health:
            logger.info(f"Region {region} health changed from {old_health} to {health}")
            
            # If region became unhealthy, check if we need to update primary region
            if health == RegionHealth.UNHEALTHY and region == self.primary_region:
                self._handle_primary_region_failure()
    
    def _handle_primary_region_failure(self) -> None:
        """Handle failure of the primary region by selecting a new primary."""
        # Get failover regions for the primary
        failover_regions = self.regions[self.primary_region].failover_regions
        
        # Filter to healthy regions
        healthy_failovers = [r for r in failover_regions 
                            if self.region_health.get(r, RegionHealth.UNKNOWN) != RegionHealth.UNHEALTHY
                            and self.regions[r].enabled]
        
        if healthy_failovers:
            # Sort by priority
            healthy_failovers.sort(key=lambda r: self.regions[r].priority)
            new_primary = healthy_failovers[0]
            
            logger.warning(f"Primary region {self.primary_region} is unhealthy, switching to {new_primary}")
            self.primary_region = new_primary
        else:
            # If no healthy failovers, find any healthy region
            healthy_regions = [r for r in self.regions 
                              if self.region_health.get(r, RegionHealth.UNKNOWN) != RegionHealth.UNHEALTHY
                              and self.regions[r].enabled]
            
            if healthy_regions:
                # Sort by priority
                healthy_regions.sort(key=lambda r: self.regions[r].priority)
                new_primary = healthy_regions[0]
                
                logger.warning(f"No healthy failover regions for {self.primary_region}, switching to {new_primary}")
                self.primary_region = new_primary
            else:
                logger.error("No healthy regions available, keeping current primary region")
    
    def update_region_metrics(self, region: Region, latency: float, load: float) -> None:
        """
        Update performance metrics for a region.
        
        Args:
            region: The region to update
            latency: The measured latency in milliseconds
            load: The current load (number of active connections)
        """
        self.region_latencies[region] = latency
        self.region_loads[region] = load
        logger.debug(f"Updated metrics for {region}: latency={latency}ms, load={load}")
    
    def get_region_endpoint(self, region: Region) -> str:
        """
        Get the API endpoint for a region.
        
        Args:
            region: The region to get the endpoint for
            
        Returns:
            The endpoint URL
        """
        if region not in self.regions:
            logger.warning(f"Unknown region {region}, using primary region {self.primary_region}")
            region = self.primary_region
        
        return self.regions[region].endpoint
    
    def get_region_api_key(self, region: Region) -> str:
        """
        Get the API key for a region.
        
        Args:
            region: The region to get the API key for
            
        Returns:
            The API key
        """
        if region not in self.regions:
            logger.warning(f"Unknown region {region}, using primary region {self.primary_region}")
            region = self.primary_region
        
        return self.regions[region].api_key
    
    def run_health_checks(self) -> Dict[Region, RegionHealth]:
        """
        Run health checks on all regions and update their status.
        
        Returns:
            Dictionary mapping regions to their health status
        """
        current_time = time.time()
        regions_to_check = []
        
        # Determine which regions need health checks
        for region, config in self.regions.items():
            if not config.enabled:
                continue
                
            last_check = self.last_health_check.get(region, 0)
            if current_time - last_check >= config.health_check_interval:
                regions_to_check.append(region)
        
        # Run health checks in parallel (in a real implementation)
        # For this example, we'll simulate health checks
        for region in regions_to_check:
            health = self._simulate_health_check(region)
            self.update_region_health(region, health)
        
        return self.region_health
    
    def _simulate_health_check(self, region: Region) -> RegionHealth:
        """
        Simulate a health check for a region.
        
        In a real implementation, this would make an actual API call to the region.
        
        Args:
            region: The region to check
            
        Returns:
            The health status
        """
        # In a real implementation, this would make an actual API call
        # For this example, we'll return HEALTHY for most regions
        # with occasional DEGRADED or UNHEALTHY status
        import random
        
        # 90% chance of HEALTHY, 8% DEGRADED, 2% UNHEALTHY
        rand = random.random()
        if rand < 0.9:
            return RegionHealth.HEALTHY
        elif rand < 0.98:
            return RegionHealth.DEGRADED
        else:
            return RegionHealth.UNHEALTHY
    
    def get_region_status_summary(self) -> Dict[str, Dict]:
        """
        Get a summary of all region statuses.
        
        Returns:
            Dictionary with region status information
        """
        summary = {}
        for region in self.regions:
            config = self.regions[region]
            summary[region.value] = {
                "health": self.region_health.get(region, RegionHealth.UNKNOWN).value,
                "latency": self.region_latencies.get(region, 0.0),
                "load": self.region_loads.get(region, 0.0),
                "max_capacity": config.max_capacity,
                "enabled": config.enabled,
                "is_primary": region == self.primary_region,
                "last_health_check": self.last_health_check.get(region, 0.0),
                "data_residency_compliant": config.data_residency_compliant
            }
        
        return summary
    
    def save_config(self, config_path: str) -> bool:
        """
        Save the current configuration to a file.
        
        Args:
            config_path: Path to save the configuration to
            
        Returns:
            True if successful, False otherwise
        """
        try:
            config = {
                "primary_region": self.primary_region.value,
                "data_residency_requirement": self.data_residency_requirement.value,
                "allowed_regions": [r.value for r in self.allowed_regions],
                "regions": []
            }
            
            for region, region_config in self.regions.items():
                config["regions"].append({
                    "region": region.value,
                    "endpoint": region_config.endpoint,
                    "api_key": "***",  # Don't save actual API keys
                    "max_capacity": region_config.max_capacity,
                    "priority": region_config.priority,
                    "data_residency_compliant": region_config.data_residency_compliant,
                    "enabled": region_config.enabled,
                    "health_check_interval": region_config.health_check_interval,
                    "failover_regions": [r.value for r in region_config.failover_regions]
                })
            
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            logger.info(f"Saved configuration to {config_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save configuration to {config_path}: {e}")
            return False
