"""
Mock video processor module for Dr. TARDIS Gemini Live API integration.

This module provides a mock implementation of the video processor for testing
and development purposes without requiring actual camera hardware.

Author: ApexAgent Development Team
Date: May 26, 2025
"""

import logging
from src.video.video_processor import VideoProcessor, VideoState

class MockVideoProcessor(VideoProcessor):
    """
    Mock implementation of the video processor for testing.
    
    Simulates video processing capabilities without requiring actual hardware.
    """
    
    def __init__(self, config=None):
        """
        Initialize the mock video processor.
        
        Args:
            config: Optional configuration dictionary
        """
        super().__init__(config)
        self.logger = logging.getLogger("MockVideoProcessor")
        self.frame_count = 0
        self.test_frames = []
        
    def initialize(self):
        """
        Initialize the mock video processor.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        self.state = VideoState.INITIALIZING
        self.logger.info("Initializing mock video processor")
        
        # Generate test frames
        self._generate_test_frames()
        
        self.state = VideoState.ACTIVE
        self.logger.info("Mock video processor initialized successfully")
        return True
        
    def _generate_test_frames(self):
        """Generate test frames for simulation."""
        # Create 10 test frames with different simulated content
        for i in range(10):
            self.test_frames.append({
                "timestamp": f"2025-05-26T08:{i:02d}:00.000Z",
                "resolution": self.resolution,
                "format": "RGB",
                "data": f"Simulated frame data {i}",
                "test_metadata": {
                    "frame_number": i,
                    "simulated": True
                }
            })
        
        self.logger.info(f"Generated {len(self.test_frames)} test frames")
        
    def get_current_frame(self):
        """
        Get the current video frame from the test frames.
        
        Returns:
            dict: Frame data with metadata
        """
        if self.state != VideoState.ACTIVE:
            self.logger.warning("Cannot get frame: mock video capture not active")
            return None
            
        # Return frames in sequence, cycling through test frames
        frame_index = self.frame_count % len(self.test_frames)
        frame_data = self.test_frames[frame_index]
        self.frame_count += 1
        
        # Add to buffer
        self.frame_buffer.append(frame_data)
        if len(self.frame_buffer) > self.max_buffer_size:
            self.frame_buffer.pop(0)
            
        return frame_data
        
    def analyze_frame(self, frame_data):
        """
        Analyze a video frame with mock analysis.
        
        Args:
            frame_data: Frame data to analyze
            
        Returns:
            dict: Mock analysis results
        """
        if frame_data is None:
            self.logger.error("Cannot analyze: invalid frame data")
            return None
            
        # Generate deterministic mock analysis based on frame data
        frame_number = frame_data.get("test_metadata", {}).get("frame_number", 0)
        
        # Different mock analysis results based on frame number
        if frame_number % 3 == 0:
            objects = ["laptop", "desk", "chair"]
            text = "Office environment"
            confidence = 0.95
        elif frame_number % 3 == 1:
            objects = ["person", "whiteboard", "marker"]
            text = "Meeting room"
            confidence = 0.92
        else:
            objects = ["coffee cup", "notebook", "pen"]
            text = "Work items"
            confidence = 0.88
            
        analysis_results = {
            "objects_detected": objects,
            "text_detected": text,
            "confidence": confidence,
            "is_mock_analysis": True
        }
        
        self.logger.info("Mock frame analysis completed")
        return analysis_results
        
    def get_diagnostics(self):
        """
        Get diagnostic information about the mock video processor.
        
        Returns:
            dict: Diagnostic information
        """
        diagnostics = super().get_diagnostics()
        diagnostics.update({
            "is_mock": True,
            "test_frames_count": len(self.test_frames),
            "frames_processed": self.frame_count
        })
        
        return diagnostics
