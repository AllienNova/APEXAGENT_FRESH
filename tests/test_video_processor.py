"""
Unit Tests for Video Processor Module

This module contains unit tests for the VideoProcessor class in the
video_processor.py module.

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

class TestVideoProcessor(unittest.TestCase):
    """Test cases for the VideoProcessor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.processor = VideoProcessor(device_id=0, width=640, height=480, fps=30)
        
        # Create a mock frame for testing
        self.mock_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        # Add some content to the frame to make it testable
        cv2.rectangle(self.mock_frame, (100, 100), (300, 300), (0, 255, 0), 2)
        cv2.putText(self.mock_frame, "Test Frame", (150, 150), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.processor.close()
    
    @patch('cv2.VideoCapture')
    async def test_initialize(self, mock_video_capture):
        """Test initializing the video processor."""
        # Configure mock
        mock_instance = mock_video_capture.return_value
        mock_instance.isOpened.return_value = True
        mock_instance.read.return_value = (True, self.mock_frame)
        mock_instance.get.return_value = 30  # fps
        
        # Test initialization
        result = await self.processor.initialize()
        
        # Verify results
        self.assertTrue(result)
        self.assertEqual(self.processor.state, VideoState.IDLE)
        mock_instance.set.assert_any_call(cv2.CAP_PROP_FRAME_WIDTH, 640)
        mock_instance.set.assert_any_call(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        mock_instance.set.assert_any_call(cv2.CAP_PROP_FPS, 30)
    
    @patch('cv2.VideoCapture')
    async def test_initialize_failure(self, mock_video_capture):
        """Test initialization failure."""
        # Configure mock
        mock_instance = mock_video_capture.return_value
        mock_instance.isOpened.return_value = False
        
        # Test initialization
        result = await self.processor.initialize()
        
        # Verify results
        self.assertFalse(result)
        self.assertEqual(self.processor.state, VideoState.ERROR)
    
    @patch('cv2.VideoCapture')
    async def test_start_capture(self, mock_video_capture):
        """Test starting video capture."""
        # Configure mock
        mock_instance = mock_video_capture.return_value
        mock_instance.isOpened.return_value = True
        mock_instance.read.return_value = (True, self.mock_frame)
        mock_instance.get.return_value = 30  # fps
        
        # Initialize and start capture
        await self.processor.initialize()
        
        # Mock the _process_frames method to avoid actual processing
        self.processor._process_frames = MagicMock(return_value=None)
        
        result = await self.processor.start_capture()
        
        # Verify results
        self.assertTrue(result)
        self.assertEqual(self.processor.state, VideoState.CAPTURING)
    
    @patch('cv2.VideoCapture')
    async def test_stop_capture(self, mock_video_capture):
        """Test stopping video capture."""
        # Configure mock
        mock_instance = mock_video_capture.return_value
        mock_instance.isOpened.return_value = True
        mock_instance.read.return_value = (True, self.mock_frame)
        mock_instance.get.return_value = 30  # fps
        
        # Initialize and start capture
        await self.processor.initialize()
        
        # Mock the _process_frames method to avoid actual processing
        self.processor._process_frames = MagicMock(return_value=None)
        
        await self.processor.start_capture()
        
        # Set state directly since we mocked _process_frames
        self.processor.state = VideoState.CAPTURING
        
        result = await self.processor.stop_capture()
        
        # Verify results
        self.assertTrue(result)
        self.assertEqual(self.processor.state, VideoState.IDLE)
    
    @patch('cv2.VideoCapture')
    async def test_get_frame(self, mock_video_capture):
        """Test getting a frame."""
        # Configure mock
        mock_instance = mock_video_capture.return_value
        mock_instance.isOpened.return_value = True
        mock_instance.read.return_value = (True, self.mock_frame)
        mock_instance.get.return_value = 30  # fps
        
        # Initialize and add a frame to the buffer
        await self.processor.initialize()
        self.processor._frame_buffer.append(self.mock_frame)
        
        # Get the frame
        frame = await self.processor.get_frame()
        
        # Verify results
        self.assertIsNotNone(frame)
        self.assertEqual(frame.shape, (480, 640, 3))
    
    @patch('cv2.VideoCapture')
    async def test_save_frame(self, mock_video_capture):
        """Test saving a frame to a file."""
        # Configure mock
        mock_instance = mock_video_capture.return_value
        mock_instance.isOpened.return_value = True
        mock_instance.read.return_value = (True, self.mock_frame)
        mock_instance.get.return_value = 30  # fps
        
        # Initialize and add a frame to the buffer
        await self.processor.initialize()
        self.processor._frame_buffer.append(self.mock_frame)
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            # Save the frame
            result = await self.processor.save_frame(temp_path)
            
            # Verify results
            self.assertTrue(result)
            self.assertTrue(os.path.exists(temp_path))
            self.assertTrue(os.path.getsize(temp_path) > 0)
            
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    @patch('cv2.VideoCapture')
    async def test_callbacks(self, mock_video_capture):
        """Test callback registration and invocation."""
        # Configure mock
        mock_instance = mock_video_capture.return_value
        mock_instance.isOpened.return_value = True
        mock_instance.read.return_value = (True, self.mock_frame)
        mock_instance.get.return_value = 30  # fps
        
        # Create mock callbacks
        frame_callback = MagicMock()
        error_callback = MagicMock()
        state_change_callback = MagicMock()
        
        # Register callbacks
        self.processor.register_callback("on_frame", frame_callback)
        self.processor.register_callback("on_error", error_callback)
        self.processor.register_callback("on_state_change", state_change_callback)
        
        # Verify callback registration
        self.assertEqual(self.processor.on_frame, frame_callback)
        self.assertEqual(self.processor.on_error, error_callback)
        self.assertEqual(self.processor.on_state_change, state_change_callback)
    
    @patch('cv2.VideoCapture')
    async def test_error_handling(self, mock_video_capture):
        """Test error handling during initialization."""
        # Configure mock to raise an exception
        mock_video_capture.side_effect = Exception("Test exception")
        
        # Mock the error callback
        error_callback = MagicMock()
        self.processor.register_callback("on_error", error_callback)
        
        # Test initialization
        result = await self.processor.initialize()
        
        # Verify results
        self.assertFalse(result)
        self.assertEqual(self.processor.state, VideoState.ERROR)
        # Verify error callback was called
        # Note: In the actual implementation, this would be awaited
        # but for testing purposes we're just checking if it was called
        self.assertTrue(error_callback.called)

# Run the tests
if __name__ == '__main__':
    unittest.main()
