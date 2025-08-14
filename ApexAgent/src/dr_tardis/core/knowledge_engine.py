"""
Knowledge Engine for Dr. TARDIS

This module implements the knowledge management, retrieval, and application
components of Dr. TARDIS as defined in the architecture.
"""

import datetime
import json
import os
import re
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple, Set, Union

class KnowledgeCategory(Enum):
    """Categories of knowledge in the Dr. TARDIS knowledge base."""
    GENERAL = "general"
    INSTALLATION = "installation"
    TROUBLESHOOTING = "troubleshooting"
    FEATURE = "feature"
    SECURITY = "security"
    ACCOUNT = "account"
    SYSTEM = "system"
    FAQ = "faq"
    PROCEDURE = "procedure"

class KnowledgeFormat(Enum):
    """Formats of knowledge items in the knowledge base."""
    TEXT = "text"
    MARKDOWN = "markdown"
    HTML = "html"
    JSON = "json"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    PROCEDURE = "procedure"
    DECISION_TREE = "decision_tree"

class SensitivityLevel(Enum):
    """Information sensitivity levels for security classification."""
    PUBLIC = 0
    INTERNAL = 1
    CONFIDENTIAL = 2
    RESTRICTED = 3
    SECRET = 4

class KnowledgeItem:
    """Represents a single item of knowledge in the knowledge base."""
    
    def __init__(
        self,
        item_id: str,
        title: str,
        content: str,
        category: KnowledgeCategory,
        format: KnowledgeFormat,
        tags: List[str],
        created_at: datetime.datetime,
        updated_at: datetime.datetime,
        version: str,
        sensitivity: SensitivityLevel = SensitivityLevel.PUBLIC,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.item_id = item_id
        self.title = title
        self.content = content
        self.category = category
        self.format = format
        self.tags = tags
        self.created_at = created_at
        self.updated_at = updated_at
        self.version = version
        self.sensitivity = sensitivity
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the knowledge item to a dictionary."""
        return {
            "item_id": self.item_id,
            "title": self.title,
            "content": self.content,
            "category": self.category.value,
            "format": self.format.value,
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "version": self.version,
            "sensitivity": self.sensitivity.value,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'KnowledgeItem':
        """Create a knowledge item from a dictionary."""
        return cls(
            item_id=data["item_id"],
            title=data["title"],
            content=data["content"],
            category=KnowledgeCategory(data["category"]),
            format=KnowledgeFormat(data["format"]),
            tags=data["tags"],
            created_at=datetime.datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.datetime.fromisoformat(data["updated_at"]),
            version=data["version"],
            sensitivity=SensitivityLevel(data["sensitivity"]),
            metadata=data.get("metadata", {})
        )

class DiagnosticStep:
    """Represents a single step in a diagnostic procedure."""
    
    def __init__(
        self,
        step_id: str,
        instruction: str,
        expected_outcome: str,
        possible_outcomes: Dict[str, str],
        next_steps: Dict[str, str],
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.step_id = step_id
        self.instruction = instruction
        self.expected_outcome = expected_outcome
        self.possible_outcomes = possible_outcomes
        self.next_steps = next_steps
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the diagnostic step to a dictionary."""
        return {
            "step_id": self.step_id,
            "instruction": self.instruction,
            "expected_outcome": self.expected_outcome,
            "possible_outcomes": self.possible_outcomes,
            "next_steps": self.next_steps,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DiagnosticStep':
        """Create a diagnostic step from a dictionary."""
        return cls(
            step_id=data["step_id"],
            instruction=data["instruction"],
            expected_outcome=data["expected_outcome"],
            possible_outcomes=data["possible_outcomes"],
            next_steps=data["next_steps"],
            metadata=data.get("metadata", {})
        )

class DiagnosticProcedure:
    """Represents a diagnostic procedure with multiple steps."""
    
    def __init__(
        self,
        procedure_id: str,
        title: str,
        description: str,
        initial_step_id: str,
        steps: Dict[str, DiagnosticStep],
        tags: List[str],
        created_at: datetime.datetime,
        updated_at: datetime.datetime,
        version: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.procedure_id = procedure_id
        self.title = title
        self.description = description
        self.initial_step_id = initial_step_id
        self.steps = steps
        self.tags = tags
        self.created_at = created_at
        self.updated_at = updated_at
        self.version = version
        self.metadata = metadata or {}
    
    def get_initial_step(self) -> DiagnosticStep:
        """Get the initial step of the procedure."""
        return self.steps[self.initial_step_id]
    
    def get_step(self, step_id: str) -> Optional[DiagnosticStep]:
        """Get a step by ID."""
        return self.steps.get(step_id)
    
    def get_next_step(self, current_step_id: str, outcome: str) -> Optional[DiagnosticStep]:
        """Get the next step based on the outcome of the current step."""
        current_step = self.get_step(current_step_id)
        if not current_step:
            return None
        
        next_step_id = current_step.next_steps.get(outcome)
        if not next_step_id:
            return None
        
        return self.get_step(next_step_id)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the diagnostic procedure to a dictionary."""
        return {
            "procedure_id": self.procedure_id,
            "title": self.title,
            "description": self.description,
            "initial_step_id": self.initial_step_id,
            "steps": {step_id: step.to_dict() for step_id, step in self.steps.items()},
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "version": self.version,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DiagnosticProcedure':
        """Create a diagnostic procedure from a dictionary."""
        steps = {
            step_id: DiagnosticStep.from_dict(step_data)
            for step_id, step_data in data["steps"].items()
        }
        
        return cls(
            procedure_id=data["procedure_id"],
            title=data["title"],
            description=data["description"],
            initial_step_id=data["initial_step_id"],
            steps=steps,
            tags=data["tags"],
            created_at=datetime.datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.datetime.fromisoformat(data["updated_at"]),
            version=data["version"],
            metadata=data.get("metadata", {})
        )

class KnowledgeBase:
    """Manages the storage and retrieval of knowledge items."""
    
    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = storage_path
        self.items: Dict[str, KnowledgeItem] = {}
        self.procedures: Dict[str, DiagnosticProcedure] = {}
        
        # Initialize with some sample knowledge if storage path is not provided
        if not storage_path:
            self._initialize_sample_knowledge()
    
    def _initialize_sample_knowledge(self) -> None:
        """Initialize with sample knowledge items for testing."""
        # Sample general knowledge
        self.add_item(KnowledgeItem(
            item_id="general-001",
            title="About ApexAgent",
            content="ApexAgent is an advanced AI platform designed to provide intelligent assistance and automation for various tasks.",
            category=KnowledgeCategory.GENERAL,
            format=KnowledgeFormat.TEXT,
            tags=["overview", "introduction", "apexagent"],
            created_at=datetime.datetime.now(),
            updated_at=datetime.datetime.now(),
            version="1.0"
        ))
        
        # Sample installation knowledge
        self.add_item(KnowledgeItem(
            item_id="install-001",
            title="Windows Installation Guide",
            content="# Windows Installation Guide\n\n## System Requirements\n- Windows 10 or later\n- 8GB RAM minimum\n- 4GB free disk space\n\n## Installation Steps\n1. Download the installer from the official website\n2. Run the installer as administrator\n3. Follow the on-screen instructions\n4. Complete the setup wizard\n5. Launch ApexAgent from the Start menu",
            category=KnowledgeCategory.INSTALLATION,
            format=KnowledgeFormat.MARKDOWN,
            tags=["installation", "windows", "setup"],
            created_at=datetime.datetime.now(),
            updated_at=datetime.datetime.now(),
            version="1.0"
        ))
        
        # Sample troubleshooting knowledge
        self.add_item(KnowledgeItem(
            item_id="trouble-001",
            title="Common Login Issues",
            content="# Common Login Issues\n\n## Issue: Forgotten Password\nUse the 'Forgot Password' link on the login page to reset your password.\n\n## Issue: Account Locked\nAfter multiple failed login attempts, accounts may be temporarily locked. Wait 30 minutes and try again.\n\n## Issue: Authentication Error\nEnsure you're using the correct email address and that your account has been activated.",
            category=KnowledgeCategory.TROUBLESHOOTING,
            format=KnowledgeFormat.MARKDOWN,
            tags=["login", "authentication", "password", "troubleshooting"],
            created_at=datetime.datetime.now(),
            updated_at=datetime.datetime.now(),
            version="1.0"
        ))
        
        # Sample FAQ
        self.add_item(KnowledgeItem(
            item_id="faq-001",
            title="Frequently Asked Questions",
            content="# Frequently Asked Questions\n\n## Q: How do I update ApexAgent?\nA: ApexAgent automatically checks for updates. You can also manually check by going to Settings > Check for Updates.\n\n## Q: Is my data secure?\nA: Yes, ApexAgent uses end-to-end encryption for all data transmission and storage.\n\n## Q: Can I use ApexAgent offline?\nA: Basic functionality is available offline, but some features require an internet connection.",
            category=KnowledgeCategory.FAQ,
            format=KnowledgeFormat.MARKDOWN,
            tags=["faq", "questions", "help"],
            created_at=datetime.datetime.now(),
            updated_at=datetime.datetime.now(),
            version="1.0"
        ))
        
        # Sample diagnostic procedure
        step1 = DiagnosticStep(
            step_id="network-diag-1",
            instruction="Check if you can access other websites in your browser.",
            expected_outcome="You can access other websites.",
            possible_outcomes={
                "yes": "Can access other websites",
                "no": "Cannot access any websites"
            },
            next_steps={
                "yes": "network-diag-2",
                "no": "network-diag-5"
            }
        )
        
        step2 = DiagnosticStep(
            step_id="network-diag-2",
            instruction="Check if ApexAgent is allowed through your firewall.",
            expected_outcome="ApexAgent is allowed through the firewall.",
            possible_outcomes={
                "yes": "ApexAgent is allowed",
                "no": "ApexAgent is blocked",
                "unsure": "Not sure how to check"
            },
            next_steps={
                "yes": "network-diag-3",
                "no": "network-diag-4",
                "unsure": "network-diag-6"
            }
        )
        
        step3 = DiagnosticStep(
            step_id="network-diag-3",
            instruction="Try restarting the ApexAgent service.",
            expected_outcome="The service restarts successfully.",
            possible_outcomes={
                "success": "Service restarted successfully",
                "failure": "Service failed to restart"
            },
            next_steps={
                "success": "network-diag-7",
                "failure": "network-diag-8"
            }
        )
        
        step4 = DiagnosticStep(
            step_id="network-diag-4",
            instruction="Add ApexAgent to your firewall's allowed applications.",
            expected_outcome="ApexAgent is added to the firewall exceptions.",
            possible_outcomes={
                "success": "Added to firewall exceptions",
                "failure": "Failed to add to exceptions"
            },
            next_steps={
                "success": "network-diag-3",
                "failure": "network-diag-9"
            }
        )
        
        step5 = DiagnosticStep(
            step_id="network-diag-5",
            instruction="Check your internet connection settings.",
            expected_outcome="Internet connection is properly configured.",
            possible_outcomes={
                "fixed": "Internet connection is working now",
                "still_broken": "Internet connection is still not working"
            },
            next_steps={
                "fixed": "network-diag-2",
                "still_broken": "network-diag-10"
            }
        )
        
        step6 = DiagnosticStep(
            step_id="network-diag-6",
            instruction="Open Windows Defender Firewall and check if ApexAgent is in the allowed apps list.",
            expected_outcome="You can verify if ApexAgent is allowed.",
            possible_outcomes={
                "allowed": "ApexAgent is in the allowed list",
                "blocked": "ApexAgent is not in the allowed list",
                "cannot_find": "Cannot find the firewall settings"
            },
            next_steps={
                "allowed": "network-diag-3",
                "blocked": "network-diag-4",
                "cannot_find": "network-diag-11"
            }
        )
        
        step7 = DiagnosticStep(
            step_id="network-diag-7",
            instruction="Try connecting to ApexAgent again.",
            expected_outcome="Connection is successful.",
            possible_outcomes={
                "success": "Connection successful",
                "failure": "Connection still fails"
            },
            next_steps={
                "success": "network-diag-12",
                "failure": "network-diag-13"
            }
        )
        
        step8 = DiagnosticStep(
            step_id="network-diag-8",
            instruction="Check the ApexAgent error logs for service startup issues.",
            expected_outcome="You can identify the cause of the service failure.",
            possible_outcomes={
                "found_issue": "Found an error in the logs",
                "no_issue": "No clear errors in the logs"
            },
            next_steps={
                "found_issue": "network-diag-14",
                "no_issue": "network-diag-15"
            }
        )
        
        step9 = DiagnosticStep(
            step_id="network-diag-9",
            instruction="Try temporarily disabling your firewall to test the connection.",
            expected_outcome="You can test if the firewall is the issue.",
            possible_outcomes={
                "works": "Connection works with firewall disabled",
                "still_fails": "Connection still fails with firewall disabled"
            },
            next_steps={
                "works": "network-diag-16",
                "still_fails": "network-diag-13"
            }
        )
        
        step10 = DiagnosticStep(
            step_id="network-diag-10",
            instruction="Contact your internet service provider for assistance.",
            expected_outcome="Your ISP helps resolve the connection issue.",
            possible_outcomes={
                "resolved": "Internet issue resolved",
                "unresolved": "Internet issue not resolved"
            },
            next_steps={
                "resolved": "network-diag-2",
                "unresolved": "network-diag-17"
            }
        )
        
        step11 = DiagnosticStep(
            step_id="network-diag-11",
            instruction="Follow these steps to open Windows Defender Firewall: Start > Settings > Network & Internet > Windows Firewall.",
            expected_outcome="You can access the firewall settings.",
            possible_outcomes={
                "success": "Found the firewall settings",
                "failure": "Still cannot find firewall settings"
            },
            next_steps={
                "success": "network-diag-6",
                "failure": "network-diag-18"
            }
        )
        
        step12 = DiagnosticStep(
            step_id="network-diag-12",
            instruction="Your network connection issue is resolved. Is there anything else you need help with?",
            expected_outcome="Issue is fully resolved.",
            possible_outcomes={
                "yes": "Need more help",
                "no": "No further help needed"
            },
            next_steps={
                "yes": "network-diag-19",
                "no": "network-diag-20"
            }
        )
        
        step13 = DiagnosticStep(
            step_id="network-diag-13",
            instruction="Let's check if the ApexAgent server is operational. Visit the status page at status.apexagent.com.",
            expected_outcome="You can check the server status.",
            possible_outcomes={
                "operational": "Servers are operational",
                "outage": "There's a server outage",
                "cannot_access": "Cannot access the status page"
            },
            next_steps={
                "operational": "network-diag-21",
                "outage": "network-diag-22",
                "cannot_access": "network-diag-5"
            }
        )
        
        step14 = DiagnosticStep(
            step_id="network-diag-14",
            instruction="Based on the error logs, let's address the specific issue with the service.",
            expected_outcome="We can resolve the specific service issue.",
            possible_outcomes={
                "resolved": "Service issue resolved",
                "unresolved": "Service issue not resolved"
            },
            next_steps={
                "resolved": "network-diag-3",
                "unresolved": "network-diag-23"
            }
        )
        
        step15 = DiagnosticStep(
            step_id="network-diag-15",
            instruction="Try reinstalling the ApexAgent service.",
            expected_outcome="Service is successfully reinstalled.",
            possible_outcomes={
                "success": "Reinstallation successful",
                "failure": "Reinstallation failed"
            },
            next_steps={
                "success": "network-diag-3",
                "failure": "network-diag-23"
            }
        )
        
        step16 = DiagnosticStep(
            step_id="network-diag-16",
            instruction="Configure your firewall to allow ApexAgent with these specific settings...",
            expected_outcome="Firewall is properly configured for ApexAgent.",
            possible_outcomes={
                "success": "Firewall configured successfully",
                "failure": "Firewall configuration failed"
            },
            next_steps={
                "success": "network-diag-7",
                "failure": "network-diag-23"
            }
        )
        
        step17 = DiagnosticStep(
            step_id="network-diag-17",
            instruction="Try using a different network connection if available.",
            expected_outcome="You can test with an alternative network.",
            possible_outcomes={
                "works": "Works on different network",
                "still_fails": "Fails on different network too",
                "unavailable": "No alternative network available"
            },
            next_steps={
                "works": "network-diag-24",
                "still_fails": "network-diag-13",
                "unavailable": "network-diag-23"
            }
        )
        
        step18 = DiagnosticStep(
            step_id="network-diag-18",
            instruction="Let's try accessing the firewall through the Control Panel instead.",
            expected_outcome="You can access firewall settings through Control Panel.",
            possible_outcomes={
                "success": "Found firewall in Control Panel",
                "failure": "Still cannot access firewall"
            },
            next_steps={
                "success": "network-diag-6",
                "failure": "network-diag-23"
            }
        )
        
        step19 = DiagnosticStep(
            step_id="network-diag-19",
            instruction="What other issues are you experiencing with ApexAgent?",
            expected_outcome="User describes another issue.",
            possible_outcomes={
                "new_issue": "User describes a new issue",
                "related_issue": "User describes a related network issue"
            },
            next_steps={
                "new_issue": "network-diag-25",
                "related_issue": "network-diag-1"
            }
        )
        
        step20 = DiagnosticStep(
            step_id="network-diag-20",
            instruction="Great! Your network connection issue has been resolved. The ApexAgent service is now properly connected.",
            expected_outcome="User is satisfied with the resolution.",
            possible_outcomes={},
            next_steps={}
        )
        
        step21 = DiagnosticStep(
            step_id="network-diag-21",
            instruction="Let's check your ApexAgent configuration file for correct server settings.",
            expected_outcome="Configuration file has correct server settings.",
            possible_outcomes={
                "correct": "Server settings are correct",
                "incorrect": "Server settings are incorrect"
            },
            next_steps={
                "correct": "network-diag-26",
                "incorrect": "network-diag-27"
            }
        )
        
        step22 = DiagnosticStep(
            step_id="network-diag-22",
            instruction="There's currently a server outage. Please wait until the servers are operational again.",
            expected_outcome="User understands they need to wait for server restoration.",
            possible_outcomes={
                "ok": "User will wait",
                "not_ok": "User needs immediate solution"
            },
            next_steps={
                "ok": "network-diag-28",
                "not_ok": "network-diag-29"
            }
        )
        
        step23 = DiagnosticStep(
            step_id="network-diag-23",
            instruction="This issue requires more advanced troubleshooting. Would you like to submit a support ticket?",
            expected_outcome="User decides on next support steps.",
            possible_outcomes={
                "yes": "User wants to submit ticket",
                "no": "User doesn't want to submit ticket"
            },
            next_steps={
                "yes": "network-diag-30",
                "no": "network-diag-31"
            }
        )
        
        step24 = DiagnosticStep(
            step_id="network-diag-24",
            instruction="The issue appears to be with your primary network. Let's troubleshoot your router/modem.",
            expected_outcome="User can troubleshoot their network equipment.",
            possible_outcomes={
                "fixed": "Network equipment issue fixed",
                "not_fixed": "Network equipment issue not fixed"
            },
            next_steps={
                "fixed": "network-diag-7",
                "not_fixed": "network-diag-10"
            }
        )
        
        step25 = DiagnosticStep(
            step_id="network-diag-25",
            instruction="Let me help you with that new issue. Can you describe it in detail?",
            expected_outcome="User provides details about a new issue.",
            possible_outcomes={},
            next_steps={}
        )
        
        step26 = DiagnosticStep(
            step_id="network-diag-26",
            instruction="Let's try clearing the ApexAgent cache and reconnecting.",
            expected_outcome="Cache is cleared and connection is retried.",
            possible_outcomes={
                "success": "Connection successful after clearing cache",
                "failure": "Connection still fails after clearing cache"
            },
            next_steps={
                "success": "network-diag-12",
                "failure": "network-diag-23"
            }
        )
        
        step27 = DiagnosticStep(
            step_id="network-diag-27",
            instruction="Let's update your configuration file with the correct server settings.",
            expected_outcome="Configuration file is updated correctly.",
            possible_outcomes={
                "success": "Configuration updated successfully",
                "failure": "Configuration update failed"
            },
            next_steps={
                "success": "network-diag-7",
                "failure": "network-diag-23"
            }
        )
        
        step28 = DiagnosticStep(
            step_id="network-diag-28",
            instruction="You can check the status page later for updates on the server outage.",
            expected_outcome="User knows how to check for status updates.",
            possible_outcomes={},
            next_steps={}
        )
        
        step29 = DiagnosticStep(
            step_id="network-diag-29",
            instruction="While the servers are down, you can still use these offline features of ApexAgent...",
            expected_outcome="User understands available offline options.",
            possible_outcomes={},
            next_steps={}
        )
        
        step30 = DiagnosticStep(
            step_id="network-diag-30",
            instruction="Let's submit a support ticket with all the diagnostic information we've gathered.",
            expected_outcome="Support ticket is submitted successfully.",
            possible_outcomes={},
            next_steps={}
        )
        
        step31 = DiagnosticStep(
            step_id="network-diag-31",
            instruction="Here are some additional resources that might help you resolve this issue on your own.",
            expected_outcome="User receives additional self-help resources.",
            possible_outcomes={},
            next_steps={}
        )
        
        steps = {
            "network-diag-1": step1,
            "network-diag-2": step2,
            "network-diag-3": step3,
            "network-diag-4": step4,
            "network-diag-5": step5,
            "network-diag-6": step6,
            "network-diag-7": step7,
            "network-diag-8": step8,
            "network-diag-9": step9,
            "network-diag-10": step10,
            "network-diag-11": step11,
            "network-diag-12": step12,
            "network-diag-13": step13,
            "network-diag-14": step14,
            "network-diag-15": step15,
            "network-diag-16": step16,
            "network-diag-17": step17,
            "network-diag-18": step18,
            "network-diag-19": step19,
            "network-diag-20": step20,
            "network-diag-21": step21,
            "network-diag-22": step22,
            "network-diag-23": step23,
            "network-diag-24": step24,
            "network-diag-25": step25,
            "network-diag-26": step26,
            "network-diag-27": step27,
            "network-diag-28": step28,
            "network-diag-29": step29,
            "network-diag-30": step30,
            "network-diag-31": step31
        }
        
        self.add_procedure(DiagnosticProcedure(
            procedure_id="network-connectivity",
            title="Network Connectivity Troubleshooting",
            description="A step-by-step guide to diagnose and resolve network connectivity issues with ApexAgent.",
            initial_step_id="network-diag-1",
            steps=steps,
            tags=["network", "connectivity", "troubleshooting", "connection"],
            created_at=datetime.datetime.now(),
            updated_at=datetime.datetime.now(),
            version="1.0"
        ))
    
    def add_item(self, item: KnowledgeItem) -> bool:
        """Add a knowledge item to the knowledge base."""
        if item.item_id in self.items:
            return False
        
        self.items[item.item_id] = item
        return True
    
    def get_item(self, item_id: str) -> Optional[KnowledgeItem]:
        """Get a knowledge item by ID."""
        return self.items.get(item_id)
    
    def update_item(self, item: KnowledgeItem) -> bool:
        """Update an existing knowledge item."""
        if item.item_id not in self.items:
            return False
        
        self.items[item.item_id] = item
        return True
    
    def delete_item(self, item_id: str) -> bool:
        """Delete a knowledge item."""
        if item_id not in self.items:
            return False
        
        del self.items[item_id]
        return True
    
    def add_procedure(self, procedure: DiagnosticProcedure) -> bool:
        """Add a diagnostic procedure to the knowledge base."""
        if procedure.procedure_id in self.procedures:
            return False
        
        self.procedures[procedure.procedure_id] = procedure
        return True
    
    def get_procedure(self, procedure_id: str) -> Optional[DiagnosticProcedure]:
        """Get a diagnostic procedure by ID."""
        return self.procedures.get(procedure_id)
    
    def update_procedure(self, procedure: DiagnosticProcedure) -> bool:
        """Update an existing diagnostic procedure."""
        if procedure.procedure_id not in self.procedures:
            return False
        
        self.procedures[procedure.procedure_id] = procedure
        return True
    
    def delete_procedure(self, procedure_id: str) -> bool:
        """Delete a diagnostic procedure."""
        if procedure_id not in self.procedures:
            return False
        
        del self.procedures[procedure_id]
        return True
    
    def search_items(self, query: str, category: Optional[KnowledgeCategory] = None, 
                    max_results: int = 10) -> List[KnowledgeItem]:
        """Search for knowledge items matching a query."""
        results = []
        query_lower = query.lower()
        
        for item in self.items.values():
            # Skip items that don't match the category filter
            if category and item.category != category:
                continue
            
            # Check for matches in title, content, and tags
            if query_lower in item.title.lower() or query_lower in item.content.lower():
                results.append(item)
                continue
            
            # Check tags
            if any(query_lower in tag.lower() for tag in item.tags):
                results.append(item)
                continue
        
        # Sort by relevance (simple implementation - title matches first)
        results.sort(key=lambda item: query_lower in item.title.lower(), reverse=True)
        
        return results[:max_results]
    
    def search_procedures(self, query: str, max_results: int = 10) -> List[DiagnosticProcedure]:
        """Search for diagnostic procedures matching a query."""
        results = []
        query_lower = query.lower()
        
        for procedure in self.procedures.values():
            # Check for matches in title, description, and tags
            if query_lower in procedure.title.lower() or query_lower in procedure.description.lower():
                results.append(procedure)
                continue
            
            # Check tags
            if any(query_lower in tag.lower() for tag in procedure.tags):
                results.append(procedure)
                continue
            
            # Check step instructions
            if any(query_lower in step.instruction.lower() for step in procedure.steps.values()):
                results.append(procedure)
                continue
        
        # Sort by relevance (simple implementation - title matches first)
        results.sort(key=lambda proc: query_lower in proc.title.lower(), reverse=True)
        
        return results[:max_results]
    
    def get_items_by_category(self, category: KnowledgeCategory, 
                             max_results: int = 10) -> List[KnowledgeItem]:
        """Get knowledge items by category."""
        results = [item for item in self.items.values() if item.category == category]
        
        # Sort by updated_at (most recent first)
        results.sort(key=lambda item: item.updated_at, reverse=True)
        
        return results[:max_results]
    
    def get_items_by_tags(self, tags: List[str], 
                         require_all: bool = False, 
                         max_results: int = 10) -> List[KnowledgeItem]:
        """Get knowledge items by tags."""
        results = []
        
        for item in self.items.values():
            if require_all:
                # Item must have all specified tags
                if all(tag in item.tags for tag in tags):
                    results.append(item)
            else:
                # Item must have at least one of the specified tags
                if any(tag in item.tags for tag in tags):
                    results.append(item)
        
        # Sort by updated_at (most recent first)
        results.sort(key=lambda item: item.updated_at, reverse=True)
        
        return results[:max_results]
    
    def save_to_storage(self) -> bool:
        """Save the knowledge base to storage."""
        if not self.storage_path:
            return False
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(self.storage_path, exist_ok=True)
            
            # Save items
            items_data = {item_id: item.to_dict() for item_id, item in self.items.items()}
            with open(os.path.join(self.storage_path, "items.json"), "w") as f:
                json.dump(items_data, f, indent=2)
            
            # Save procedures
            procedures_data = {proc_id: proc.to_dict() for proc_id, proc in self.procedures.items()}
            with open(os.path.join(self.storage_path, "procedures.json"), "w") as f:
                json.dump(procedures_data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving knowledge base: {e}")
            return False
    
    def load_from_storage(self) -> bool:
        """Load the knowledge base from storage."""
        if not self.storage_path:
            return False
        
        try:
            # Load items
            items_path = os.path.join(self.storage_path, "items.json")
            if os.path.exists(items_path):
                with open(items_path, "r") as f:
                    items_data = json.load(f)
                
                self.items = {
                    item_id: KnowledgeItem.from_dict(item_data)
                    for item_id, item_data in items_data.items()
                }
            
            # Load procedures
            procedures_path = os.path.join(self.storage_path, "procedures.json")
            if os.path.exists(procedures_path):
                with open(procedures_path, "r") as f:
                    procedures_data = json.load(f)
                
                self.procedures = {
                    proc_id: DiagnosticProcedure.from_dict(proc_data)
                    for proc_id, proc_data in procedures_data.items()
                }
            
            return True
        except Exception as e:
            print(f"Error loading knowledge base: {e}")
            return False

class KnowledgeRetriever:
    """Retrieves relevant knowledge based on queries and context."""
    
    def __init__(self, knowledge_base: KnowledgeBase):
        self.knowledge_base = knowledge_base
    
    def retrieve(self, query: str, context: Dict[str, Any], 
                top_k: int = 5) -> List[KnowledgeItem]:
        """Retrieve relevant knowledge items based on query and context."""
        # Extract category from context if available
        category = None
        if "category" in context:
            try:
                category = KnowledgeCategory(context["category"])
            except ValueError:
                pass
        
        # Extract tags from context if available
        tags = context.get("tags", [])
        
        # Expand query with context
        expanded_query = self.expand_query(query, context)
        
        # Search for items
        results = self.knowledge_base.search_items(expanded_query, category, top_k)
        
        # If we have tags and not enough results, try searching by tags
        if tags and len(results) < top_k:
            tag_results = self.knowledge_base.get_items_by_tags(tags, False, top_k - len(results))
            
            # Add tag results that aren't already in the results
            for item in tag_results:
                if item not in results:
                    results.append(item)
                    if len(results) >= top_k:
                        break
        
        return results
    
    def expand_query(self, query: str, context: Dict[str, Any]) -> str:
        """Expand query with contextual information."""
        expanded_terms = [query]
        
        # Add product information if available
        if "product" in context:
            expanded_terms.append(context["product"])
        
        # Add operating system information if available
        if "operating_system" in context:
            expanded_terms.append(context["operating_system"])
        
        # Add version information if available
        if "version" in context:
            expanded_terms.append(f"version {context['version']}")
        
        # Add error code if available
        if "error_code" in context:
            expanded_terms.append(context["error_code"])
        
        # Join terms with spaces
        return " ".join(expanded_terms)
    
    def retrieve_procedure(self, problem_description: str, 
                          context: Dict[str, Any]) -> Optional[DiagnosticProcedure]:
        """Retrieve a diagnostic procedure based on problem description and context."""
        # Expand query with context
        expanded_query = self.expand_query(problem_description, context)
        
        # Search for procedures
        procedures = self.knowledge_base.search_procedures(expanded_query, 1)
        
        return procedures[0] if procedures else None
    
    def retrieve_by_id(self, item_id: str) -> Optional[KnowledgeItem]:
        """Retrieve a knowledge item by ID."""
        return self.knowledge_base.get_item(item_id)
    
    def retrieve_procedure_by_id(self, procedure_id: str) -> Optional[DiagnosticProcedure]:
        """Retrieve a diagnostic procedure by ID."""
        return self.knowledge_base.get_procedure(procedure_id)

class KnowledgeApplicator:
    """Applies knowledge to specific user situations."""
    
    def __init__(self, knowledge_base: KnowledgeBase):
        self.knowledge_base = knowledge_base
    
    def apply_procedure(self, procedure: DiagnosticProcedure, 
                       user_context: Dict[str, Any]) -> DiagnosticProcedure:
        """Customize a procedure for a specific user context."""
        # Create a copy of the procedure
        customized_steps = {}
        
        for step_id, step in procedure.steps.items():
            # Create a copy of the step
            customized_step = DiagnosticStep(
                step_id=step.step_id,
                instruction=self._customize_text(step.instruction, user_context),
                expected_outcome=self._customize_text(step.expected_outcome, user_context),
                possible_outcomes={
                    outcome: self._customize_text(description, user_context)
                    for outcome, description in step.possible_outcomes.items()
                },
                next_steps=step.next_steps.copy(),
                metadata=step.metadata.copy()
            )
            
            customized_steps[step_id] = customized_step
        
        # Create a customized procedure
        customized_procedure = DiagnosticProcedure(
            procedure_id=procedure.procedure_id,
            title=procedure.title,
            description=self._customize_text(procedure.description, user_context),
            initial_step_id=procedure.initial_step_id,
            steps=customized_steps,
            tags=procedure.tags.copy(),
            created_at=procedure.created_at,
            updated_at=procedure.updated_at,
            version=procedure.version,
            metadata=procedure.metadata.copy()
        )
        
        return customized_procedure
    
    def _customize_text(self, text: str, user_context: Dict[str, Any]) -> str:
        """Customize text based on user context."""
        customized = text
        
        # Replace placeholders with context values
        for key, value in user_context.items():
            placeholder = f"{{{key}}}"
            if placeholder in customized:
                customized = customized.replace(placeholder, str(value))
        
        # Handle operating system-specific instructions
        if "operating_system" in user_context:
            os_name = user_context["operating_system"].lower()
            
            # Extract OS-specific instructions
            windows_pattern = r"\[Windows\](.*?)\[/Windows\]"
            mac_pattern = r"\[Mac\](.*?)\[/Mac\]"
            linux_pattern = r"\[Linux\](.*?)\[/Linux\]"
            
            if os_name == "windows":
                # Keep Windows instructions, remove others
                customized = re.sub(windows_pattern, r"\1", customized)
                customized = re.sub(mac_pattern, "", customized)
                customized = re.sub(linux_pattern, "", customized)
            elif os_name == "macos":
                # Keep Mac instructions, remove others
                customized = re.sub(windows_pattern, "", customized)
                customized = re.sub(mac_pattern, r"\1", customized)
                customized = re.sub(linux_pattern, "", customized)
            elif os_name == "linux":
                # Keep Linux instructions, remove others
                customized = re.sub(windows_pattern, "", customized)
                customized = re.sub(mac_pattern, "", customized)
                customized = re.sub(linux_pattern, r"\1", customized)
        
        return customized
    
    def evaluate_solution_applicability(self, solution: KnowledgeItem, 
                                      problem_description: str) -> float:
        """Evaluate how well a solution applies to a described problem."""
        # This is a placeholder for a more sophisticated relevance scoring algorithm
        # In a real implementation, this would use semantic similarity or other NLP techniques
        
        # Simple keyword matching for demonstration
        relevance_score = 0.0
        problem_lower = problem_description.lower()
        
        # Check title relevance
        title_words = set(solution.title.lower().split())
        problem_words = set(problem_lower.split())
        title_overlap = len(title_words.intersection(problem_words))
        if title_overlap > 0:
            relevance_score += 0.3 * (title_overlap / len(title_words))
        
        # Check content relevance (simple keyword matching)
        content_lower = solution.content.lower()
        keyword_matches = sum(1 for word in problem_words if word in content_lower)
        if keyword_matches > 0:
            relevance_score += 0.5 * (keyword_matches / len(problem_words))
        
        # Check tag relevance
        tag_matches = sum(1 for tag in solution.tags if tag.lower() in problem_lower)
        if tag_matches > 0:
            relevance_score += 0.2 * (tag_matches / len(solution.tags))
        
        return min(1.0, relevance_score)
    
    def extract_key_points(self, knowledge_item: KnowledgeItem, 
                          max_points: int = 5) -> List[str]:
        """Extract key points from a knowledge item."""
        # This is a placeholder for a more sophisticated key point extraction algorithm
        # In a real implementation, this would use text summarization or other NLP techniques
        
        # Simple extraction based on formatting for demonstration
        key_points = []
        
        if knowledge_item.format == KnowledgeFormat.MARKDOWN:
            # Extract headers and list items
            lines = knowledge_item.content.split("\n")
            
            for line in lines:
                # Extract headers (level 2 and 3)
                if line.startswith("## "):
                    key_points.append(line[3:].strip())
                elif line.startswith("### "):
                    key_points.append(line[4:].strip())
                
                # Extract list items
                elif line.strip().startswith("- ") or line.strip().startswith("* "):
                    key_points.append(line.strip()[2:].strip())
                
                # Extract numbered list items
                elif re.match(r"^\d+\.\s", line.strip()):
                    key_points.append(re.sub(r"^\d+\.\s", "", line.strip()))
        
        # Limit to max_points
        return key_points[:max_points]
    
    def generate_summary(self, knowledge_items: List[KnowledgeItem]) -> str:
        """Generate a summary from multiple knowledge items."""
        # This is a placeholder for a more sophisticated summarization algorithm
        # In a real implementation, this would use text summarization or other NLP techniques
        
        if not knowledge_items:
            return "No relevant information found."
        
        # Extract titles and key points
        summary_parts = []
        
        for item in knowledge_items:
            summary_parts.append(f"# {item.title}")
            
            key_points = self.extract_key_points(item)
            if key_points:
                summary_parts.append("Key points:")
                for point in key_points:
                    summary_parts.append(f"- {point}")
            
            summary_parts.append("")  # Add blank line between items
        
        return "\n".join(summary_parts)

class KnowledgeEngine:
    """Main class that coordinates knowledge management components."""
    
    def __init__(self, storage_path: Optional[str] = None):
        self.knowledge_base = KnowledgeBase(storage_path)
        self.retriever = KnowledgeRetriever(self.knowledge_base)
        self.applicator = KnowledgeApplicator(self.knowledge_base)
        
        # Load knowledge base if storage path is provided
        if storage_path:
            self.knowledge_base.load_from_storage()
    
    def query(self, query_text: str, context: Dict[str, Any], 
             max_results: int = 5) -> List[KnowledgeItem]:
        """Query the knowledge engine for relevant information."""
        return self.retriever.retrieve(query_text, context, max_results)
    
    def get_diagnostic_procedure(self, problem_description: str, 
                               context: Dict[str, Any]) -> Optional[DiagnosticProcedure]:
        """Get a diagnostic procedure for a problem."""
        procedure = self.retriever.retrieve_procedure(problem_description, context)
        
        if procedure:
            # Customize procedure for user context
            return self.applicator.apply_procedure(procedure, context)
        
        return None
    
    def get_next_diagnostic_step(self, procedure_id: str, current_step_id: str, 
                               outcome: str) -> Optional[DiagnosticStep]:
        """Get the next step in a diagnostic procedure based on the outcome of the current step."""
        procedure = self.knowledge_base.get_procedure(procedure_id)
        if not procedure:
            return None
        
        return procedure.get_next_step(current_step_id, outcome)
    
    def summarize_knowledge(self, query_text: str, context: Dict[str, Any], 
                          max_items: int = 3) -> str:
        """Generate a summary of relevant knowledge."""
        items = self.query(query_text, context, max_items)
        return self.applicator.generate_summary(items)
    
    def add_knowledge_item(self, title: str, content: str, category: KnowledgeCategory, 
                         format: KnowledgeFormat, tags: List[str]) -> str:
        """Add a new knowledge item to the knowledge base."""
        # Generate a unique ID
        item_id = f"{category.value}-{len(self.knowledge_base.items) + 1:03d}"
        
        # Create the knowledge item
        item = KnowledgeItem(
            item_id=item_id,
            title=title,
            content=content,
            category=category,
            format=format,
            tags=tags,
            created_at=datetime.datetime.now(),
            updated_at=datetime.datetime.now(),
            version="1.0"
        )
        
        # Add to knowledge base
        success = self.knowledge_base.add_item(item)
        
        # Save to storage if available
        if success and self.knowledge_base.storage_path:
            self.knowledge_base.save_to_storage()
        
        return item_id if success else ""
    
    def update_knowledge_item(self, item_id: str, title: Optional[str] = None, 
                            content: Optional[str] = None, 
                            tags: Optional[List[str]] = None) -> bool:
        """Update an existing knowledge item."""
        # Get the existing item
        item = self.knowledge_base.get_item(item_id)
        if not item:
            return False
        
        # Update fields
        if title is not None:
            item.title = title
        
        if content is not None:
            item.content = content
        
        if tags is not None:
            item.tags = tags
        
        # Update timestamp and version
        item.updated_at = datetime.datetime.now()
        
        # Version numbering (simple increment)
        version_parts = item.version.split(".")
        if len(version_parts) >= 2:
            minor_version = int(version_parts[-1]) + 1
            version_parts[-1] = str(minor_version)
            item.version = ".".join(version_parts)
        
        # Update in knowledge base
        success = self.knowledge_base.update_item(item)
        
        # Save to storage if available
        if success and self.knowledge_base.storage_path:
            self.knowledge_base.save_to_storage()
        
        return success
    
    def delete_knowledge_item(self, item_id: str) -> bool:
        """Delete a knowledge item."""
        success = self.knowledge_base.delete_item(item_id)
        
        # Save to storage if available
        if success and self.knowledge_base.storage_path:
            self.knowledge_base.save_to_storage()
        
        return success
    
    def save(self) -> bool:
        """Save the knowledge base to storage."""
        if not self.knowledge_base.storage_path:
            return False
        
        return self.knowledge_base.save_to_storage()
    
    def load(self) -> bool:
        """Load the knowledge base from storage."""
        if not self.knowledge_base.storage_path:
            return False
        
        return self.knowledge_base.load_from_storage()
