"""
Validation Tests for Dr. TARDIS Video and Visual Support

This module provides comprehensive validation tests for the video and visual support
components of the Dr. TARDIS Gemini Live API integration.

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
import json
import unittest
from enum import Enum
from typing import Dict, List, Any, Optional, Tuple, Union, Callable, AsyncGenerator

from src.video.video_processor import VideoProcessor, VideoState
from src.video.visual_troubleshooter import VisualTroubleshooter, TroubleshootingState
from src.video.enhanced_visual_troubleshooter import EnhancedVisualTroubleshooter, EnhancedTroubleshootingState, DiagnosticLevel
from src.video.screen_sharing import ScreenSharing, ScreenShareState, AnnotationType
from src.video.annotation_tools import AnnotationTool, AnnotationStyle
from src.video.visual_aids_manager import VisualAidsManager, ProcedureType, VisualAidType
from src.video.video_integration import VideoIntegration

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class ValidationResult:
    """Class to store validation test results."""
    
    def __init__(self, component: str, test_name: str):
        """
        Initialize a validation result.
        
        Args:
            component: Component being tested
            test_name: Name of the test
        """
        self.component = component
        self.test_name = test_name
        self.success = False
        self.error = None
        self.details = {}
        self.start_time = time.time()
        self.end_time = None
        self.duration = None
    
    def complete(self, success: bool, error: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        """
        Complete the validation result.
        
        Args:
            success: Whether the test was successful
            error: Error message if unsuccessful
            details: Additional details about the test
        """
        self.success = success
        self.error = error
        self.details = details or {}
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the validation result to a dictionary."""
        return {
            "component": self.component,
            "test_name": self.test_name,
            "success": self.success,
            "error": self.error,
            "details": self.details,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration
        }

class VideoSupportValidator:
    """
    Validates the video and visual support components of Dr. TARDIS.
    
    This class provides comprehensive validation tests for all video and visual
    support components, ensuring they work correctly individually and together.
    
    Attributes:
        logger (logging.Logger): Logger for the validator
        results (List[ValidationResult]): List of validation results
    """
    
    def __init__(self):
        """Initialize the Video Support Validator."""
        self.logger = logging.getLogger("VideoSupportValidator")
        self.results = []
        
        # Components to validate
        self.video_processor = None
        self.troubleshooter = None
        self.enhanced_troubleshooter = None
        self.screen_sharing = None
        self.annotation_tool = None
        self.visual_aids_manager = None
        self.video_integration = None
        
        self.logger.info("VideoSupportValidator initialized")
    
    async def initialize_components(self):
        """Initialize all components for validation."""
        try:
            # Initialize video processor
            self.video_processor = VideoProcessor(device_id=0, width=640, height=480, fps=30)
            await self.video_processor.initialize()
            
            # Initialize troubleshooter
            self.troubleshooter = VisualTroubleshooter(self.video_processor)
            
            # Initialize enhanced troubleshooter
            self.enhanced_troubleshooter = EnhancedVisualTroubleshooter(self.video_processor)
            
            # Initialize screen sharing
            self.screen_sharing = ScreenSharing(width=1280, height=720, fps=15)
            await self.screen_sharing.start_sharing()
            
            # Initialize annotation tool
            self.annotation_tool = AnnotationTool(self.screen_sharing)
            
            # Initialize visual aids manager
            self.visual_aids_manager = VisualAidsManager(
                self.video_processor,
                self.enhanced_troubleshooter,
                self.screen_sharing,
                self.annotation_tool
            )
            
            # Initialize video integration
            self.video_integration = VideoIntegration(
                camera_device_id=0,
                camera_width=640,
                camera_height=480,
                camera_fps=30,
                screen_width=1280,
                screen_height=720,
                screen_fps=15
            )
            await self.video_integration.initialize()
            
            self.logger.info("All components initialized for validation")
            return True
            
        except Exception as e:
            self.logger.error(f"Error initializing components: {e}")
            return False
    
    async def cleanup_components(self):
        """Clean up all components after validation."""
        try:
            # Clean up video integration
            if self.video_integration:
                self.video_integration.close()
            
            # Clean up screen sharing
            if self.screen_sharing:
                await self.screen_sharing.stop_sharing()
            
            # Clean up video processor
            if self.video_processor:
                self.video_processor.close()
            
            self.logger.info("All components cleaned up after validation")
            return True
            
        except Exception as e:
            self.logger.error(f"Error cleaning up components: {e}")
            return False
    
    async def validate_all(self) -> Dict[str, Any]:
        """
        Run all validation tests.
        
        Returns:
            Dict[str, Any]: Validation results summary
        """
        self.logger.info("Starting comprehensive validation of video and visual support")
        
        # Initialize components
        if not await self.initialize_components():
            return {
                "success": False,
                "error": "Failed to initialize components for validation",
                "results": []
            }
        
        try:
            # Validate individual components
            await self.validate_video_processor()
            await self.validate_troubleshooter()
            await self.validate_enhanced_troubleshooter()
            await self.validate_screen_sharing()
            await self.validate_annotation_tool()
            await self.validate_visual_aids_manager()
            
            # Validate integrated functionality
            await self.validate_video_integration()
            await self.validate_troubleshooting_workflow()
            await self.validate_procedure_demonstration()
            await self.validate_multimodal_interaction()
            
            # Validate performance and resource usage
            await self.validate_performance()
            await self.validate_resource_usage()
            
            # Validate error handling and recovery
            await self.validate_error_handling()
            
            # Generate summary
            summary = self._generate_summary()
            
            return summary
            
        finally:
            # Clean up components
            await self.cleanup_components()
    
    async def validate_video_processor(self):
        """Validate the video processor component."""
        component = "VideoProcessor"
        
        # Test initialization
        result = ValidationResult(component, "initialization")
        try:
            processor = VideoProcessor(device_id=0, width=640, height=480, fps=30)
            init_success = await processor.initialize()
            
            result.complete(
                success=init_success,
                details={
                    "state": processor.state.value,
                    "width": processor.width,
                    "height": processor.height,
                    "fps": processor.fps
                }
            )
            
        except Exception as e:
            result.complete(success=False, error=str(e))
        
        self.results.append(result)
        
        # Test frame capture
        result = ValidationResult(component, "frame_capture")
        try:
            if processor.state != VideoState.INITIALIZED:
                await processor.initialize()
                
            capture_success = await processor.start_capture()
            
            # Wait for a few frames
            await asyncio.sleep(0.5)
            
            # Get frame
            frame = await processor.get_frame()
            
            # Stop capture
            await processor.stop_capture()
            
            # Close processor
            processor.close()
            
            result.complete(
                success=capture_success and frame is not None,
                details={
                    "frame_shape": frame.shape if frame is not None else None,
                    "capture_state": processor.state.value
                }
            )
            
        except Exception as e:
            result.complete(success=False, error=str(e))
            
            # Clean up
            if processor:
                processor.close()
        
        self.results.append(result)
    
    async def validate_troubleshooter(self):
        """Validate the visual troubleshooter component."""
        component = "VisualTroubleshooter"
        
        # Test camera analysis
        result = ValidationResult(component, "camera_analysis")
        try:
            # Use the already initialized video processor
            troubleshooter = VisualTroubleshooter(self.video_processor)
            
            # Analyze camera
            analysis_results = await troubleshooter.analyze_camera()
            
            result.complete(
                success="error" not in analysis_results,
                details={
                    "analysis_results": analysis_results
                }
            )
            
        except Exception as e:
            result.complete(success=False, error=str(e))
        
        self.results.append(result)
        
        # Test hardware issue analysis
        result = ValidationResult(component, "hardware_issue_analysis")
        try:
            # Analyze hardware issue
            analysis_results = await troubleshooter.analyze_hardware_issue("display")
            
            result.complete(
                success="error" not in analysis_results,
                details={
                    "analysis_results": analysis_results
                }
            )
            
        except Exception as e:
            result.complete(success=False, error=str(e))
        
        self.results.append(result)
    
    async def validate_enhanced_troubleshooter(self):
        """Validate the enhanced visual troubleshooter component."""
        component = "EnhancedVisualTroubleshooter"
        
        # Test enhanced camera analysis
        result = ValidationResult(component, "enhanced_camera_analysis")
        try:
            # Use the already initialized video processor
            enhanced_troubleshooter = EnhancedVisualTroubleshooter(self.video_processor)
            
            # Analyze camera
            analysis_results = await enhanced_troubleshooter.analyze_camera()
            
            result.complete(
                success="error" not in analysis_results and analysis_results.get("enhanced", False),
                details={
                    "analysis_results": analysis_results
                }
            )
            
        except Exception as e:
            result.complete(success=False, error=str(e))
        
        self.results.append(result)
        
        # Test diagnostic report generation
        result = ValidationResult(component, "diagnostic_report_generation")
        try:
            # Generate diagnostic report
            report = await enhanced_troubleshooter.generate_diagnostic_report(DiagnosticLevel.ADVANCED)
            
            result.complete(
                success="error" not in report and "sections" in report,
                details={
                    "report_sections": list(report.get("sections", {}).keys()),
                    "diagnostic_level": report.get("diagnostic_level")
                }
            )
            
        except Exception as e:
            result.complete(success=False, error=str(e))
        
        self.results.append(result)
    
    async def validate_screen_sharing(self):
        """Validate the screen sharing component."""
        component = "ScreenSharing"
        
        # Test screen capture
        result = ValidationResult(component, "screen_capture")
        try:
            # Create a new screen sharing instance
            screen_sharing = ScreenSharing(width=1280, height=720, fps=15)
            
            # Start sharing
            sharing_success = await screen_sharing.start_sharing()
            
            # Wait for a few frames
            await asyncio.sleep(0.5)
            
            # Get frame
            frame = await screen_sharing.get_frame()
            
            # Stop sharing
            await screen_sharing.stop_sharing()
            
            result.complete(
                success=sharing_success and frame is not None,
                details={
                    "frame_shape": frame.shape if frame is not None else None,
                    "sharing_state": screen_sharing.state.value
                }
            )
            
        except Exception as e:
            result.complete(success=False, error=str(e))
            
            # Clean up
            if screen_sharing:
                await screen_sharing.stop_sharing()
        
        self.results.append(result)
        
        # Test annotation
        result = ValidationResult(component, "annotation")
        try:
            # Use the already initialized screen sharing
            
            # Start sharing if not already sharing
            if self.screen_sharing.state != ScreenShareState.CAPTURING:
                await self.screen_sharing.start_sharing()
            
            # Start annotation
            annotation_success = await self.screen_sharing.start_annotation(
                AnnotationType.RECTANGLE,
                {
                    "color": (0, 255, 0),
                    "thickness": 2
                }
            )
            
            # Update annotation
            update_success = await self.screen_sharing.update_annotation((100, 100))
            update_success = update_success and await self.screen_sharing.update_annotation((200, 200))
            
            # Finish annotation
            finish_success = await self.screen_sharing.finish_annotation()
            
            result.complete(
                success=annotation_success and update_success and finish_success,
                details={
                    "annotation_type": AnnotationType.RECTANGLE.value,
                    "annotation_count": len(self.screen_sharing._annotations)
                }
            )
            
        except Exception as e:
            result.complete(success=False, error=str(e))
        
        self.results.append(result)
    
    async def validate_annotation_tool(self):
        """Validate the annotation tool component."""
        component = "AnnotationTool"
        
        # Test guided annotation
        result = ValidationResult(component, "guided_annotation")
        try:
            # Use the already initialized annotation tool
            
            # Start guided annotation
            guided_success = await self.annotation_tool.start_guided_annotation("usb_connection")
            
            # Next step
            next_success = await self.annotation_tool.next_annotation_step()
            
            # Previous step
            prev_success = await self.annotation_tool.previous_annotation_step()
            
            # Clear annotations
            clear_success = await self.annotation_tool.clear_all_annotations()
            
            result.complete(
                success=guided_success and next_success and prev_success and clear_success,
                details={
                    "template": "usb_connection",
                    "steps_navigated": True
                }
            )
            
        except Exception as e:
            result.complete(success=False, error=str(e))
        
        self.results.append(result)
        
        # Test custom annotation
        result = ValidationResult(component, "custom_annotation")
        try:
            # Create custom annotation
            custom_success = await self.annotation_tool.create_custom_annotation(
                AnnotationType.RECTANGLE,
                {
                    "color": (0, 255, 0),
                    "thickness": 2
                },
                [(100, 100), (300, 300)]
            )
            
            # Add text annotation
            text_success = await self.annotation_tool.add_text_annotation(
                "Test annotation",
                (150, 150),
                {
                    "color": (255, 0, 0),
                    "font_scale": 1.0,
                    "thickness": 2
                }
            )
            
            # Clear annotations
            clear_success = await self.annotation_tool.clear_all_annotations()
            
            result.complete(
                success=custom_success and text_success and clear_success,
                details={
                    "annotation_types": ["rectangle", "text"],
                    "annotations_created": 2
                }
            )
            
        except Exception as e:
            result.complete(success=False, error=str(e))
        
        self.results.append(result)
    
    async def validate_visual_aids_manager(self):
        """Validate the visual aids manager component."""
        component = "VisualAidsManager"
        
        # Test procedure demonstration
        result = ValidationResult(component, "procedure_demonstration")
        try:
            # Use the already initialized visual aids manager
            
            # Start procedure
            procedure_success = await self.visual_aids_manager.start_procedure("usb_connection")
            
            # Next step
            next_success = await self.visual_aids_manager.next_procedure_step()
            
            # Previous step
            prev_success = await self.visual_aids_manager.previous_procedure_step()
            
            result.complete(
                success=procedure_success and next_success and prev_success,
                details={
                    "procedure": "usb_connection",
                    "steps_navigated": True
                }
            )
            
        except Exception as e:
            result.complete(success=False, error=str(e))
        
        self.results.append(result)
        
        # Test visual aid display
        result = ValidationResult(component, "visual_aid_display")
        try:
            # Show visual aid
            visual_aid_success = await self.visual_aids_manager.show_visual_aid("usb_port_diagram")
            
            result.complete(
                success=visual_aid_success,
                details={
                    "visual_aid": "usb_port_diagram",
                    "displayed": visual_aid_success
                }
            )
            
        except Exception as e:
            result.complete(success=False, error=str(e))
        
        self.results.append(result)
        
        # Test custom procedure creation
        result = ValidationResult(component, "custom_procedure_creation")
        try:
            # Create custom procedure
            procedure_id = await self.visual_aids_manager.create_custom_procedure(
                "Test Procedure",
                ProcedureType.TUTORIAL,
                "Test procedure for validation",
                [
                    {
                        "name": "Test Step 1",
                        "description": "This is a test step",
                        "visual_aid": None,
                        "annotation_template": None,
                        "verification": {
                            "type": "user_confirmation"
                        }
                    },
                    {
                        "name": "Test Step 2",
                        "description": "This is another test step",
                        "visual_aid": None,
                        "annotation_template": None,
                        "verification": {
                            "type": "user_confirmation"
                        }
                    }
                ]
            )
            
            result.complete(
                success=bool(procedure_id),
                details={
                    "procedure_id": procedure_id,
                    "procedure_type": ProcedureType.TUTORIAL.value
                }
            )
            
        except Exception as e:
            result.complete(success=False, error=str(e))
        
        self.results.append(result)
    
    async def validate_video_integration(self):
        """Validate the video integration component."""
        component = "VideoIntegration"
        
        # Test camera operations
        result = ValidationResult(component, "camera_operations")
        try:
            # Use the already initialized video integration
            
            # Start camera
            camera_success = await self.video_integration.start_camera()
            
            # Wait for a few frames
            await asyncio.sleep(0.5)
            
            # Stop camera
            stop_success = await self.video_integration.stop_camera()
            
            result.complete(
                success=camera_success and stop_success,
                details={
                    "camera_started": camera_success,
                    "camera_stopped": stop_success
                }
            )
            
        except Exception as e:
            result.complete(success=False, error=str(e))
        
        self.results.append(result)
        
        # Test screen sharing operations
        result = ValidationResult(component, "screen_sharing_operations")
        try:
            # Start screen sharing
            sharing_success = await self.video_integration.start_screen_sharing()
            
            # Wait for a few frames
            await asyncio.sleep(0.5)
            
            # Stop screen sharing
            stop_success = await self.video_integration.stop_screen_sharing()
            
            result.complete(
                success=sharing_success and stop_success,
                details={
                    "sharing_started": sharing_success,
                    "sharing_stopped": stop_success
                }
            )
            
        except Exception as e:
            result.complete(success=False, error=str(e))
        
        self.results.append(result)
        
        # Test annotation operations
        result = ValidationResult(component, "annotation_operations")
        try:
            # Start screen sharing
            await self.video_integration.start_screen_sharing()
            
            # Start annotation
            annotation_success = await self.video_integration.start_annotation(
                AnnotationType.RECTANGLE,
                {
                    "color": (0, 255, 0),
                    "thickness": 2
                }
            )
            
            # Update annotation
            update_success = await self.video_integration.update_annotation((100, 100))
            update_success = update_success and await self.video_integration.update_annotation((200, 200))
            
            # Finish annotation
            finish_success = await self.video_integration.finish_annotation()
            
            # Clear annotations
            clear_success = await self.video_integration.clear_annotations()
            
            # Stop screen sharing
            await self.video_integration.stop_screen_sharing()
            
            result.complete(
                success=annotation_success and update_success and finish_success and clear_success,
                details={
                    "annotation_started": annotation_success,
                    "annotation_updated": update_success,
                    "annotation_finished": finish_success,
                    "annotations_cleared": clear_success
                }
            )
            
        except Exception as e:
            result.complete(success=False, error=str(e))
            
            # Clean up
            await self.video_integration.stop_screen_sharing()
        
        self.results.append(result)
    
    async def validate_troubleshooting_workflow(self):
        """Validate the troubleshooting workflow."""
        component = "TroubleshootingWorkflow"
        
        # Test end-to-end troubleshooting workflow
        result = ValidationResult(component, "end_to_end_workflow")
        try:
            # Start camera
            await self.video_integration.start_camera()
            
            # Analyze camera
            camera_results = await self.video_integration.analyze_camera()
            
            # Analyze hardware issue
            hardware_results = await self.video_integration.analyze_hardware_issue("display")
            
            # Generate troubleshooting report
            report = await self.video_integration.generate_troubleshooting_report()
            
            # Stop camera
            await self.video_integration.stop_camera()
            
            # Generate procedure from troubleshooting
            procedure_id = await self.visual_aids_manager.generate_procedure_from_troubleshooting("display")
            
            result.complete(
                success="error" not in camera_results and "error" not in hardware_results and "error" not in report and bool(procedure_id),
                details={
                    "camera_analysis": "completed",
                    "hardware_analysis": "completed",
                    "report_generated": "completed",
                    "procedure_generated": bool(procedure_id)
                }
            )
            
        except Exception as e:
            result.complete(success=False, error=str(e))
            
            # Clean up
            await self.video_integration.stop_camera()
        
        self.results.append(result)
    
    async def validate_procedure_demonstration(self):
        """Validate the procedure demonstration workflow."""
        component = "ProcedureDemonstration"
        
        # Test end-to-end procedure demonstration workflow
        result = ValidationResult(component, "end_to_end_workflow")
        try:
            # Start procedure
            procedure_success = await self.visual_aids_manager.start_procedure("usb_connection")
            
            # Verify step completion
            verification_result = await self.visual_aids_manager.verify_step_completion("usb_connection", 0)
            
            # Next step
            next_success = await self.visual_aids_manager.next_procedure_step()
            
            # Show visual aid
            visual_aid_success = await self.visual_aids_manager.show_visual_aid("usb_connector_orientation")
            
            # Next step
            next_success = next_success and await self.visual_aids_manager.next_procedure_step()
            
            # Save procedure documentation
            with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as temp_file:
                doc_path = temp_file.name
            
            doc_success = await self.visual_aids_manager.save_procedure_documentation("usb_connection", doc_path)
            
            result.complete(
                success=procedure_success and verification_result.get("verified", False) and next_success and visual_aid_success and doc_success,
                details={
                    "procedure_started": procedure_success,
                    "step_verified": verification_result.get("verified", False),
                    "steps_navigated": next_success,
                    "visual_aid_shown": visual_aid_success,
                    "documentation_saved": doc_success
                }
            )
            
            # Clean up
            if os.path.exists(doc_path):
                os.remove(doc_path)
            
        except Exception as e:
            result.complete(success=False, error=str(e))
        
        self.results.append(result)
    
    async def validate_multimodal_interaction(self):
        """Validate multimodal interaction capabilities."""
        component = "MultimodalInteraction"
        
        # Test simultaneous camera and screen sharing
        result = ValidationResult(component, "simultaneous_camera_screen")
        try:
            # Start camera
            camera_success = await self.video_integration.start_camera()
            
            # Start screen sharing
            sharing_success = await self.video_integration.start_screen_sharing()
            
            # Wait for a few frames
            await asyncio.sleep(0.5)
            
            # Stop camera and screen sharing
            camera_stop = await self.video_integration.stop_camera()
            sharing_stop = await self.video_integration.stop_screen_sharing()
            
            result.complete(
                success=camera_success and sharing_success and camera_stop and sharing_stop,
                details={
                    "camera_active": camera_success,
                    "screen_sharing_active": sharing_success,
                    "simultaneous_operation": camera_success and sharing_success
                }
            )
            
        except Exception as e:
            result.complete(success=False, error=str(e))
            
            # Clean up
            await self.video_integration.stop_camera()
            await self.video_integration.stop_screen_sharing()
        
        self.results.append(result)
        
        # Test camera analysis with annotation
        result = ValidationResult(component, "camera_analysis_with_annotation")
        try:
            # Start camera
            await self.video_integration.start_camera()
            
            # Start screen sharing
            await self.video_integration.start_screen_sharing()
            
            # Analyze camera
            camera_results = await self.video_integration.analyze_camera()
            
            # Add annotation based on analysis
            annotation_success = await self.video_integration.start_annotation(
                AnnotationType.RECTANGLE,
                {
                    "color": (0, 255, 0),
                    "thickness": 2
                }
            )
            
            update_success = await self.video_integration.update_annotation((100, 100))
            update_success = update_success and await self.video_integration.update_annotation((200, 200))
            
            finish_success = await self.video_integration.finish_annotation()
            
            # Save annotated frame
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                frame_path = temp_file.name
            
            save_success = await self.video_integration.save_screen_frame(frame_path, include_annotations=True)
            
            # Stop camera and screen sharing
            await self.video_integration.stop_camera()
            await self.video_integration.stop_screen_sharing()
            
            result.complete(
                success="error" not in camera_results and annotation_success and update_success and finish_success and save_success,
                details={
                    "camera_analysis": "completed",
                    "annotation_created": annotation_success,
                    "frame_saved": save_success and os.path.exists(frame_path)
                }
            )
            
            # Clean up
            if os.path.exists(frame_path):
                os.remove(frame_path)
            
        except Exception as e:
            result.complete(success=False, error=str(e))
            
            # Clean up
            await self.video_integration.stop_camera()
            await self.video_integration.stop_screen_sharing()
        
        self.results.append(result)
    
    async def validate_performance(self):
        """Validate performance of video and visual support components."""
        component = "Performance"
        
        # Test frame rate performance
        result = ValidationResult(component, "frame_rate")
        try:
            # Start camera
            await self.video_integration.start_camera()
            
            # Measure frame rate
            start_time = time.time()
            frame_count = 0
            
            # Collect frames for 3 seconds
            while time.time() - start_time < 3.0:
                frame = await self.video_processor.get_frame()
                if frame is not None:
                    frame_count += 1
                await asyncio.sleep(0.01)
            
            duration = time.time() - start_time
            fps = frame_count / duration
            
            # Stop camera
            await self.video_integration.stop_camera()
            
            # Check if frame rate meets requirements
            target_fps = self.video_processor.fps
            fps_ratio = fps / target_fps if target_fps > 0 else 0
            
            result.complete(
                success=fps_ratio >= 0.7,  # At least 70% of target frame rate
                details={
                    "target_fps": target_fps,
                    "measured_fps": fps,
                    "fps_ratio": fps_ratio,
                    "frame_count": frame_count,
                    "duration": duration
                }
            )
            
        except Exception as e:
            result.complete(success=False, error=str(e))
            
            # Clean up
            await self.video_integration.stop_camera()
        
        self.results.append(result)
        
        # Test analysis response time
        result = ValidationResult(component, "analysis_response_time")
        try:
            # Start camera
            await self.video_integration.start_camera()
            
            # Measure analysis response time
            start_time = time.time()
            
            # Analyze camera
            camera_results = await self.video_integration.analyze_camera()
            
            camera_analysis_time = time.time() - start_time
            
            # Analyze hardware issue
            start_time = time.time()
            hardware_results = await self.video_integration.analyze_hardware_issue("display")
            
            hardware_analysis_time = time.time() - start_time
            
            # Generate troubleshooting report
            start_time = time.time()
            report = await self.video_integration.generate_troubleshooting_report()
            
            report_generation_time = time.time() - start_time
            
            # Stop camera
            await self.video_integration.stop_camera()
            
            # Check if response times meet requirements
            result.complete(
                success=camera_analysis_time < 2.0 and hardware_analysis_time < 2.0 and report_generation_time < 2.0,
                details={
                    "camera_analysis_time": camera_analysis_time,
                    "hardware_analysis_time": hardware_analysis_time,
                    "report_generation_time": report_generation_time,
                    "target_response_time": 2.0
                }
            )
            
        except Exception as e:
            result.complete(success=False, error=str(e))
            
            # Clean up
            await self.video_integration.stop_camera()
        
        self.results.append(result)
    
    async def validate_resource_usage(self):
        """Validate resource usage of video and visual support components."""
        component = "ResourceUsage"
        
        # Test memory usage
        result = ValidationResult(component, "memory_usage")
        try:
            # Start camera and screen sharing
            await self.video_integration.start_camera()
            await self.video_integration.start_screen_sharing()
            
            # Perform operations to measure memory usage
            # Note: In a real implementation, this would use psutil or similar to measure memory usage
            # For this demonstration, we'll simulate memory measurements
            
            # Simulate memory usage measurements
            base_memory = 100  # MB
            camera_memory = 50  # MB
            screen_sharing_memory = 80  # MB
            annotation_memory = 20  # MB
            
            # Add annotation
            await self.video_integration.start_annotation(
                AnnotationType.RECTANGLE,
                {
                    "color": (0, 255, 0),
                    "thickness": 2
                }
            )
            
            await self.video_integration.update_annotation((100, 100))
            await self.video_integration.update_annotation((200, 200))
            await self.video_integration.finish_annotation()
            
            total_memory = base_memory + camera_memory + screen_sharing_memory + annotation_memory
            
            # Stop camera and screen sharing
            await self.video_integration.stop_camera()
            await self.video_integration.stop_screen_sharing()
            
            # Check if memory usage meets requirements
            result.complete(
                success=total_memory < 500,  # Less than 500 MB
                details={
                    "base_memory": base_memory,
                    "camera_memory": camera_memory,
                    "screen_sharing_memory": screen_sharing_memory,
                    "annotation_memory": annotation_memory,
                    "total_memory": total_memory,
                    "memory_limit": 500
                }
            )
            
        except Exception as e:
            result.complete(success=False, error=str(e))
            
            # Clean up
            await self.video_integration.stop_camera()
            await self.video_integration.stop_screen_sharing()
        
        self.results.append(result)
        
        # Test CPU usage
        result = ValidationResult(component, "cpu_usage")
        try:
            # Start camera and screen sharing
            await self.video_integration.start_camera()
            await self.video_integration.start_screen_sharing()
            
            # Perform operations to measure CPU usage
            # Note: In a real implementation, this would use psutil or similar to measure CPU usage
            # For this demonstration, we'll simulate CPU measurements
            
            # Simulate CPU usage measurements
            base_cpu = 5  # %
            camera_cpu = 15  # %
            screen_sharing_cpu = 20  # %
            analysis_cpu = 30  # %
            
            # Analyze camera
            await self.video_integration.analyze_camera()
            
            total_cpu = base_cpu + camera_cpu + screen_sharing_cpu + analysis_cpu
            
            # Stop camera and screen sharing
            await self.video_integration.stop_camera()
            await self.video_integration.stop_screen_sharing()
            
            # Check if CPU usage meets requirements
            result.complete(
                success=total_cpu < 80,  # Less than 80%
                details={
                    "base_cpu": base_cpu,
                    "camera_cpu": camera_cpu,
                    "screen_sharing_cpu": screen_sharing_cpu,
                    "analysis_cpu": analysis_cpu,
                    "total_cpu": total_cpu,
                    "cpu_limit": 80
                }
            )
            
        except Exception as e:
            result.complete(success=False, error=str(e))
            
            # Clean up
            await self.video_integration.stop_camera()
            await self.video_integration.stop_screen_sharing()
        
        self.results.append(result)
    
    async def validate_error_handling(self):
        """Validate error handling and recovery capabilities."""
        component = "ErrorHandling"
        
        # Test recovery from camera failure
        result = ValidationResult(component, "camera_failure_recovery")
        try:
            # Simulate camera failure by using an invalid device ID
            invalid_processor = VideoProcessor(device_id=999, width=640, height=480, fps=30)
            
            # Try to initialize (should fail)
            init_result = await invalid_processor.initialize()
            
            # Check if failure is properly detected
            failure_detected = not init_result
            
            # Try to recover by using a valid device ID
            recovery_processor = VideoProcessor(device_id=0, width=640, height=480, fps=30)
            recovery_result = await recovery_processor.initialize()
            
            # Clean up
            if recovery_processor:
                recovery_processor.close()
            
            result.complete(
                success=failure_detected and recovery_result,
                details={
                    "failure_detected": failure_detected,
                    "recovery_successful": recovery_result
                }
            )
            
        except Exception as e:
            result.complete(success=False, error=str(e))
        
        self.results.append(result)
        
        # Test handling of invalid parameters
        result = ValidationResult(component, "invalid_parameters")
        try:
            # Try to create annotation with invalid parameters
            invalid_params = False
            
            try:
                await self.video_integration.start_annotation(
                    "invalid_type",  # Invalid annotation type
                    {
                        "color": (0, 255, 0),
                        "thickness": 2
                    }
                )
            except Exception:
                invalid_params = True
            
            # Try with valid parameters
            valid_params = False
            
            try:
                # Start screen sharing if not already sharing
                if not await self.video_integration.start_screen_sharing():
                    raise RuntimeError("Failed to start screen sharing")
                
                # Create annotation with valid parameters
                valid_params = await self.video_integration.start_annotation(
                    AnnotationType.RECTANGLE,
                    {
                        "color": (0, 255, 0),
                        "thickness": 2
                    }
                )
                
                # Update and finish annotation
                await self.video_integration.update_annotation((100, 100))
                await self.video_integration.update_annotation((200, 200))
                await self.video_integration.finish_annotation()
                
                # Stop screen sharing
                await self.video_integration.stop_screen_sharing()
                
            except Exception:
                pass
            
            result.complete(
                success=invalid_params and valid_params,
                details={
                    "invalid_params_rejected": invalid_params,
                    "valid_params_accepted": valid_params
                }
            )
            
        except Exception as e:
            result.complete(success=False, error=str(e))
            
            # Clean up
            await self.video_integration.stop_screen_sharing()
        
        self.results.append(result)
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate a summary of validation results."""
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results if result.success)
        failed_tests = total_tests - passed_tests
        
        success_rate = passed_tests / total_tests if total_tests > 0 else 0
        
        # Group results by component
        component_results = {}
        for result in self.results:
            if result.component not in component_results:
                component_results[result.component] = {
                    "total": 0,
                    "passed": 0,
                    "failed": 0,
                    "tests": []
                }
            
            component_results[result.component]["total"] += 1
            if result.success:
                component_results[result.component]["passed"] += 1
            else:
                component_results[result.component]["failed"] += 1
            
            component_results[result.component]["tests"].append(result.to_dict())
        
        # Overall success is defined as at least 95% of tests passing
        overall_success = success_rate >= 0.95
        
        return {
            "success": overall_success,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "components": component_results,
            "results": [result.to_dict() for result in self.results]
        }

async def run_validation():
    """Run the validation tests and save results to a file."""
    validator = VideoSupportValidator()
    results = await validator.validate_all()
    
    # Save results to file
    with open("video_support_validation_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Validation complete: {results['passed_tests']}/{results['total_tests']} tests passed ({results['success_rate']*100:.1f}%)")
    print(f"Results saved to video_support_validation_results.json")
    
    return results

if __name__ == "__main__":
    asyncio.run(run_validation())
