"""
Integration Tests for Video and Visual Support

This module contains integration tests for the video and visual support components
of the Dr. TARDIS Gemini Live API integration.

Author: ApexAgent Development Team
Date: May 26, 2025
"""

import asyncio
import cv2
import numpy as np
import os
import pytest
import tempfile
import time
import unittest
from unittest.mock import MagicMock, patch

import sys
sys.path.append('/home/ubuntu/gemini_live_integration/src')
from video.video_processor import VideoProcessor, VideoState
from video.visual_troubleshooter import VisualTroubleshooter, TroubleshootingState
from video.screen_sharing import ScreenSharing, ScreenShareState, AnnotationType

class TestVideoIntegration(unittest.TestCase):
    """Integration tests for video and visual support components."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create components
        self.video_processor = VideoProcessor(device_id=0, width=640, height=480, fps=30)
        self.troubleshooter = VisualTroubleshooter(self.video_processor)
        self.screen_sharing = ScreenSharing(width=1280, height=720, fps=15)
        
        # Create a mock frame for testing
        self.mock_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        # Add some content to the frame to make it testable
        cv2.rectangle(self.mock_frame, (100, 100), (300, 300), (0, 255, 0), 2)
        cv2.putText(self.mock_frame, "Test Frame", (150, 150), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.video_processor.close()
    
    @patch('cv2.VideoCapture')
    async def test_video_processor_to_troubleshooter(self, mock_video_capture):
        """Test integration between VideoProcessor and VisualTroubleshooter."""
        # Configure mock
        mock_instance = mock_video_capture.return_value
        mock_instance.isOpened.return_value = True
        mock_instance.read.return_value = (True, self.mock_frame)
        mock_instance.get.return_value = 30  # fps
        
        # Initialize video processor
        await self.video_processor.initialize()
        
        # Mock the _analyze_camera_frame method
        self.troubleshooter._analyze_camera_frame = MagicMock(return_value=asyncio.Future())
        self.troubleshooter._analyze_camera_frame.return_value.set_result({
            "brightness": 0.5,
            "contrast": 0.7,
            "focus_score": 0.8,
            "faces_detected": 0,
            "resolution": "640x480",
            "quality_score": 0.75
        })
        
        # Analyze camera
        results = await self.troubleshooter.analyze_camera()
        
        # Verify results
        self.assertEqual(self.troubleshooter.state, TroubleshootingState.IDLE)
        self.assertIn("brightness", results)
        self.assertIn("contrast", results)
        self.assertIn("focus_score", results)
        self.assertIn("resolution", results)
    
    @patch('cv2.VideoCapture')
    @patch('pyautogui.screenshot')
    async def test_video_processor_and_screen_sharing(self, mock_screenshot, mock_video_capture):
        """Test integration between VideoProcessor and ScreenSharing."""
        # Configure mocks
        mock_video_capture_instance = mock_video_capture.return_value
        mock_video_capture_instance.isOpened.return_value = True
        mock_video_capture_instance.read.return_value = (True, self.mock_frame)
        mock_video_capture_instance.get.return_value = 30  # fps
        
        mock_screenshot.return_value = MagicMock()
        mock_screenshot.return_value.tobytes.return_value = b'test'
        
        # Initialize video processor
        await self.video_processor.initialize()
        
        # Mock the _capture_screen method to avoid actual screen capture
        self.screen_sharing._capture_screen = MagicMock(return_value=None)
        
        # Start screen sharing
        await self.screen_sharing.start_sharing()
        
        # Set state directly since we mocked _capture_screen
        self.screen_sharing.state = ScreenShareState.CAPTURING
        
        # Add a frame to the screen sharing buffer
        self.screen_sharing._frame_buffer.append(self.mock_frame)
        
        # Start annotation
        await self.screen_sharing.start_annotation(
            AnnotationType.RECTANGLE,
            {
                "color": (255, 0, 0),
                "thickness": 2
            }
        )
        
        # Update annotation
        await self.screen_sharing.update_annotation((200, 200))
        await self.screen_sharing.update_annotation((400, 400))
        
        # Finish annotation
        await self.screen_sharing.finish_annotation()
        
        # Get annotated frame
        annotated_frame = await self.screen_sharing.get_annotated_frame()
        
        # Verify results
        self.assertIsNotNone(annotated_frame)
        self.assertEqual(annotated_frame.shape, (480, 640, 3))
        
        # Stop screen sharing
        await self.screen_sharing.stop_sharing()
        self.assertEqual(self.screen_sharing.state, ScreenShareState.IDLE)
    
    @patch('cv2.VideoCapture')
    async def test_troubleshooter_report_generation(self, mock_video_capture):
        """Test troubleshooter report generation with video processor."""
        # Configure mock
        mock_instance = mock_video_capture.return_value
        mock_instance.isOpened.return_value = True
        mock_instance.read.return_value = (True, self.mock_frame)
        mock_instance.get.return_value = 30  # fps
        
        # Initialize video processor
        await self.video_processor.initialize()
        
        # Mock the analysis methods
        self.troubleshooter._analyze_camera_frame = MagicMock(return_value=asyncio.Future())
        self.troubleshooter._analyze_camera_frame.return_value.set_result({
            "brightness": 0.2,  # Low brightness to trigger recommendation
            "contrast": 0.7,
            "focus_score": 0.4,  # Low focus to trigger recommendation
            "faces_detected": 0,
            "resolution": "640x480",
            "quality_score": 0.6
        })
        
        self.troubleshooter._analyze_display_issue = MagicMock(return_value=asyncio.Future())
        self.troubleshooter._analyze_display_issue.return_value.set_result({
            "detected": True,
            "issue_type": "display",
            "confidence": 0.85,
            "details": "Screen flickering detected",
            "recommendation": "Check display cable connection"
        })
        
        # Perform analyses
        camera_results = await self.troubleshooter.analyze_camera()
        self.troubleshooter._analysis_results["camera"] = camera_results
        
        display_results = await self.troubleshooter.analyze_hardware_issue("display")
        if "hardware_issues" not in self.troubleshooter._analysis_results:
            self.troubleshooter._analysis_results["hardware_issues"] = {}
        self.troubleshooter._analysis_results["hardware_issues"]["display"] = display_results
        
        # Generate report
        report = await self.troubleshooter.generate_troubleshooting_report()
        
        # Verify report
        self.assertIn("timestamp", report)
        self.assertIn("date", report)
        self.assertIn("analyses", report)
        self.assertIn("recommendations", report)
        
        # Verify recommendations
        self.assertGreaterEqual(len(report["recommendations"]), 2)  # At least low brightness and display issue
        
        # Check for specific recommendations
        recommendation_issues = [rec["issue"] for rec in report["recommendations"]]
        self.assertIn("Low lighting", recommendation_issues)
        self.assertIn("Poor focus", recommendation_issues)
        self.assertIn("Display detected", recommendation_issues)
    
    @patch('cv2.VideoCapture')
    @patch('pyautogui.screenshot')
    async def test_end_to_end_workflow(self, mock_screenshot, mock_video_capture):
        """Test end-to-end workflow with all components."""
        # Configure mocks
        mock_video_capture_instance = mock_video_capture.return_value
        mock_video_capture_instance.isOpened.return_value = True
        mock_video_capture_instance.read.return_value = (True, self.mock_frame)
        mock_video_capture_instance.get.return_value = 30  # fps
        
        mock_screenshot.return_value = MagicMock()
        mock_screenshot.return_value.tobytes.return_value = b'test'
        
        # Initialize video processor
        await self.video_processor.initialize()
        
        # Start video capture
        await self.video_processor.start_capture()
        
        # Analyze camera
        self.troubleshooter._analyze_camera_frame = MagicMock(return_value=asyncio.Future())
        self.troubleshooter._analyze_camera_frame.return_value.set_result({
            "brightness": 0.5,
            "contrast": 0.7,
            "focus_score": 0.8,
            "faces_detected": 0,
            "resolution": "640x480",
            "quality_score": 0.75
        })
        
        camera_results = await self.troubleshooter.analyze_camera()
        self.troubleshooter._analysis_results["camera"] = camera_results
        
        # Stop video capture
        await self.video_processor.stop_capture()
        
        # Start screen sharing
        self.screen_sharing._capture_screen = MagicMock(return_value=None)
        await self.screen_sharing.start_sharing()
        
        # Set state directly since we mocked _capture_screen
        self.screen_sharing.state = ScreenShareState.CAPTURING
        
        # Add a frame to the screen sharing buffer
        self.screen_sharing._frame_buffer.append(self.mock_frame)
        
        # Create annotations
        await self.screen_sharing.start_annotation(
            AnnotationType.RECTANGLE,
            {
                "color": (255, 0, 0),
                "thickness": 2
            }
        )
        
        await self.screen_sharing.update_annotation((200, 200))
        await self.screen_sharing.update_annotation((400, 400))
        await self.screen_sharing.finish_annotation()
        
        # Create a temporary file for saving
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            # Save annotated frame
            result = await self.screen_sharing.save_frame(temp_path, include_annotations=True)
            
            # Verify results
            self.assertTrue(result)
            self.assertTrue(os.path.exists(temp_path))
            self.assertTrue(os.path.getsize(temp_path) > 0)
            
            # Stop screen sharing
            await self.screen_sharing.stop_sharing()
            self.assertEqual(self.screen_sharing.state, ScreenShareState.IDLE)
            
            # Generate troubleshooting report
            report = await self.troubleshooter.generate_troubleshooting_report()
            
            # Verify report
            self.assertIn("timestamp", report)
            self.assertIn("date", report)
            self.assertIn("analyses", report)
            
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)

# Run the tests
if __name__ == '__main__':
    unittest.main()
