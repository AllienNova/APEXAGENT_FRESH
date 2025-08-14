"""
Specialized Knowledge Modules for Dr. TARDIS

This module provides specialized knowledge modules for the Dr. TARDIS system,
including support scenario modules and domain-specific knowledge providers.

Author: ApexAgent Development Team
Date: May 26, 2025
"""

import os
import logging
import json
import asyncio
import re
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime
import hashlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class SpecializedKnowledgeModule:
    """
    Base class for specialized knowledge modules.
    
    This class provides common functionality for specialized knowledge
    modules, including provider registration and management.
    
    Attributes:
        logger (logging.Logger): Logger for specialized knowledge module
        providers (Dict): Dictionary of knowledge providers
        data_path (str): Path to the data directory
    """
    
    def __init__(self, data_path: str = None):
        """
        Initialize the Specialized Knowledge Module.
        
        Args:
            data_path: Path to the data directory (default: None)
        """
        self.logger = logging.getLogger("SpecializedKnowledgeModule")
        
        # Set default data path if not provided
        if data_path is None:
            module_dir = os.path.dirname(os.path.abspath(__file__))
            self.data_path = os.path.join(module_dir, "data", "specialized")
        else:
            self.data_path = data_path
            
        # Create data directory if it doesn't exist
        os.makedirs(self.data_path, exist_ok=True)
        
        # Initialize providers
        self.providers = {}
        
        self.logger.info("SpecializedKnowledgeModule initialized")
    
    def register_knowledge_provider(self, provider):
        """
        Register a knowledge provider.
        
        Args:
            provider: Knowledge provider instance
        """
        # Get provider info
        provider_info = provider.get_provider_info()
        provider_id = provider_info.get("id")
        
        if not provider_id:
            self.logger.error("Provider ID is required")
            return
        
        # Register provider
        self.providers[provider_id] = provider
        
        self.logger.info(f"Registered knowledge provider: {provider_id}")
    
    def get_provider(self, provider_id: str):
        """
        Get a knowledge provider by ID.
        
        Args:
            provider_id: Provider ID
            
        Returns:
            Provider instance or None if not found
        """
        return self.providers.get(provider_id)
    
    def get_all_providers(self) -> List[Dict[str, Any]]:
        """
        Get information about all registered providers.
        
        Returns:
            List: List of provider information
        """
        provider_info = []
        
        for provider_id, provider in self.providers.items():
            info = provider.get_provider_info()
            provider_info.append(info)
        
        return provider_info
    
    def query_provider(self, provider_id: str, query: str) -> List[Dict[str, Any]]:
        """
        Query a specific knowledge provider.
        
        Args:
            provider_id: Provider ID
            query: Query string
            
        Returns:
            List: Query results
        """
        provider = self.get_provider(provider_id)
        
        if not provider:
            self.logger.warning(f"Provider not found: {provider_id}")
            return []
        
        try:
            results = provider.query(query)
            return results
        except Exception as e:
            self.logger.error(f"Error querying provider {provider_id}: {e}")
            return []
    
    def query_all_providers(self, query: str) -> List[Dict[str, Any]]:
        """
        Query all registered knowledge providers.
        
        Args:
            query: Query string
            
        Returns:
            List: Combined query results from all providers
        """
        all_results = []
        
        for provider_id, provider in self.providers.items():
            try:
                results = provider.query(query)
                
                # Add provider ID to results
                provider_results = {
                    "provider_id": provider_id,
                    "results": results
                }
                
                all_results.append(provider_results)
            except Exception as e:
                self.logger.error(f"Error querying provider {provider_id}: {e}")
        
        return all_results
    
    async def async_query_provider(self, provider_id: str, query: str) -> List[Dict[str, Any]]:
        """
        Asynchronously query a specific knowledge provider.
        
        Args:
            provider_id: Provider ID
            query: Query string
            
        Returns:
            List: Query results
        """
        provider = self.get_provider(provider_id)
        
        if not provider:
            self.logger.warning(f"Provider not found: {provider_id}")
            return []
        
        try:
            # Check if provider supports async queries
            if hasattr(provider, "async_query"):
                results = await provider.async_query(query)
            else:
                # Fall back to synchronous query
                results = provider.query(query)
                
            return results
        except Exception as e:
            self.logger.error(f"Error in async query of provider {provider_id}: {e}")
            return []
    
    async def async_query_all_providers(self, query: str) -> List[Dict[str, Any]]:
        """
        Asynchronously query all registered knowledge providers.
        
        Args:
            query: Query string
            
        Returns:
            List: Combined query results from all providers
        """
        all_results = []
        tasks = []
        
        # Create tasks for all providers
        for provider_id in self.providers:
            task = asyncio.create_task(self.async_query_provider(provider_id, query))
            tasks.append((provider_id, task))
        
        # Wait for all tasks to complete
        for provider_id, task in tasks:
            try:
                results = await task
                
                # Add provider ID to results
                provider_results = {
                    "provider_id": provider_id,
                    "results": results
                }
                
                all_results.append(provider_results)
            except Exception as e:
                self.logger.error(f"Error in async query of provider {provider_id}: {e}")
        
        return all_results


class SupportScenarioModule:
    """
    Provides support scenario functionality for the Dr. TARDIS system.
    
    This class manages support scenarios, including storage, retrieval,
    and search capabilities.
    
    Attributes:
        logger (logging.Logger): Logger for support scenario module
        scenarios (Dict): Dictionary of support scenarios
        data_path (str): Path to the data directory
    """
    
    def __init__(self, data_path: str = None):
        """
        Initialize the Support Scenario Module.
        
        Args:
            data_path: Path to the data directory (default: None)
        """
        self.logger = logging.getLogger("SupportScenarioModule")
        
        # Set default data path if not provided
        if data_path is None:
            module_dir = os.path.dirname(os.path.abspath(__file__))
            self.data_path = os.path.join(module_dir, "data", "scenarios")
        else:
            self.data_path = data_path
            
        # Create data directory if it doesn't exist
        os.makedirs(self.data_path, exist_ok=True)
        
        # Initialize scenarios
        self.scenarios = self._load_scenarios()
        
        self.logger.info("SupportScenarioModule initialized")
    
    def _load_scenarios(self) -> Dict[str, Any]:
        """
        Load scenarios from data files.
        
        Returns:
            Dict: Dictionary of scenarios
        """
        scenarios = {}
        
        # Load from scenarios directory if it exists
        scenarios_dir = os.path.join(self.data_path, "scenarios")
        os.makedirs(scenarios_dir, exist_ok=True)
        
        for filename in os.listdir(scenarios_dir):
            if filename.endswith(".json"):
                scenario_id = filename[:-5]  # Remove .json extension
                file_path = os.path.join(scenarios_dir, filename)
                
                try:
                    with open(file_path, 'r') as f:
                        scenario_data = json.load(f)
                    scenarios[scenario_id] = scenario_data
                except Exception as e:
                    self.logger.error(f"Error loading scenario {scenario_id}: {e}")
        
        self.logger.info(f"Loaded {len(scenarios)} scenarios")
        return scenarios
    
    def _save_scenario(self, scenario_id: str, scenario_data: Dict[str, Any]):
        """
        Save scenario to file.
        
        Args:
            scenario_id: Scenario ID
            scenario_data: Scenario data
        """
        scenarios_dir = os.path.join(self.data_path, "scenarios")
        os.makedirs(scenarios_dir, exist_ok=True)
        
        file_path = os.path.join(scenarios_dir, f"{scenario_id}.json")
        
        try:
            with open(file_path, 'w') as f:
                json.dump(scenario_data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving scenario {scenario_id}: {e}")
    
    def add_scenario(self, scenario: Dict[str, Any]):
        """
        Add a support scenario.
        
        Args:
            scenario: Scenario data
        """
        # Ensure scenario has an ID
        if "id" not in scenario:
            scenario_id = hashlib.md5(json.dumps(scenario, sort_keys=True).encode()).hexdigest()
            scenario["id"] = scenario_id
        else:
            scenario_id = scenario["id"]
        
        # Add timestamp if not present
        if "timestamp" not in scenario:
            scenario["timestamp"] = datetime.now().isoformat()
        
        # Add scenario to scenarios
        self.scenarios[scenario_id] = scenario
        
        # Save scenario to file
        self._save_scenario(scenario_id, scenario)
        
        self.logger.info(f"Added scenario: {scenario_id}")
    
    def get_scenario(self, scenario_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a support scenario by ID.
        
        Args:
            scenario_id: Scenario ID
            
        Returns:
            Dict: Scenario data or None if not found
        """
        return self.scenarios.get(scenario_id)
    
    def update_scenario(self, scenario_id: str, scenario_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update a support scenario.
        
        Args:
            scenario_id: Scenario ID
            scenario_data: Updated scenario data
            
        Returns:
            Dict: Updated scenario data or None if not found
        """
        if scenario_id not in self.scenarios:
            self.logger.warning(f"Scenario not found: {scenario_id}")
            return None
        
        # Update scenario
        scenario = self.scenarios[scenario_id]
        for key, value in scenario_data.items():
            if key != "id":  # Don't update ID
                scenario[key] = value
        
        # Update timestamp
        scenario["updated_at"] = datetime.now().isoformat()
        
        # Save updated scenario
        self._save_scenario(scenario_id, scenario)
        
        self.logger.info(f"Updated scenario: {scenario_id}")
        return scenario
    
    def delete_scenario(self, scenario_id: str) -> bool:
        """
        Delete a support scenario.
        
        Args:
            scenario_id: Scenario ID
            
        Returns:
            bool: True if deleted, False if not found
        """
        if scenario_id not in self.scenarios:
            self.logger.warning(f"Scenario not found: {scenario_id}")
            return False
        
        # Remove from scenarios
        del self.scenarios[scenario_id]
        
        # Remove file if it exists
        file_path = os.path.join(self.data_path, "scenarios", f"{scenario_id}.json")
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                self.logger.error(f"Error removing scenario file: {e}")
        
        self.logger.info(f"Deleted scenario: {scenario_id}")
        return True
    
    def search_scenarios(self, query: str, tags: List[str] = None, 
                       limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search support scenarios.
        
        Args:
            query: Search query
            tags: Optional list of tags to filter by
            limit: Maximum number of results to return
            
        Returns:
            List: List of matching scenarios
        """
        results = []
        
        # Convert query to lowercase for case-insensitive search
        query_lower = query.lower()
        
        # Search all scenarios
        for scenario_id, scenario in self.scenarios.items():
            # Calculate relevance score
            relevance = 0
            
            # Check name
            name = scenario.get("name", "").lower()
            if query_lower in name:
                # Higher relevance for name matches
                relevance += 0.5
                # Even higher if it's an exact match
                if query_lower == name:
                    relevance += 0.3
            
            # Check description
            description = scenario.get("description", "").lower()
            if query_lower in description:
                # Lower relevance for description matches
                relevance += 0.3
            
            # Check steps
            steps = scenario.get("steps", [])
            for step in steps:
                if isinstance(step, str) and query_lower in step.lower():
                    # Medium relevance for step matches
                    relevance += 0.2
            
            # Check tags
            scenario_tags = [tag.lower() for tag in scenario.get("tags", [])]
            for word in query_lower.split():
                if word in scenario_tags:
                    # Medium relevance for tag matches
                    relevance += 0.4
            
            # Filter by tags if provided
            if tags:
                # Convert tags to lowercase for case-insensitive comparison
                tags_lower = [tag.lower() for tag in tags]
                
                # Check if scenario has all required tags
                has_all_tags = all(tag in scenario_tags for tag in tags_lower)
                
                if not has_all_tags:
                    continue
            
            # Add to results if relevant
            if relevance > 0 or (not query and tags):
                # Add a copy of the scenario with relevance score
                result = scenario.copy()
                result["relevance"] = relevance
                results.append(result)
        
        # Sort by relevance
        sorted_results = sorted(results, key=lambda x: x["relevance"], reverse=True)
        
        # Limit results
        return sorted_results[:limit]
    
    def get_all_scenarios(self) -> List[Dict[str, Any]]:
        """
        Get all support scenarios.
        
        Returns:
            List: List of all scenarios
        """
        return list(self.scenarios.values())
    
    def get_scenarios_by_tags(self, tags: List[str]) -> List[Dict[str, Any]]:
        """
        Get scenarios by tags.
        
        Args:
            tags: List of tags to filter by
            
        Returns:
            List: List of matching scenarios
        """
        return self.search_scenarios("", tags=tags)
    
    def get_recent_scenarios(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent scenarios.
        
        Args:
            limit: Maximum number of scenarios to return
            
        Returns:
            List: List of recent scenarios
        """
        # Sort by timestamp
        sorted_scenarios = sorted(
            self.scenarios.values(),
            key=lambda x: x.get("timestamp", ""),
            reverse=True
        )
        
        return sorted_scenarios[:limit]


class DomainSpecificProvider:
    """
    Base class for domain-specific knowledge providers.
    
    This class defines the interface for domain-specific knowledge
    providers that can be registered with the SpecializedKnowledgeModule.
    """
    
    def get_provider_info(self) -> Dict[str, Any]:
        """
        Get information about the provider.
        
        Returns:
            Dict: Provider information
        """
        raise NotImplementedError("Subclasses must implement get_provider_info")
    
    def query(self, query: str) -> List[Dict[str, Any]]:
        """
        Query the provider.
        
        Args:
            query: Query string
            
        Returns:
            List: Query results
        """
        raise NotImplementedError("Subclasses must implement query")
    
    async def async_query(self, query: str) -> List[Dict[str, Any]]:
        """
        Asynchronously query the provider.
        
        Args:
            query: Query string
            
        Returns:
            List: Query results
        """
        # Default implementation falls back to synchronous query
        return self.query(query)


class MedicalKnowledgeProvider(DomainSpecificProvider):
    """
    Provides medical knowledge for the Dr. TARDIS system.
    
    This class implements a domain-specific knowledge provider for
    medical information.
    
    Attributes:
        logger (logging.Logger): Logger for medical knowledge provider
        data_path (str): Path to the data directory
    """
    
    def __init__(self, data_path: str = None):
        """
        Initialize the Medical Knowledge Provider.
        
        Args:
            data_path: Path to the data directory (default: None)
        """
        self.logger = logging.getLogger("MedicalKnowledgeProvider")
        
        # Set default data path if not provided
        if data_path is None:
            module_dir = os.path.dirname(os.path.abspath(__file__))
            self.data_path = os.path.join(module_dir, "data", "medical")
        else:
            self.data_path = data_path
            
        # Create data directory if it doesn't exist
        os.makedirs(self.data_path, exist_ok=True)
        
        self.logger.info("MedicalKnowledgeProvider initialized")
    
    def get_provider_info(self) -> Dict[str, Any]:
        """
        Get information about the provider.
        
        Returns:
            Dict: Provider information
        """
        return {
            "id": "medical",
            "name": "Medical Knowledge Provider",
            "description": "Provides medical knowledge for the Dr. TARDIS system",
            "version": "1.0.0"
        }
    
    def query(self, query: str) -> List[Dict[str, Any]]:
        """
        Query the provider.
        
        Args:
            query: Query string
            
        Returns:
            List: Query results
        """
        # This is a placeholder implementation
        # In a real implementation, this would query a medical knowledge base
        self.logger.info(f"Querying medical knowledge: {query}")
        
        # Simulate results
        results = [
            {
                "id": "med1",
                "title": f"Medical information for '{query}'",
                "content": f"This is simulated medical information for the query '{query}'.",
                "relevance": 0.9
            },
            {
                "id": "med2",
                "title": f"Related medical information for '{query}'",
                "content": f"This is related medical information for the query '{query}'.",
                "relevance": 0.7
            }
        ]
        
        return results


class TechnicalKnowledgeProvider(DomainSpecificProvider):
    """
    Provides technical knowledge for the Dr. TARDIS system.
    
    This class implements a domain-specific knowledge provider for
    technical information.
    
    Attributes:
        logger (logging.Logger): Logger for technical knowledge provider
        data_path (str): Path to the data directory
    """
    
    def __init__(self, data_path: str = None):
        """
        Initialize the Technical Knowledge Provider.
        
        Args:
            data_path: Path to the data directory (default: None)
        """
        self.logger = logging.getLogger("TechnicalKnowledgeProvider")
        
        # Set default data path if not provided
        if data_path is None:
            module_dir = os.path.dirname(os.path.abspath(__file__))
            self.data_path = os.path.join(module_dir, "data", "technical")
        else:
            self.data_path = data_path
            
        # Create data directory if it doesn't exist
        os.makedirs(self.data_path, exist_ok=True)
        
        self.logger.info("TechnicalKnowledgeProvider initialized")
    
    def get_provider_info(self) -> Dict[str, Any]:
        """
        Get information about the provider.
        
        Returns:
            Dict: Provider information
        """
        return {
            "id": "technical",
            "name": "Technical Knowledge Provider",
            "description": "Provides technical knowledge for the Dr. TARDIS system",
            "version": "1.0.0"
        }
    
    def query(self, query: str) -> List[Dict[str, Any]]:
        """
        Query the provider.
        
        Args:
            query: Query string
            
        Returns:
            List: Query results
        """
        # This is a placeholder implementation
        # In a real implementation, this would query a technical knowledge base
        self.logger.info(f"Querying technical knowledge: {query}")
        
        # Simulate results
        results = [
            {
                "id": "tech1",
                "title": f"Technical information for '{query}'",
                "content": f"This is simulated technical information for the query '{query}'.",
                "relevance": 0.9
            },
            {
                "id": "tech2",
                "title": f"Related technical information for '{query}'",
                "content": f"This is related technical information for the query '{query}'.",
                "relevance": 0.7
            }
        ]
        
        return results


# Example usage
def example_usage():
    # Create specialized knowledge module
    specialized = SpecializedKnowledgeModule()
    
    # Create and register providers
    medical_provider = MedicalKnowledgeProvider()
    technical_provider = TechnicalKnowledgeProvider()
    
    specialized.register_knowledge_provider(medical_provider)
    specialized.register_knowledge_provider(technical_provider)
    
    # Query providers
    medical_results = specialized.query_provider("medical", "heart disease")
    print(f"Medical results: {len(medical_results)}")
    for result in medical_results:
        print(f"- {result['title']} (relevance: {result['relevance']})")
    
    technical_results = specialized.query_provider("technical", "network troubleshooting")
    print(f"Technical results: {len(technical_results)}")
    for result in technical_results:
        print(f"- {result['title']} (relevance: {result['relevance']})")
    
    # Create support scenario module
    support = SupportScenarioModule()
    
    # Add scenarios
    support.add_scenario({
        "name": "Network Troubleshooting",
        "description": "Steps to troubleshoot network issues",
        "steps": ["Check connection", "Verify settings", "Restart router"],
        "tags": ["network", "troubleshooting"]
    })
    
    support.add_scenario({
        "name": "Password Reset",
        "description": "Process for resetting passwords",
        "steps": ["Verify identity", "Reset password", "Notify user"],
        "tags": ["password", "security"]
    })
    
    # Search scenarios
    network_scenarios = support.search_scenarios("network")
    print(f"Network scenarios: {len(network_scenarios)}")
    for scenario in network_scenarios:
        print(f"- {scenario['name']} (relevance: {scenario['relevance']})")
    
    security_scenarios = support.search_scenarios("", tags=["security"])
    print(f"Security scenarios: {len(security_scenarios)}")
    for scenario in security_scenarios:
        print(f"- {scenario['name']}")

if __name__ == "__main__":
    example_usage()
