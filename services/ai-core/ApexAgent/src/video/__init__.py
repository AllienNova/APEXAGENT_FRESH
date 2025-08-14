"""
Video module for Dr. TARDIS Gemini Live API integration.

This module provides video processing, analysis, and interaction capabilities
for the Dr. TARDIS system.

Author: ApexAgent Development Team
Date: May 26, 2025
"""

from src.video.video_processor import VideoProcessor, VideoState
from src.video.mock_video_processor import MockVideoProcessor

__all__ = [
    'VideoProcessor',
    'VideoState',
    'MockVideoProcessor',
]
