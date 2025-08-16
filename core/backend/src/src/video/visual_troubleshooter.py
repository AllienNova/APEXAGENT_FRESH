"""
Visual Troubleshooting Module for Dr. TARDIS Gemini Live API Integration

This module provides visual troubleshooting capabilities for hardware issues,
enabling Dr. TARDIS to analyze visual input and provide diagnostic assistance.

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
from typing import Dict, List, Any, Optional, Tuple, Union, Callable, AsyncGenerator

from .video_processor import VideoProcessor, VideoState

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class TroubleshootingState(Enum):
    """Enum for different states of the visual troubleshooter."""
    IDLE = "idle"
    ANALYZING = "analyzing"
    GENERATING_REPORT = "generating_report"
    ERROR = "error"

class VisualTroubleshooter:
    """
    Provides visual troubleshooting capabilities for hardware issues.
    
    This class analyzes visual input to identify hardware issues and
    provides diagnostic assistance for Dr. TARDIS technical support.
    
    Attributes:
        video_processor (VideoProcessor): Video processor for capturing frames
        state (TroubleshootingState): Current state of the troubleshooter
        logger (logging.Logger): Logger for the troubleshooter
    """
    
    def __init__(self, video_processor: VideoProcessor):
        """
        Initialize the Visual Troubleshooter.
        
        Args:
            video_processor: Video processor for capturing frames
        """
        self.video_processor = video_processor
        self.state = TroubleshootingState.IDLE
        self.logger = logging.getLogger("VisualTroubleshooter")
        
        # Analysis results
        self._analysis_results = {}
        
        # Callbacks
        self.on_analysis_complete = None
        self.on_error = None
        
        # Analysis models and detectors
        self._initialize_models()
        
        self.logger.info("VisualTroubleshooter initialized")
    
    def _initialize_models(self):
        """Initialize analysis models and detectors."""
        # Load pre-trained models for hardware analysis
        try:
            # Initialize face detector for camera testing
            self._face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            
            # Initialize QR code detector
            self._qr_detector = cv2.QRCodeDetector()
            
            # Initialize text detector (EAST text detector)
            # Note: This requires OpenCV with DNN support and the EAST model
            # self._text_detector = cv2.dnn.readNet("frozen_east_text_detection.pb")
            
            self.logger.info("Analysis models initialized")
            
        except Exception as e:
            self.logger.error(f"Error initializing analysis models: {e}")
    
    def register_callback(self, event_type: str, callback: Callable):
        """
        Register a callback function for a specific event type.
        
        Args:
            event_type: Type of event to register callback for
                ('on_analysis_complete', 'on_error')
            callback: Function to call when the event occurs
        """
        if event_type == "on_analysis_complete":
            self.on_analysis_complete = callback
        elif event_type == "on_error":
            self.on_error = callback
        else:
            self.logger.warning(f"Unknown event type: {event_type}")
    
    async def analyze_camera(self) -> Dict[str, Any]:
        """
        Analyze camera functionality and quality.
        
        Returns:
            Dict[str, Any]: Analysis results
        """
        self.state = TroubleshootingState.ANALYZING
        self.logger.info("Analyzing camera functionality and quality")
        
        try:
            # Ensure video processor is initialized
            if self.video_processor.state == VideoState.IDLE:
                await self.video_processor.initialize()
            
            # Start capturing if not already capturing
            was_capturing = self.video_processor.state == VideoState.CAPTURING
            if not was_capturing:
                await self.video_processor.start_capture()
            
            # Wait for a few frames to stabilize
            await asyncio.sleep(1.0)
            
            # Get the most recent frame
            frame = await self.video_processor.get_frame()
            
            if frame is None:
                raise RuntimeError("Failed to capture frame for analysis")
            
            # Analyze frame
            results = await self._analyze_camera_frame(frame)
            
            # Stop capturing if it wasn't capturing before
            if not was_capturing:
                await self.video_processor.stop_capture()
            
            self.state = TroubleshootingState.IDLE
            
            # Call the analysis complete callback if registered
            if self.on_analysis_complete:
                try:
                    await self.on_analysis_complete(results)
                except Exception as e:
                    self.logger.error(f"Error in analysis complete callback: {e}")
            
            return results
            
        except Exception as e:
            self.state = TroubleshootingState.ERROR
            self.logger.error(f"Error analyzing camera: {e}")
            
            # Call the error callback if registered
            if self.on_error:
                try:
                    await self.on_error(str(e))
                except Exception as e:
                    self.logger.error(f"Error in error callback: {e}")
            
            return {"error": str(e)}
    
    async def analyze_qr_code(self) -> Dict[str, Any]:
        """
        Analyze QR code in camera view.
        
        Returns:
            Dict[str, Any]: Analysis results with decoded QR code data
        """
        self.state = TroubleshootingState.ANALYZING
        self.logger.info("Analyzing QR code in camera view")
        
        try:
            # Ensure video processor is initialized
            if self.video_processor.state == VideoState.IDLE:
                await self.video_processor.initialize()
            
            # Start capturing if not already capturing
            was_capturing = self.video_processor.state == VideoState.CAPTURING
            if not was_capturing:
                await self.video_processor.start_capture()
            
            # Wait for a few frames to stabilize
            await asyncio.sleep(1.0)
            
            # Try to detect QR code for up to 5 seconds
            start_time = time.time()
            qr_data = None
            qr_points = None
            
            while time.time() - start_time < 5.0 and qr_data is None:
                # Get the most recent frame
                frame = await self.video_processor.get_frame()
                
                if frame is None:
                    await asyncio.sleep(0.1)
                    continue
                
                # Detect QR code
                data, points, _ = self._qr_detector.detectAndDecode(frame)
                
                if data:
                    qr_data = data
                    qr_points = points
                    break
                
                await asyncio.sleep(0.1)
            
            # Stop capturing if it wasn't capturing before
            if not was_capturing:
                await self.video_processor.stop_capture()
            
            # Prepare results
            if qr_data:
                results = {
                    "detected": True,
                    "data": qr_data,
                    "points": qr_points.tolist() if qr_points is not None else None
                }
            else:
                results = {
                    "detected": False,
                    "error": "No QR code detected"
                }
            
            self.state = TroubleshootingState.IDLE
            
            # Call the analysis complete callback if registered
            if self.on_analysis_complete:
                try:
                    await self.on_analysis_complete(results)
                except Exception as e:
                    self.logger.error(f"Error in analysis complete callback: {e}")
            
            return results
            
        except Exception as e:
            self.state = TroubleshootingState.ERROR
            self.logger.error(f"Error analyzing QR code: {e}")
            
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
        self.state = TroubleshootingState.ANALYZING
        self.logger.info(f"Analyzing hardware issue: {issue_type}")
        
        try:
            # Ensure video processor is initialized
            if self.video_processor.state == VideoState.IDLE:
                await self.video_processor.initialize()
            
            # Start capturing if not already capturing
            was_capturing = self.video_processor.state == VideoState.CAPTURING
            if not was_capturing:
                await self.video_processor.start_capture()
            
            # Wait for a few frames to stabilize
            await asyncio.sleep(1.0)
            
            # Get the most recent frame
            frame = await self.video_processor.get_frame()
            
            if frame is None:
                raise RuntimeError("Failed to capture frame for analysis")
            
            # Analyze frame based on issue type
            if issue_type == "display":
                results = await self._analyze_display_issue(frame)
            elif issue_type == "connection":
                results = await self._analyze_connection_issue(frame)
            elif issue_type == "physical_damage":
                results = await self._analyze_physical_damage(frame)
            elif issue_type == "led_status":
                results = await self._analyze_led_status(frame)
            else:
                results = {"error": f"Unknown issue type: {issue_type}"}
            
            # Stop capturing if it wasn't capturing before
            if not was_capturing:
                await self.video_processor.stop_capture()
            
            self.state = TroubleshootingState.IDLE
            
            # Call the analysis complete callback if registered
            if self.on_analysis_complete:
                try:
                    await self.on_analysis_complete(results)
                except Exception as e:
                    self.logger.error(f"Error in analysis complete callback: {e}")
            
            return results
            
        except Exception as e:
            self.state = TroubleshootingState.ERROR
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
        self.state = TroubleshootingState.GENERATING_REPORT
        self.logger.info("Generating troubleshooting report")
        
        try:
            # Compile all analysis results
            report = {
                "timestamp": time.time(),
                "date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "analyses": self._analysis_results,
                "recommendations": []
            }
            
            # Generate recommendations based on analysis results
            if "camera" in self._analysis_results:
                camera_results = self._analysis_results["camera"]
                
                if camera_results.get("brightness", 0) < 0.3:
                    report["recommendations"].append({
                        "issue": "Low lighting",
                        "recommendation": "Increase lighting in the environment for better visibility"
                    })
                
                if camera_results.get("focus_score", 0) < 0.5:
                    report["recommendations"].append({
                        "issue": "Poor focus",
                        "recommendation": "Adjust camera focus or clean lens"
                    })
            
            if "hardware_issues" in self._analysis_results:
                for issue_type, results in self._analysis_results["hardware_issues"].items():
                    if results.get("detected", False):
                        report["recommendations"].append({
                            "issue": f"{issue_type.replace('_', ' ').title()} detected",
                            "recommendation": results.get("recommendation", "Contact technical support")
                        })
            
            self.state = TroubleshootingState.IDLE
            
            return report
            
        except Exception as e:
            self.state = TroubleshootingState.ERROR
            self.logger.error(f"Error generating troubleshooting report: {e}")
            
            # Call the error callback if registered
            if self.on_error:
                try:
                    await self.on_error(str(e))
                except Exception as e:
                    self.logger.error(f"Error in error callback: {e}")
            
            return {"error": str(e)}
    
    async def save_annotated_frame(self, file_path: str, annotations: Dict[str, Any]) -> bool:
        """
        Save an annotated frame with troubleshooting information.
        
        Args:
            file_path: Path to save the annotated frame
            annotations: Annotations to add to the frame
                
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get the most recent frame
            frame = await self.video_processor.get_frame()
            
            if frame is None:
                self.logger.warning("No frame available to annotate")
                return False
            
            # Create a copy of the frame for annotation
            annotated_frame = frame.copy()
            
            # Add annotations
            if "text" in annotations:
                for text_item in annotations["text"]:
                    cv2.putText(
                        annotated_frame,
                        text_item["text"],
                        (text_item.get("x", 10), text_item.get("y", 30)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        text_item.get("scale", 1.0),
                        text_item.get("color", (0, 255, 0)),
                        text_item.get("thickness", 2)
                    )
            
            if "rectangles" in annotations:
                for rect in annotations["rectangles"]:
                    cv2.rectangle(
                        annotated_frame,
                        (rect.get("x1", 0), rect.get("y1", 0)),
                        (rect.get("x2", 100), rect.get("y2", 100)),
                        rect.get("color", (0, 255, 0)),
                        rect.get("thickness", 2)
                    )
            
            if "circles" in annotations:
                for circle in annotations["circles"]:
                    cv2.circle(
                        annotated_frame,
                        (circle.get("x", 0), circle.get("y", 0)),
                        circle.get("radius", 10),
                        circle.get("color", (0, 255, 0)),
                        circle.get("thickness", 2)
                    )
            
            if "lines" in annotations:
                for line in annotations["lines"]:
                    cv2.line(
                        annotated_frame,
                        (line.get("x1", 0), line.get("y1", 0)),
                        (line.get("x2", 100), line.get("y2", 100)),
                        line.get("color", (0, 255, 0)),
                        line.get("thickness", 2)
                    )
            
            # Save the annotated frame
            cv2.imwrite(file_path, annotated_frame)
            self.logger.info(f"Annotated frame saved to {file_path}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving annotated frame: {e}")
            
            # Call the error callback if registered
            if self.on_error:
                try:
                    await self.on_error(str(e))
                except Exception as e:
                    self.logger.error(f"Error in error callback: {e}")
            
            return False
    
    async def _analyze_camera_frame(self, frame: np.ndarray) -> Dict[str, Any]:
        """
        Analyze camera frame for quality and functionality.
        
        Args:
            frame: Camera frame as numpy array
                
        Returns:
            Dict[str, Any]: Analysis results
        """
        # Convert to grayscale for analysis
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Calculate brightness
        brightness = np.mean(gray) / 255.0
        
        # Calculate contrast
        contrast = np.std(gray) / 255.0
        
        # Calculate sharpness (Laplacian variance)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        sharpness = np.var(laplacian)
        
        # Normalize sharpness to 0-1 range (empirical max value of 1000)
        sharpness_normalized = min(1.0, sharpness / 1000.0)
        
        # Detect faces to test camera functionality
        faces = self._face_cascade.detectMultiScale(gray, 1.3, 5)
        
        # Calculate focus score (higher is better)
        focus_score = sharpness_normalized
        
        # Calculate overall quality score
        quality_score = (brightness + contrast + focus_score) / 3.0
        
        # Prepare results
        results = {
            "brightness": brightness,
            "contrast": contrast,
            "sharpness": sharpness_normalized,
            "focus_score": focus_score,
            "quality_score": quality_score,
            "faces_detected": len(faces),
            "resolution": {
                "width": frame.shape[1],
                "height": frame.shape[0]
            },
            "issues": []
        }
        
        # Identify issues
        if brightness < 0.3:
            results["issues"].append({
                "type": "low_brightness",
                "severity": "medium",
                "message": "Low lighting conditions detected"
            })
        
        if contrast < 0.1:
            results["issues"].append({
                "type": "low_contrast",
                "severity": "medium",
                "message": "Low contrast detected"
            })
        
        if focus_score < 0.3:
            results["issues"].append({
                "type": "poor_focus",
                "severity": "high",
                "message": "Camera appears to be out of focus"
            })
        
        # Store results for later use
        self._analysis_results["camera"] = results
        
        return results
    
    async def _analyze_display_issue(self, frame: np.ndarray) -> Dict[str, Any]:
        """
        Analyze display issues in the frame.
        
        Args:
            frame: Camera frame as numpy array
                
        Returns:
            Dict[str, Any]: Analysis results
        """
        # Convert to HSV for color analysis
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Check for color issues
        color_distribution = {
            "red": np.sum((hsv[:,:,0] < 10) | (hsv[:,:,0] > 170)),
            "green": np.sum((hsv[:,:,0] > 35) & (hsv[:,:,0] < 85)),
            "blue": np.sum((hsv[:,:,0] > 85) & (hsv[:,:,0] < 135))
        }
        
        # Check for dead pixels (extreme bright spots)
        _, bright_mask = cv2.threshold(frame, 250, 255, cv2.THRESH_BINARY)
        bright_mask = cv2.cvtColor(bright_mask, cv2.COLOR_BGR2GRAY)
        bright_spots = cv2.findContours(bright_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
        
        # Check for black spots (dead pixels)
        _, dark_mask = cv2.threshold(frame, 5, 255, cv2.THRESH_BINARY_INV)
        dark_mask = cv2.cvtColor(dark_mask, cv2.COLOR_BGR2GRAY)
        dark_spots = cv2.findContours(dark_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
        
        # Prepare results
        results = {
            "color_distribution": color_distribution,
            "bright_spots": len(bright_spots),
            "dark_spots": len(dark_spots),
            "detected": False,
            "issues": []
        }
        
        # Identify issues
        total_pixels = frame.shape[0] * frame.shape[1]
        
        if len(bright_spots) > 10:
            results["detected"] = True
            results["issues"].append({
                "type": "bright_spots",
                "severity": "medium",
                "message": f"Detected {len(bright_spots)} bright spots, possible dead pixels"
            })
        
        if len(dark_spots) > 10:
            results["detected"] = True
            results["issues"].append({
                "type": "dark_spots",
                "severity": "medium",
                "message": f"Detected {len(dark_spots)} dark spots, possible dead pixels"
            })
        
        # Store results for later use
        if "hardware_issues" not in self._analysis_results:
            self._analysis_results["hardware_issues"] = {}
        
        self._analysis_results["hardware_issues"]["display"] = results
        
        return results
    
    async def _analyze_connection_issue(self, frame: np.ndarray) -> Dict[str, Any]:
        """
        Analyze connection issues in the frame.
        
        Args:
            frame: Camera frame as numpy array
                
        Returns:
            Dict[str, Any]: Analysis results
        """
        # This is a simplified implementation that would need to be expanded
        # with actual connection issue detection logic
        
        # For demonstration, we'll just check for common connection port colors
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Define color ranges for common ports
        blue_lower = np.array([100, 50, 50])
        blue_upper = np.array([130, 255, 255])
        blue_mask = cv2.inRange(hsv, blue_lower, blue_upper)
        blue_area = np.sum(blue_mask > 0)
        
        # Check for USB port blue color
        usb_port_detected = blue_area > 1000
        
        # Prepare results
        results = {
            "usb_port_detected": usb_port_detected,
            "detected": False,
            "issues": []
        }
        
        # In a real implementation, we would analyze the image for connection issues
        # such as bent pins, loose connections, etc.
        
        # Store results for later use
        if "hardware_issues" not in self._analysis_results:
            self._analysis_results["hardware_issues"] = {}
        
        self._analysis_results["hardware_issues"]["connection"] = results
        
        return results
    
    async def _analyze_physical_damage(self, frame: np.ndarray) -> Dict[str, Any]:
        """
        Analyze physical damage in the frame.
        
        Args:
            frame: Camera frame as numpy array
                
        Returns:
            Dict[str, Any]: Analysis results
        """
        # This is a simplified implementation that would need to be expanded
        # with actual physical damage detection logic
        
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply edge detection to find cracks or damage
        edges = cv2.Canny(gray, 50, 150)
        
        # Find contours in the edge image
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter contours by size and shape to identify potential cracks
        cracks = []
        for contour in contours:
            area = cv2.contourArea(contour)
            perimeter = cv2.arcLength(contour, True)
            
            # Skip small contours
            if area < 100:
                continue
            
            # Calculate shape features
            circularity = 4 * np.pi * area / (perimeter * perimeter) if perimeter > 0 else 0
            
            # Cracks typically have low circularity
            if circularity < 0.2:
                cracks.append(contour)
        
        # Prepare results
        results = {
            "potential_cracks": len(cracks),
            "detected": len(cracks) > 0,
            "issues": []
        }
        
        if len(cracks) > 0:
            results["issues"].append({
                "type": "potential_cracks",
                "severity": "high",
                "message": f"Detected {len(cracks)} potential cracks or damage"
            })
        
        # Store results for later use
        if "hardware_issues" not in self._analysis_results:
            self._analysis_results["hardware_issues"] = {}
        
        self._analysis_results["hardware_issues"]["physical_damage"] = results
        
        return results
    
    async def _analyze_led_status(self, frame: np.ndarray) -> Dict[str, Any]:
        """
        Analyze LED status in the frame.
        
        Args:
            frame: Camera frame as numpy array
                
        Returns:
            Dict[str, Any]: Analysis results
        """
        # Convert to HSV for color analysis
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Define color ranges for common LED colors
        green_lower = np.array([35, 100, 100])
        green_upper = np.array([85, 255, 255])
        green_mask = cv2.inRange(hsv, green_lower, green_upper)
        green_area = np.sum(green_mask > 0)
        
        red_lower1 = np.array([0, 100, 100])
        red_upper1 = np.array([10, 255, 255])
        red_mask1 = cv2.inRange(hsv, red_lower1, red_upper1)
        
        red_lower2 = np.array([170, 100, 100])
        red_upper2 = np.array([180, 255, 255])
        red_mask2 = cv2.inRange(hsv, red_lower2, red_upper2)
        
        red_mask = cv2.bitwise_or(red_mask1, red_mask2)
        red_area = np.sum(red_mask > 0)
        
        # Find bright spots that could be LEDs
        _, bright_mask = cv2.threshold(frame, 200, 255, cv2.THRESH_BINARY)
        bright_mask = cv2.cvtColor(bright_mask, cv2.COLOR_BGR2GRAY)
        bright_spots = cv2.findContours(bright_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
        
        # Determine LED status
        green_led_on = green_area > 500
        red_led_on = red_area > 500
        
        # Prepare results
        results = {
            "green_led_detected": green_led_on,
            "red_led_detected": red_led_on,
            "bright_spots": len(bright_spots),
            "detected": green_led_on or red_led_on,
            "issues": []
        }
        
        if red_led_on:
            results["issues"].append({
                "type": "red_led",
                "severity": "high",
                "message": "Red LED detected, indicating potential error state"
            })
        
        # Store results for later use
        if "hardware_issues" not in self._analysis_results:
            self._analysis_results["hardware_issues"] = {}
        
        self._analysis_results["hardware_issues"]["led_status"] = results
        
        return results

# Example usage
async def example_usage():
    # Create a video processor
    processor = VideoProcessor(device_id=0, width=640, height=480, fps=30)
    
    # Create a visual troubleshooter
    troubleshooter = VisualTroubleshooter(processor)
    
    # Define callbacks
    async def on_analysis_complete(results):
        print(f"Analysis complete: {results}")
    
    async def on_error(error):
        print(f"Error: {error}")
    
    # Register callbacks
    troubleshooter.register_callback("on_analysis_complete", on_analysis_complete)
    troubleshooter.register_callback("on_error", on_error)
    
    try:
        # Initialize video capture
        await processor.initialize()
        
        # Analyze camera
        print("Analyzing camera...")
        camera_results = await troubleshooter.analyze_camera()
        print(f"Camera analysis results: {camera_results}")
        
        # Analyze QR code
        print("Analyzing QR code...")
        qr_results = await troubleshooter.analyze_qr_code()
        print(f"QR code analysis results: {qr_results}")
        
        # Analyze hardware issues
        print("Analyzing display issues...")
        display_results = await troubleshooter.analyze_hardware_issue("display")
        print(f"Display analysis results: {display_results}")
        
        # Generate troubleshooting report
        print("Generating troubleshooting report...")
        report = await troubleshooter.generate_troubleshooting_report()
        print(f"Troubleshooting report: {report}")
        
        # Save annotated frame
        annotations = {
            "text": [
                {"text": "Camera Quality: Good", "x": 10, "y": 30, "color": (0, 255, 0)},
                {"text": "No issues detected", "x": 10, "y": 60, "color": (0, 255, 0)}
            ],
            "rectangles": [
                {"x1": 100, "y1": 100, "x2": 200, "y2": 200, "color": (0, 255, 0)}
            ]
        }
        
        await troubleshooter.save_annotated_frame("troubleshooting_report.jpg", annotations)
        
    finally:
        # Clean up
        processor.close()

if __name__ == "__main__":
    asyncio.run(example_usage())
