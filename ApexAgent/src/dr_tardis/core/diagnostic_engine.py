"""
Diagnostic Engine for Dr. TARDIS

This module implements the problem analysis, troubleshooting workflow,
and solution management components of Dr. TARDIS as defined in the architecture.
"""

import datetime
import json
import os
import uuid
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple, Set, Union

class ProblemSeverity(Enum):
    """Severity levels for problems."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ProblemCategory(Enum):
    """Categories of problems that can be diagnosed."""
    INSTALLATION = "installation"
    CONFIGURATION = "configuration"
    CONNECTIVITY = "connectivity"
    PERFORMANCE = "performance"
    SECURITY = "security"
    ACCOUNT = "account"
    DATA = "data"
    COMPATIBILITY = "compatibility"
    FEATURE = "feature"
    UNKNOWN = "unknown"

class DiagnosticStepType(Enum):
    """Types of diagnostic steps."""
    INFORMATION_GATHERING = "information_gathering"
    VERIFICATION = "verification"
    ACTION = "action"
    DECISION = "decision"
    RESOLUTION = "resolution"
    ESCALATION = "escalation"

class DiagnosticStepStatus(Enum):
    """Status of a diagnostic step."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

class ProblemAnalysis:
    """Represents the analysis of a user problem."""
    
    def __init__(
        self,
        problem_id: str,
        description: str,
        categories: List[ProblemCategory],
        severity: ProblemSeverity,
        potential_causes: List[str],
        confidence: float,
        created_at: datetime.datetime,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.problem_id = problem_id
        self.description = description
        self.categories = categories
        self.severity = severity
        self.potential_causes = potential_causes
        self.confidence = confidence
        self.created_at = created_at
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the problem analysis to a dictionary."""
        return {
            "problem_id": self.problem_id,
            "description": self.description,
            "categories": [category.value for category in self.categories],
            "severity": self.severity.value,
            "potential_causes": self.potential_causes,
            "confidence": self.confidence,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProblemAnalysis':
        """Create a problem analysis from a dictionary."""
        return cls(
            problem_id=data["problem_id"],
            description=data["description"],
            categories=[ProblemCategory(category) for category in data["categories"]],
            severity=ProblemSeverity(data["severity"]),
            potential_causes=data["potential_causes"],
            confidence=data["confidence"],
            created_at=datetime.datetime.fromisoformat(data["created_at"]),
            metadata=data.get("metadata", {})
        )

class DiagnosticStep:
    """Represents a single step in a diagnostic workflow."""
    
    def __init__(
        self,
        step_id: str,
        title: str,
        description: str,
        step_type: DiagnosticStepType,
        expected_outcome: str,
        possible_outcomes: Dict[str, str],
        next_steps: Dict[str, str],
        status: DiagnosticStepStatus = DiagnosticStepStatus.PENDING,
        result: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.step_id = step_id
        self.title = title
        self.description = description
        self.step_type = step_type
        self.expected_outcome = expected_outcome
        self.possible_outcomes = possible_outcomes
        self.next_steps = next_steps
        self.status = status
        self.result = result
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the diagnostic step to a dictionary."""
        return {
            "step_id": self.step_id,
            "title": self.title,
            "description": self.description,
            "step_type": self.step_type.value,
            "expected_outcome": self.expected_outcome,
            "possible_outcomes": self.possible_outcomes,
            "next_steps": self.next_steps,
            "status": self.status.value,
            "result": self.result,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DiagnosticStep':
        """Create a diagnostic step from a dictionary."""
        return cls(
            step_id=data["step_id"],
            title=data["title"],
            description=data["description"],
            step_type=DiagnosticStepType(data["step_type"]),
            expected_outcome=data["expected_outcome"],
            possible_outcomes=data["possible_outcomes"],
            next_steps=data["next_steps"],
            status=DiagnosticStepStatus(data["status"]),
            result=data.get("result"),
            metadata=data.get("metadata", {})
        )

class DiagnosticWorkflow:
    """Represents a diagnostic workflow with multiple steps."""
    
    def __init__(
        self,
        workflow_id: str,
        problem_analysis: ProblemAnalysis,
        steps: Dict[str, DiagnosticStep],
        initial_step_id: str,
        current_step_id: Optional[str] = None,
        created_at: datetime.datetime = None,
        updated_at: datetime.datetime = None,
        completed_steps: List[str] = None,
        status: str = "active",
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.workflow_id = workflow_id
        self.problem_analysis = problem_analysis
        self.steps = steps
        self.initial_step_id = initial_step_id
        self.current_step_id = current_step_id or initial_step_id
        self.created_at = created_at or datetime.datetime.now()
        self.updated_at = updated_at or datetime.datetime.now()
        self.completed_steps = completed_steps or []
        self.status = status
        self.metadata = metadata or {}
    
    def get_current_step(self) -> Optional[DiagnosticStep]:
        """Get the current step in the workflow."""
        if not self.current_step_id:
            return None
        
        return self.steps.get(self.current_step_id)
    
    def get_step(self, step_id: str) -> Optional[DiagnosticStep]:
        """Get a step by ID."""
        return self.steps.get(step_id)
    
    def advance_to_next_step(self, outcome: str) -> Optional[DiagnosticStep]:
        """Advance to the next step based on the outcome of the current step."""
        current_step = self.get_current_step()
        if not current_step:
            return None
        
        # Mark current step as completed
        current_step.status = DiagnosticStepStatus.COMPLETED
        current_step.result = outcome
        
        if current_step.step_id not in self.completed_steps:
            self.completed_steps.append(current_step.step_id)
        
        # Get next step ID based on outcome
        next_step_id = current_step.next_steps.get(outcome)
        if not next_step_id:
            # No next step for this outcome
            return None
        
        # Update current step ID
        self.current_step_id = next_step_id
        self.updated_at = datetime.datetime.now()
        
        # Get next step
        next_step = self.get_step(next_step_id)
        if next_step:
            next_step.status = DiagnosticStepStatus.IN_PROGRESS
        
        return next_step
    
    def is_complete(self) -> bool:
        """Check if the workflow is complete."""
        current_step = self.get_current_step()
        if not current_step:
            return True
        
        # If current step has no next steps, it's the final step
        return len(current_step.next_steps) == 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the diagnostic workflow to a dictionary."""
        return {
            "workflow_id": self.workflow_id,
            "problem_analysis": self.problem_analysis.to_dict(),
            "steps": {step_id: step.to_dict() for step_id, step in self.steps.items()},
            "initial_step_id": self.initial_step_id,
            "current_step_id": self.current_step_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "completed_steps": self.completed_steps,
            "status": self.status,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DiagnosticWorkflow':
        """Create a diagnostic workflow from a dictionary."""
        problem_analysis = ProblemAnalysis.from_dict(data["problem_analysis"])
        steps = {
            step_id: DiagnosticStep.from_dict(step_data)
            for step_id, step_data in data["steps"].items()
        }
        
        return cls(
            workflow_id=data["workflow_id"],
            problem_analysis=problem_analysis,
            steps=steps,
            initial_step_id=data["initial_step_id"],
            current_step_id=data["current_step_id"],
            created_at=datetime.datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.datetime.fromisoformat(data["updated_at"]),
            completed_steps=data["completed_steps"],
            status=data["status"],
            metadata=data.get("metadata", {})
        )

class Solution:
    """Represents a solution to a problem."""
    
    def __init__(
        self,
        solution_id: str,
        title: str,
        description: str,
        steps: List[str],
        applicable_problems: List[str],
        effectiveness_rating: float,
        complexity: int,
        created_at: datetime.datetime,
        updated_at: datetime.datetime,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.solution_id = solution_id
        self.title = title
        self.description = description
        self.steps = steps
        self.applicable_problems = applicable_problems
        self.effectiveness_rating = effectiveness_rating
        self.complexity = complexity
        self.created_at = created_at
        self.updated_at = updated_at
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the solution to a dictionary."""
        return {
            "solution_id": self.solution_id,
            "title": self.title,
            "description": self.description,
            "steps": self.steps,
            "applicable_problems": self.applicable_problems,
            "effectiveness_rating": self.effectiveness_rating,
            "complexity": self.complexity,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Solution':
        """Create a solution from a dictionary."""
        return cls(
            solution_id=data["solution_id"],
            title=data["title"],
            description=data["description"],
            steps=data["steps"],
            applicable_problems=data["applicable_problems"],
            effectiveness_rating=data["effectiveness_rating"],
            complexity=data["complexity"],
            created_at=datetime.datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.datetime.fromisoformat(data["updated_at"]),
            metadata=data.get("metadata", {})
        )

class ProblemAnalyzer:
    """Analyzes and categorizes user issues."""
    
    def __init__(self):
        # Initialize problem analysis components
        self.symptom_patterns = self._initialize_symptom_patterns()
    
    def _initialize_symptom_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize patterns for symptom recognition."""
        # This is a placeholder for actual symptom patterns
        # In a real implementation, this would be more sophisticated
        
        return {
            "installation_failure": {
                "keywords": ["install", "setup", "failed", "error", "can't install"],
                "category": ProblemCategory.INSTALLATION,
                "severity": ProblemSeverity.HIGH
            },
            "connection_issue": {
                "keywords": ["connect", "connection", "network", "offline", "can't connect"],
                "category": ProblemCategory.CONNECTIVITY,
                "severity": ProblemSeverity.HIGH
            },
            "slow_performance": {
                "keywords": ["slow", "lag", "performance", "freezing", "unresponsive"],
                "category": ProblemCategory.PERFORMANCE,
                "severity": ProblemSeverity.MEDIUM
            },
            "login_problem": {
                "keywords": ["login", "password", "account", "authentication", "can't log in"],
                "category": ProblemCategory.ACCOUNT,
                "severity": ProblemSeverity.HIGH
            },
            "data_loss": {
                "keywords": ["lost", "missing", "data", "file", "deleted"],
                "category": ProblemCategory.DATA,
                "severity": ProblemSeverity.CRITICAL
            },
            "feature_not_working": {
                "keywords": ["feature", "function", "not working", "broken", "doesn't work"],
                "category": ProblemCategory.FEATURE,
                "severity": ProblemSeverity.MEDIUM
            },
            "compatibility_issue": {
                "keywords": ["compatible", "version", "support", "old", "new"],
                "category": ProblemCategory.COMPATIBILITY,
                "severity": ProblemSeverity.MEDIUM
            },
            "security_concern": {
                "keywords": ["security", "breach", "hack", "virus", "malware"],
                "category": ProblemCategory.SECURITY,
                "severity": ProblemSeverity.CRITICAL
            },
            "configuration_problem": {
                "keywords": ["config", "setting", "preference", "option", "setup"],
                "category": ProblemCategory.CONFIGURATION,
                "severity": ProblemSeverity.MEDIUM
            }
        }
    
    def analyze_problem(self, description: str, 
                       context: Dict[str, Any]) -> ProblemAnalysis:
        """Analyze a problem description to identify causes and categories."""
        # Generate a unique problem ID
        problem_id = str(uuid.uuid4())
        
        # Identify categories and severity
        categories, severity, confidence = self._identify_categories_and_severity(description)
        
        # Identify potential causes
        potential_causes = self._identify_potential_causes(description, categories, context)
        
        # Create problem analysis
        return ProblemAnalysis(
            problem_id=problem_id,
            description=description,
            categories=categories,
            severity=severity,
            potential_causes=potential_causes,
            confidence=confidence,
            created_at=datetime.datetime.now(),
            metadata={"context": context}
        )
    
    def _identify_categories_and_severity(self, description: str) -> Tuple[List[ProblemCategory], ProblemSeverity, float]:
        """Identify problem categories and severity from description."""
        description_lower = description.lower()
        
        # Count matches for each symptom pattern
        matches = {}
        for symptom, pattern in self.symptom_patterns.items():
            match_count = sum(1 for keyword in pattern["keywords"] if keyword in description_lower)
            if match_count > 0:
                matches[symptom] = match_count
        
        # If no matches, return unknown category
        if not matches:
            return [ProblemCategory.UNKNOWN], ProblemSeverity.MEDIUM, 0.5
        
        # Sort matches by count
        sorted_matches = sorted(matches.items(), key=lambda x: x[1], reverse=True)
        
        # Get top categories
        top_categories = []
        for symptom, _ in sorted_matches[:2]:  # Get top 2 categories
            category = self.symptom_patterns[symptom]["category"]
            if category not in top_categories:
                top_categories.append(category)
        
        # If still no categories, return unknown
        if not top_categories:
            return [ProblemCategory.UNKNOWN], ProblemSeverity.MEDIUM, 0.5
        
        # Determine severity (use highest severity from matched categories)
        severity = ProblemSeverity.LOW
        for symptom, _ in sorted_matches:
            pattern_severity = self.symptom_patterns[symptom]["severity"]
            if pattern_severity.value > severity.value:
                severity = pattern_severity
        
        # Calculate confidence based on match quality
        top_match_count = sorted_matches[0][1]
        total_words = len(description_lower.split())
        confidence = min(0.9, top_match_count / max(5, total_words) + 0.5)
        
        return top_categories, severity, confidence
    
    def _identify_potential_causes(self, description: str, 
                                 categories: List[ProblemCategory], 
                                 context: Dict[str, Any]) -> List[str]:
        """Identify potential causes based on description and categories."""
        # This is a placeholder for actual cause identification logic
        # In a real implementation, this would use more sophisticated analysis
        
        causes = []
        description_lower = description.lower()
        
        # Add causes based on categories
        for category in categories:
            if category == ProblemCategory.INSTALLATION:
                causes.append("Incomplete or corrupted installation")
                causes.append("Missing dependencies")
                if "permission" in description_lower:
                    causes.append("Insufficient permissions")
            
            elif category == ProblemCategory.CONNECTIVITY:
                causes.append("Network connection issues")
                causes.append("Firewall blocking connection")
                if "server" in description_lower:
                    causes.append("Server may be down or unreachable")
            
            elif category == ProblemCategory.PERFORMANCE:
                causes.append("Insufficient system resources")
                causes.append("Background processes consuming resources")
                if "memory" in description_lower:
                    causes.append("Memory leak or insufficient RAM")
            
            elif category == ProblemCategory.ACCOUNT:
                causes.append("Incorrect login credentials")
                causes.append("Account may be locked or disabled")
                if "password" in description_lower:
                    causes.append("Password may have expired")
            
            elif category == ProblemCategory.DATA:
                causes.append("Data corruption")
                causes.append("Accidental deletion")
                if "backup" in description_lower:
                    causes.append("Backup failure or corruption")
            
            elif category == ProblemCategory.FEATURE:
                causes.append("Feature may require activation")
                causes.append("Feature may not be available in current version")
                if "update" in description_lower:
                    causes.append("Feature may require an update")
            
            elif category == ProblemCategory.COMPATIBILITY:
                causes.append("Incompatible software version")
                causes.append("Incompatible operating system")
                if "driver" in description_lower:
                    causes.append("Outdated or incompatible drivers")
            
            elif category == ProblemCategory.SECURITY:
                causes.append("Security settings may be blocking functionality")
                causes.append("Potential security breach")
                if "permission" in description_lower:
                    causes.append("Insufficient security permissions")
            
            elif category == ProblemCategory.CONFIGURATION:
                causes.append("Incorrect configuration settings")
                causes.append("Configuration file corruption")
                if "default" in description_lower:
                    causes.append("Default settings may have been reset")
        
        # Add causes based on context
        if context.get("recent_update", False):
            causes.append("Recent software update may have caused issues")
        
        if context.get("new_hardware", False):
            causes.append("New hardware may not be properly configured")
        
        # Limit to top 5 causes
        return causes[:5]
    
    def refine_analysis(self, initial_analysis: ProblemAnalysis, 
                       additional_info: str) -> ProblemAnalysis:
        """Refine analysis based on additional information."""
        # Create a new analysis with the same problem ID
        refined_categories = initial_analysis.categories.copy()
        refined_causes = initial_analysis.potential_causes.copy()
        
        # Extract context from initial analysis
        context = initial_analysis.metadata.get("context", {}).copy()
        
        # Update description
        refined_description = f"{initial_analysis.description}\nAdditional info: {additional_info}"
        
        # Analyze additional info for new categories
        additional_categories, additional_severity, additional_confidence = self._identify_categories_and_severity(additional_info)
        
        # Add new categories if they're not already included
        for category in additional_categories:
            if category not in refined_categories and category != ProblemCategory.UNKNOWN:
                refined_categories.append(category)
        
        # Determine new severity (use highest severity)
        refined_severity = initial_analysis.severity
        if additional_severity.value > refined_severity.value:
            refined_severity = additional_severity
        
        # Calculate new confidence
        # If additional info increases confidence, weight it more heavily
        if additional_confidence > initial_analysis.confidence:
            refined_confidence = (initial_analysis.confidence + additional_confidence * 2) / 3
        else:
            refined_confidence = (initial_analysis.confidence * 2 + additional_confidence) / 3
        
        # Update potential causes
        additional_causes = self._identify_potential_causes(additional_info, additional_categories, context)
        
        # Add new causes if they're not already included
        for cause in additional_causes:
            if cause not in refined_causes:
                refined_causes.append(cause)
        
        # Limit to top 5 causes
        refined_causes = refined_causes[:5]
        
        # Create refined analysis
        return ProblemAnalysis(
            problem_id=initial_analysis.problem_id,
            description=refined_description,
            categories=refined_categories,
            severity=refined_severity,
            potential_causes=refined_causes,
            confidence=refined_confidence,
            created_at=initial_analysis.created_at,
            metadata=initial_analysis.metadata
        )

class TroubleshootingWorkflowEngine:
    """Manages diagnostic procedures and workflows."""
    
    def __init__(self):
        # Initialize workflow components
        self.workflow_templates = self._initialize_workflow_templates()
    
    def _initialize_workflow_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize workflow templates for different problem categories."""
        # This is a placeholder for actual workflow templates
        # In a real implementation, these would be more sophisticated
        
        templates = {}
        
        # Template for connectivity issues
        connectivity_steps = {
            "conn-step-1": {
                "title": "Check Internet Connection",
                "description": "Verify that your device has an active internet connection.",
                "step_type": DiagnosticStepType.VERIFICATION,
                "expected_outcome": "Internet connection is working",
                "possible_outcomes": {
                    "connected": "Internet is working",
                    "disconnected": "No internet connection"
                },
                "next_steps": {
                    "connected": "conn-step-2",
                    "disconnected": "conn-step-1a"
                }
            },
            "conn-step-1a": {
                "title": "Restore Internet Connection",
                "description": "Try to restore your internet connection by checking your router or contacting your ISP.",
                "step_type": DiagnosticStepType.ACTION,
                "expected_outcome": "Internet connection is restored",
                "possible_outcomes": {
                    "restored": "Internet connection restored",
                    "still_disconnected": "Still no internet connection"
                },
                "next_steps": {
                    "restored": "conn-step-2",
                    "still_disconnected": "conn-step-escalation"
                }
            },
            "conn-step-2": {
                "title": "Check Server Status",
                "description": "Check if the service servers are operational.",
                "step_type": DiagnosticStepType.VERIFICATION,
                "expected_outcome": "Servers are operational",
                "possible_outcomes": {
                    "operational": "Servers are operational",
                    "outage": "Server outage detected"
                },
                "next_steps": {
                    "operational": "conn-step-3",
                    "outage": "conn-step-2a"
                }
            },
            "conn-step-2a": {
                "title": "Wait for Server Restoration",
                "description": "The service is experiencing a server outage. Please wait for the servers to be restored.",
                "step_type": DiagnosticStepType.ACTION,
                "expected_outcome": "User understands the situation",
                "possible_outcomes": {
                    "understood": "User will wait for restoration"
                },
                "next_steps": {
                    "understood": "conn-step-resolution-outage"
                }
            },
            "conn-step-3": {
                "title": "Check Firewall Settings",
                "description": "Verify that your firewall is not blocking the application.",
                "step_type": DiagnosticStepType.VERIFICATION,
                "expected_outcome": "Firewall is not blocking the application",
                "possible_outcomes": {
                    "not_blocked": "Firewall is not blocking",
                    "blocked": "Firewall is blocking",
                    "unsure": "Unable to determine firewall status"
                },
                "next_steps": {
                    "not_blocked": "conn-step-4",
                    "blocked": "conn-step-3a",
                    "unsure": "conn-step-3b"
                }
            },
            "conn-step-3a": {
                "title": "Configure Firewall",
                "description": "Add the application to your firewall's allowed applications list.",
                "step_type": DiagnosticStepType.ACTION,
                "expected_outcome": "Application is allowed through firewall",
                "possible_outcomes": {
                    "configured": "Firewall configured successfully",
                    "failed": "Failed to configure firewall"
                },
                "next_steps": {
                    "configured": "conn-step-4",
                    "failed": "conn-step-escalation"
                }
            },
            "conn-step-3b": {
                "title": "Temporarily Disable Firewall",
                "description": "Temporarily disable your firewall to test if it's causing the issue.",
                "step_type": DiagnosticStepType.ACTION,
                "expected_outcome": "Firewall is temporarily disabled for testing",
                "possible_outcomes": {
                    "disabled": "Firewall temporarily disabled",
                    "cannot_disable": "Cannot disable firewall"
                },
                "next_steps": {
                    "disabled": "conn-step-3c",
                    "cannot_disable": "conn-step-4"
                }
            },
            "conn-step-3c": {
                "title": "Test Connection with Firewall Disabled",
                "description": "Test the application connection with the firewall disabled.",
                "step_type": DiagnosticStepType.VERIFICATION,
                "expected_outcome": "Connection works with firewall disabled",
                "possible_outcomes": {
                    "works": "Connection works with firewall disabled",
                    "still_fails": "Connection still fails with firewall disabled"
                },
                "next_steps": {
                    "works": "conn-step-3a",
                    "still_fails": "conn-step-4"
                }
            },
            "conn-step-4": {
                "title": "Check Proxy Settings",
                "description": "Verify that your proxy settings are correctly configured.",
                "step_type": DiagnosticStepType.VERIFICATION,
                "expected_outcome": "Proxy settings are correct",
                "possible_outcomes": {
                    "correct": "Proxy settings are correct",
                    "incorrect": "Proxy settings are incorrect",
                    "no_proxy": "Not using a proxy"
                },
                "next_steps": {
                    "correct": "conn-step-5",
                    "incorrect": "conn-step-4a",
                    "no_proxy": "conn-step-5"
                }
            },
            "conn-step-4a": {
                "title": "Configure Proxy Settings",
                "description": "Update your proxy settings to the correct configuration.",
                "step_type": DiagnosticStepType.ACTION,
                "expected_outcome": "Proxy settings are updated",
                "possible_outcomes": {
                    "updated": "Proxy settings updated",
                    "failed": "Failed to update proxy settings"
                },
                "next_steps": {
                    "updated": "conn-step-5",
                    "failed": "conn-step-escalation"
                }
            },
            "conn-step-5": {
                "title": "Restart Application",
                "description": "Close and restart the application to apply any changes.",
                "step_type": DiagnosticStepType.ACTION,
                "expected_outcome": "Application is restarted",
                "possible_outcomes": {
                    "restarted": "Application restarted",
                    "failed": "Failed to restart application"
                },
                "next_steps": {
                    "restarted": "conn-step-6",
                    "failed": "conn-step-escalation"
                }
            },
            "conn-step-6": {
                "title": "Test Connection",
                "description": "Test if the connection issue is resolved.",
                "step_type": DiagnosticStepType.VERIFICATION,
                "expected_outcome": "Connection is working",
                "possible_outcomes": {
                    "working": "Connection is working",
                    "still_failing": "Connection is still failing"
                },
                "next_steps": {
                    "working": "conn-step-resolution-success",
                    "still_failing": "conn-step-escalation"
                }
            },
            "conn-step-resolution-success": {
                "title": "Connection Issue Resolved",
                "description": "The connection issue has been successfully resolved.",
                "step_type": DiagnosticStepType.RESOLUTION,
                "expected_outcome": "User confirms issue is resolved",
                "possible_outcomes": {},
                "next_steps": {}
            },
            "conn-step-resolution-outage": {
                "title": "Server Outage Identified",
                "description": "The issue is due to a server outage. Please try again later.",
                "step_type": DiagnosticStepType.RESOLUTION,
                "expected_outcome": "User understands the issue is due to server outage",
                "possible_outcomes": {},
                "next_steps": {}
            },
            "conn-step-escalation": {
                "title": "Escalate to Support",
                "description": "This issue requires additional support. Please contact our support team.",
                "step_type": DiagnosticStepType.ESCALATION,
                "expected_outcome": "User contacts support for further assistance",
                "possible_outcomes": {},
                "next_steps": {}
            }
        }
        
        templates["connectivity"] = {
            "initial_step_id": "conn-step-1",
            "steps": connectivity_steps
        }
        
        # Add more templates for other categories here
        
        return templates
    
    def create_workflow(self, problem_analysis: ProblemAnalysis) -> DiagnosticWorkflow:
        """Create a diagnostic workflow for a specific problem."""
        # Generate a unique workflow ID
        workflow_id = str(uuid.uuid4())
        
        # Determine which template to use based on problem categories
        template_key = None
        for category in problem_analysis.categories:
            if category == ProblemCategory.CONNECTIVITY:
                template_key = "connectivity"
                break
            # Add more category mappings here
        
        # If no specific template, use a generic one
        if not template_key:
            template_key = "connectivity"  # Use connectivity as default for now
        
        # Get template
        template = self.workflow_templates.get(template_key)
        
        # Create steps from template
        steps = {}
        for step_id, step_data in template["steps"].items():
            steps[step_id] = DiagnosticStep(
                step_id=step_id,
                title=step_data["title"],
                description=step_data["description"],
                step_type=DiagnosticStepType(step_data["step_type"]),
                expected_outcome=step_data["expected_outcome"],
                possible_outcomes=step_data["possible_outcomes"],
                next_steps=step_data["next_steps"],
                status=DiagnosticStepStatus.PENDING
            )
        
        # Set initial step to in progress
        initial_step_id = template["initial_step_id"]
        if initial_step_id in steps:
            steps[initial_step_id].status = DiagnosticStepStatus.IN_PROGRESS
        
        # Create workflow
        return DiagnosticWorkflow(
            workflow_id=workflow_id,
            problem_analysis=problem_analysis,
            steps=steps,
            initial_step_id=initial_step_id,
            current_step_id=initial_step_id,
            created_at=datetime.datetime.now(),
            updated_at=datetime.datetime.now(),
            completed_steps=[],
            status="active",
            metadata={}
        )
    
    def get_next_step(self, workflow: DiagnosticWorkflow, 
                     current_results: Dict[str, Any]) -> Optional[DiagnosticStep]:
        """Determine the next diagnostic step based on current results."""
        current_step = workflow.get_current_step()
        if not current_step:
            return None
        
        # Get outcome from results
        outcome = current_results.get("outcome")
        if not outcome:
            return current_step  # No outcome provided, stay on current step
        
        # Advance to next step
        return workflow.advance_to_next_step(outcome)
    
    def branch_workflow(self, workflow: DiagnosticWorkflow, 
                       branch_condition: str) -> DiagnosticWorkflow:
        """Create a new branch in the workflow based on a condition."""
        # This is a placeholder for actual workflow branching logic
        # In a real implementation, this would create a custom branch
        
        # For now, just return the original workflow
        return workflow

class SolutionManager:
    """Handles solution delivery and verification."""
    
    def __init__(self):
        # Initialize solution management components
        self.solutions = self._initialize_solutions()
    
    def _initialize_solutions(self) -> Dict[str, Solution]:
        """Initialize solution database."""
        # This is a placeholder for actual solution database
        # In a real implementation, this would be loaded from storage
        
        solutions = {}
        
        # Solution for firewall blocking connection
        solutions["firewall-blocking"] = Solution(
            solution_id="firewall-blocking",
            title="Configure Firewall to Allow Application",
            description="This solution helps you configure your firewall to allow the application to connect to the internet.",
            steps=[
                "Open your firewall settings",
                "Add the application to the allowed applications list",
                "Save the changes and restart the application"
            ],
            applicable_problems=["connectivity-firewall"],
            effectiveness_rating=0.9,
            complexity=2,
            created_at=datetime.datetime.now(),
            updated_at=datetime.datetime.now()
        )
        
        # Solution for proxy settings
        solutions["proxy-settings"] = Solution(
            solution_id="proxy-settings",
            title="Configure Proxy Settings",
            description="This solution helps you configure the correct proxy settings for the application.",
            steps=[
                "Open the application settings",
                "Navigate to the network or proxy settings section",
                "Enter the correct proxy server address and port",
                "Save the changes and restart the application"
            ],
            applicable_problems=["connectivity-proxy"],
            effectiveness_rating=0.85,
            complexity=3,
            created_at=datetime.datetime.now(),
            updated_at=datetime.datetime.now()
        )
        
        # Add more solutions here
        
        return solutions
    
    def select_solution(self, problem_analysis: ProblemAnalysis) -> Optional[Solution]:
        """Select an appropriate solution for an identified problem."""
        # This is a placeholder for actual solution selection logic
        # In a real implementation, this would use more sophisticated matching
        
        # For now, just return a solution based on problem category
        for category in problem_analysis.categories:
            if category == ProblemCategory.CONNECTIVITY:
                # Check for specific connectivity issues in the description
                if "firewall" in problem_analysis.description.lower():
                    return self.solutions.get("firewall-blocking")
                elif "proxy" in problem_analysis.description.lower():
                    return self.solutions.get("proxy-settings")
        
        # No matching solution found
        return None
    
    def customize_solution(self, solution: Solution, 
                         context: Dict[str, Any]) -> Solution:
        """Customize a solution based on user context."""
        # This is a placeholder for actual solution customization logic
        # In a real implementation, this would adapt the solution to the user's context
        
        # For now, just return the original solution
        return solution
    
    def verify_resolution(self, problem_analysis: ProblemAnalysis, 
                         solution: Solution, 
                         verification_data: Dict[str, Any]) -> bool:
        """Verify that a problem has been resolved."""
        # This is a placeholder for actual resolution verification logic
        # In a real implementation, this would check if the problem is actually resolved
        
        # For now, just return the verification result from the data
        return verification_data.get("resolved", False)

class DiagnosticEngine:
    """Main class that coordinates diagnostic components."""
    
    def __init__(self):
        self.problem_analyzer = ProblemAnalyzer()
        self.workflow_engine = TroubleshootingWorkflowEngine()
        self.solution_manager = SolutionManager()
        self.active_workflows = {}
    
    def analyze_problem(self, description: str, context: Dict[str, Any]) -> ProblemAnalysis:
        """Analyze a problem description."""
        return self.problem_analyzer.analyze_problem(description, context)
    
    def refine_analysis(self, problem_id: str, additional_info: str) -> Optional[ProblemAnalysis]:
        """Refine an existing problem analysis with additional information."""
        # Find the workflow with this problem ID
        for workflow_id, workflow in self.active_workflows.items():
            if workflow.problem_analysis.problem_id == problem_id:
                refined_analysis = self.problem_analyzer.refine_analysis(
                    workflow.problem_analysis, additional_info
                )
                
                # Update the workflow with the refined analysis
                workflow.problem_analysis = refined_analysis
                return refined_analysis
        
        return None
    
    def create_diagnostic_workflow(self, problem_analysis: ProblemAnalysis) -> str:
        """Create a diagnostic workflow for a problem and return the workflow ID."""
        workflow = self.workflow_engine.create_workflow(problem_analysis)
        self.active_workflows[workflow.workflow_id] = workflow
        return workflow.workflow_id
    
    def get_current_step(self, workflow_id: str) -> Optional[DiagnosticStep]:
        """Get the current step in a diagnostic workflow."""
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            return None
        
        return workflow.get_current_step()
    
    def advance_workflow(self, workflow_id: str, outcome: str) -> Optional[DiagnosticStep]:
        """Advance a workflow to the next step based on the outcome of the current step."""
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            return None
        
        return workflow.advance_to_next_step(outcome)
    
    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get the status of a diagnostic workflow."""
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            return {"error": "Workflow not found"}
        
        current_step = workflow.get_current_step()
        
        return {
            "workflow_id": workflow.workflow_id,
            "problem_id": workflow.problem_analysis.problem_id,
            "status": workflow.status,
            "completed_steps": len(workflow.completed_steps),
            "total_steps": len(workflow.steps),
            "current_step": current_step.step_id if current_step else None,
            "is_complete": workflow.is_complete()
        }
    
    def select_solution(self, workflow_id: str) -> Optional[Solution]:
        """Select an appropriate solution for a workflow."""
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            return None
        
        return self.solution_manager.select_solution(workflow.problem_analysis)
    
    def customize_solution(self, solution: Solution, 
                         context: Dict[str, Any]) -> Solution:
        """Customize a solution based on user context."""
        return self.solution_manager.customize_solution(solution, context)
    
    def verify_resolution(self, workflow_id: str, 
                         verification_data: Dict[str, Any]) -> bool:
        """Verify that a problem has been resolved."""
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            return False
        
        solution = self.solution_manager.select_solution(workflow.problem_analysis)
        if not solution:
            return False
        
        resolved = self.solution_manager.verify_resolution(
            workflow.problem_analysis, solution, verification_data
        )
        
        if resolved:
            # Mark workflow as complete
            workflow.status = "completed"
        
        return resolved
    
    def save_workflow(self, workflow_id: str, storage_path: str) -> bool:
        """Save a workflow to storage."""
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            return False
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(storage_path, exist_ok=True)
            
            # Save workflow
            with open(os.path.join(storage_path, f"{workflow_id}.json"), "w") as f:
                json.dump(workflow.to_dict(), f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving workflow: {e}")
            return False
    
    def load_workflow(self, workflow_id: str, storage_path: str) -> bool:
        """Load a workflow from storage."""
        try:
            # Load workflow
            with open(os.path.join(storage_path, f"{workflow_id}.json"), "r") as f:
                workflow_data = json.load(f)
            
            # Create workflow
            workflow = DiagnosticWorkflow.from_dict(workflow_data)
            
            # Add to active workflows
            self.active_workflows[workflow_id] = workflow
            
            return True
        except Exception as e:
            print(f"Error loading workflow: {e}")
            return False
    
    def get_all_workflows(self) -> List[str]:
        """Get all active workflow IDs."""
        return list(self.active_workflows.keys())
    
    def close_workflow(self, workflow_id: str) -> bool:
        """Close and remove a workflow."""
        if workflow_id in self.active_workflows:
            del self.active_workflows[workflow_id]
            return True
        
        return False
"""
