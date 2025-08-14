#!/usr/bin/env python3
"""
User Onboarding and Education System for ApexAgent

This module provides a comprehensive framework for user onboarding,
interactive tutorials, contextual help, and educational resources
to help users effectively utilize the ApexAgent platform.
"""

import os
import sys
import json
import uuid
import logging
import threading
import time
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union, Callable, Set, TypeVar
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
import queue

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("onboarding.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("onboarding")

# Type variables for generic functions
T = TypeVar("T")

class OnboardingStage(Enum):
    """Enumeration of onboarding stages."""
    WELCOME = "welcome"
    BASICS = "basics"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"
    COMPLETED = "completed"

class UserExperienceLevel(Enum):
    """Enumeration of user experience levels."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class TutorialType(Enum):
    """Enumeration of tutorial types."""
    INTERACTIVE = "interactive"
    VIDEO = "video"
    DOCUMENT = "document"
    WALKTHROUGH = "walkthrough"
    QUIZ = "quiz"

class TutorialCategory(Enum):
    """Enumeration of tutorial categories."""
    GETTING_STARTED = "getting_started"
    BASIC_FEATURES = "basic_features"
    ADVANCED_FEATURES = "advanced_features"
    BEST_PRACTICES = "best_practices"
    TROUBLESHOOTING = "troubleshooting"
    INTEGRATION = "integration"
    CUSTOMIZATION = "customization"
    ADMINISTRATION = "administration"

class HelpContextType(Enum):
    """Enumeration of help context types."""
    FEATURE = "feature"
    ERROR = "error"
    CONCEPT = "concept"
    WORKFLOW = "workflow"
    INTEGRATION = "integration"
    SETTING = "setting"

@dataclass
class OnboardingConfig:
    """Configuration for the onboarding system."""
    enabled: bool = True
    default_experience_level: UserExperienceLevel = UserExperienceLevel.BEGINNER
    auto_suggest_tutorials: bool = True
    show_tooltips: bool = True
    show_feature_highlights: bool = True
    tutorial_completion_rewards: bool = True
    tutorial_storage_path: str = "tutorials"
    user_progress_storage_path: str = "user_progress"
    help_content_storage_path: str = "help_content"
    feedback_storage_path: str = "feedback"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the configuration to a dictionary."""
        return {
            "enabled": self.enabled,
            "default_experience_level": self.default_experience_level.value,
            "auto_suggest_tutorials": self.auto_suggest_tutorials,
            "show_tooltips": self.show_tooltips,
            "show_feature_highlights": self.show_feature_highlights,
            "tutorial_completion_rewards": self.tutorial_completion_rewards,
            "tutorial_storage_path": self.tutorial_storage_path,
            "user_progress_storage_path": self.user_progress_storage_path,
            "help_content_storage_path": self.help_content_storage_path,
            "feedback_storage_path": self.feedback_storage_path
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OnboardingConfig":
        """Create a configuration from a dictionary."""
        return cls(
            enabled=data.get("enabled", True),
            default_experience_level=UserExperienceLevel(data.get("default_experience_level", "beginner")),
            auto_suggest_tutorials=data.get("auto_suggest_tutorials", True),
            show_tooltips=data.get("show_tooltips", True),
            show_feature_highlights=data.get("show_feature_highlights", True),
            tutorial_completion_rewards=data.get("tutorial_completion_rewards", True),
            tutorial_storage_path=data.get("tutorial_storage_path", "tutorials"),
            user_progress_storage_path=data.get("user_progress_storage_path", "user_progress"),
            help_content_storage_path=data.get("help_content_storage_path", "help_content"),
            feedback_storage_path=data.get("feedback_storage_path", "feedback")
        )

@dataclass
class TutorialStep:
    """A single step in a tutorial."""
    step_id: str
    title: str
    description: str
    action: str  # What the user needs to do
    completion_criteria: Dict[str, Any]  # Criteria to determine if step is completed
    hints: List[str] = field(default_factory=list)
    media_url: Optional[str] = None  # URL to image or video
    estimated_time: int = 60  # seconds
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "step_id": self.step_id,
            "title": self.title,
            "description": self.description,
            "action": self.action,
            "completion_criteria": self.completion_criteria,
            "hints": self.hints,
            "media_url": self.media_url,
            "estimated_time": self.estimated_time
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TutorialStep":
        """Create from dictionary."""
        return cls(
            step_id=data["step_id"],
            title=data["title"],
            description=data["description"],
            action=data["action"],
            completion_criteria=data["completion_criteria"],
            hints=data.get("hints", []),
            media_url=data.get("media_url"),
            estimated_time=data.get("estimated_time", 60)
        )

@dataclass
class Tutorial:
    """A tutorial for the onboarding system."""
    tutorial_id: str
    title: str
    description: str
    category: TutorialCategory
    type: TutorialType
    experience_level: UserExperienceLevel
    steps: List[TutorialStep]
    prerequisites: List[str] = field(default_factory=list)  # List of tutorial_ids
    tags: List[str] = field(default_factory=list)
    estimated_time: int = 0  # seconds, calculated from steps
    version: str = "1.0"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Calculate total estimated time if not provided."""
        if self.estimated_time == 0:
            self.estimated_time = sum(step.estimated_time for step in self.steps)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "tutorial_id": self.tutorial_id,
            "title": self.title,
            "description": self.description,
            "category": self.category.value,
            "type": self.type.value,
            "experience_level": self.experience_level.value,
            "steps": [step.to_dict() for step in self.steps],
            "prerequisites": self.prerequisites,
            "tags": self.tags,
            "estimated_time": self.estimated_time,
            "version": self.version,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Tutorial":
        """Create from dictionary."""
        return cls(
            tutorial_id=data["tutorial_id"],
            title=data["title"],
            description=data["description"],
            category=TutorialCategory(data["category"]),
            type=TutorialType(data["type"]),
            experience_level=UserExperienceLevel(data["experience_level"]),
            steps=[TutorialStep.from_dict(step) for step in data["steps"]],
            prerequisites=data.get("prerequisites", []),
            tags=data.get("tags", []),
            estimated_time=data.get("estimated_time", 0),
            version=data.get("version", "1.0"),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
            updated_at=datetime.fromisoformat(data.get("updated_at", datetime.now().isoformat()))
        )

@dataclass
class HelpContent:
    """Help content for contextual help system."""
    content_id: str
    title: str
    content: str
    context_type: HelpContextType
    context_identifier: str  # Feature name, error code, etc.
    related_tutorials: List[str] = field(default_factory=list)  # List of tutorial_ids
    tags: List[str] = field(default_factory=list)
    media_urls: List[str] = field(default_factory=list)
    version: str = "1.0"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "content_id": self.content_id,
            "title": self.title,
            "content": self.content,
            "context_type": self.context_type.value,
            "context_identifier": self.context_identifier,
            "related_tutorials": self.related_tutorials,
            "tags": self.tags,
            "media_urls": self.media_urls,
            "version": self.version,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HelpContent":
        """Create from dictionary."""
        return cls(
            content_id=data["content_id"],
            title=data["title"],
            content=data["content"],
            context_type=HelpContextType(data["context_type"]),
            context_identifier=data["context_identifier"],
            related_tutorials=data.get("related_tutorials", []),
            tags=data.get("tags", []),
            media_urls=data.get("media_urls", []),
            version=data.get("version", "1.0"),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
            updated_at=datetime.fromisoformat(data.get("updated_at", datetime.now().isoformat()))
        )

@dataclass
class UserProgress:
    """User progress data structure."""
    user_id: str
    experience_level: UserExperienceLevel
    onboarding_stage: OnboardingStage
    completed_tutorials: Dict[str, datetime] = field(default_factory=dict)  # tutorial_id -> completion_time
    current_tutorial: Optional[str] = None  # tutorial_id
    current_step: Optional[str] = None  # step_id
    tutorial_progress: Dict[str, List[str]] = field(default_factory=dict)  # tutorial_id -> list of completed step_ids
    viewed_help_content: Dict[str, datetime] = field(default_factory=dict)  # content_id -> view_time
    feature_usage_count: Dict[str, int] = field(default_factory=dict)  # feature_id -> usage count
    last_active: datetime = field(default_factory=datetime.now)
    preferences: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "user_id": self.user_id,
            "experience_level": self.experience_level.value,
            "onboarding_stage": self.onboarding_stage.value,
            "completed_tutorials": {tid: dt.isoformat() for tid, dt in self.completed_tutorials.items()},
            "current_tutorial": self.current_tutorial,
            "current_step": self.current_step,
            "tutorial_progress": self.tutorial_progress,
            "viewed_help_content": {cid: dt.isoformat() for cid, dt in self.viewed_help_content.items()},
            "feature_usage_count": self.feature_usage_count,
            "last_active": self.last_active.isoformat(),
            "preferences": self.preferences
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserProgress":
        """Create from dictionary."""
        return cls(
            user_id=data["user_id"],
            experience_level=UserExperienceLevel(data["experience_level"]),
            onboarding_stage=OnboardingStage(data["onboarding_stage"]),
            completed_tutorials={tid: datetime.fromisoformat(dt) for tid, dt in data.get("completed_tutorials", {}).items()},
            current_tutorial=data.get("current_tutorial"),
            current_step=data.get("current_step"),
            tutorial_progress=data.get("tutorial_progress", {}),
            viewed_help_content={cid: datetime.fromisoformat(dt) for cid, dt in data.get("viewed_help_content", {}).items()},
            feature_usage_count=data.get("feature_usage_count", {}),
            last_active=datetime.fromisoformat(data.get("last_active", datetime.now().isoformat())),
            preferences=data.get("preferences", {})
        )

@dataclass
class UserFeedback:
    """User feedback data structure."""
    feedback_id: str
    user_id: str
    feedback_type: str  # tutorial, help_content, feature, general
    reference_id: Optional[str] = None  # tutorial_id, content_id, feature_id
    rating: Optional[int] = None  # 1-5
    comments: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "feedback_id": self.feedback_id,
            "user_id": self.user_id,
            "feedback_type": self.feedback_type,
            "reference_id": self.reference_id,
            "rating": self.rating,
            "comments": self.comments,
            "created_at": self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserFeedback":
        """Create from dictionary."""
        return cls(
            feedback_id=data["feedback_id"],
            user_id=data["user_id"],
            feedback_type=data["feedback_type"],
            reference_id=data.get("reference_id"),
            rating=data.get("rating"),
            comments=data.get("comments"),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat()))
        )

class TutorialManager:
    """Manages tutorials for the onboarding system."""
    
    def __init__(self, config: OnboardingConfig):
        """Initialize the tutorial manager."""
        self.config = config
        self.tutorials: Dict[str, Tutorial] = {}
        self._lock = threading.RLock()
        self._load_tutorials()
    
    def _load_tutorials(self) -> None:
        """Load tutorials from storage."""
        with self._lock:
            self.tutorials = {}
            tutorial_dir = Path(self.config.tutorial_storage_path)
            tutorial_dir.mkdir(parents=True, exist_ok=True)
            
            for file_path in tutorial_dir.glob("*.json"):
                try:
                    with open(file_path, "r") as f:
                        tutorial_data = json.load(f)
                    
                    tutorial = Tutorial.from_dict(tutorial_data)
                    self.tutorials[tutorial.tutorial_id] = tutorial
                except Exception as e:
                    logger.error(f"Failed to load tutorial from {file_path}: {str(e)}")
    
    def _save_tutorial(self, tutorial: Tutorial) -> None:
        """Save a tutorial to storage."""
        tutorial_dir = Path(self.config.tutorial_storage_path)
        tutorial_dir.mkdir(parents=True, exist_ok=True)
        file_path = tutorial_dir / f"{tutorial.tutorial_id}.json"
        
        try:
            with open(file_path, "w") as f:
                json.dump(tutorial.to_dict(), f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save tutorial {tutorial.tutorial_id}: {str(e)}")
    
    def add_tutorial(self, title: str, description: str, category: TutorialCategory,
                    type: TutorialType, experience_level: UserExperienceLevel,
                    steps: List[TutorialStep], prerequisites: List[str] = None,
                    tags: List[str] = None) -> Tutorial:
        """Add a new tutorial."""
        with self._lock:
            tutorial_id = str(uuid.uuid4())
            tutorial = Tutorial(
                tutorial_id=tutorial_id,
                title=title,
                description=description,
                category=category,
                type=type,
                experience_level=experience_level,
                steps=steps,
                prerequisites=prerequisites or [],
                tags=tags or []
            )
            self.tutorials[tutorial_id] = tutorial
            self._save_tutorial(tutorial)
            logger.info(f"Added new tutorial: {tutorial_id} ({title})")
            return tutorial
    
    def update_tutorial(self, tutorial_id: str, **kwargs) -> Optional[Tutorial]:
        """Update an existing tutorial."""
        with self._lock:
            if tutorial_id not in self.tutorials:
                logger.error(f"Tutorial not found: {tutorial_id}")
                return None
            
            tutorial = self.tutorials[tutorial_id]
            updated = False
            
            for key, value in kwargs.items():
                if hasattr(tutorial, key):
                    setattr(tutorial, key, value)
                    updated = True
            
            if updated:
                tutorial.updated_at = datetime.now()
                self._save_tutorial(tutorial)
                logger.info(f"Updated tutorial: {tutorial_id}")
            
            return tutorial
    
    def get_tutorial(self, tutorial_id: str) -> Optional[Tutorial]:
        """Get a tutorial by ID."""
        with self._lock:
            return self.tutorials.get(tutorial_id)
    
    def get_tutorials(self, category: Optional[TutorialCategory] = None,
                     type: Optional[TutorialType] = None,
                     experience_level: Optional[UserExperienceLevel] = None,
                     tags: Optional[List[str]] = None) -> List[Tutorial]:
        """Get tutorials filtered by criteria."""
        with self._lock:
            filtered_tutorials = list(self.tutorials.values())
            
            if category:
                filtered_tutorials = [t for t in filtered_tutorials if t.category == category]
            
            if type:
                filtered_tutorials = [t for t in filtered_tutorials if t.type == type]
            
            if experience_level:
                filtered_tutorials = [t for t in filtered_tutorials if t.experience_level == experience_level]
            
            if tags:
                filtered_tutorials = [t for t in filtered_tutorials if any(tag in t.tags for tag in tags)]
            
            return filtered_tutorials
    
    def get_tutorial_path(self, user_progress: UserProgress) -> List[Tutorial]:
        """Get a recommended path of tutorials based on user progress."""
        with self._lock:
            # Get all tutorials for the user's experience level or lower
            available_tutorials = [
                t for t in self.tutorials.values()
                if t.experience_level.value <= user_progress.experience_level.value
            ]
            
            # Filter out completed tutorials
            uncompleted_tutorials = [
                t for t in available_tutorials
                if t.tutorial_id not in user_progress.completed_tutorials
            ]
            
            # Filter for tutorials where prerequisites are met
            eligible_tutorials = []
            for tutorial in uncompleted_tutorials:
                prerequisites_met = all(
                    prereq in user_progress.completed_tutorials
                    for prereq in tutorial.prerequisites
                )
                if prerequisites_met:
                    eligible_tutorials.append(tutorial)
            
            # Sort by category priority (getting started first, then basic, etc.)
            category_priority = {
                TutorialCategory.GETTING_STARTED: 0,
                TutorialCategory.BASIC_FEATURES: 1,
                TutorialCategory.ADVANCED_FEATURES: 2,
                TutorialCategory.BEST_PRACTICES: 3,
                TutorialCategory.TROUBLESHOOTING: 4,
                TutorialCategory.INTEGRATION: 5,
                TutorialCategory.CUSTOMIZATION: 6,
                TutorialCategory.ADMINISTRATION: 7
            }
            
            eligible_tutorials.sort(key=lambda t: category_priority.get(t.category, 999))
            
            return eligible_tutorials
    
    def check_step_completion(self, tutorial_id: str, step_id: str, context: Dict[str, Any]) -> bool:
        """Check if a tutorial step is completed based on context."""
        with self._lock:
            tutorial = self.get_tutorial(tutorial_id)
            if not tutorial:
                logger.error(f"Tutorial not found: {tutorial_id}")
                return False
            
            step = next((s for s in tutorial.steps if s.step_id == step_id), None)
            if not step:
                logger.error(f"Step not found: {step_id} in tutorial {tutorial_id}")
                return False
            
            # Simple criteria matching
            # In a real implementation, this would be more sophisticated
            criteria = step.completion_criteria
            
            # Example: Check if a specific action was performed
            if "action_performed" in criteria:
                required_action = criteria["action_performed"]
                if context.get("last_action") != required_action:
                    return False
            
            # Example: Check if a specific feature was used
            if "feature_used" in criteria:
                required_feature = criteria["feature_used"]
                if required_feature not in context.get("used_features", []):
                    return False
            
            # Example: Check if a specific value was entered
            if "value_entered" in criteria:
                required_value = criteria["value_entered"]
                if context.get("entered_value") != required_value:
                    return False
            
            return True

class HelpContentManager:
    """Manages help content for the contextual help system."""
    
    def __init__(self, config: OnboardingConfig):
        """Initialize the help content manager."""
        self.config = config
        self.help_contents: Dict[str, HelpContent] = {}
        self.context_index: Dict[Tuple[HelpContextType, str], List[str]] = {}
        self._lock = threading.RLock()
        self._load_help_contents()
    
    def _load_help_contents(self) -> None:
        """Load help contents from storage."""
        with self._lock:
            self.help_contents = {}
            self.context_index = {}
            help_dir = Path(self.config.help_content_storage_path)
            help_dir.mkdir(parents=True, exist_ok=True)
            
            for file_path in help_dir.glob("*.json"):
                try:
                    with open(file_path, "r") as f:
                        content_data = json.load(f)
                    
                    help_content = HelpContent.from_dict(content_data)
                    self.help_contents[help_content.content_id] = help_content
                    
                    # Update context index
                    context_key = (help_content.context_type, help_content.context_identifier)
                    if context_key not in self.context_index:
                        self.context_index[context_key] = []
                    self.context_index[context_key].append(help_content.content_id)
                except Exception as e:
                    logger.error(f"Failed to load help content from {file_path}: {str(e)}")
    
    def _save_help_content(self, help_content: HelpContent) -> None:
        """Save help content to storage."""
        help_dir = Path(self.config.help_content_storage_path)
        help_dir.mkdir(parents=True, exist_ok=True)
        file_path = help_dir / f"{help_content.content_id}.json"
        
        try:
            with open(file_path, "w") as f:
                json.dump(help_content.to_dict(), f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save help content {help_content.content_id}: {str(e)}")
    
    def add_help_content(self, title: str, content: str, context_type: HelpContextType,
                        context_identifier: str, related_tutorials: List[str] = None,
                        tags: List[str] = None, media_urls: List[str] = None) -> HelpContent:
        """Add new help content."""
        with self._lock:
            content_id = str(uuid.uuid4())
            help_content = HelpContent(
                content_id=content_id,
                title=title,
                content=content,
                context_type=context_type,
                context_identifier=context_identifier,
                related_tutorials=related_tutorials or [],
                tags=tags or [],
                media_urls=media_urls or []
            )
            self.help_contents[content_id] = help_content
            
            # Update context index
            context_key = (context_type, context_identifier)
            if context_key not in self.context_index:
                self.context_index[context_key] = []
            self.context_index[context_key].append(content_id)
            
            self._save_help_content(help_content)
            logger.info(f"Added new help content: {content_id} ({title})")
            return help_content
    
    def update_help_content(self, content_id: str, **kwargs) -> Optional[HelpContent]:
        """Update existing help content."""
        with self._lock:
            if content_id not in self.help_contents:
                logger.error(f"Help content not found: {content_id}")
                return None
            
            help_content = self.help_contents[content_id]
            updated = False
            
            # Remove from old context index if context is changing
            old_context_key = None
            if "context_type" in kwargs or "context_identifier" in kwargs:
                old_context_key = (help_content.context_type, help_content.context_identifier)
                if old_context_key in self.context_index and content_id in self.context_index[old_context_key]:
                    self.context_index[old_context_key].remove(content_id)
            
            for key, value in kwargs.items():
                if hasattr(help_content, key):
                    setattr(help_content, key, value)
                    updated = True
            
            if updated:
                help_content.updated_at = datetime.now()
                
                # Update context index if context changed
                if old_context_key:
                    new_context_key = (help_content.context_type, help_content.context_identifier)
                    if new_context_key not in self.context_index:
                        self.context_index[new_context_key] = []
                    self.context_index[new_context_key].append(content_id)
                
                self._save_help_content(help_content)
                logger.info(f"Updated help content: {content_id}")
            
            return help_content
    
    def get_help_content(self, content_id: str) -> Optional[HelpContent]:
        """Get help content by ID."""
        with self._lock:
            return self.help_contents.get(content_id)
    
    def get_help_for_context(self, context_type: HelpContextType, context_identifier: str) -> List[HelpContent]:
        """Get help content for a specific context."""
        with self._lock:
            context_key = (context_type, context_identifier)
            content_ids = self.context_index.get(context_key, [])
            return [self.help_contents[cid] for cid in content_ids if cid in self.help_contents]
    
    def search_help_content(self, query: str, tags: Optional[List[str]] = None) -> List[HelpContent]:
        """Search help content by query and tags."""
        with self._lock:
            # Simple search implementation
            # In a real implementation, this would use more sophisticated search techniques
            query = query.lower()
            results = []
            
            for content in self.help_contents.values():
                # Check if query matches title or content
                if query in content.title.lower() or query in content.content.lower():
                    # Check tags if provided
                    if tags and not any(tag in content.tags for tag in tags):
                        continue
                    results.append(content)
            
            return results

class UserProgressManager:
    """Manages user progress for the onboarding system."""
    
    def __init__(self, config: OnboardingConfig):
        """Initialize the user progress manager."""
        self.config = config
        self.user_progress: Dict[str, UserProgress] = {}
        self._lock = threading.RLock()
        self._load_user_progress()
    
    def _load_user_progress(self) -> None:
        """Load user progress from storage."""
        with self._lock:
            self.user_progress = {}
            progress_dir = Path(self.config.user_progress_storage_path)
            progress_dir.mkdir(parents=True, exist_ok=True)
            
            for file_path in progress_dir.glob("*.json"):
                try:
                    with open(file_path, "r") as f:
                        progress_data = json.load(f)
                    
                    user_id = progress_data["user_id"]
                    progress = UserProgress.from_dict(progress_data)
                    self.user_progress[user_id] = progress
                except Exception as e:
                    logger.error(f"Failed to load user progress from {file_path}: {str(e)}")
    
    def _save_user_progress(self, progress: UserProgress) -> None:
        """Save user progress to storage."""
        progress_dir = Path(self.config.user_progress_storage_path)
        progress_dir.mkdir(parents=True, exist_ok=True)
        file_path = progress_dir / f"{progress.user_id}.json"
        
        try:
            with open(file_path, "w") as f:
                json.dump(progress.to_dict(), f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save user progress for {progress.user_id}: {str(e)}")
    
    def get_user_progress(self, user_id: str) -> UserProgress:
        """Get user progress, creating a new record if it doesn't exist."""
        with self._lock:
            if user_id not in self.user_progress:
                # Create new user progress with default settings
                progress = UserProgress(
                    user_id=user_id,
                    experience_level=self.config.default_experience_level,
                    onboarding_stage=OnboardingStage.WELCOME
                )
                self.user_progress[user_id] = progress
                self._save_user_progress(progress)
                logger.info(f"Created new user progress for {user_id}")
            
            return self.user_progress[user_id]
    
    def update_user_progress(self, user_id: str, **kwargs) -> UserProgress:
        """Update user progress."""
        with self._lock:
            progress = self.get_user_progress(user_id)
            updated = False
            
            for key, value in kwargs.items():
                if hasattr(progress, key):
                    setattr(progress, key, value)
                    updated = True
            
            if updated:
                progress.last_active = datetime.now()
                self._save_user_progress(progress)
                logger.info(f"Updated user progress for {user_id}")
            
            return progress
    
    def record_tutorial_progress(self, user_id: str, tutorial_id: str, step_id: str) -> UserProgress:
        """Record progress on a tutorial step."""
        with self._lock:
            progress = self.get_user_progress(user_id)
            
            # Initialize tutorial progress if needed
            if tutorial_id not in progress.tutorial_progress:
                progress.tutorial_progress[tutorial_id] = []
            
            # Add step if not already completed
            if step_id not in progress.tutorial_progress[tutorial_id]:
                progress.tutorial_progress[tutorial_id].append(step_id)
            
            # Update current tutorial and step
            progress.current_tutorial = tutorial_id
            progress.current_step = step_id
            
            progress.last_active = datetime.now()
            self._save_user_progress(progress)
            logger.info(f"Recorded tutorial progress for {user_id}: {tutorial_id}/{step_id}")
            
            return progress
    
    def complete_tutorial(self, user_id: str, tutorial_id: str) -> UserProgress:
        """Mark a tutorial as completed."""
        with self._lock:
            progress = self.get_user_progress(user_id)
            
            # Mark as completed with timestamp
            progress.completed_tutorials[tutorial_id] = datetime.now()
            
            # Clear current tutorial if it's the one that was completed
            if progress.current_tutorial == tutorial_id:
                progress.current_tutorial = None
                progress.current_step = None
            
            progress.last_active = datetime.now()
            self._save_user_progress(progress)
            logger.info(f"Completed tutorial for {user_id}: {tutorial_id}")
            
            return progress
    
    def record_help_content_view(self, user_id: str, content_id: str) -> UserProgress:
        """Record that a user viewed help content."""
        with self._lock:
            progress = self.get_user_progress(user_id)
            
            # Record view with timestamp
            progress.viewed_help_content[content_id] = datetime.now()
            
            progress.last_active = datetime.now()
            self._save_user_progress(progress)
            logger.info(f"Recorded help content view for {user_id}: {content_id}")
            
            return progress
    
    def record_feature_usage(self, user_id: str, feature_id: str) -> UserProgress:
        """Record that a user used a feature."""
        with self._lock:
            progress = self.get_user_progress(user_id)
            
            # Increment usage count
            if feature_id not in progress.feature_usage_count:
                progress.feature_usage_count[feature_id] = 0
            progress.feature_usage_count[feature_id] += 1
            
            progress.last_active = datetime.now()
            self._save_user_progress(progress)
            logger.info(f"Recorded feature usage for {user_id}: {feature_id}")
            
            return progress
    
    def update_onboarding_stage(self, user_id: str, stage: OnboardingStage) -> UserProgress:
        """Update the user's onboarding stage."""
        with self._lock:
            progress = self.get_user_progress(user_id)
            
            progress.onboarding_stage = stage
            
            progress.last_active = datetime.now()
            self._save_user_progress(progress)
            logger.info(f"Updated onboarding stage for {user_id}: {stage.value}")
            
            return progress
    
    def update_experience_level(self, user_id: str, level: UserExperienceLevel) -> UserProgress:
        """Update the user's experience level."""
        with self._lock:
            progress = self.get_user_progress(user_id)
            
            progress.experience_level = level
            
            progress.last_active = datetime.now()
            self._save_user_progress(progress)
            logger.info(f"Updated experience level for {user_id}: {level.value}")
            
            return progress
    
    def get_completion_percentage(self, user_id: str, tutorial_id: str) -> float:
        """Get the completion percentage for a tutorial."""
        with self._lock:
            progress = self.get_user_progress(user_id)
            
            # If tutorial is completed, return 100%
            if tutorial_id in progress.completed_tutorials:
                return 100.0
            
            # Get tutorial to check total steps
            tutorial_manager = TutorialManager(self.config)
            tutorial = tutorial_manager.get_tutorial(tutorial_id)
            if not tutorial:
                logger.error(f"Tutorial not found: {tutorial_id}")
                return 0.0
            
            total_steps = len(tutorial.steps)
            if total_steps == 0:
                return 0.0
            
            # Count completed steps
            completed_steps = len(progress.tutorial_progress.get(tutorial_id, []))
            
            return (completed_steps / total_steps) * 100.0

class FeedbackManager:
    """Manages user feedback for the onboarding system."""
    
    def __init__(self, config: OnboardingConfig):
        """Initialize the feedback manager."""
        self.config = config
        self.feedback: Dict[str, UserFeedback] = {}
        self._lock = threading.RLock()
        self._load_feedback()
    
    def _load_feedback(self) -> None:
        """Load feedback from storage."""
        with self._lock:
            self.feedback = {}
            feedback_dir = Path(self.config.feedback_storage_path)
            feedback_dir.mkdir(parents=True, exist_ok=True)
            
            for file_path in feedback_dir.glob("*.json"):
                try:
                    with open(file_path, "r") as f:
                        feedback_data = json.load(f)
                    
                    feedback = UserFeedback.from_dict(feedback_data)
                    self.feedback[feedback.feedback_id] = feedback
                except Exception as e:
                    logger.error(f"Failed to load feedback from {file_path}: {str(e)}")
    
    def _save_feedback(self, feedback: UserFeedback) -> None:
        """Save feedback to storage."""
        feedback_dir = Path(self.config.feedback_storage_path)
        feedback_dir.mkdir(parents=True, exist_ok=True)
        file_path = feedback_dir / f"{feedback.feedback_id}.json"
        
        try:
            with open(file_path, "w") as f:
                json.dump(feedback.to_dict(), f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save feedback {feedback.feedback_id}: {str(e)}")
    
    def add_feedback(self, user_id: str, feedback_type: str, reference_id: Optional[str] = None,
                    rating: Optional[int] = None, comments: Optional[str] = None) -> UserFeedback:
        """Add new user feedback."""
        with self._lock:
            feedback_id = str(uuid.uuid4())
            feedback = UserFeedback(
                feedback_id=feedback_id,
                user_id=user_id,
                feedback_type=feedback_type,
                reference_id=reference_id,
                rating=rating,
                comments=comments
            )
            self.feedback[feedback_id] = feedback
            self._save_feedback(feedback)
            logger.info(f"Added new feedback from {user_id}: {feedback_type}")
            return feedback
    
    def get_feedback(self, feedback_id: str) -> Optional[UserFeedback]:
        """Get feedback by ID."""
        with self._lock:
            return self.feedback.get(feedback_id)
    
    def get_feedback_for_user(self, user_id: str) -> List[UserFeedback]:
        """Get all feedback from a user."""
        with self._lock:
            return [f for f in self.feedback.values() if f.user_id == user_id]
    
    def get_feedback_for_reference(self, reference_id: str) -> List[UserFeedback]:
        """Get all feedback for a specific reference (tutorial, help content, etc.)."""
        with self._lock:
            return [f for f in self.feedback.values() if f.reference_id == reference_id]
    
    def get_average_rating(self, reference_id: str) -> Optional[float]:
        """Get the average rating for a specific reference."""
        with self._lock:
            feedback_list = self.get_feedback_for_reference(reference_id)
            ratings = [f.rating for f in feedback_list if f.rating is not None]
            
            if not ratings:
                return None
            
            return sum(ratings) / len(ratings)

class OnboardingSystem:
    """Main onboarding system class."""
    
    _instance = None
    
    @classmethod
    def get_instance(cls) -> "OnboardingSystem":
        """Get the singleton instance."""
        if cls._instance is None:
            cls._instance = OnboardingSystem()
        return cls._instance
    
    def __init__(self):
        """Initialize the onboarding system."""
        self.config = OnboardingConfig()
        self.tutorial_manager = TutorialManager(self.config)
        self.help_content_manager = HelpContentManager(self.config)
        self.user_progress_manager = UserProgressManager(self.config)
        self.feedback_manager = FeedbackManager(self.config)
        self._initialized = False
        self._lock = threading.RLock()
        self._event_queue = queue.Queue()
        self._event_thread = None
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
                    self.config = OnboardingConfig.from_dict(config_data)
                except Exception as e:
                    logger.error(f"Failed to load onboarding config from {config_path}: {str(e)}. Using defaults.")
                    self.config = OnboardingConfig()
            else:
                logger.warning("Onboarding config file not found. Using defaults.")
                self.config = OnboardingConfig()
            
            # Re-initialize managers with the loaded config
            self.tutorial_manager = TutorialManager(self.config)
            self.help_content_manager = HelpContentManager(self.config)
            self.user_progress_manager = UserProgressManager(self.config)
            self.feedback_manager = FeedbackManager(self.config)
            
            # Start event processing thread
            self._running = True
            self._event_thread = threading.Thread(target=self._process_events, daemon=True)
            self._event_thread.start()
            
            self._initialized = True
            logger.info("Onboarding system initialized")
    
    def shutdown(self) -> None:
        """Shutdown the system."""
        with self._lock:
            if not self._initialized:
                return
            
            self._running = False
            if self._event_thread:
                self._event_thread.join(timeout=5.0)
                self._event_thread = None
            
            self._initialized = False
            logger.info("Onboarding system shutdown")
    
    def ensure_initialized(self) -> None:
        """Ensure the system is initialized."""
        if not self._initialized:
            self.initialize()
    
    def _process_events(self) -> None:
        """Process events from the queue."""
        while self._running:
            try:
                event = self._event_queue.get(timeout=1.0)
                self._handle_event(event)
                self._event_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error processing onboarding event: {str(e)}")
    
    def _handle_event(self, event: Dict[str, Any]) -> None:
        """Handle an onboarding event."""
        event_type = event.get("type")
        user_id = event.get("user_id")
        
        if not user_id:
            logger.error(f"Event missing user_id: {event}")
            return
        
        if event_type == "feature_used":
            feature_id = event.get("feature_id")
            if feature_id:
                self.user_progress_manager.record_feature_usage(user_id, feature_id)
                
                # Check if this feature usage completes any tutorial steps
                if "tutorial_id" in event and "step_id" in event:
                    tutorial_id = event["tutorial_id"]
                    step_id = event["step_id"]
                    context = {"used_features": [feature_id]}
                    if self.tutorial_manager.check_step_completion(tutorial_id, step_id, context):
                        self.user_progress_manager.record_tutorial_progress(user_id, tutorial_id, step_id)
        
        elif event_type == "help_viewed":
            content_id = event.get("content_id")
            if content_id:
                self.user_progress_manager.record_help_content_view(user_id, content_id)
        
        elif event_type == "tutorial_started":
            tutorial_id = event.get("tutorial_id")
            if tutorial_id:
                progress = self.user_progress_manager.get_user_progress(user_id)
                progress.current_tutorial = tutorial_id
                progress.current_step = None
                self.user_progress_manager._save_user_progress(progress)
        
        elif event_type == "tutorial_step_completed":
            tutorial_id = event.get("tutorial_id")
            step_id = event.get("step_id")
            if tutorial_id and step_id:
                self.user_progress_manager.record_tutorial_progress(user_id, tutorial_id, step_id)
                
                # Check if all steps are completed
                progress = self.user_progress_manager.get_user_progress(user_id)
                tutorial = self.tutorial_manager.get_tutorial(tutorial_id)
                if tutorial:
                    completed_steps = progress.tutorial_progress.get(tutorial_id, [])
                    all_steps = [step.step_id for step in tutorial.steps]
                    if all(step in completed_steps for step in all_steps):
                        self.user_progress_manager.complete_tutorial(user_id, tutorial_id)
        
        elif event_type == "tutorial_completed":
            tutorial_id = event.get("tutorial_id")
            if tutorial_id:
                self.user_progress_manager.complete_tutorial(user_id, tutorial_id)
        
        elif event_type == "feedback_submitted":
            feedback_type = event.get("feedback_type")
            reference_id = event.get("reference_id")
            rating = event.get("rating")
            comments = event.get("comments")
            if feedback_type:
                self.feedback_manager.add_feedback(user_id, feedback_type, reference_id, rating, comments)
    
    def track_event(self, event: Dict[str, Any]) -> None:
        """Track an onboarding event."""
        self.ensure_initialized()
        self._event_queue.put(event)
    
    def get_user_progress(self, user_id: str) -> UserProgress:
        """Get user progress."""
        self.ensure_initialized()
        return self.user_progress_manager.get_user_progress(user_id)
    
    def get_recommended_tutorials(self, user_id: str, limit: int = 5) -> List[Tutorial]:
        """Get recommended tutorials for a user."""
        self.ensure_initialized()
        progress = self.user_progress_manager.get_user_progress(user_id)
        tutorial_path = self.tutorial_manager.get_tutorial_path(progress)
        return tutorial_path[:limit]
    
    def get_contextual_help(self, context_type: HelpContextType, context_identifier: str) -> List[HelpContent]:
        """Get contextual help for a specific context."""
        self.ensure_initialized()
        return self.help_content_manager.get_help_for_context(context_type, context_identifier)
    
    def search_help(self, query: str, tags: Optional[List[str]] = None) -> List[HelpContent]:
        """Search help content."""
        self.ensure_initialized()
        return self.help_content_manager.search_help_content(query, tags)
    
    def get_tutorial(self, tutorial_id: str) -> Optional[Tutorial]:
        """Get a tutorial by ID."""
        self.ensure_initialized()
        return self.tutorial_manager.get_tutorial(tutorial_id)
    
    def get_help_content(self, content_id: str) -> Optional[HelpContent]:
        """Get help content by ID."""
        self.ensure_initialized()
        return self.help_content_manager.get_help_content(content_id)
    
    def submit_feedback(self, user_id: str, feedback_type: str, reference_id: Optional[str] = None,
                       rating: Optional[int] = None, comments: Optional[str] = None) -> UserFeedback:
        """Submit user feedback."""
        self.ensure_initialized()
        return self.feedback_manager.add_feedback(user_id, feedback_type, reference_id, rating, comments)
    
    def get_tutorial_completion_percentage(self, user_id: str, tutorial_id: str) -> float:
        """Get the completion percentage for a tutorial."""
        self.ensure_initialized()
        return self.user_progress_manager.get_completion_percentage(user_id, tutorial_id)
    
    def update_user_experience_level(self, user_id: str, level: UserExperienceLevel) -> UserProgress:
        """Update the user's experience level."""
        self.ensure_initialized()
        return self.user_progress_manager.update_experience_level(user_id, level)
    
    def update_onboarding_stage(self, user_id: str, stage: OnboardingStage) -> UserProgress:
        """Update the user's onboarding stage."""
        self.ensure_initialized()
        return self.user_progress_manager.update_onboarding_stage(user_id, stage)
    
    def create_tutorial(self, title: str, description: str, category: TutorialCategory,
                       type: TutorialType, experience_level: UserExperienceLevel,
                       steps: List[TutorialStep], prerequisites: List[str] = None,
                       tags: List[str] = None) -> Tutorial:
        """Create a new tutorial."""
        self.ensure_initialized()
        return self.tutorial_manager.add_tutorial(title, description, category, type, experience_level, steps, prerequisites, tags)
    
    def create_help_content(self, title: str, content: str, context_type: HelpContextType,
                           context_identifier: str, related_tutorials: List[str] = None,
                           tags: List[str] = None, media_urls: List[str] = None) -> HelpContent:
        """Create new help content."""
        self.ensure_initialized()
        return self.help_content_manager.add_help_content(title, content, context_type, context_identifier, related_tutorials, tags, media_urls)

# Global instance for easy access
onboarding_system = OnboardingSystem.get_instance()

# --- Helper Functions --- #

def initialize_onboarding(config_path: Optional[str] = None) -> None:
    """Initialize the onboarding system."""
    onboarding_system.initialize(config_path)

def shutdown_onboarding() -> None:
    """Shutdown the onboarding system."""
    onboarding_system.shutdown()

def track_feature_usage(user_id: str, feature_id: str) -> None:
    """Track feature usage."""
    onboarding_system.track_event({
        "type": "feature_used",
        "user_id": user_id,
        "feature_id": feature_id
    })

def track_help_content_view(user_id: str, content_id: str) -> None:
    """Track help content view."""
    onboarding_system.track_event({
        "type": "help_viewed",
        "user_id": user_id,
        "content_id": content_id
    })

def track_tutorial_step_completion(user_id: str, tutorial_id: str, step_id: str) -> None:
    """Track tutorial step completion."""
    onboarding_system.track_event({
        "type": "tutorial_step_completed",
        "user_id": user_id,
        "tutorial_id": tutorial_id,
        "step_id": step_id
    })

def create_tutorial_step(title: str, description: str, action: str, completion_criteria: Dict[str, Any],
                        hints: List[str] = None, media_url: Optional[str] = None,
                        estimated_time: int = 60) -> TutorialStep:
    """Create a tutorial step."""
    return TutorialStep(
        step_id=str(uuid.uuid4()),
        title=title,
        description=description,
        action=action,
        completion_criteria=completion_criteria,
        hints=hints or [],
        media_url=media_url,
        estimated_time=estimated_time
    )

# Example usage
if __name__ == "__main__":
    # Initialize
    initialize_onboarding()
    
    # Create a tutorial
    steps = [
        create_tutorial_step(
            title="Create a New Project",
            description="Learn how to create a new project in ApexAgent.",
            action="Click the 'New Project' button in the top-left corner.",
            completion_criteria={"action_performed": "create_project"},
            hints=["Look for the + icon in the top navigation bar."],
            estimated_time=30
        ),
        create_tutorial_step(
            title="Configure Project Settings",
            description="Set up your project with the right settings.",
            action="Fill in the project name and select a template.",
            completion_criteria={"feature_used": "project_settings"},
            hints=["The template selection affects available tools and features."],
            estimated_time=60
        ),
        create_tutorial_step(
            title="Add Your First Task",
            description="Create a task to get started with your project.",
            action="Click 'Add Task' and enter a task description.",
            completion_criteria={"feature_used": "add_task"},
            hints=["Be specific in your task description for better results."],
            estimated_time=45
        )
    ]
    
    tutorial = onboarding_system.create_tutorial(
        title="Getting Started with ApexAgent",
        description="Learn the basics of using ApexAgent to create and manage projects.",
        category=TutorialCategory.GETTING_STARTED,
        type=TutorialType.INTERACTIVE,
        experience_level=UserExperienceLevel.BEGINNER,
        steps=steps,
        tags=["beginner", "projects", "basics"]
    )
    
    # Create help content
    help_content = onboarding_system.create_help_content(
        title="Understanding Project Templates",
        content="Project templates provide pre-configured settings and tools for specific use cases. "
                "This guide explains each template and when to use it.",
        context_type=HelpContextType.CONCEPT,
        context_identifier="project_templates",
        related_tutorials=[tutorial.tutorial_id],
        tags=["projects", "templates", "configuration"]
    )
    
    # Simulate user activity
    user_id = "user_123"
    
    # Track feature usage
    track_feature_usage(user_id, "create_project")
    
    # Track tutorial progress
    track_tutorial_step_completion(user_id, tutorial.tutorial_id, steps[0].step_id)
    
    # Track help content view
    track_help_content_view(user_id, help_content.content_id)
    
    # Get user progress
    progress = onboarding_system.get_user_progress(user_id)
    print(f"User {user_id} progress:")
    print(f"- Experience level: {progress.experience_level.value}")
    print(f"- Onboarding stage: {progress.onboarding_stage.value}")
    print(f"- Completed tutorials: {len(progress.completed_tutorials)}")
    
    # Get recommended tutorials
    recommended = onboarding_system.get_recommended_tutorials(user_id)
    print(f"Recommended tutorials for {user_id}:")
    for tut in recommended:
        print(f"- {tut.title} ({tut.experience_level.value})")
    
    # Submit feedback
    feedback = onboarding_system.submit_feedback(
        user_id=user_id,
        feedback_type="tutorial",
        reference_id=tutorial.tutorial_id,
        rating=4,
        comments="Very helpful for getting started!"
    )
    
    # Shutdown
    shutdown_onboarding()
