"""
Validation Tests for Dr. TARDIS Video and Visual Support with Mock Components

This module provides validation tests for Dr. TARDIS's video and visual support
functionality using mock components for hardware and asset-dependent features.

Author: ApexAgent Development Team
Date: May 26, 2025
"""

import asyncio
import cv2
import json
import logging
import numpy as np
import os
import sys
import tempfile
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import mock components
from src.video.mock_video_processor import MockVideoProcessor
from src.video.mock_animation_tools import MockAnimationTools, AnimationType
from src.video.visual_troubleshooter import VisualTroubleshooter
from src.video.enhanced_visual_troubleshooter import EnhancedVisualTroubleshooter
from src.video.screen_sharing import ScreenSharing
from src.video.annotation_tools import AnnotationTools
from src.video.visual_aids_manager import VisualAidsManager
from src.video.video_integration import VideoIntegration

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class VideoSupportValidator:
    """
    Validator for Dr. TARDIS video and visual support functionality.
    
    This class provides comprehensive validation tests for all video and visual
    support components, using mock implementations for hardware and asset-dependent
    features to enable testing in sandbox environments.
    """
    
    def __init__(self):
        """Initialize the validator."""
        self.logger = logging.getLogger("VideoSupportValidator")
        self.results = {
            "success": False,
            "results": [],
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "success_rate": 0.0,
            "components": {}
        }
        self.logger.info("VideoSupportValidator initialized")
    
    async def validate_all(self) -> Dict[str, Any]:
        """
        Run all validation tests.
        
        Returns:
            Dict[str, Any]: Validation results
        """
        self.logger.info("Starting comprehensive validation of video and visual support")
        
        try:
            # Initialize components with mock implementations
            video_processor = MockVideoProcessor(width=640, height=480, fps=30)
            animation_tools = MockAnimationTools(width=640, height=480)
            visual_troubleshooter = VisualTroubleshooter(video_processor=video_processor)
            enhanced_troubleshooter = EnhancedVisualTroubleshooter(video_processor=video_processor)
            screen_sharing = ScreenSharing()
            annotation_tools = AnnotationTools()
            visual_aids = VisualAidsManager(
                video_processor=video_processor,
                enhanced_troubleshooter=enhanced_troubleshooter,
                screen_sharing=screen_sharing,
                annotation_tool=annotation_tools
            )
            
            # Initialize video integration with mock components
            video_integration = VideoIntegration(
                camera_device_id=0,
                camera_width=640,
                camera_height=480,
                camera_fps=30,
                screen_width=1280,
                screen_height=720,
                screen_fps=15
            )
            
            # Run component validation tests
            await self.validate_video_processor(video_processor)
            await self.validate_visual_troubleshooter(visual_troubleshooter)
            await self.validate_enhanced_troubleshooter(enhanced_troubleshooter)
            await self.validate_screen_sharing(screen_sharing)
            await self.validate_annotation_tools(annotation_tools, animation_tools)
            await self.validate_visual_aids(visual_aids, animation_tools)
            await self.validate_video_integration(video_integration)
            
            # Calculate overall results
            self.results["total_tests"] = sum(component["total"] for component in self.results["components"].values())
            self.results["passed_tests"] = sum(component["passed"] for component in self.results["components"].values())
            self.results["failed_tests"] = self.results["total_tests"] - self.results["passed_tests"]
            
            if self.results["total_tests"] > 0:
                self.results["success_rate"] = self.results["passed_tests"] / self.results["total_tests"]
            
            self.results["success"] = self.results["success_rate"] >= 0.95
            
        except Exception as e:
            self.logger.error(f"Error during validation: {e}")
            self.results["error"] = str(e)
        
        # Clean up resources
        video_processor.close()
        
        return self.results
    
    async def validate_video_processor(self, video_processor: MockVideoProcessor) -> None:
        """
        Validate the video processor component.
        
        Args:
            video_processor: Video processor to validate
        """
        component_name = "VideoProcessor"
        self.results["components"][component_name] = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "tests": []
        }
        
        # Test initialization
        await self._run_test(
            component_name,
            "initialize",
            self._test_video_processor_initialize,
            video_processor
        )
        
        # Test frame capture
        await self._run_test(
            component_name,
            "capture_frames",
            self._test_video_processor_capture,
            video_processor
        )
        
        # Test frame saving
        await self._run_test(
            component_name,
            "save_frame",
            self._test_video_processor_save_frame,
            video_processor
        )
        
        # Test video saving
        await self._run_test(
            component_name,
            "save_video",
            self._test_video_processor_save_video,
            video_processor
        )
    
    async def validate_visual_troubleshooter(self, troubleshooter: VisualTroubleshooter) -> None:
        """
        Validate the visual troubleshooter component.
        
        Args:
            troubleshooter: Visual troubleshooter to validate
        """
        component_name = "VisualTroubleshooter"
        self.results["components"][component_name] = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "tests": []
        }
        
        # Test initialization
        await self._run_test(
            component_name,
            "initialize",
            self._test_troubleshooter_initialize,
            troubleshooter
        )
        
        # Test analysis
        await self._run_test(
            component_name,
            "analyze_image",
            self._test_troubleshooter_analyze,
            troubleshooter
        )
        
        # Test diagnostics
        await self._run_test(
            component_name,
            "generate_diagnostics",
            self._test_troubleshooter_diagnostics,
            troubleshooter
        )
    
    async def validate_enhanced_troubleshooter(self, troubleshooter: EnhancedVisualTroubleshooter) -> None:
        """
        Validate the enhanced visual troubleshooter component.
        
        Args:
            troubleshooter: Enhanced visual troubleshooter to validate
        """
        component_name = "EnhancedVisualTroubleshooter"
        self.results["components"][component_name] = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "tests": []
        }
        
        # Test initialization
        await self._run_test(
            component_name,
            "initialize",
            self._test_enhanced_troubleshooter_initialize,
            troubleshooter
        )
        
        # Test advanced analysis
        await self._run_test(
            component_name,
            "advanced_analysis",
            self._test_enhanced_troubleshooter_analysis,
            troubleshooter
        )
        
        # Test historical comparison
        await self._run_test(
            component_name,
            "historical_comparison",
            self._test_enhanced_troubleshooter_historical,
            troubleshooter
        )
    
    async def validate_screen_sharing(self, screen_sharing: ScreenSharing) -> None:
        """
        Validate the screen sharing component.
        
        Args:
            screen_sharing: Screen sharing to validate
        """
        component_name = "ScreenSharing"
        self.results["components"][component_name] = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "tests": []
        }
        
        # Test initialization
        await self._run_test(
            component_name,
            "initialize",
            self._test_screen_sharing_initialize,
            screen_sharing
        )
        
        # Test screen capture
        await self._run_test(
            component_name,
            "capture_screen",
            self._test_screen_sharing_capture,
            screen_sharing
        )
        
        # Test annotation
        await self._run_test(
            component_name,
            "annotate_screen",
            self._test_screen_sharing_annotate,
            screen_sharing
        )
    
    async def validate_annotation_tools(self, annotation_tools: AnnotationTools, 
                                      animation_tools: MockAnimationTools) -> None:
        """
        Validate the annotation tools component.
        
        Args:
            annotation_tools: Annotation tools to validate
            animation_tools: Mock animation tools for testing
        """
        component_name = "AnnotationTools"
        self.results["components"][component_name] = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "tests": []
        }
        
        # Test initialization
        await self._run_test(
            component_name,
            "initialize",
            self._test_annotation_tools_initialize,
            annotation_tools
        )
        
        # Test annotation creation
        await self._run_test(
            component_name,
            "create_annotation",
            self._test_annotation_tools_create,
            annotation_tools,
            animation_tools
        )
        
        # Test annotation sequence
        await self._run_test(
            component_name,
            "create_sequence",
            self._test_annotation_tools_sequence,
            annotation_tools,
            animation_tools
        )
    
    async def validate_visual_aids(self, visual_aids: VisualAidsManager,
                                 animation_tools: MockAnimationTools) -> None:
        """
        Validate the visual aids manager component.
        
        Args:
            visual_aids: Visual aids manager to validate
            animation_tools: Mock animation tools for testing
        """
        component_name = "VisualAidsManager"
        self.results["components"][component_name] = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "tests": []
        }
        
        # Test initialization
        await self._run_test(
            component_name,
            "initialize",
            self._test_visual_aids_initialize,
            visual_aids
        )
        
        # Test procedure creation
        await self._run_test(
            component_name,
            "create_procedure",
            self._test_visual_aids_procedure,
            visual_aids,
            animation_tools
        )
        
        # Test visual aid generation
        await self._run_test(
            component_name,
            "generate_visual_aid",
            self._test_visual_aids_generation,
            visual_aids,
            animation_tools
        )
    
    async def validate_video_integration(self, video_integration: VideoIntegration) -> None:
        """
        Validate the video integration component.
        
        Args:
            video_integration: Video integration to validate
        """
        component_name = "VideoIntegration"
        self.results["components"][component_name] = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "tests": []
        }
        
        # Test initialization
        await self._run_test(
            component_name,
            "initialize",
            self._test_video_integration_initialize,
            video_integration
        )
        
        # Test camera analysis
        await self._run_test(
            component_name,
            "camera_analysis",
            self._test_video_integration_camera_analysis,
            video_integration
        )
        
        # Test screen sharing
        await self._run_test(
            component_name,
            "screen_sharing",
            self._test_video_integration_screen_sharing,
            video_integration
        )
        
        # Test event handling
        await self._run_test(
            component_name,
            "event_handling",
            self._test_video_integration_events,
            video_integration
        )
    
    async def _run_test(self, component_name: str, test_name: str, test_func, *args) -> None:
        """
        Run a single test and record results.
        
        Args:
            component_name: Name of the component being tested
            test_name: Name of the test
            test_func: Test function to run
            *args: Arguments to pass to the test function
        """
        self.logger.info(f"Running test: {component_name}.{test_name}")
        
        test_result = {
            "test_name": test_name,
            "success": False,
            "duration": 0.0,
            "error": None,
            "details": {}
        }
        
        start_time = time.time()
        
        try:
            # Run the test
            test_result["details"] = await test_func(*args)
            test_result["success"] = True
            
        except Exception as e:
            self.logger.error(f"Test failed: {component_name}.{test_name} - {e}")
            test_result["error"] = str(e)
        
        # Calculate duration
        test_result["duration"] = time.time() - start_time
        
        # Update component results
        self.results["components"][component_name]["total"] += 1
        if test_result["success"]:
            self.results["components"][component_name]["passed"] += 1
        else:
            self.results["components"][component_name]["failed"] += 1
        
        # Add test result
        self.results["components"][component_name]["tests"].append(test_result)
        
        self.logger.info(f"Test {component_name}.{test_name} {'passed' if test_result['success'] else 'failed'} in {test_result['duration']:.2f}s")
    
    # Test implementations
    
    async def _test_video_processor_initialize(self, video_processor: MockVideoProcessor) -> Dict[str, Any]:
        """Test video processor initialization."""
        # Initialize video processor
        success = await video_processor.initialize()
        
        # Verify state
        state_valid = video_processor.state.value == "idle"
        
        return {
            "initialization_success": success,
            "state_valid": state_valid,
            "state": video_processor.state.value,
            "width": video_processor.width,
            "height": video_processor.height,
            "fps": video_processor.fps
        }
    
    async def _test_video_processor_capture(self, video_processor: MockVideoProcessor) -> Dict[str, Any]:
        """Test video processor frame capture."""
        # Start capture
        start_success = await video_processor.start_capture()
        
        # Wait for frames
        await asyncio.sleep(1.0)
        
        # Get a frame
        frame = await video_processor.get_frame()
        
        # Stop capture
        stop_success = await video_processor.stop_capture()
        
        # Verify frame
        frame_valid = frame is not None and frame.shape == (video_processor.height, video_processor.width, 3)
        
        return {
            "start_success": start_success,
            "stop_success": stop_success,
            "frame_valid": frame_valid,
            "frame_shape": str(frame.shape) if frame is not None else "None"
        }
    
    async def _test_video_processor_save_frame(self, video_processor: MockVideoProcessor) -> Dict[str, Any]:
        """Test video processor frame saving."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
            temp_path = temp_file.name
        
        # Start capture
        await video_processor.start_capture()
        
        # Wait for frames
        await asyncio.sleep(0.5)
        
        # Save a frame
        save_success = await video_processor.save_frame(temp_path)
        
        # Stop capture
        await video_processor.stop_capture()
        
        # Verify saved file
        file_exists = os.path.exists(temp_path)
        file_size = os.path.getsize(temp_path) if file_exists else 0
        
        # Clean up
        if file_exists:
            os.unlink(temp_path)
        
        return {
            "save_success": save_success,
            "file_exists": file_exists,
            "file_size": file_size
        }
    
    async def _test_video_processor_save_video(self, video_processor: MockVideoProcessor) -> Dict[str, Any]:
        """Test video processor video saving."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix=".avi", delete=False) as temp_file:
            temp_path = temp_file.name
        
        # Start capture
        await video_processor.start_capture()
        
        # Save a short video
        save_success = await video_processor.save_video(temp_path, 1.0)
        
        # Stop capture
        await video_processor.stop_capture()
        
        # Verify saved file
        file_exists = os.path.exists(temp_path)
        file_size = os.path.getsize(temp_path) if file_exists else 0
        
        # Clean up
        if file_exists:
            os.unlink(temp_path)
        
        return {
            "save_success": save_success,
            "file_exists": file_exists,
            "file_size": file_size
        }
    
    async def _test_troubleshooter_initialize(self, troubleshooter: VisualTroubleshooter) -> Dict[str, Any]:
        """Test visual troubleshooter initialization."""
        # Verify initialization
        models_loaded = troubleshooter.models_loaded
        
        return {
            "models_loaded": models_loaded,
            "supported_devices": len(troubleshooter.supported_devices)
        }
    
    async def _test_troubleshooter_analyze(self, troubleshooter: VisualTroubleshooter) -> Dict[str, Any]:
        """Test visual troubleshooter image analysis."""
        # Create a test image
        image = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(image, "Test Image", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
        
        # Analyze image
        analysis = await troubleshooter.analyze_image(image)
        
        return {
            "analysis_success": analysis is not None,
            "analysis_keys": list(analysis.keys()) if analysis else []
        }
    
    async def _test_troubleshooter_diagnostics(self, troubleshooter: VisualTroubleshooter) -> Dict[str, Any]:
        """Test visual troubleshooter diagnostics."""
        # Create a test image
        image = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(image, "Test Image", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
        
        # Generate diagnostics
        diagnostics = await troubleshooter.generate_diagnostics(image)
        
        return {
            "diagnostics_success": diagnostics is not None,
            "diagnostics_keys": list(diagnostics.keys()) if diagnostics else []
        }
    
    async def _test_enhanced_troubleshooter_initialize(self, troubleshooter: EnhancedVisualTroubleshooter) -> Dict[str, Any]:
        """Test enhanced visual troubleshooter initialization."""
        # Verify initialization
        models_loaded = troubleshooter.models_loaded
        
        return {
            "models_loaded": models_loaded,
            "supported_devices": len(troubleshooter.supported_devices)
        }
    
    async def _test_enhanced_troubleshooter_analysis(self, troubleshooter: EnhancedVisualTroubleshooter) -> Dict[str, Any]:
        """Test enhanced visual troubleshooter advanced analysis."""
        # Create a test image
        image = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(image, "Test Image", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
        
        # Perform advanced analysis
        analysis = await troubleshooter.analyze_image_advanced(image)
        
        return {
            "analysis_success": analysis is not None,
            "analysis_keys": list(analysis.keys()) if analysis else []
        }
    
    async def _test_enhanced_troubleshooter_historical(self, troubleshooter: EnhancedVisualTroubleshooter) -> Dict[str, Any]:
        """Test enhanced visual troubleshooter historical comparison."""
        # Create test images
        image1 = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(image1, "Image 1", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
        
        image2 = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(image2, "Image 2", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
        
        # Perform historical comparison
        comparison = await troubleshooter.compare_historical(image1, image2)
        
        return {
            "comparison_success": comparison is not None,
            "comparison_keys": list(comparison.keys()) if comparison else []
        }
    
    async def _test_screen_sharing_initialize(self, screen_sharing: ScreenSharing) -> Dict[str, Any]:
        """Test screen sharing initialization."""
        # Verify initialization
        initialized = screen_sharing.width > 0 and screen_sharing.height > 0
        
        return {
            "initialized": initialized,
            "width": screen_sharing.width,
            "height": screen_sharing.height,
            "fps": screen_sharing.fps
        }
    
    async def _test_screen_sharing_capture(self, screen_sharing: ScreenSharing) -> Dict[str, Any]:
        """Test screen sharing capture."""
        # Start screen sharing
        start_success = await screen_sharing.start()
        
        # Wait for capture
        await asyncio.sleep(0.5)
        
        # Get screen
        screen = await screen_sharing.get_screen()
        
        # Stop screen sharing
        stop_success = await screen_sharing.stop()
        
        # Verify screen
        screen_valid = screen is not None
        
        return {
            "start_success": start_success,
            "stop_success": stop_success,
            "screen_valid": screen_valid,
            "screen_shape": str(screen.shape) if screen is not None else "None"
        }
    
    async def _test_screen_sharing_annotate(self, screen_sharing: ScreenSharing) -> Dict[str, Any]:
        """Test screen sharing annotation."""
        # Create a test screen
        screen = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(screen, "Test Screen", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
        
        # Add annotation
        annotated = await screen_sharing.annotate(screen, "arrow", (320, 240))
        
        # Verify annotation
        annotation_valid = annotated is not None and not np.array_equal(screen, annotated)
        
        return {
            "annotation_valid": annotation_valid,
            "annotated_shape": str(annotated.shape) if annotated is not None else "None"
        }
    
    async def _test_annotation_tools_initialize(self, annotation_tools: AnnotationTools) -> Dict[str, Any]:
        """Test annotation tools initialization."""
        # Verify initialization
        initialized = annotation_tools.styles is not None and len(annotation_tools.styles) > 0
        
        return {
            "initialized": initialized,
            "styles": list(annotation_tools.styles.keys()) if annotation_tools.styles else []
        }
    
    async def _test_annotation_tools_create(self, annotation_tools: AnnotationTools,
                                         animation_tools: MockAnimationTools) -> Dict[str, Any]:
        """Test annotation tools creation."""
        # Create a test image
        image = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(image, "Test Image", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
        
        # Create annotation
        arrow_animation = animation_tools.get_animation(AnimationType.ARROW.value)
        annotated = await annotation_tools.create_annotation(image, "standard", "arrow", (320, 240), arrow_animation[0])
        
        # Verify annotation
        annotation_valid = annotated is not None and not np.array_equal(image, annotated)
        
        return {
            "annotation_valid": annotation_valid,
            "annotated_shape": str(annotated.shape) if annotated is not None else "None"
        }
    
    async def _test_annotation_tools_sequence(self, annotation_tools: AnnotationTools,
                                           animation_tools: MockAnimationTools) -> Dict[str, Any]:
        """Test annotation tools sequence creation."""
        # Create a test image
        image = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(image, "Test Image", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
        
        # Create annotation sequence
        arrow_animation = animation_tools.get_animation(AnimationType.ANIMATED_ARROW.value)
        sequence = await annotation_tools.create_annotation_sequence(image, "standard", "arrow", [(320, 240)], arrow_animation)
        
        # Verify sequence
        sequence_valid = sequence is not None and len(sequence) > 0
        
        return {
            "sequence_valid": sequence_valid,
            "sequence_length": len(sequence) if sequence else 0
        }
    
    async def _test_visual_aids_initialize(self, visual_aids: VisualAidsManager) -> Dict[str, Any]:
        """Test visual aids manager initialization."""
        # Verify initialization
        initialized = visual_aids.templates is not None and len(visual_aids.templates) > 0
        
        return {
            "initialized": initialized,
            "templates": list(visual_aids.templates.keys()) if visual_aids.templates else []
        }
    
    async def _test_visual_aids_procedure(self, visual_aids: VisualAidsManager,
                                       animation_tools: MockAnimationTools) -> Dict[str, Any]:
        """Test visual aids procedure creation."""
        # Create a test procedure
        procedure = await visual_aids.create_procedure("Test Procedure", [
            {"type": "step", "title": "Step 1", "description": "This is step 1"},
            {"type": "step", "title": "Step 2", "description": "This is step 2"}
        ])
        
        # Verify procedure
        procedure_valid = procedure is not None and len(procedure["steps"]) == 2
        
        return {
            "procedure_valid": procedure_valid,
            "procedure_steps": len(procedure["steps"]) if procedure else 0
        }
    
    async def _test_visual_aids_generation(self, visual_aids: VisualAidsManager,
                                        animation_tools: MockAnimationTools) -> Dict[str, Any]:
        """Test visual aids generation."""
        # Create a test image
        image = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(image, "Test Image", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
        
        # Create a visual aid
        arrow_animation = animation_tools.get_animation(AnimationType.ARROW.value)
        visual_aid = await visual_aids.generate_visual_aid("standard", image, "Test Visual Aid", 
                                                        "This is a test visual aid", arrow_animation[0])
        
        # Verify visual aid
        visual_aid_valid = visual_aid is not None and not np.array_equal(image, visual_aid)
        
        return {
            "visual_aid_valid": visual_aid_valid,
            "visual_aid_shape": str(visual_aid.shape) if visual_aid is not None else "None"
        }
    
    async def _test_video_integration_initialize(self, video_integration: VideoIntegration) -> Dict[str, Any]:
        """Test video integration initialization."""
        # Verify initialization
        initialized = (video_integration.video_processor is not None and 
                      video_integration.visual_troubleshooter is not None and 
                      video_integration.screen_sharing is not None)
        
        return {
            "initialized": initialized,
            "components": {
                "video_processor": video_integration.video_processor is not None,
                "visual_troubleshooter": video_integration.visual_troubleshooter is not None,
                "screen_sharing": video_integration.screen_sharing is not None
            }
        }
    
    async def _test_video_integration_camera_analysis(self, video_integration: VideoIntegration) -> Dict[str, Any]:
        """Test video integration camera analysis."""
        # Start camera
        await video_integration.start_camera()
        
        # Wait for camera
        await asyncio.sleep(0.5)
        
        # Analyze camera
        analysis = await video_integration.analyze_camera()
        
        # Stop camera
        await video_integration.stop_camera()
        
        # Verify analysis
        analysis_valid = analysis is not None
        
        return {
            "analysis_valid": analysis_valid,
            "analysis_keys": list(analysis.keys()) if analysis else []
        }
    
    async def _test_video_integration_screen_sharing(self, video_integration: VideoIntegration) -> Dict[str, Any]:
        """Test video integration screen sharing."""
        # Start screen sharing
        await video_integration.start_screen_sharing()
        
        # Wait for screen
        await asyncio.sleep(0.5)
        
        # Get screen
        screen = await video_integration.get_screen()
        
        # Annotate screen
        annotated = await video_integration.annotate_screen("arrow", (320, 240))
        
        # Stop screen sharing
        await video_integration.stop_screen_sharing()
        
        # Verify screen and annotation
        screen_valid = screen is not None
        annotation_valid = annotated is not None and not np.array_equal(screen, annotated) if screen is not None else False
        
        return {
            "screen_valid": screen_valid,
            "annotation_valid": annotation_valid
        }
    
    async def _test_video_integration_events(self, video_integration: VideoIntegration) -> Dict[str, Any]:
        """Test video integration event handling."""
        events_received = []
        
        # Define event handler
        async def event_handler(event_type, event_data):
            events_received.append({"type": event_type, "data": event_data})
        
        # Register event handler
        video_integration.register_event_handler(event_handler)
        
        # Trigger events
        await video_integration.start_camera()
        await asyncio.sleep(0.5)
        await video_integration.stop_camera()
        
        # Verify events
        events_valid = len(events_received) > 0
        
        return {
            "events_valid": events_valid,
            "events_count": len(events_received),
            "event_types": [event["type"] for event in events_received]
        }

async def run_validation() -> Tuple[Dict[str, Any], str]:
    """
    Run comprehensive validation of Dr. TARDIS video and visual support.
    
    Returns:
        Tuple[Dict[str, Any], str]: Validation results and report file path
    """
    print("Starting comprehensive validation of Dr. TARDIS video and visual support components...")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 80)
    
    # Create validator
    validator = VideoSupportValidator()
    
    # Run validation
    start_time = time.time()
    results = await validator.validate_all()
    duration = time.time() - start_time
    
    # Save results to file
    results_file = os.path.join(os.path.dirname(__file__), "video_validation_results.json")
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)
    
    # Generate HTML report
    report_file = os.path.join(os.path.dirname(__file__), "video_validation_report.html")
    html_report = generate_html_report(results, duration)
    with open(report_file, "w") as f:
        f.write(html_report)
    
    # Print summary
    print("Validation Summary:")
    print(f"Total tests: {results['total_tests']}")
    print(f"Passed tests: {results['passed_tests']}")
    print(f"Failed tests: {results['failed_tests']}")
    print(f"Success rate: {results.get('success_rate', 0.0)*100:.1f}%")
    print(f"Overall result: {'PASSED' if results.get('success', False) else 'FAILED'}")
    print(f"Duration: {duration:.2f} seconds")
    print(f"Detailed results saved to: {results_file}")
    print(f"HTML report saved to: {report_file}")
    print("-" * 80)
    
    return results, report_file

def generate_html_report(results, duration):
    """Generate an HTML report from validation results."""
    # Get timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Create a simple HTML report
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Dr. TARDIS Video Support Validation Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .success {{ color: green; font-weight: bold; }}
        .failure {{ color: red; font-weight: bold; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <h1>Dr. TARDIS Video Support Validation Report</h1>
    <p>Generated on: {timestamp}</p>
    
    <h2>Validation Summary</h2>
    <p><strong>Overall Result:</strong> 
       <span class="{'success' if results.get('success', False) else 'failure'}">
           {results.get('success_rate', 0.0)*100:.1f}% - {'PASSED' if results.get('success', False) else 'FAILED'}
       </span>
    </p>
    <p><strong>Total Tests:</strong> {results.get('total_tests', 0)}</p>
    <p><strong>Passed Tests:</strong> {results.get('passed_tests', 0)}</p>
    <p><strong>Failed Tests:</strong> {results.get('failed_tests', 0)}</p>
    <p><strong>Duration:</strong> {duration:.2f} seconds</p>
    
    <h2>Component Results</h2>
    <table>
        <tr>
            <th>Component</th>
            <th>Success Rate</th>
            <th>Passed/Total</th>
        </tr>
"""
    
    # Add component results
    for component_name, component_data in results.get('components', {}).items():
        total = component_data.get('total', 0)
        passed = component_data.get('passed', 0)
        success_rate = passed / total if total > 0 else 0
        html += f"""
        <tr>
            <td>{component_name}</td>
            <td class="{'success' if success_rate >= 0.95 else 'failure'}">{success_rate*100:.1f}%</td>
            <td>{passed}/{total}</td>
        </tr>"""
    
    html += """
    </table>
</body>
</html>
"""
    
    return html

async def run_validation_with_report():
    """Run validation and generate report."""
    results, report_file = await run_validation()
    return results, report_file

if __name__ == "__main__":
    asyncio.run(run_validation())
