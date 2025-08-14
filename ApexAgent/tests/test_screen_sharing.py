"""
Unit Tests for Screen Sharing Module

This module contains unit tests for the ScreenSharing class in the
screen_sharing.py module.

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
from video.screen_sharing import ScreenSharing, ScreenShareState, AnnotationType

class TestScreenSharing(unittest.TestCase):
    """Test cases for the ScreenSharing class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.screen_sharing = ScreenSharing(width=1280, height=720, fps=15)
        
        # Create a mock frame for testing
        self.mock_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        # Add some content to the frame to make it testable
        cv2.rectangle(self.mock_frame, (200, 200), (600, 500), (0, 255, 0), 2)
        cv2.putText(self.mock_frame, "Test Screen", (300, 300), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    @patch('pyautogui.screenshot')
    async def test_start_sharing(self, mock_screenshot):
        """Test starting screen sharing."""
        # Configure mock
        mock_screenshot.return_value = MagicMock()
        mock_screenshot.return_value.tobytes.return_value = b'test'
        
        # Mock the _capture_screen method to avoid actual screen capture
        self.screen_sharing._capture_screen = MagicMock(return_value=None)
        
        # Start sharing
        result = await self.screen_sharing.start_sharing()
        
        # Verify results
        self.assertTrue(result)
        self.assertEqual(self.screen_sharing.state, ScreenShareState.CAPTURING)
    
    async def test_stop_sharing(self):
        """Test stopping screen sharing."""
        # Mock the _capture_screen method to avoid actual screen capture
        self.screen_sharing._capture_screen = MagicMock(return_value=None)
        
        # Start sharing
        await self.screen_sharing.start_sharing()
        
        # Set state directly since we mocked _capture_screen
        self.screen_sharing.state = ScreenShareState.CAPTURING
        
        # Stop sharing
        result = await self.screen_sharing.stop_sharing()
        
        # Verify results
        self.assertTrue(result)
        self.assertEqual(self.screen_sharing.state, ScreenShareState.IDLE)
    
    async def test_get_frame(self):
        """Test getting a frame."""
        # Add a frame to the buffer
        self.screen_sharing._frame_buffer.append(self.mock_frame)
        
        # Get the frame
        frame = await self.screen_sharing.get_frame()
        
        # Verify results
        self.assertIsNotNone(frame)
        self.assertEqual(frame.shape, (720, 1280, 3))
    
    async def test_get_annotated_frame_no_annotations(self):
        """Test getting an annotated frame with no annotations."""
        # Add a frame to the buffer
        self.screen_sharing._frame_buffer.append(self.mock_frame)
        
        # Get the annotated frame
        frame = await self.screen_sharing.get_annotated_frame()
        
        # Verify results
        self.assertIsNotNone(frame)
        self.assertEqual(frame.shape, (720, 1280, 3))
    
    async def test_get_annotated_frame_with_annotations(self):
        """Test getting an annotated frame with annotations."""
        # Add a frame to the buffer
        self.screen_sharing._frame_buffer.append(self.mock_frame)
        
        # Add an annotation
        self.screen_sharing._annotations.append({
            "type": AnnotationType.RECTANGLE.value,
            "properties": {
                "color": (255, 0, 0),
                "thickness": 2
            },
            "points": [(300, 300), (500, 500)]
        })
        
        # Mock the _draw_annotation method
        self.screen_sharing._draw_annotation = MagicMock()
        
        # Get the annotated frame
        frame = await self.screen_sharing.get_annotated_frame()
        
        # Verify results
        self.assertIsNotNone(frame)
        self.assertEqual(frame.shape, (720, 1280, 3))
        self.screen_sharing._draw_annotation.assert_called_once()
    
    async def test_save_frame(self):
        """Test saving a frame to a file."""
        # Add a frame to the buffer
        self.screen_sharing._frame_buffer.append(self.mock_frame)
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            # Save the frame
            result = await self.screen_sharing.save_frame(temp_path, include_annotations=False)
            
            # Verify results
            self.assertTrue(result)
            self.assertTrue(os.path.exists(temp_path))
            self.assertTrue(os.path.getsize(temp_path) > 0)
            
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    async def test_start_annotation(self):
        """Test starting an annotation."""
        # Start annotation
        result = await self.screen_sharing.start_annotation(
            AnnotationType.RECTANGLE,
            {
                "color": (255, 0, 0),
                "thickness": 2
            }
        )
        
        # Verify results
        self.assertFalse(result)  # Should fail because not in CAPTURING state
        
        # Set state to CAPTURING
        self.screen_sharing.state = ScreenShareState.CAPTURING
        
        # Start annotation again
        result = await self.screen_sharing.start_annotation(
            AnnotationType.RECTANGLE,
            {
                "color": (255, 0, 0),
                "thickness": 2
            }
        )
        
        # Verify results
        self.assertTrue(result)
        self.assertEqual(self.screen_sharing.state, ScreenShareState.ANNOTATING)
        self.assertIsNotNone(self.screen_sharing._current_annotation)
        self.assertEqual(self.screen_sharing._current_annotation["type"], AnnotationType.RECTANGLE.value)
        self.assertEqual(self.screen_sharing._current_annotation["properties"]["color"], (255, 0, 0))
        self.assertEqual(self.screen_sharing._current_annotation["properties"]["thickness"], 2)
    
    async def test_update_annotation(self):
        """Test updating an annotation."""
        # Set state to ANNOTATING and create current annotation
        self.screen_sharing.state = ScreenShareState.ANNOTATING
        self.screen_sharing._current_annotation = {
            "type": AnnotationType.RECTANGLE.value,
            "properties": {
                "color": (255, 0, 0),
                "thickness": 2
            },
            "points": []
        }
        
        # Update annotation
        result = await self.screen_sharing.update_annotation((300, 300))
        
        # Verify results
        self.assertTrue(result)
        self.assertEqual(len(self.screen_sharing._current_annotation["points"]), 1)
        self.assertEqual(self.screen_sharing._current_annotation["points"][0], (300, 300))
    
    async def test_finish_annotation(self):
        """Test finishing an annotation."""
        # Set state to ANNOTATING and create current annotation
        self.screen_sharing.state = ScreenShareState.ANNOTATING
        self.screen_sharing._current_annotation = {
            "type": AnnotationType.RECTANGLE.value,
            "properties": {
                "color": (255, 0, 0),
                "thickness": 2
            },
            "points": [(300, 300), (500, 500)]
        }
        
        # Finish annotation
        result = await self.screen_sharing.finish_annotation()
        
        # Verify results
        self.assertTrue(result)
        self.assertEqual(self.screen_sharing.state, ScreenShareState.CAPTURING)
        self.assertIsNone(self.screen_sharing._current_annotation)
        self.assertEqual(len(self.screen_sharing._annotations), 1)
        self.assertEqual(self.screen_sharing._annotations[0]["type"], AnnotationType.RECTANGLE.value)
        self.assertEqual(len(self.screen_sharing._annotations[0]["points"]), 2)
    
    async def test_cancel_annotation(self):
        """Test cancelling an annotation."""
        # Set state to ANNOTATING and create current annotation
        self.screen_sharing.state = ScreenShareState.ANNOTATING
        self.screen_sharing._current_annotation = {
            "type": AnnotationType.RECTANGLE.value,
            "properties": {
                "color": (255, 0, 0),
                "thickness": 2
            },
            "points": [(300, 300), (500, 500)]
        }
        
        # Cancel annotation
        result = await self.screen_sharing.cancel_annotation()
        
        # Verify results
        self.assertTrue(result)
        self.assertEqual(self.screen_sharing.state, ScreenShareState.CAPTURING)
        self.assertIsNone(self.screen_sharing._current_annotation)
        self.assertEqual(len(self.screen_sharing._annotations), 0)
    
    async def test_clear_annotations(self):
        """Test clearing all annotations."""
        # Add some annotations
        self.screen_sharing._annotations = [
            {
                "type": AnnotationType.RECTANGLE.value,
                "properties": {
                    "color": (255, 0, 0),
                    "thickness": 2
                },
                "points": [(300, 300), (500, 500)]
            },
            {
                "type": AnnotationType.CIRCLE.value,
                "properties": {
                    "color": (0, 255, 0),
                    "thickness": 2
                },
                "points": [(400, 400), (450, 450)]
            }
        ]
        
        # Clear annotations
        result = await self.screen_sharing.clear_annotations()
        
        # Verify results
        self.assertTrue(result)
        self.assertEqual(len(self.screen_sharing._annotations), 0)
    
    async def test_callbacks(self):
        """Test callback registration and invocation."""
        # Create mock callbacks
        frame_callback = MagicMock()
        error_callback = MagicMock()
        state_change_callback = MagicMock()
        
        # Register callbacks
        self.screen_sharing.register_callback("on_frame", frame_callback)
        self.screen_sharing.register_callback("on_error", error_callback)
        self.screen_sharing.register_callback("on_state_change", state_change_callback)
        
        # Verify callback registration
        self.assertEqual(self.screen_sharing.on_frame, frame_callback)
        self.assertEqual(self.screen_sharing.on_error, error_callback)
        self.assertEqual(self.screen_sharing.on_state_change, state_change_callback)
    
    async def test_error_handling(self):
        """Test error handling during screen sharing."""
        # Mock pyautogui to raise an exception
        with patch('pyautogui.screenshot', side_effect=Exception("Test exception")):
            # Mock the error callback
            error_callback = MagicMock()
            self.screen_sharing.register_callback("on_error", error_callback)
            
            # Start sharing
            result = await self.screen_sharing.start_sharing()
            
            # Verify results
            self.assertFalse(result)
            self.assertEqual(self.screen_sharing.state, ScreenShareState.ERROR)
            
            # Verify error callback was called
            # Note: In the actual implementation, this would be awaited
            # but for testing purposes we're just checking if it was called
            self.assertTrue(error_callback.called)

# Run the tests
if __name__ == '__main__':
    unittest.main()
