"""
Screen Sharing Module for Dr. TARDIS Gemini Live API Integration

This module provides screen sharing capabilities with annotation tools,
enabling Dr. TARDIS to share visual content and provide interactive guidance.

Author: ApexAgent Development Team
Date: May 26, 2025
"""

import asyncio
import cv2
import logging
import numpy as np
import os
import pyautogui
import tempfile
import time
from enum import Enum
from typing import Dict, List, Any, Optional, Tuple, Union, Callable, AsyncGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class ScreenShareState(Enum):
    """Enum for different states of the screen sharing module."""
    IDLE = "idle"
    CAPTURING = "capturing"
    ANNOTATING = "annotating"
    ERROR = "error"

class AnnotationType(Enum):
    """Enum for different types of annotations."""
    TEXT = "text"
    RECTANGLE = "rectangle"
    CIRCLE = "circle"
    ARROW = "arrow"
    FREEHAND = "freehand"
    HIGHLIGHT = "highlight"
    ANIMATED_ARROW = "animated_arrow"
    ANIMATED_HIGHLIGHT = "animated_highlight"
    ANIMATED_CIRCLE = "animated_circle"
    PULSE = "pulse"
    PULSING_CIRCLE = "pulsing_circle"
    PATH = "path"

class ScreenSharing:
    """
    Provides screen sharing capabilities with annotation tools.
    
    This class enables capturing and sharing screen content with
    interactive annotations for Dr. TARDIS visual guidance.
    
    Attributes:
        state (ScreenShareState): Current state of the screen sharing module
        logger (logging.Logger): Logger for the screen sharing module
    """
    
    def __init__(self, width: int = 1280, height: int = 720, fps: int = 15):
        """
        Initialize the Screen Sharing module.
        
        Args:
            width: Frame width in pixels
            height: Frame height in pixels
            fps: Frames per second
        """
        self.width = width
        self.height = height
        self.fps = fps
        self.state = ScreenShareState.IDLE
        self.logger = logging.getLogger("ScreenSharing")
        
        # Screen capture
        self._capture_task = None
        self._stop_capturing = asyncio.Event()
        self._current_frame = None
        self._frame_buffer = []
        self._max_buffer_size = 10
        
        # Annotations
        self._annotations = []
        self._current_annotation = None
        
        # Callbacks
        self.on_frame = None
        self.on_error = None
        self.on_state_change = None
        
        self.logger.info(f"ScreenSharing initialized with width={width}, height={height}, fps={fps}")
    
    def register_callback(self, event_type: str, callback: Callable):
        """
        Register a callback function for a specific event type.
        
        Args:
            event_type: Type of event to register callback for
                ('on_frame', 'on_error', 'on_state_change')
            callback: Function to call when the event occurs
        """
        if event_type == "on_frame":
            self.on_frame = callback
        elif event_type == "on_error":
            self.on_error = callback
        elif event_type == "on_state_change":
            self.on_state_change = callback
        else:
            self.logger.warning(f"Unknown event type: {event_type}")
    
    def _set_state(self, new_state: ScreenShareState):
        """
        Set the state of the screen sharing module and trigger the state change callback.
        
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
    
    async def start_sharing(self) -> bool:
        """
        Start capturing and sharing screen content.
        
        Returns:
            bool: True if sharing started successfully, False otherwise
        """
        if self.state != ScreenShareState.IDLE and self.state != ScreenShareState.ERROR:
            self.logger.warning(f"Cannot start sharing in state {self.state}")
            return False
        
        self.logger.info("Starting screen sharing")
        
        try:
            # Clear stop flag and frame buffer
            self._stop_capturing.clear()
            self._frame_buffer.clear()
            
            # Start capture task
            self._capture_task = asyncio.create_task(self._capture_screen())
            
            self._set_state(ScreenShareState.CAPTURING)
            return True
            
        except Exception as e:
            self._set_state(ScreenShareState.ERROR)
            self.logger.error(f"Error starting screen sharing: {e}")
            
            # Call the error callback if registered
            if self.on_error:
                try:
                    await self.on_error(str(e))
                except Exception as e:
                    self.logger.error(f"Error in error callback: {e}")
            
            return False
    
    async def stop_sharing(self) -> bool:
        """
        Stop capturing and sharing screen content.
        
        Returns:
            bool: True if sharing stopped successfully, False otherwise
        """
        if self.state != ScreenShareState.CAPTURING and self.state != ScreenShareState.ANNOTATING:
            self.logger.warning(f"Not sharing (current state: {self.state})")
            return False
        
        self.logger.info("Stopping screen sharing")
        
        try:
            # Signal capture task to stop
            self._stop_capturing.set()
            
            # Wait for capture task to complete
            if self._capture_task and not self._capture_task.done():
                try:
                    await asyncio.wait_for(asyncio.shield(self._capture_task), timeout=2.0)
                except asyncio.TimeoutError:
                    self.logger.warning("Timeout waiting for capture task to complete")
            
            self._set_state(ScreenShareState.IDLE)
            return True
            
        except Exception as e:
            self._set_state(ScreenShareState.ERROR)
            self.logger.error(f"Error stopping screen sharing: {e}")
            
            # Call the error callback if registered
            if self.on_error:
                try:
                    await self.on_error(str(e))
                except Exception as e:
                    self.logger.error(f"Error in error callback: {e}")
            
            return False
    
    async def get_frame(self) -> Optional[np.ndarray]:
        """
        Get the most recent screen frame.
        
        Returns:
            np.ndarray: Frame as numpy array or None if no frame available
        """
        if not self._frame_buffer:
            return None
        
        return self._frame_buffer[-1]
    
    async def get_annotated_frame(self) -> Optional[np.ndarray]:
        """
        Get the most recent screen frame with annotations.
        
        Returns:
            np.ndarray: Annotated frame as numpy array or None if no frame available
        """
        frame = await self.get_frame()
        
        if frame is None:
            return None
        
        # Create a copy of the frame for annotation
        annotated_frame = frame.copy()
        
        # Add annotations
        for annotation in self._annotations:
            self._draw_annotation(annotated_frame, annotation)
        
        # Add current annotation if in progress
        if self._current_annotation:
            self._draw_annotation(annotated_frame, self._current_annotation)
        
        return annotated_frame
    
    async def save_frame(self, file_path: str, include_annotations: bool = True) -> bool:
        """
        Save the current screen frame to a file.
        
        Args:
            file_path: Path to save the frame
            include_annotations: Whether to include annotations in the saved frame
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get frame with or without annotations
            if include_annotations:
                frame = await self.get_annotated_frame()
            else:
                frame = await self.get_frame()
            
            if frame is None:
                self.logger.warning("No frame available to save")
                return False
            
            # Save the frame
            cv2.imwrite(file_path, frame)
            self.logger.info(f"Frame saved to {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving frame: {e}")
            
            # Call the error callback if registered
            if self.on_error:
                try:
                    await self.on_error(str(e))
                except Exception as e:
                    self.logger.error(f"Error in error callback: {e}")
            
            return False
    
    async def save_video(self, file_path: str, duration: float, include_annotations: bool = True) -> bool:
        """
        Save a video clip of the screen to a file.
        
        Args:
            file_path: Path to save the video
            duration: Duration of the video in seconds
            include_annotations: Whether to include annotations in the saved video
            
        Returns:
            bool: True if successful, False otherwise
        """
        if self.state != ScreenShareState.CAPTURING and self.state != ScreenShareState.ANNOTATING:
            self.logger.warning(f"Not sharing (current state: {self.state})")
            return False
        
        try:
            # Create video writer
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            out = cv2.VideoWriter(file_path, fourcc, self.fps, (self.width, self.height))
            
            # Calculate number of frames to capture
            num_frames = int(duration * self.fps)
            
            self.logger.info(f"Recording {num_frames} frames at {self.fps}fps for {duration}s")
            
            # Capture frames
            frames_captured = 0
            start_time = time.time()
            
            while frames_captured < num_frames and time.time() - start_time < duration + 1.0:
                # Get frame with or without annotations
                if include_annotations:
                    frame = await self.get_annotated_frame()
                else:
                    frame = await self.get_frame()
                
                if frame is not None:
                    # Write frame to video
                    out.write(frame)
                    frames_captured += 1
                
                # Wait for next frame
                await asyncio.sleep(1.0 / self.fps)
            
            # Release video writer
            out.release()
            
            self.logger.info(f"Video saved to {file_path} ({frames_captured} frames)")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving video: {e}")
            
            # Call the error callback if registered
            if self.on_error:
                try:
                    await self.on_error(str(e))
                except Exception as e:
                    self.logger.error(f"Error in error callback: {e}")
            
            return False
    
    async def start_annotation(self, annotation_type: AnnotationType, properties: Dict[str, Any]) -> bool:
        """
        Start a new annotation on the screen.
        
        Args:
            annotation_type: Type of annotation to start
            properties: Properties of the annotation (color, thickness, etc.)
            
        Returns:
            bool: True if annotation started successfully, False otherwise
        """
        if self.state != ScreenShareState.CAPTURING and self.state != ScreenShareState.ANNOTATING:
            self.logger.warning(f"Not sharing (current state: {self.state})")
            return False
        
        self.logger.info(f"Starting annotation of type {annotation_type.name}")
        
        try:
            # Create new annotation
            self._current_annotation = {
                "type": annotation_type.value,
                "properties": properties,
                "points": []
            }
            
            self._set_state(ScreenShareState.ANNOTATING)
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting annotation: {e}")
            
            # Call the error callback if registered
            if self.on_error:
                try:
                    await self.on_error(str(e))
                except Exception as e:
                    self.logger.error(f"Error in error callback: {e}")
            
            return False
    
    async def update_annotation(self, point: Tuple[int, int]) -> bool:
        """
        Update the current annotation with a new point.
        
        Args:
            point: New point coordinates (x, y)
            
        Returns:
            bool: True if annotation updated successfully, False otherwise
        """
        if self.state != ScreenShareState.ANNOTATING:
            self.logger.warning(f"Not annotating (current state: {self.state})")
            return False
        
        if self._current_annotation is None:
            self.logger.warning("No current annotation to update")
            return False
        
        try:
            # Add point to current annotation
            self._current_annotation["points"].append(point)
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating annotation: {e}")
            
            # Call the error callback if registered
            if self.on_error:
                try:
                    await self.on_error(str(e))
                except Exception as e:
                    self.logger.error(f"Error in error callback: {e}")
            
            return False
    
    async def finish_annotation(self) -> bool:
        """
        Finish the current annotation and add it to the list of annotations.
        
        Returns:
            bool: True if annotation finished successfully, False otherwise
        """
        if self.state != ScreenShareState.ANNOTATING:
            self.logger.warning(f"Not annotating (current state: {self.state})")
            return False
        
        if self._current_annotation is None:
            self.logger.warning("No current annotation to finish")
            return False
        
        try:
            # Add current annotation to list of annotations
            self._annotations.append(self._current_annotation)
            
            # Clear current annotation
            self._current_annotation = None
            
            self._set_state(ScreenShareState.CAPTURING)
            return True
            
        except Exception as e:
            self.logger.error(f"Error finishing annotation: {e}")
            
            # Call the error callback if registered
            if self.on_error:
                try:
                    await self.on_error(str(e))
                except Exception as e:
                    self.logger.error(f"Error in error callback: {e}")
            
            return False
    
    async def cancel_annotation(self) -> bool:
        """
        Cancel the current annotation without adding it to the list.
        
        Returns:
            bool: True if annotation cancelled successfully, False otherwise
        """
        if self.state != ScreenShareState.ANNOTATING:
            self.logger.warning(f"Not annotating (current state: {self.state})")
            return False
        
        try:
            # Clear current annotation
            self._current_annotation = None
            
            self._set_state(ScreenShareState.CAPTURING)
            return True
            
        except Exception as e:
            self.logger.error(f"Error cancelling annotation: {e}")
            
            # Call the error callback if registered
            if self.on_error:
                try:
                    await self.on_error(str(e))
                except Exception as e:
                    self.logger.error(f"Error in error callback: {e}")
            
            return False
    
    async def clear_annotations(self) -> bool:
        """
        Clear all annotations from the screen.
        
        Returns:
            bool: True if annotations cleared successfully, False otherwise
        """
        try:
            # Clear annotations
            self._annotations = []
            self._current_annotation = None
            
            if self.state == ScreenShareState.ANNOTATING:
                self._set_state(ScreenShareState.CAPTURING)
            
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
    
    async def add_text_annotation(self, text: str, position: Tuple[int, int], properties: Dict[str, Any]) -> bool:
        """
        Add a text annotation to the screen.
        
        Args:
            text: Text to add
            position: Position of the text (x, y)
            properties: Properties of the text (font, size, color, etc.)
            
        Returns:
            bool: True if text added successfully, False otherwise
        """
        if self.state != ScreenShareState.CAPTURING and self.state != ScreenShareState.ANNOTATING:
            self.logger.warning(f"Not sharing (current state: {self.state})")
            return False
        
        try:
            # Create text annotation
            annotation = {
                "type": AnnotationType.TEXT.value,
                "properties": properties,
                "points": [position],
                "text": text
            }
            
            # Add annotation to list
            self._annotations.append(annotation)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding text annotation: {e}")
            
            # Call the error callback if registered
            if self.on_error:
                try:
                    await self.on_error(str(e))
                except Exception as e:
                    self.logger.error(f"Error in error callback: {e}")
            
            return False
    
    async def add_highlight_region(self, region: Tuple[int, int, int, int], properties: Dict[str, Any]) -> bool:
        """
        Add a highlighted region to the screen.
        
        Args:
            region: Region to highlight (x1, y1, x2, y2)
            properties: Properties of the highlight (color, opacity, etc.)
            
        Returns:
            bool: True if highlight added successfully, False otherwise
        """
        if self.state != ScreenShareState.CAPTURING and self.state != ScreenShareState.ANNOTATING:
            self.logger.warning(f"Not sharing (current state: {self.state})")
            return False
        
        try:
            # Create highlight annotation
            annotation = {
                "type": AnnotationType.HIGHLIGHT.value,
                "properties": properties,
                "points": [(region[0], region[1]), (region[2], region[3])]
            }
            
            # Add annotation to list
            self._annotations.append(annotation)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding highlight region: {e}")
            
            # Call the error callback if registered
            if self.on_error:
                try:
                    await self.on_error(str(e))
                except Exception as e:
                    self.logger.error(f"Error in error callback: {e}")
            
            return False
    
    async def _capture_screen(self):
        """Capture screen content in a loop."""
        try:
            while not self._stop_capturing.is_set():
                # Capture screen
                screenshot = pyautogui.screenshot()
                
                # Convert to numpy array
                frame = np.array(screenshot)
                
                # Convert from RGB to BGR (OpenCV format)
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                
                # Resize if needed
                if frame.shape[1] != self.width or frame.shape[0] != self.height:
                    frame = cv2.resize(frame, (self.width, self.height))
                
                # Store current frame
                self._current_frame = frame
                
                # Add frame to buffer
                self._frame_buffer.append(frame)
                
                # Limit buffer size
                while len(self._frame_buffer) > self._max_buffer_size:
                    self._frame_buffer.pop(0)
                
                # Call the frame callback if registered
                if self.on_frame:
                    try:
                        await self.on_frame(frame)
                    except Exception as e:
                        self.logger.error(f"Error in frame callback: {e}")
                
                # Limit frame rate
                await asyncio.sleep(1.0 / self.fps)
            
        except Exception as e:
            self._set_state(ScreenShareState.ERROR)
            self.logger.error(f"Error capturing screen: {e}")
            
            # Call the error callback if registered
            if self.on_error:
                try:
                    await self.on_error(str(e))
                except Exception as e:
                    self.logger.error(f"Error in error callback: {e}")
    
    def _draw_annotation(self, frame: np.ndarray, annotation: Dict[str, Any]):
        """
        Draw an annotation on a frame.
        
        Args:
            frame: Frame to draw on
            annotation: Annotation to draw
        """
        annotation_type = annotation["type"]
        properties = annotation["properties"]
        points = annotation["points"]
        
        # Default properties
        color = properties.get("color", (0, 255, 0))
        thickness = properties.get("thickness", 2)
        
        if annotation_type == AnnotationType.TEXT.value:
            text = annotation.get("text", "")
            position = points[0] if points else (10, 30)
            font = properties.get("font", cv2.FONT_HERSHEY_SIMPLEX)
            font_scale = properties.get("font_scale", 1.0)
            
            cv2.putText(frame, text, position, font, font_scale, color, thickness)
            
        elif annotation_type == AnnotationType.RECTANGLE.value:
            if len(points) >= 2:
                cv2.rectangle(frame, points[0], points[-1], color, thickness)
                
        elif annotation_type == AnnotationType.CIRCLE.value:
            if len(points) >= 2:
                center = points[0]
                # Calculate radius as distance between first and last point
                radius = int(np.sqrt((points[-1][0] - points[0][0])**2 + (points[-1][1] - points[0][1])**2))
                cv2.circle(frame, center, radius, color, thickness)
                
        elif annotation_type == AnnotationType.ARROW.value:
            if len(points) >= 2:
                cv2.arrowedLine(frame, points[0], points[-1], color, thickness)
                
        elif annotation_type == AnnotationType.FREEHAND.value:
            if len(points) >= 2:
                for i in range(1, len(points)):
                    cv2.line(frame, points[i-1], points[i], color, thickness)
                    
        elif annotation_type == AnnotationType.HIGHLIGHT.value:
            if len(points) >= 2:
                # Create a semi-transparent overlay
                overlay = frame.copy()
                alpha = properties.get("opacity", 0.3)
                
                cv2.rectangle(overlay, points[0], points[-1], color, -1)  # Filled rectangle
                cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
                
                # Draw border
                cv2.rectangle(frame, points[0], points[-1], color, thickness)

# Example usage
async def example_usage():
    # Create a screen sharing module
    screen_sharing = ScreenSharing(width=1280, height=720, fps=15)
    
    # Define callbacks
    async def on_frame(frame):
        print(f"Frame received: {frame.shape}")
    
    async def on_error(error):
        print(f"Error: {error}")
    
    async def on_state_change(old_state, new_state):
        print(f"State changed: {old_state.name} -> {new_state.name}")
    
    # Register callbacks
    screen_sharing.register_callback("on_frame", on_frame)
    screen_sharing.register_callback("on_error", on_error)
    screen_sharing.register_callback("on_state_change", on_state_change)
    
    try:
        # Start screen sharing
        await screen_sharing.start_sharing()
        
        # Share for a few seconds
        print("Sharing screen for 3 seconds...")
        await asyncio.sleep(3)
        
        # Add text annotation
        await screen_sharing.add_text_annotation(
            "This is an important area",
            (100, 100),
            {"color": (0, 0, 255), "font_scale": 1.0}
        )
        
        # Add highlight region
        await screen_sharing.add_highlight_region(
            (200, 200, 400, 300),
            {"color": (255, 255, 0), "opacity": 0.3}
        )
        
        # Start freehand annotation
        await screen_sharing.start_annotation(
            AnnotationType.FREEHAND,
            {"color": (255, 0, 0), "thickness": 3}
        )
        
        # Add points to annotation
        for i in range(10):
            await screen_sharing.update_annotation((500 + i*10, 400 + i*5))
            await asyncio.sleep(0.1)
        
        # Finish annotation
        await screen_sharing.finish_annotation()
        
        # Save annotated frame
        await screen_sharing.save_frame("screen_with_annotations.jpg")
        
        # Save video clip
        await screen_sharing.save_video("screen_recording.avi", duration=3.0)
        
        # Clear annotations
        await screen_sharing.clear_annotations()
        
        # Stop sharing
        await screen_sharing.stop_sharing()
        
    except Exception as e:
        print(f"Error in example: {e}")

if __name__ == "__main__":
    asyncio.run(example_usage())
