#!/usr/bin/env python3
"""
Test suite for the User Onboarding System.

This module provides comprehensive tests for the user onboarding system
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

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import modules to test
from onboarding.onboarding_system import (
    OnboardingSystem, OnboardingConfig, OnboardingStep, OnboardingFlow,
    OnboardingProgress, OnboardingTemplate, UserProfile, TutorialManager,
    WalkthroughManager, OnboardingAnalytics
)

class TestOnboardingSystem(unittest.TestCase):
    """Test cases for the OnboardingSystem class."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = OnboardingConfig(
            enabled=True,
            data_directory=self.temp_dir,
            default_flow="standard",
            analytics_enabled=True,
            personalization_enabled=True,
            tutorial_enabled=True,
            walkthrough_enabled=True
        )
        self.onboarding_system = OnboardingSystem.get_instance()
        self.onboarding_system.initialize(self.config)
    
    def tearDown(self):
        """Clean up test environment."""
        self.onboarding_system.shutdown()
    
    def test_singleton_pattern(self):
        """Test that the onboarding system follows the singleton pattern."""
        instance1 = OnboardingSystem.get_instance()
        instance2 = OnboardingSystem.get_instance()
        self.assertIs(instance1, instance2)
    
    def test_register_onboarding_flow(self):
        """Test registering an onboarding flow."""
        # Create a flow
        flow = OnboardingFlow(
            flow_id="developer",
            name="Developer Onboarding",
            description="Onboarding flow for developers",
            steps=[
                OnboardingStep(
                    step_id="step1",
                    name="Setup Development Environment",
                    description="Set up your local development environment",
                    content="Follow these steps to set up your environment...",
                    estimated_time=10
                ),
                OnboardingStep(
                    step_id="step2",
                    name="Clone Repository",
                    description="Clone the project repository",
                    content="Use git clone to get the repository...",
                    estimated_time=5
                )
            ]
        )
        
        # Register the flow
        self.onboarding_system.register_onboarding_flow(flow)
        
        # Verify flow was registered
        registered_flow = self.onboarding_system.get_onboarding_flow("developer")
        self.assertEqual(registered_flow, flow)
    
    def test_get_onboarding_flows(self):
        """Test getting all onboarding flows."""
        # Register multiple flows
        flow1 = OnboardingFlow(flow_id="standard", name="Standard Onboarding")
        flow2 = OnboardingFlow(flow_id="developer", name="Developer Onboarding")
        flow3 = OnboardingFlow(flow_id="admin", name="Admin Onboarding")
        
        self.onboarding_system.register_onboarding_flow(flow1)
        self.onboarding_system.register_onboarding_flow(flow2)
        self.onboarding_system.register_onboarding_flow(flow3)
        
        # Get all flows
        flows = self.onboarding_system.get_onboarding_flows()
        
        # Verify flows
        self.assertEqual(len(flows), 3)
        self.assertIn(flow1, flows)
        self.assertIn(flow2, flows)
        self.assertIn(flow3, flows)
    
    def test_start_onboarding(self):
        """Test starting an onboarding process."""
        # Register a flow
        flow = OnboardingFlow(
            flow_id="standard",
            name="Standard Onboarding",
            steps=[
                OnboardingStep(step_id="step1", name="Step 1"),
                OnboardingStep(step_id="step2", name="Step 2")
            ]
        )
        self.onboarding_system.register_onboarding_flow(flow)
        
        # Start onboarding
        with patch.object(self.onboarding_system, '_store_progress') as mock_store:
            progress = self.onboarding_system.start_onboarding(
                user_id="user-123",
                flow_id="standard"
            )
            
            # Verify progress
            self.assertEqual(progress.user_id, "user-123")
            self.assertEqual(progress.flow_id, "standard")
            self.assertEqual(progress.current_step_id, "step1")
            self.assertEqual(progress.completed_steps, [])
            self.assertFalse(progress.completed)
            
            # Verify progress was stored
            mock_store.assert_called_once_with(progress)
    
    @patch('onboarding.onboarding_system.OnboardingSystem._load_progress')
    def test_get_onboarding_progress(self, mock_load):
        """Test getting onboarding progress."""
        # Mock loaded progress
        mock_progress = OnboardingProgress(
            progress_id="progress-123",
            user_id="user-123",
            flow_id="standard",
            current_step_id="step2",
            completed_steps=["step1"],
            completed=False,
            start_time=datetime.datetime.now() - datetime.timedelta(days=1)
        )
        mock_load.return_value = mock_progress
        
        # Get progress
        progress = self.onboarding_system.get_onboarding_progress("user-123")
        
        # Verify progress
        self.assertEqual(progress, mock_progress)
        mock_load.assert_called_once_with("user-123")
    
    @patch('onboarding.onboarding_system.OnboardingSystem._load_progress')
    def test_complete_onboarding_step(self, mock_load):
        """Test completing an onboarding step."""
        # Register a flow
        flow = OnboardingFlow(
            flow_id="standard",
            name="Standard Onboarding",
            steps=[
                OnboardingStep(step_id="step1", name="Step 1"),
                OnboardingStep(step_id="step2", name="Step 2"),
                OnboardingStep(step_id="step3", name="Step 3")
            ]
        )
        self.onboarding_system.register_onboarding_flow(flow)
        
        # Mock loaded progress
        mock_progress = OnboardingProgress(
            progress_id="progress-123",
            user_id="user-123",
            flow_id="standard",
            current_step_id="step1",
            completed_steps=[],
            completed=False
        )
        mock_load.return_value = mock_progress
        
        # Complete step
        with patch.object(self.onboarding_system, '_store_progress') as mock_store:
            with patch.object(self.onboarding_system, '_track_step_completion') as mock_track:
                updated_progress = self.onboarding_system.complete_onboarding_step(
                    user_id="user-123",
                    step_id="step1"
                )
                
                # Verify progress was updated
                self.assertEqual(updated_progress.current_step_id, "step2")
                self.assertEqual(updated_progress.completed_steps, ["step1"])
                self.assertFalse(updated_progress.completed)
                
                # Verify progress was stored
                mock_store.assert_called_once()
                
                # Verify analytics were tracked
                mock_track.assert_called_once()
    
    @patch('onboarding.onboarding_system.OnboardingSystem._load_progress')
    def test_complete_final_step(self, mock_load):
        """Test completing the final onboarding step."""
        # Register a flow
        flow = OnboardingFlow(
            flow_id="standard",
            name="Standard Onboarding",
            steps=[
                OnboardingStep(step_id="step1", name="Step 1"),
                OnboardingStep(step_id="step2", name="Step 2")
            ]
        )
        self.onboarding_system.register_onboarding_flow(flow)
        
        # Mock loaded progress
        mock_progress = OnboardingProgress(
            progress_id="progress-123",
            user_id="user-123",
            flow_id="standard",
            current_step_id="step2",
            completed_steps=["step1"],
            completed=False
        )
        mock_load.return_value = mock_progress
        
        # Complete final step
        with patch.object(self.onboarding_system, '_store_progress') as mock_store:
            with patch.object(self.onboarding_system, '_track_step_completion') as mock_track:
                with patch.object(self.onboarding_system, '_track_flow_completion') as mock_track_flow:
                    updated_progress = self.onboarding_system.complete_onboarding_step(
                        user_id="user-123",
                        step_id="step2"
                    )
                    
                    # Verify progress was updated
                    self.assertEqual(updated_progress.completed_steps, ["step1", "step2"])
                    self.assertTrue(updated_progress.completed)
                    
                    # Verify progress was stored
                    mock_store.assert_called_once()
                    
                    # Verify analytics were tracked
                    mock_track.assert_called_once()
                    mock_track_flow.assert_called_once()
    
    @patch('onboarding.onboarding_system.OnboardingSystem._load_progress')
    def test_reset_onboarding(self, mock_load):
        """Test resetting onboarding progress."""
        # Mock loaded progress
        mock_progress = OnboardingProgress(
            progress_id="progress-123",
            user_id="user-123",
            flow_id="standard",
            current_step_id="step2",
            completed_steps=["step1"],
            completed=False
        )
        mock_load.return_value = mock_progress
        
        # Reset onboarding
        with patch.object(self.onboarding_system, '_store_progress') as mock_store:
            with patch.object(self.onboarding_system, '_track_onboarding_reset') as mock_track:
                self.onboarding_system.reset_onboarding("user-123")
                
                # Verify progress was stored
                mock_store.assert_called_once()
                args, _ = mock_store.call_args
                reset_progress = args[0]
                
                # Verify reset progress
                self.assertEqual(reset_progress.user_id, "user-123")
                self.assertEqual(reset_progress.flow_id, "standard")
                self.assertEqual(reset_progress.current_step_id, "step1")  # First step
                self.assertEqual(reset_progress.completed_steps, [])
                self.assertFalse(reset_progress.completed)
                
                # Verify analytics were tracked
                mock_track.assert_called_once()
    
    def test_get_personalized_flow(self):
        """Test getting a personalized onboarding flow."""
        # Register multiple flows
        flow1 = OnboardingFlow(flow_id="standard", name="Standard Onboarding")
        flow2 = OnboardingFlow(flow_id="developer", name="Developer Onboarding")
        flow3 = OnboardingFlow(flow_id="admin", name="Admin Onboarding")
        
        self.onboarding_system.register_onboarding_flow(flow1)
        self.onboarding_system.register_onboarding_flow(flow2)
        self.onboarding_system.register_onboarding_flow(flow3)
        
        # Create user profile
        profile = UserProfile(
            user_id="user-123",
            role="developer",
            experience_level="intermediate",
            preferences={"technical_content": True}
        )
        
        # Get personalized flow
        with patch.object(self.onboarding_system, '_get_user_profile') as mock_get_profile:
            mock_get_profile.return_value = profile
            
            flow = self.onboarding_system.get_personalized_flow("user-123")
            
            # Verify flow (should be developer flow based on role)
            self.assertEqual(flow.flow_id, "developer")

class TestOnboardingFlow(unittest.TestCase):
    """Test cases for the OnboardingFlow class."""
    
    def test_flow_creation(self):
        """Test creating an onboarding flow."""
        flow = OnboardingFlow(
            flow_id="standard",
            name="Standard Onboarding",
            description="Standard onboarding flow for new users",
            steps=[
                OnboardingStep(step_id="step1", name="Step 1"),
                OnboardingStep(step_id="step2", name="Step 2")
            ],
            target_roles=["user", "customer"],
            estimated_time=15
        )
        
        self.assertEqual(flow.flow_id, "standard")
        self.assertEqual(flow.name, "Standard Onboarding")
        self.assertEqual(flow.description, "Standard onboarding flow for new users")
        self.assertEqual(len(flow.steps), 2)
        self.assertEqual(flow.steps[0].step_id, "step1")
        self.assertEqual(flow.steps[1].step_id, "step2")
        self.assertEqual(flow.target_roles, ["user", "customer"])
        self.assertEqual(flow.estimated_time, 15)
    
    def test_add_step(self):
        """Test adding a step to a flow."""
        flow = OnboardingFlow(
            flow_id="standard",
            name="Standard Onboarding"
        )
        
        step = OnboardingStep(
            step_id="step1",
            name="Step 1",
            description="First step"
        )
        
        flow.add_step(step)
        
        self.assertEqual(len(flow.steps), 1)
        self.assertEqual(flow.steps[0], step)
    
    def test_get_step(self):
        """Test getting a step by ID."""
        flow = OnboardingFlow(
            flow_id="standard",
            name="Standard Onboarding",
            steps=[
                OnboardingStep(step_id="step1", name="Step 1"),
                OnboardingStep(step_id="step2", name="Step 2")
            ]
        )
        
        step = flow.get_step("step2")
        
        self.assertEqual(step.step_id, "step2")
        self.assertEqual(step.name, "Step 2")
        
        # Test non-existent step
        self.assertIsNone(flow.get_step("non_existent"))
    
    def test_get_next_step(self):
        """Test getting the next step in a flow."""
        flow = OnboardingFlow(
            flow_id="standard",
            name="Standard Onboarding",
            steps=[
                OnboardingStep(step_id="step1", name="Step 1"),
                OnboardingStep(step_id="step2", name="Step 2"),
                OnboardingStep(step_id="step3", name="Step 3")
            ]
        )
        
        # Get next step after step1
        next_step = flow.get_next_step("step1")
        self.assertEqual(next_step.step_id, "step2")
        
        # Get next step after step2
        next_step = flow.get_next_step("step2")
        self.assertEqual(next_step.step_id, "step3")
        
        # Get next step after final step
        next_step = flow.get_next_step("step3")
        self.assertIsNone(next_step)
    
    def test_to_dict(self):
        """Test converting flow to dictionary."""
        flow = OnboardingFlow(
            flow_id="standard",
            name="Standard Onboarding",
            description="Standard onboarding flow for new users",
            steps=[
                OnboardingStep(step_id="step1", name="Step 1"),
                OnboardingStep(step_id="step2", name="Step 2")
            ],
            target_roles=["user", "customer"],
            estimated_time=15
        )
        
        flow_dict = flow.to_dict()
        
        self.assertEqual(flow_dict["flow_id"], "standard")
        self.assertEqual(flow_dict["name"], "Standard Onboarding")
        self.assertEqual(flow_dict["description"], "Standard onboarding flow for new users")
        self.assertEqual(len(flow_dict["steps"]), 2)
        self.assertEqual(flow_dict["steps"][0]["step_id"], "step1")
        self.assertEqual(flow_dict["steps"][1]["step_id"], "step2")
        self.assertEqual(flow_dict["target_roles"], ["user", "customer"])
        self.assertEqual(flow_dict["estimated_time"], 15)
    
    def test_from_dict(self):
        """Test creating flow from dictionary."""
        flow_dict = {
            "flow_id": "standard",
            "name": "Standard Onboarding",
            "description": "Standard onboarding flow for new users",
            "steps": [
                {
                    "step_id": "step1",
                    "name": "Step 1",
                    "description": "First step"
                },
                {
                    "step_id": "step2",
                    "name": "Step 2",
                    "description": "Second step"
                }
            ],
            "target_roles": ["user", "customer"],
            "estimated_time": 15
        }
        
        flow = OnboardingFlow.from_dict(flow_dict)
        
        self.assertEqual(flow.flow_id, "standard")
        self.assertEqual(flow.name, "Standard Onboarding")
        self.assertEqual(flow.description, "Standard onboarding flow for new users")
        self.assertEqual(len(flow.steps), 2)
        self.assertEqual(flow.steps[0].step_id, "step1")
        self.assertEqual(flow.steps[1].step_id, "step2")
        self.assertEqual(flow.target_roles, ["user", "customer"])
        self.assertEqual(flow.estimated_time, 15)

class TestOnboardingStep(unittest.TestCase):
    """Test cases for the OnboardingStep class."""
    
    def test_step_creation(self):
        """Test creating an onboarding step."""
        step = OnboardingStep(
            step_id="welcome",
            name="Welcome",
            description="Welcome to the application",
            content="Welcome to our application! This guide will help you get started.",
            media_url="https://example.com/welcome.mp4",
            estimated_time=5,
            required=True,
            tags=["introduction", "welcome"]
        )
        
        self.assertEqual(step.step_id, "welcome")
        self.assertEqual(step.name, "Welcome")
        self.assertEqual(step.description, "Welcome to the application")
        self.assertEqual(step.content, "Welcome to our application! This guide will help you get started.")
        self.assertEqual(step.media_url, "https://example.com/welcome.mp4")
        self.assertEqual(step.estimated_time, 5)
        self.assertTrue(step.required)
        self.assertEqual(step.tags, ["introduction", "welcome"])
    
    def test_to_dict(self):
        """Test converting step to dictionary."""
        step = OnboardingStep(
            step_id="welcome",
            name="Welcome",
            description="Welcome to the application",
            content="Welcome to our application!",
            media_url="https://example.com/welcome.mp4",
            estimated_time=5,
            required=True,
            tags=["introduction", "welcome"]
        )
        
        step_dict = step.to_dict()
        
        self.assertEqual(step_dict["step_id"], "welcome")
        self.assertEqual(step_dict["name"], "Welcome")
        self.assertEqual(step_dict["description"], "Welcome to the application")
        self.assertEqual(step_dict["content"], "Welcome to our application!")
        self.assertEqual(step_dict["media_url"], "https://example.com/welcome.mp4")
        self.assertEqual(step_dict["estimated_time"], 5)
        self.assertTrue(step_dict["required"])
        self.assertEqual(step_dict["tags"], ["introduction", "welcome"])
    
    def test_from_dict(self):
        """Test creating step from dictionary."""
        step_dict = {
            "step_id": "welcome",
            "name": "Welcome",
            "description": "Welcome to the application",
            "content": "Welcome to our application!",
            "media_url": "https://example.com/welcome.mp4",
            "estimated_time": 5,
            "required": True,
            "tags": ["introduction", "welcome"]
        }
        
        step = OnboardingStep.from_dict(step_dict)
        
        self.assertEqual(step.step_id, "welcome")
        self.assertEqual(step.name, "Welcome")
        self.assertEqual(step.description, "Welcome to the application")
        self.assertEqual(step.content, "Welcome to our application!")
        self.assertEqual(step.media_url, "https://example.com/welcome.mp4")
        self.assertEqual(step.estimated_time, 5)
        self.assertTrue(step.required)
        self.assertEqual(step.tags, ["introduction", "welcome"])

class TestOnboardingProgress(unittest.TestCase):
    """Test cases for the OnboardingProgress class."""
    
    def test_progress_creation(self):
        """Test creating onboarding progress."""
        progress = OnboardingProgress(
            progress_id="progress-123",
            user_id="user-123",
            flow_id="standard",
            current_step_id="step2",
            completed_steps=["step1"],
            completed=False,
            start_time=datetime.datetime(2023, 1, 1, 12, 0),
            last_activity=datetime.datetime(2023, 1, 1, 12, 30)
        )
        
        self.assertEqual(progress.progress_id, "progress-123")
        self.assertEqual(progress.user_id, "user-123")
        self.assertEqual(progress.flow_id, "standard")
        self.assertEqual(progress.current_step_id, "step2")
        self.assertEqual(progress.completed_steps, ["step1"])
        self.assertFalse(progress.completed)
        self.assertEqual(progress.start_time, datetime.datetime(2023, 1, 1, 12, 0))
        self.assertEqual(progress.last_activity, datetime.datetime(2023, 1, 1, 12, 30))
    
    def test_complete_step(self):
        """Test completing a step."""
        progress = OnboardingProgress(
            progress_id="progress-123",
            user_id="user-123",
            flow_id="standard",
            current_step_id="step1",
            completed_steps=[]
        )
        
        # Complete step1 and move to step2
        progress.complete_step("step1", "step2")
        
        self.assertEqual(progress.current_step_id, "step2")
        self.assertEqual(progress.completed_steps, ["step1"])
        self.assertFalse(progress.completed)
        
        # Complete step2 with no next step (final step)
        progress.complete_step("step2", None)
        
        self.assertIsNone(progress.current_step_id)
        self.assertEqual(progress.completed_steps, ["step1", "step2"])
        self.assertTrue(progress.completed)
    
    def test_reset(self):
        """Test resetting progress."""
        progress = OnboardingProgress(
            progress_id="progress-123",
            user_id="user-123",
            flow_id="standard",
            current_step_id="step3",
            completed_steps=["step1", "step2"],
            completed=False
        )
        
        # Reset progress
        progress.reset("step1")
        
        self.assertEqual(progress.current_step_id, "step1")
        self.assertEqual(progress.completed_steps, [])
        self.assertFalse(progress.completed)
    
    def test_to_dict(self):
        """Test converting progress to dictionary."""
        progress = OnboardingProgress(
            progress_id="progress-123",
            user_id="user-123",
            flow_id="standard",
            current_step_id="step2",
            completed_steps=["step1"],
            completed=False,
            start_time=datetime.datetime(2023, 1, 1, 12, 0),
            last_activity=datetime.datetime(2023, 1, 1, 12, 30)
        )
        
        progress_dict = progress.to_dict()
        
        self.assertEqual(progress_dict["progress_id"], "progress-123")
        self.assertEqual(progress_dict["user_id"], "user-123")
        self.assertEqual(progress_dict["flow_id"], "standard")
        self.assertEqual(progress_dict["current_step_id"], "step2")
        self.assertEqual(progress_dict["completed_steps"], ["step1"])
        self.assertFalse(progress_dict["completed"])
        self.assertEqual(progress_dict["start_time"], "2023-01-01T12:00:00")
        self.assertEqual(progress_dict["last_activity"], "2023-01-01T12:30:00")
    
    def test_from_dict(self):
        """Test creating progress from dictionary."""
        progress_dict = {
            "progress_id": "progress-123",
            "user_id": "user-123",
            "flow_id": "standard",
            "current_step_id": "step2",
            "completed_steps": ["step1"],
            "completed": False,
            "start_time": "2023-01-01T12:00:00",
            "last_activity": "2023-01-01T12:30:00"
        }
        
        progress = OnboardingProgress.from_dict(progress_dict)
        
        self.assertEqual(progress.progress_id, "progress-123")
        self.assertEqual(progress.user_id, "user-123")
        self.assertEqual(progress.flow_id, "standard")
        self.assertEqual(progress.current_step_id, "step2")
        self.assertEqual(progress.completed_steps, ["step1"])
        self.assertFalse(progress.completed)
        self.assertEqual(progress.start_time.isoformat(), "2023-01-01T12:00:00")
        self.assertEqual(progress.last_activity.isoformat(), "2023-01-01T12:30:00")

class TestTutorialManager(unittest.TestCase):
    """Test cases for the TutorialManager class."""
    
    def setUp(self):
        """Set up test environment."""
        self.config = OnboardingConfig(
            enabled=True,
            tutorial_enabled=True
        )
        self.tutorial_manager = TutorialManager(self.config)
    
    def test_register_tutorial(self):
        """Test registering a tutorial."""
        tutorial = OnboardingTemplate(
            template_id="git-basics",
            name="Git Basics",
            description="Learn the basics of Git",
            content="# Git Basics\n\nGit is a version control system...",
            media_url="https://example.com/git-basics.mp4",
            estimated_time=15,
            tags=["git", "version-control"]
        )
        
        self.tutorial_manager.register_tutorial(tutorial)
        
        # Verify tutorial was registered
        registered_tutorial = self.tutorial_manager.get_tutorial("git-basics")
        self.assertEqual(registered_tutorial, tutorial)
    
    def test_get_tutorials(self):
        """Test getting all tutorials."""
        # Register multiple tutorials
        tutorial1 = OnboardingTemplate(template_id="git-basics", name="Git Basics")
        tutorial2 = OnboardingTemplate(template_id="docker-intro", name="Docker Introduction")
        tutorial3 = OnboardingTemplate(template_id="python-101", name="Python 101")
        
        self.tutorial_manager.register_tutorial(tutorial1)
        self.tutorial_manager.register_tutorial(tutorial2)
        self.tutorial_manager.register_tutorial(tutorial3)
        
        # Get all tutorials
        tutorials = self.tutorial_manager.get_tutorials()
        
        # Verify tutorials
        self.assertEqual(len(tutorials), 3)
        self.assertIn(tutorial1, tutorials)
        self.assertIn(tutorial2, tutorials)
        self.assertIn(tutorial3, tutorials)
    
    def test_get_tutorials_by_tag(self):
        """Test getting tutorials by tag."""
        # Register tutorials with different tags
        tutorial1 = OnboardingTemplate(
            template_id="git-basics",
            name="Git Basics",
            tags=["git", "version-control"]
        )
        tutorial2 = OnboardingTemplate(
            template_id="docker-intro",
            name="Docker Introduction",
            tags=["docker", "containers"]
        )
        tutorial3 = OnboardingTemplate(
            template_id="git-advanced",
            name="Advanced Git",
            tags=["git", "advanced"]
        )
        
        self.tutorial_manager.register_tutorial(tutorial1)
        self.tutorial_manager.register_tutorial(tutorial2)
        self.tutorial_manager.register_tutorial(tutorial3)
        
        # Get tutorials by tag
        git_tutorials = self.tutorial_manager.get_tutorials_by_tag("git")
        
        # Verify tutorials
        self.assertEqual(len(git_tutorials), 2)
        self.assertIn(tutorial1, git_tutorials)
        self.assertIn(tutorial3, git_tutorials)
    
    @patch('onboarding.onboarding_system.TutorialManager._track_tutorial_view')
    def test_view_tutorial(self, mock_track):
        """Test viewing a tutorial."""
        # Register a tutorial
        tutorial = OnboardingTemplate(
            template_id="git-basics",
            name="Git Basics",
            content="# Git Basics\n\nGit is a version control system..."
        )
        self.tutorial_manager.register_tutorial(tutorial)
        
        # View tutorial
        viewed_tutorial = self.tutorial_manager.view_tutorial(
            user_id="user-123",
            tutorial_id="git-basics"
        )
        
        # Verify tutorial
        self.assertEqual(viewed_tutorial, tutorial)
        
        # Verify analytics were tracked
        mock_track.assert_called_once_with("user-123", "git-basics")

class TestWalkthroughManager(unittest.TestCase):
    """Test cases for the WalkthroughManager class."""
    
    def setUp(self):
        """Set up test environment."""
        self.config = OnboardingConfig(
            enabled=True,
            walkthrough_enabled=True
        )
        self.walkthrough_manager = WalkthroughManager(self.config)
    
    def test_register_walkthrough(self):
        """Test registering a walkthrough."""
        walkthrough = OnboardingTemplate(
            template_id="dashboard-intro",
            name="Dashboard Introduction",
            description="Learn how to use the dashboard",
            content="# Dashboard Introduction\n\nThe dashboard provides...",
            ui_elements=[
                {"selector": "#header", "description": "This is the header"},
                {"selector": "#sidebar", "description": "This is the sidebar"}
            ],
            estimated_time=5
        )
        
        self.walkthrough_manager.register_walkthrough(walkthrough)
        
        # Verify walkthrough was registered
        registered_walkthrough = self.walkthrough_manager.get_walkthrough("dashboard-intro")
        self.assertEqual(registered_walkthrough, walkthrough)
    
    def test_get_walkthroughs(self):
        """Test getting all walkthroughs."""
        # Register multiple walkthroughs
        walkthrough1 = OnboardingTemplate(template_id="dashboard-intro", name="Dashboard Introduction")
        walkthrough2 = OnboardingTemplate(template_id="profile-setup", name="Profile Setup")
        walkthrough3 = OnboardingTemplate(template_id="project-creation", name="Project Creation")
        
        self.walkthrough_manager.register_walkthrough(walkthrough1)
        self.walkthrough_manager.register_walkthrough(walkthrough2)
        self.walkthrough_manager.register_walkthrough(walkthrough3)
        
        # Get all walkthroughs
        walkthroughs = self.walkthrough_manager.get_walkthroughs()
        
        # Verify walkthroughs
        self.assertEqual(len(walkthroughs), 3)
        self.assertIn(walkthrough1, walkthroughs)
        self.assertIn(walkthrough2, walkthroughs)
        self.assertIn(walkthrough3, walkthroughs)
    
    def test_get_walkthrough_for_page(self):
        """Test getting walkthrough for a specific page."""
        # Register walkthroughs for different pages
        walkthrough1 = OnboardingTemplate(
            template_id="dashboard-intro",
            name="Dashboard Introduction",
            page_url="/dashboard"
        )
        walkthrough2 = OnboardingTemplate(
            template_id="profile-setup",
            name="Profile Setup",
            page_url="/profile"
        )
        
        self.walkthrough_manager.register_walkthrough(walkthrough1)
        self.walkthrough_manager.register_walkthrough(walkthrough2)
        
        # Get walkthrough for page
        dashboard_walkthrough = self.walkthrough_manager.get_walkthrough_for_page("/dashboard")
        
        # Verify walkthrough
        self.assertEqual(dashboard_walkthrough, walkthrough1)
    
    @patch('onboarding.onboarding_system.WalkthroughManager._track_walkthrough_start')
    def test_start_walkthrough(self, mock_track):
        """Test starting a walkthrough."""
        # Register a walkthrough
        walkthrough = OnboardingTemplate(
            template_id="dashboard-intro",
            name="Dashboard Introduction",
            ui_elements=[
                {"selector": "#header", "description": "This is the header"},
                {"selector": "#sidebar", "description": "This is the sidebar"}
            ]
        )
        self.walkthrough_manager.register_walkthrough(walkthrough)
        
        # Start walkthrough
        with patch.object(self.walkthrough_manager, '_store_walkthrough_progress') as mock_store:
            progress = self.walkthrough_manager.start_walkthrough(
                user_id="user-123",
                walkthrough_id="dashboard-intro"
            )
            
            # Verify progress
            self.assertEqual(progress.user_id, "user-123")
            self.assertEqual(progress.template_id, "dashboard-intro")
            self.assertEqual(progress.current_step, 0)
            self.assertFalse(progress.completed)
            
            # Verify progress was stored
            mock_store.assert_called_once()
            
            # Verify analytics were tracked
            mock_track.assert_called_once_with("user-123", "dashboard-intro")
    
    @patch('onboarding.onboarding_system.WalkthroughManager._load_walkthrough_progress')
    @patch('onboarding.onboarding_system.WalkthroughManager._track_walkthrough_step')
    def test_next_walkthrough_step(self, mock_track, mock_load):
        """Test advancing to the next walkthrough step."""
        # Register a walkthrough
        walkthrough = OnboardingTemplate(
            template_id="dashboard-intro",
            name="Dashboard Introduction",
            ui_elements=[
                {"selector": "#header", "description": "This is the header"},
                {"selector": "#sidebar", "description": "This is the sidebar"},
                {"selector": "#content", "description": "This is the content area"}
            ]
        )
        self.walkthrough_manager.register_walkthrough(walkthrough)
        
        # Mock loaded progress
        mock_progress = MagicMock(
            user_id="user-123",
            template_id="dashboard-intro",
            current_step=0,
            completed=False
        )
        mock_load.return_value = mock_progress
        
        # Advance to next step
        with patch.object(self.walkthrough_manager, '_store_walkthrough_progress') as mock_store:
            step = self.walkthrough_manager.next_walkthrough_step(
                user_id="user-123",
                walkthrough_id="dashboard-intro"
            )
            
            # Verify step
            self.assertEqual(step["selector"], "#sidebar")
            self.assertEqual(step["description"], "This is the sidebar")
            
            # Verify progress was updated
            self.assertEqual(mock_progress.current_step, 1)
            
            # Verify progress was stored
            mock_store.assert_called_once()
            
            # Verify analytics were tracked
            mock_track.assert_called_once()

class TestOnboardingAnalytics(unittest.TestCase):
    """Test cases for the OnboardingAnalytics class."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = OnboardingConfig(
            enabled=True,
            data_directory=self.temp_dir,
            analytics_enabled=True
        )
        self.analytics = OnboardingAnalytics(self.config)
    
    @patch('onboarding.onboarding_system.os.path.exists')
    @patch('onboarding.onboarding_system.os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    def test_track_event(self, mock_file, mock_makedirs, mock_exists):
        """Test tracking an onboarding event."""
        # Mock path exists
        mock_exists.return_value = False
        
        # Track event
        self.analytics.track_event(
            event_type="flow_start",
            user_id="user-123",
            properties={
                "flow_id": "standard",
                "timestamp": datetime.datetime.now().isoformat()
            }
        )
        
        # Verify event was tracked
        mock_makedirs.assert_called_once()
        mock_file.assert_called_once()
        mock_file().write.assert_called_once()
    
    @patch('onboarding.onboarding_system.glob.glob')
    @patch('builtins.open', new_callable=mock_open)
    def test_get_events(self, mock_file, mock_glob):
        """Test getting onboarding events."""
        # Mock glob to return file paths
        mock_glob.return_value = [
            os.path.join(self.temp_dir, "analytics", "2023-01-01", "event1.json"),
            os.path.join(self.temp_dir, "analytics", "2023-01-01", "event2.json")
        ]
        
        # Mock file content
        mock_file.return_value.__enter__.return_value.read.side_effect = [
            json.dumps({
                "event_type": "flow_start",
                "user_id": "user-123",
                "properties": {"flow_id": "standard"},
                "timestamp": "2023-01-01T12:00:00"
            }),
            json.dumps({
                "event_type": "step_complete",
                "user_id": "user-123",
                "properties": {"step_id": "step1"},
                "timestamp": "2023-01-01T12:05:00"
            })
        ]
        
        # Get events
        start_date = datetime.datetime(2023, 1, 1)
        end_date = datetime.datetime(2023, 1, 2)
        events = self.analytics.get_events(
            start_date=start_date,
            end_date=end_date,
            event_type="flow_start"
        )
        
        # Verify events
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["event_type"], "flow_start")
        self.assertEqual(events[0]["user_id"], "user-123")
        
        # Get all events
        all_events = self.analytics.get_events(
            start_date=start_date,
            end_date=end_date
        )
        
        # Verify all events
        self.assertEqual(len(all_events), 2)
    
    @patch('onboarding.onboarding_system.OnboardingAnalytics.get_events')
    def test_get_completion_rate(self, mock_get_events):
        """Test getting flow completion rate."""
        # Mock events
        mock_get_events.side_effect = [
            # Flow start events
            [
                {"user_id": "user1", "properties": {"flow_id": "standard"}},
                {"user_id": "user2", "properties": {"flow_id": "standard"}},
                {"user_id": "user3", "properties": {"flow_id": "standard"}},
                {"user_id": "user4", "properties": {"flow_id": "standard"}}
            ],
            # Flow complete events
            [
                {"user_id": "user1", "properties": {"flow_id": "standard"}},
                {"user_id": "user2", "properties": {"flow_id": "standard"}}
            ]
        ]
        
        # Get completion rate
        rate = self.analytics.get_completion_rate(
            flow_id="standard",
            start_date=datetime.datetime(2023, 1, 1),
            end_date=datetime.datetime(2023, 1, 31)
        )
        
        # Verify rate (2 completed out of 4 started = 50%)
        self.assertEqual(rate, 50.0)
    
    @patch('onboarding.onboarding_system.OnboardingAnalytics.get_events')
    def test_get_average_completion_time(self, mock_get_events):
        """Test getting average flow completion time."""
        # Mock events
        mock_get_events.return_value = [
            {
                "user_id": "user1",
                "properties": {
                    "flow_id": "standard",
                    "start_time": "2023-01-01T12:00:00",
                    "end_time": "2023-01-01T12:30:00"  # 30 minutes
                }
            },
            {
                "user_id": "user2",
                "properties": {
                    "flow_id": "standard",
                    "start_time": "2023-01-02T10:00:00",
                    "end_time": "2023-01-02T11:00:00"  # 60 minutes
                }
            }
        ]
        
        # Get average completion time
        avg_time = self.analytics.get_average_completion_time(
            flow_id="standard",
            start_date=datetime.datetime(2023, 1, 1),
            end_date=datetime.datetime(2023, 1, 31)
        )
        
        # Verify average time (30 + 60) / 2 = 45 minutes
        self.assertEqual(avg_time, 45.0)
    
    @patch('onboarding.onboarding_system.OnboardingAnalytics.get_events')
    def test_get_step_completion_rates(self, mock_get_events):
        """Test getting step completion rates."""
        # Mock events
        mock_get_events.side_effect = [
            # Flow start events
            [
                {"user_id": "user1", "properties": {"flow_id": "standard"}},
                {"user_id": "user2", "properties": {"flow_id": "standard"}},
                {"user_id": "user3", "properties": {"flow_id": "standard"}},
                {"user_id": "user4", "properties": {"flow_id": "standard"}}
            ],
            # Step complete events
            [
                {"user_id": "user1", "properties": {"flow_id": "standard", "step_id": "step1"}},
                {"user_id": "user2", "properties": {"flow_id": "standard", "step_id": "step1"}},
                {"user_id": "user3", "properties": {"flow_id": "standard", "step_id": "step1"}},
                {"user_id": "user1", "properties": {"flow_id": "standard", "step_id": "step2"}},
                {"user_id": "user2", "properties": {"flow_id": "standard", "step_id": "step2"}},
                {"user_id": "user1", "properties": {"flow_id": "standard", "step_id": "step3"}}
            ]
        ]
        
        # Get step completion rates
        rates = self.analytics.get_step_completion_rates(
            flow_id="standard",
            start_date=datetime.datetime(2023, 1, 1),
            end_date=datetime.datetime(2023, 1, 31)
        )
        
        # Verify rates
        self.assertEqual(rates["step1"], 75.0)  # 3 out of 4 users
        self.assertEqual(rates["step2"], 50.0)  # 2 out of 4 users
        self.assertEqual(rates["step3"], 25.0)  # 1 out of 4 users

if __name__ == '__main__':
    unittest.main()
