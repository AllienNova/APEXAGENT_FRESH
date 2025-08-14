"""
Video Integration Module for Dr. TARDIS Gemini Live API

This module integrates the video processing, visual troubleshooting, and screen sharing
components with the Dr. TARDIS Gemini Live API integration.

Author: ApexAgent Development Team
Date: May 26, 2025
"""

import asyncio
import cv2
import logging
import numpy as np
import os
import tempfile
import time
from enum import Enum
from typing import Dict, List, Any, Optional, Tuple, Union, Callable

from .video_processor import VideoProcessor, VideoState
from .visual_troubleshooter import VisualTroubleshooter, TroubleshootingState
from .enhanced_visual_troubleshooter import EnhancedVisualTroubleshooter
from .screen_sharing import ScreenSharing, ScreenShareState, AnnotationType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class VideoIntegrationState(Enum):
    """Enum for different states of the video integration module."""
    IDLE = "idle"
    INITIALIZING = "initializing"
    RUNNING = "running"
    ERROR = "error"
    CLOSED = "closed"

class VideoIntegration:
    """
    Integrates video processing, visual troubleshooting, and screen sharing components.
    
    This class provides a unified interface for all video and visual support
    capabilities in the Dr. TARDIS Gemini Live API integration.
    
    Attributes:
        video_processor (VideoProcessor): Video processor for camera input
        troubleshooter (VisualTroubleshooter): Visual troubleshooter for diagnostics
        visual_troubleshooter (EnhancedVisualTroubleshooter): Enhanced visual troubleshooter
        screen_sharing (ScreenSharing): Screen sharing with annotation tools
        state (VideoIntegrationState): Current state of the video integration
        logger (logging.Logger): Logger for the video integration
    """
    
    def __init__(self, 
                 camera_device_id: int = 0, 
                 camera_width: int = 640, 
                 camera_height: int = 480, 
                 camera_fps: int = 30,
                 screen_width: int = 1280,
                 screen_height: int = 720,
                 screen_fps: int = 15):
        """
        Initialize the Video Integration module.
        
        Args:
            camera_device_id: Camera device ID (0 for default camera)
            camera_width: Camera frame width in pixels
            camera_height: Camera frame height in pixels
            camera_fps: Camera frames per second
            screen_width: Screen sharing frame width in pixels
            screen_height: Screen sharing frame height in pixels
            screen_fps: Screen sharing frames per second
        """
        self.video_processor = VideoProcessor(
            device_id=camera_device_id,
            width=camera_width,
            height=camera_height,
            fps=camera_fps
        )
        
        self.troubleshooter = VisualTroubleshooter(self.video_processor)
        self.visual_troubleshooter = EnhancedVisualTroubleshooter(
            troubleshooter=self.troubleshooter,
            video_processor=self.video_processor
        )
        
        self.screen_sharing = ScreenSharing(
            width=screen_width,
            height=screen_height,
            fps=screen_fps
        )
        
        self.state = VideoIntegrationState.IDLE
        self.logger = logging.getLogger("VideoIntegration")
        
        # Callbacks
        self.on_camera_frame = None
        self.on_screen_frame = None
        self.on_error = None
        self.on_state_change = None
        self.on_analysis_complete = None
        
        # Event handlers
        self._event_handlers = {}
        
        self.logger.info("VideoIntegration initialized")
    
    def __del__(self):
        """Clean up resources when the object is destroyed."""
        try:
            self.close()
        except:
            pass
    
    def close(self):
        """Close the video integration and release resources."""
        if hasattr(self, 'video_processor'):
            self.video_processor.close()
        self.state = VideoIntegrationState.CLOSED
        self.logger.info("VideoIntegration closed and resources released")
    
    def register_callback(self, event_type: str, callback: Callable):
        """
        Register a callback function for a specific event type.
        
        Args:
            event_type: Type of event to register callback for
                ('on_camera_frame', 'on_screen_frame', 'on_error', 
                 'on_state_change', 'on_analysis_complete')
            callback: Function to call when the event occurs
        """
        if event_type == "on_camera_frame":
            self.on_camera_frame = callback
            self.video_processor.register_callback("on_frame", callback)
        elif event_type == "on_screen_frame":
            self.on_screen_frame = callback
            self.screen_sharing.register_callback("on_frame", callback)
        elif event_type == "on_error":
            self.on_error = callback
            self.video_processor.register_callback("on_error", callback)
            self.troubleshooter.register_callback("on_error", callback)
            self.screen_sharing.register_callback("on_error", callback)
        elif event_type == "on_state_change":
            self.on_state_change = callback
        elif event_type == "on_analysis_complete":
            self.on_analysis_complete = callback
            self.troubleshooter.register_callback("on_analysis_complete", callback)
        else:
            self.logger.warning(f"Unknown event type: {event_type}")
    
    def register_event_handler(self, event_type: str, handler: Callable):
        """
        Register an event handler for a specific event type.
        
        Args:
            event_type: Type of event to register handler for
            handler: Function to call when the event occurs
        """
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []
        
        self._event_handlers[event_type].append(handler)
        self.logger.info(f"Registered event handler for {event_type}")
    
    async def trigger_event(self, event_type: str, event_data: Any = None):
        """
        Trigger an event and call all registered handlers.
        
        Args:
            event_type: Type of event to trigger
            event_data: Data to pass to the event handlers
        """
        if event_type not in self._event_handlers:
            return
        
        for handler in self._event_handlers[event_type]:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event_data)
                else:
                    handler(event_data)
            except Exception as e:
                self.logger.error(f"Error in event handler for {event_type}: {e}")
    
    def _set_state(self, new_state: VideoIntegrationState):
        """
        Set the state of the video integration and trigger the state change callback.
        
        Args:
            new_state: New state to set
        """
        old_state = self.state
        self.state = new_state
        
        # Call the state change callback if registered
        if self.on_state_change and old_state != new_state:
            try:
                asyncio.create_task(self.on_state_change(old_state, new_state))
            except Exception as e:
                self.logger.error(f"Error in state change callback: {e}")
    
    async def initialize(self) -> bool:
        """
        Initialize the video integration components.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        if self.state != VideoIntegrationState.IDLE and self.state != VideoIntegrationState.ERROR and self.state != VideoIntegrationState.CLOSED:
            self.logger.warning(f"Cannot initialize in state {self.state}")
            return False
        
        self._set_state(VideoIntegrationState.INITIALIZING)
        self.logger.info("Initializing video integration")
        
        try:
            # Initialize video processor
            result = await self.video_processor.initialize()
            if not result:
                raise RuntimeError("Failed to initialize video processor")
            
            self._set_state(VideoIntegrationState.IDLE)
            self.logger.info("Video integration initialized")
            return True
            
        except Exception as e:
            self._set_state(VideoIntegrationState.ERROR)
            self.logger.error(f"Error initializing video integration: {e}")
            
            # Call the error callback if registered
            if self.on_error:
                try:
                    await self.on_error(str(e))
                except Exception as e:
                    self.logger.error(f"Error in error callback: {e}")
            
            return False
    
    async def start_camera(self) -> bool:
        """
        Start the camera for video input.
        
        Returns:
            bool: True if camera started successfully, False otherwise
        """
        if self.state != VideoIntegrationState.IDLE and self.state != VideoIntegrationState.RUNNING:
            self.logger.warning(f"Cannot start camera in state {self.state}")
            return False
        
        self.logger.info("Starting camera")
        
        try:
            # Start video capture
            result = await self.video_processor.start_capture()
            if not result:
                raise RuntimeError("Failed to start video capture")
            
            self._set_state(VideoIntegrationState.RUNNING)
            return True
            
        except Exception as e:
            self._set_state(VideoIntegrationState.ERROR)
            self.logger.error(f"Error starting camera: {e}")
            
            # Call the error callback if registered
            if self.on_error:
                try:
                    await self.on_error(str(e))
                except Exception as e:
                    self.logger.error(f"Error in error callback: {e}")
            
            return False
    
    async def stop_camera(self) -> bool:
        """
        Stop the camera.
        
        Returns:
            bool: True if camera stopped successfully, False otherwise
        """
        if self.video_processor.state != VideoState.CAPTURING:
            self.logger.warning(f"Camera not capturing (current state: {self.video_processor.state})")
            return False
        
        self.logger.info("Stopping camera")
        
        try:
            # Stop video capture
            result = await self.video_processor.stop_capture()
            if not result:
                raise RuntimeError("Failed to stop video capture")
            
            if self.screen_sharing.state != ScreenShareState.CAPTURING and self.screen_sharing.state != ScreenShareState.ANNOTATING:
                self._set_state(VideoIntegrationState.IDLE)
            
            return True
            
        except Exception as e:
            self._set_state(VideoIntegrationState.ERROR)
            self.logger.error(f"Error stopping camera: {e}")
            
            # Call the error callback if registered
            if self.on_error:
                try:
                    await self.on_error(str(e))
                except Exception as e:
                    self.logger.error(f"Error in error callback: {e}")
            
            return False
    
    async def start_screen_sharing(self) -> bool:
        """
        Start screen sharing.
        
        Returns:
            bool: True if screen sharing started successfully, False otherwise
        """
        if self.state != VideoIntegrationState.IDLE and self.state != VideoIntegrationState.RUNNING:
            self.logger.warning(f"Cannot start screen sharing in state {self.state}")
            return False
        
        self.logger.info("Starting screen sharing")
        
        try:
            # Start screen sharing
            result = await self.screen_sharing.start_sharing()
            if not result:
                raise RuntimeError("Failed to start screen sharing")
            
            self._set_state(VideoIntegrationState.RUNNING)
            return True
            
        except Exception as e:
            self._set_state(VideoIntegrationState.ERROR)
            self.logger.error(f"Error starting screen sharing: {e}")
            
            # Call the error callback if registered
            if self.on_error:
                try:
                    await self.on_error(str(e))
                except Exception as e:
                    self.logger.error(f"Error in error callback: {e}")
            
            return False
    
    async def stop_screen_sharing(self) -> bool:
        """
        Stop screen sharing.
        
        Returns:
            bool: True if screen sharing stopped successfully, False otherwise
        """
        if self.screen_sharing.state != ScreenShareState.CAPTURING and self.screen_sharing.state != ScreenShareState.ANNOTATING:
            self.logger.warning(f"Screen not sharing (current state: {self.screen_sharing.state})")
            return False
        
        self.logger.info("Stopping screen sharing")
        
        try:
            # Stop screen sharing
            result = await self.screen_sharing.stop_sharing()
            if not result:
                raise RuntimeError("Failed to stop screen sharing")
            
            if self.video_processor.state != VideoState.CAPTURING:
                self._set_state(VideoIntegrationState.IDLE)
            
            return True
            
        except Exception as e:
            self._set_state(VideoIntegrationState.ERROR)
            self.logger.error(f"Error stopping screen sharing: {e}")
            
            # Call the error callback if registered
            if self.on_error:
                try:
                    await self.on_error(str(e))
                except Exception as e:
                    self.logger.error(f"Error in error callback: {e}")
            
            return False
    
    async def analyze_camera(self) -> Dict[str, Any]:
        """
        Analyze camera functionality and quality.
        
        Returns:
            Dict[str, Any]: Analysis results
        """
        self.logger.info("Analyzing camera")
        
        try:
            # Analyze camera
            results = await self.troubleshooter.analyze_camera()
            
            # Call the analysis complete callback if registered
            if self.on_analysis_complete:
                try:
                    await self.on_analysis_complete("camera", results)
                except Exception as e:
                    self.logger.error(f"Error in analysis complete callback: {e}")
            
            return results
            
        except Exception as e:
            self._set_state(VideoIntegrationState.ERROR)
            self.logger.error(f"Error analyzing camera: {e}")
            
            # Call the error callback if registered
            if self.on_error:
                try:
                    await self.on_error(str(e))
                except Exception as e:
                    self.logger.error(f"Error in error callback: {e}")
            
            return {"error": str(e)}
    
    async def analyze_hardware_issue(self, issue_type: str) -> Dict[str, Any]:
        """
        Analyze specific hardware issue based on visual input.
        
        Args:
            issue_type: Type of hardware issue to analyze
                ('display', 'connection', 'physical_damage', 'led_status')
                
        Returns:
            Dict[str, Any]: Analysis results
        """
        self.logger.info(f"Analyzing hardware issue: {issue_type}")
        
        try:
            # Analyze hardware issue
            results = await self.troubleshooter.analyze_hardware_issue(issue_type)
            
            # Call the analysis complete callback if registered
            if self.on_analysis_complete:
                try:
                    await self.on_analysis_complete(f"hardware_{issue_type}", results)
                except Exception as e:
                    self.logger.error(f"Error in analysis complete callback: {e}")
            
            return results
            
        except Exception as e:
            self._set_state(VideoIntegrationState.ERROR)
            self.logger.error(f"Error analyzing hardware issue: {e}")
            
            # Call the error callback if registered
            if self.on_error:
                try:
                    await self.on_error(str(e))
                except Exception as e:
                    self.logger.error(f"Error in error callback: {e}")
            
            return {"error": str(e)}
    
    async def generate_troubleshooting_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive troubleshooting report based on all analyses.
        
        Returns:
            Dict[str, Any]: Troubleshooting report
        """
        self.logger.info("Generating troubleshooting report")
        
        try:
            # Generate report
            report = await self.troubleshooter.generate_troubleshooting_report()
            
            # Call the analysis complete callback if registered
            if self.on_analysis_complete:
                try:
                    await self.on_analysis_complete("troubleshooting_report", report)
                except Exception as e:
                    self.logger.error(f"Error in analysis complete callback: {e}")
            
            return report
            
        except Exception as e:
            self._set_state(VideoIntegrationState.ERROR)
            self.logger.error(f"Error generating troubleshooting report: {e}")
            
            # Call the error callback if registered
            if self.on_error:
                try:
                    await self.on_error(str(e))
                except Exception as e:
                    self.logger.error(f"Error in error callback: {e}")
            
            return {"error": str(e)}
    
    async def add_annotation(self, annotation_type: AnnotationType, **kwargs) -> bool:
        """
        Add an annotation to the screen sharing.
        
        Args:
            annotation_type: Type of annotation to add
            **kwargs: Additional parameters for the annotation
                (varies by annotation type)
                
        Returns:
            bool: True if annotation added successfully, False otherwise
        """
        if self.screen_sharing.state != ScreenShareState.CAPTURING and self.screen_sharing.state != ScreenShareState.ANNOTATING:
            self.logger.warning(f"Screen not sharing (current state: {self.screen_sharing.state})")
            return False
        
        self.logger.info(f"Adding annotation: {annotation_type}")
        
        try:
            # Add annotation
            result = await self.screen_sharing.add_annotation(annotation_type, **kwargs)
            if not result:
                raise RuntimeError("Failed to add annotation")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding annotation: {e}")
            
            # Call the error callback if registered
            if self.on_error:
                try:
                    await self.on_error(str(e))
                except Exception as e:
                    self.logger.error(f"Error in error callback: {e}")
            
            return False
    
    async def clear_annotations(self) -> bool:
        """
        Clear all annotations from the screen sharing.
        
        Returns:
            bool: True if annotations cleared successfully, False otherwise
        """
        if self.screen_sharing.state != ScreenShareState.ANNOTATING:
            self.logger.warning(f"Screen not annotating (current state: {self.screen_sharing.state})")
            return False
        
        self.logger.info("Clearing annotations")
        
        try:
            # Clear annotations
            result = await self.screen_sharing.clear_annotations()
            if not result:
                raise RuntimeError("Failed to clear annotations")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error clearing annotations: {e}")
            
            # Call the error callback if registered
            if self.on_error:
                try:
                    await self.on_error(str(e))
                except Exception as e:
                    self.logger.error(f"Error in error callback: {e}")
            
            return False
    
    async def save_screenshot(self, filename: str) -> str:
        """
        Save a screenshot of the current screen sharing.
        
        Args:
            filename: Filename to save the screenshot as
            
        Returns:
            str: Path to the saved screenshot, or None if failed
        """
        if self.screen_sharing.state != ScreenShareState.CAPTURING and self.screen_sharing.state != ScreenShareState.ANNOTATING:
            self.logger.warning(f"Screen not sharing (current state: {self.screen_sharing.state})")
            return None
        
        self.logger.info(f"Saving screenshot: {filename}")
        
        try:
            # Save screenshot
            path = await self.screen_sharing.save_screenshot(filename)
            if not path:
                raise RuntimeError("Failed to save screenshot")
            
            return path
            
        except Exception as e:
            self.logger.error(f"Error saving screenshot: {e}")
            
            # Call the error callback if registered
            if self.on_error:
                try:
                    await self.on_error(str(e))
                except Exception as e:
                    self.logger.error(f"Error in error callback: {e}")
            
            return None
    
    async def save_camera_frame(self, filename: str) -> str:
        """
        Save a frame from the camera.
        
        Args:
            filename: Filename to save the frame as
            
        Returns:
            str: Path to the saved frame, or None if failed
        """
        if self.video_processor.state != VideoState.CAPTURING:
            self.logger.warning(f"Camera not capturing (current state: {self.video_processor.state})")
            return None
        
        self.logger.info(f"Saving camera frame: {filename}")
        
        try:
            # Save frame
            path = await self.video_processor.save_frame(filename)
            if not path:
                raise RuntimeError("Failed to save camera frame")
            
            return path
            
        except Exception as e:
            self.logger.error(f"Error saving camera frame: {e}")
            
            # Call the error callback if registered
            if self.on_error:
                try:
                    await self.on_error(str(e))
                except Exception as e:
                    self.logger.error(f"Error in error callback: {e}")
            
            return None
    
    async def get_camera_frame(self) -> np.ndarray:
        """
        Get the current camera frame.
        
        Returns:
            np.ndarray: Current camera frame, or None if not capturing
        """
        if self.video_processor.state != VideoState.CAPTURING:
            self.logger.warning(f"Camera not capturing (current state: {self.video_processor.state})")
            return None
        
        try:
            # Get frame
            frame = await self.video_processor.get_frame()
            return frame
            
        except Exception as e:
            self.logger.error(f"Error getting camera frame: {e}")
            
            # Call the error callback if registered
            if self.on_error:
                try:
                    await self.on_error(str(e))
                except Exception as e:
                    self.logger.error(f"Error in error callback: {e}")
            
            return None
    
    async def get_screen(self) -> np.ndarray:
        """
        Get the current screen sharing frame.
        
        Returns:
            np.ndarray: Current screen frame, or None if not sharing
        """
        if self.screen_sharing.state != ScreenShareState.CAPTURING and self.screen_sharing.state != ScreenShareState.ANNOTATING:
            self.logger.warning(f"Screen not sharing (current state: {self.screen_sharing.state})")
            return None
        
        try:
            # Get screen
            screen = await self.screen_sharing.get_screen()
            return screen
            
        except Exception as e:
            self.logger.error(f"Error getting screen: {e}")
            
            # Call the error callback if registered
            if self.on_error:
                try:
                    await self.on_error(str(e))
                except Exception as e:
                    self.logger.error(f"Error in error callback: {e}")
            
            return None
    
    async def enhanced_troubleshooting(self, issue_type: str, diagnostic_level: str = "standard") -> Dict[str, Any]:
        """
        Perform enhanced troubleshooting for a specific issue.
        
        Args:
            issue_type: Type of issue to troubleshoot
            diagnostic_level: Level of diagnostic detail
                ('basic', 'standard', 'advanced', 'expert')
                
        Returns:
            Dict[str, Any]: Troubleshooting results
        """
        self.logger.info(f"Performing enhanced troubleshooting for {issue_type} at {diagnostic_level} level")
        
        try:
            # Perform enhanced troubleshooting
            results = await self.visual_troubleshooter.diagnose_issue(issue_type, diagnostic_level)
            
            # Call the analysis complete callback if registered
            if self.on_analysis_complete:
                try:
                    await self.on_analysis_complete(f"enhanced_troubleshooting_{issue_type}", results)
                except Exception as e:
                    self.logger.error(f"Error in analysis complete callback: {e}")
            
            return results
            
        except Exception as e:
            self._set_state(VideoIntegrationState.ERROR)
            self.logger.error(f"Error performing enhanced troubleshooting: {e}")
            
            # Call the error callback if registered
            if self.on_error:
                try:
                    await self.on_error(str(e))
                except Exception as e:
                    self.logger.error(f"Error in error callback: {e}")
            
            return {"error": str(e)}

async def example_usage():
    """Example usage of the VideoIntegration class."""
    # Create video integration
    video_integration = VideoIntegration(
        camera_device_id=0,
        camera_width=640,
        camera_height=480,
        camera_fps=30,
        screen_width=1280,
        screen_height=720,
        screen_fps=15
    )
    
    # Initialize
    result = await video_integration.initialize()
    if result:
        print("Video integration initialized")
    else:
        print("Failed to initialize video integration")
        return
    
    # Start camera
    result = await video_integration.start_camera()
    if result:
        print("Camera started")
    else:
        print("Failed to start camera")
        return
    
    # Analyze camera
    results = await video_integration.analyze_camera()
    print(f"Camera analysis results: {results}")
    
    # Start screen sharing
    result = await video_integration.start_screen_sharing()
    if result:
        print("Screen sharing started")
    else:
        print("Failed to start screen sharing")
    
    # Add annotation
    result = await video_integration.add_annotation(
        AnnotationType.CIRCLE,
        coordinates=(320, 240),
        radius=50,
        color=(0, 255, 0),
        thickness=2
    )
    if result:
        print("Annotation added")
    else:
        print("Failed to add annotation")
    
    # Save screenshot
    path = await video_integration.save_screenshot("screenshot.jpg")
    if path:
        print(f"Screenshot saved to {path}")
    else:
        print("Failed to save screenshot")
    
    # Clear annotations
    result = await video_integration.clear_annotations()
    if result:
        print("Annotations cleared")
    else:
        print("Failed to clear annotations")
    
    # Stop screen sharing
    result = await video_integration.stop_screen_sharing()
    if result:
        print("Screen sharing stopped")
    else:
        print("Failed to stop screen sharing")
    
    # Stop camera
    result = await video_integration.stop_camera()
    if result:
        print("Camera stopped")
    else:
        print("Failed to stop camera")
    
    # Close
    video_integration.close()
    print("Video integration closed")

if __name__ == "__main__":
    asyncio.run(example_usage())
