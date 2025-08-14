"""
Unit Tests for Visual Troubleshooter Module

This module contains unit tests for the VisualTroubleshooter class in the
visual_troubleshooter.py module.

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
from video.visual_troubleshooter import VisualTroubleshooter, TroubleshootingState
from video.video_processor import VideoProcessor, VideoState

class TestVisualTroubleshooter(unittest.TestCase):
    """Test cases for the VisualTroubleshooter class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock video processor
        self.video_processor = MagicMock(spec=VideoProcessor)
        self.video_processor.state = VideoState.IDLE
        
        # Create the troubleshooter
        self.troubleshooter = VisualTroubleshooter(self.video_processor)
        
        # Create a mock frame for testing
        self.mock_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        # Add some content to the frame to make it testable
        cv2.rectangle(self.mock_frame, (100, 100), (300, 300), (0, 255, 0), 2)
        cv2.putText(self.mock_frame, "Test Frame", (150, 150), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # Configure video processor mock
        async def mock_get_frame():
            return self.mock_frame
        
        self.video_processor.get_frame = mock_get_frame
        self.video_processor.initialize = MagicMock(return_value=asyncio.Future())
        self.video_processor.initialize.return_value.set_result(True)
        self.video_processor.start_capture = MagicMock(return_value=asyncio.Future())
        self.video_processor.start_capture.return_value.set_result(True)
        self.video_processor.stop_capture = MagicMock(return_value=asyncio.Future())
        self.video_processor.stop_capture.return_value.set_result(True)
    
    async def test_analyze_camera(self):
        """Test analyzing camera functionality."""
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
        
        # Mock the analysis complete callback
        analysis_complete_callback = MagicMock()
        self.troubleshooter.register_callback("on_analysis_complete", analysis_complete_callback)
        
        # Analyze camera
        results = await self.troubleshooter.analyze_camera()
        
        # Verify results
        self.assertEqual(self.troubleshooter.state, TroubleshootingState.IDLE)
        self.assertIn("brightness", results)
        self.assertIn("contrast", results)
        self.assertIn("focus_score", results)
        self.assertIn("faces_detected", results)
        self.assertIn("resolution", results)
        self.assertIn("quality_score", results)
        
        # Verify video processor methods were called
        self.video_processor.initialize.assert_called_once()
        self.video_processor.start_capture.assert_called_once()
        self.video_processor.get_frame.assert_called_once()
        self.video_processor.stop_capture.assert_called_once()
        
        # Verify callback was called
        # Note: In the actual implementation, this would be awaited
        # but for testing purposes we're just checking if it was called
        self.assertTrue(analysis_complete_callback.called)
    
    async def test_analyze_qr_code_detected(self):
        """Test analyzing QR code when one is detected."""
        # Mock the QR detector
        with patch.object(self.troubleshooter, '_qr_detector') as mock_qr_detector:
            mock_qr_detector.detectAndDecode.return_value = ("test_data", np.array([[0, 0], [100, 0], [100, 100], [0, 100]]), None)
            
            # Mock the analysis complete callback
            analysis_complete_callback = MagicMock()
            self.troubleshooter.register_callback("on_analysis_complete", analysis_complete_callback)
            
            # Analyze QR code
            results = await self.troubleshooter.analyze_qr_code()
            
            # Verify results
            self.assertEqual(self.troubleshooter.state, TroubleshootingState.IDLE)
            self.assertTrue(results["detected"])
            self.assertEqual(results["data"], "test_data")
            self.assertIsNotNone(results["points"])
            
            # Verify video processor methods were called
            self.video_processor.initialize.assert_called_once()
            self.video_processor.start_capture.assert_called_once()
            self.video_processor.get_frame.assert_called_once()
            self.video_processor.stop_capture.assert_called_once()
            
            # Verify callback was called
            self.assertTrue(analysis_complete_callback.called)
    
    async def test_analyze_qr_code_not_detected(self):
        """Test analyzing QR code when none is detected."""
        # Mock the QR detector
        with patch.object(self.troubleshooter, '_qr_detector') as mock_qr_detector:
            mock_qr_detector.detectAndDecode.return_value = ("", None, None)
            
            # Mock the analysis complete callback
            analysis_complete_callback = MagicMock()
            self.troubleshooter.register_callback("on_analysis_complete", analysis_complete_callback)
            
            # Analyze QR code
            results = await self.troubleshooter.analyze_qr_code()
            
            # Verify results
            self.assertEqual(self.troubleshooter.state, TroubleshootingState.IDLE)
            self.assertFalse(results["detected"])
            self.assertIn("error", results)
            
            # Verify video processor methods were called
            self.video_processor.initialize.assert_called_once()
            self.video_processor.start_capture.assert_called_once()
            self.video_processor.get_frame.assert_called()
            self.video_processor.stop_capture.assert_called_once()
            
            # Verify callback was called
            self.assertTrue(analysis_complete_callback.called)
    
    async def test_analyze_hardware_issue(self):
        """Test analyzing hardware issues."""
        # Mock the issue analysis methods
        self.troubleshooter._analyze_display_issue = MagicMock(return_value=asyncio.Future())
        self.troubleshooter._analyze_display_issue.return_value.set_result({
            "detected": True,
            "issue_type": "display",
            "confidence": 0.85,
            "details": "Screen flickering detected",
            "recommendation": "Check display cable connection"
        })
        
        # Mock the analysis complete callback
        analysis_complete_callback = MagicMock()
        self.troubleshooter.register_callback("on_analysis_complete", analysis_complete_callback)
        
        # Analyze hardware issue
        results = await self.troubleshooter.analyze_hardware_issue("display")
        
        # Verify results
        self.assertEqual(self.troubleshooter.state, TroubleshootingState.IDLE)
        self.assertTrue(results["detected"])
        self.assertEqual(results["issue_type"], "display")
        self.assertIn("confidence", results)
        self.assertIn("details", results)
        self.assertIn("recommendation", results)
        
        # Verify video processor methods were called
        self.video_processor.initialize.assert_called_once()
        self.video_processor.start_capture.assert_called_once()
        self.video_processor.get_frame.assert_called_once()
        self.video_processor.stop_capture.assert_called_once()
        
        # Verify callback was called
        self.assertTrue(analysis_complete_callback.called)
    
    async def test_generate_troubleshooting_report(self):
        """Test generating a troubleshooting report."""
        # Set up analysis results
        self.troubleshooter._analysis_results = {
            "camera": {
                "brightness": 0.2,
                "contrast": 0.7,
                "focus_score": 0.4,
                "faces_detected": 0,
                "resolution": "640x480",
                "quality_score": 0.6
            },
            "hardware_issues": {
                "display": {
                    "detected": True,
                    "issue_type": "display",
                    "confidence": 0.85,
                    "details": "Screen flickering detected",
                    "recommendation": "Check display cable connection"
                }
            }
        }
        
        # Generate report
        report = await self.troubleshooter.generate_troubleshooting_report()
        
        # Verify report
        self.assertEqual(self.troubleshooter.state, TroubleshootingState.IDLE)
        self.assertIn("timestamp", report)
        self.assertIn("date", report)
        self.assertIn("analyses", report)
        self.assertIn("recommendations", report)
        
        # Verify recommendations
        self.assertEqual(len(report["recommendations"]), 2)  # Low brightness and display issue
        
        # Check for specific recommendations
        recommendation_issues = [rec["issue"] for rec in report["recommendations"]]
        self.assertIn("Low lighting", recommendation_issues)
        self.assertIn("Display detected", recommendation_issues)
    
    async def test_error_handling(self):
        """Test error handling during analysis."""
        # Configure video processor to raise an exception
        self.video_processor.get_frame = MagicMock(side_effect=Exception("Test exception"))
        
        # Mock the error callback
        error_callback = MagicMock()
        self.troubleshooter.register_callback("on_error", error_callback)
        
        # Analyze camera
        results = await self.troubleshooter.analyze_camera()
        
        # Verify results
        self.assertEqual(self.troubleshooter.state, TroubleshootingState.ERROR)
        self.assertIn("error", results)
        
        # Verify error callback was called
        self.assertTrue(error_callback.called)

# Run the tests
if __name__ == '__main__':
    unittest.main()
