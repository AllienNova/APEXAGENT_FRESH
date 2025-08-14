"""
Visual Aids and Procedure Demonstrations Module for Dr. TARDIS Gemini Live API Integration

This module integrates visual aids and procedure demonstrations with the video processing,
troubleshooting, and annotation components to provide comprehensive visual support.

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
from enum import Enum
from typing import Dict, List, Any, Optional, Tuple, Union, Callable, AsyncGenerator

from .video_processor import VideoProcessor, VideoState
from .visual_troubleshooter import VisualTroubleshooter, TroubleshootingState
from .enhanced_visual_troubleshooter import EnhancedVisualTroubleshooter, EnhancedTroubleshootingState, DiagnosticLevel
from .screen_sharing import ScreenSharing, ScreenShareState, AnnotationType
from .annotation_tools import AnnotationTools, AnnotationStyle

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class ProcedureType(Enum):
    """Enum for different types of procedures."""
    HARDWARE_SETUP = "hardware_setup"
    SOFTWARE_CONFIGURATION = "software_configuration"
    TROUBLESHOOTING = "troubleshooting"
    MAINTENANCE = "maintenance"
    TUTORIAL = "tutorial"

class VisualAidType(Enum):
    """Enum for different types of visual aids."""
    DIAGRAM = "diagram"
    FLOWCHART = "flowchart"
    COMPARISON = "comparison"
    HIGHLIGHT = "highlight"
    ANIMATION = "animation"
    REFERENCE = "reference"

class VisualAidsManager:
    """
    Manages visual aids and procedure demonstrations for Dr. TARDIS.
    
    This class integrates the video processing, troubleshooting, and annotation
    components to provide comprehensive visual support for technical assistance.
    
    Attributes:
        video_processor (VideoProcessor): Video processor for camera input
        enhanced_troubleshooter (EnhancedVisualTroubleshooter): Enhanced visual troubleshooter
        screen_sharing (ScreenSharing): Screen sharing component
        annotation_tool (AnnotationTools): Advanced annotation tools
        logger (logging.Logger): Logger for the visual aids manager
    """
    
    def __init__(self, 
                 video_processor: Optional[VideoProcessor] = None,
                 enhanced_troubleshooter: Optional[EnhancedVisualTroubleshooter] = None,
                 screen_sharing: Optional[ScreenSharing] = None,
                 annotation_tool: Optional[AnnotationTools] = None):
        """
        Initialize the Visual Aids Manager.
        
        Args:
            video_processor: Video processor for camera input
            enhanced_troubleshooter: Enhanced visual troubleshooter
            screen_sharing: Screen sharing component
            annotation_tool: Advanced annotation tools
        """
        self.video_processor = video_processor
        self.enhanced_troubleshooter = enhanced_troubleshooter
        self.screen_sharing = screen_sharing
        self.annotation_tool = annotation_tool
        self.logger = logging.getLogger("VisualAidsManager")
        
        # Procedure library
        self._procedure_library = {}
        
        # Visual aids library
        self._visual_aids_library = {}
        
        # Templates library
        self.templates = {}
        
        # Callbacks
        self.on_procedure_step_complete = None
        self.on_procedure_complete = None
        self.on_error = None
        
        # Active procedure tracking
        self._active_procedure = None
        self._current_step = 0
        
        # Initialize procedure library
        self._initialize_procedure_library()
        
        # Initialize visual aids library
        self._initialize_visual_aids_library()
        
        # Initialize templates library
        self._initialize_templates_library()
        
        self.logger.info("VisualAidsManager initialized")
    
    def _initialize_procedure_library(self):
        """Initialize the procedure library with predefined procedures."""
        # USB Connection Procedure
        self._procedure_library["usb_connection"] = {
            "name": "USB Connection Guide",
            "type": ProcedureType.HARDWARE_SETUP,
            "description": "Guide for properly connecting USB devices",
            "steps": [
                {
                    "name": "Identify USB Port",
                    "description": "Locate the USB port on your device",
                    "visual_aid": "usb_port_diagram",
                    "annotation_template": "usb_connection",
                    "step_index": 0,
                    "verification": {
                        "type": "visual_confirmation",
                        "parameters": {
                            "target": "usb_port",
                            "confidence_threshold": 0.7
                        }
                    }
                },
                {
                    "name": "Align USB Connector",
                    "description": "Align the USB connector with the port, noting the orientation",
                    "visual_aid": "usb_connector_orientation",
                    "annotation_template": "usb_connection",
                    "step_index": 1,
                    "verification": {
                        "type": "visual_confirmation",
                        "parameters": {
                            "target": "usb_connector",
                            "confidence_threshold": 0.7
                        }
                    }
                },
                {
                    "name": "Insert USB Connector",
                    "description": "Gently insert the USB connector into the port",
                    "visual_aid": "usb_insertion",
                    "annotation_template": "usb_connection",
                    "step_index": 2,
                    "verification": {
                        "type": "visual_confirmation",
                        "parameters": {
                            "target": "connected_usb",
                            "confidence_threshold": 0.8
                        }
                    }
                },
                {
                    "name": "Verify Connection",
                    "description": "Verify that the device is recognized by your system",
                    "visual_aid": "usb_verification",
                    "annotation_template": None,
                    "verification": {
                        "type": "user_confirmation"
                    }
                }
            ]
        }
        
        # Display Troubleshooting Procedure
        self._procedure_library["display_troubleshooting"] = {
            "name": "Display Troubleshooting Guide",
            "type": ProcedureType.TROUBLESHOOTING,
            "description": "Guide for troubleshooting common display issues",
            "steps": [
                {
                    "name": "Check Power Connection",
                    "description": "Ensure the display is properly connected to power",
                    "visual_aid": "power_connection_diagram",
                    "annotation_template": "power_button",
                    "step_index": 0,
                    "verification": {
                        "type": "visual_confirmation",
                        "parameters": {
                            "target": "power_led",
                            "confidence_threshold": 0.7
                        }
                    }
                },
                {
                    "name": "Verify Video Cable",
                    "description": "Check that the video cable is securely connected",
                    "visual_aid": "video_cable_diagram",
                    "annotation_template": None,
                    "verification": {
                        "type": "visual_confirmation",
                        "parameters": {
                            "target": "video_cable",
                            "confidence_threshold": 0.7
                        }
                    }
                },
                {
                    "name": "Test Different Input Source",
                    "description": "Try switching to a different input source on the display",
                    "visual_aid": "input_source_diagram",
                    "annotation_template": "menu_navigation",
                    "step_index": 0,
                    "verification": {
                        "type": "user_confirmation"
                    }
                },
                {
                    "name": "Check Display Settings",
                    "description": "Verify display settings are correctly configured",
                    "visual_aid": "display_settings_diagram",
                    "annotation_template": "menu_navigation",
                    "step_index": 1,
                    "verification": {
                        "type": "user_confirmation"
                    }
                },
                {
                    "name": "Run Display Diagnostic",
                    "description": "Run the built-in display diagnostic if available",
                    "visual_aid": "display_diagnostic_diagram",
                    "annotation_template": "menu_navigation",
                    "step_index": 2,
                    "verification": {
                        "type": "user_confirmation"
                    }
                }
            ]
        }
        
        # Network Setup Procedure
        self._procedure_library["network_setup"] = {
            "name": "Network Setup Guide",
            "type": ProcedureType.HARDWARE_SETUP,
            "description": "Guide for setting up a network connection",
            "steps": [
                {
                    "name": "Connect Ethernet Cable",
                    "description": "Connect the ethernet cable to your device",
                    "visual_aid": "ethernet_connection_diagram",
                    "annotation_template": None,
                    "verification": {
                        "type": "visual_confirmation",
                        "parameters": {
                            "target": "ethernet_port",
                            "confidence_threshold": 0.7
                        }
                    }
                },
                {
                    "name": "Access Network Settings",
                    "description": "Navigate to network settings on your device",
                    "visual_aid": "network_settings_diagram",
                    "annotation_template": "menu_navigation",
                    "step_index": 0,
                    "verification": {
                        "type": "user_confirmation"
                    }
                },
                {
                    "name": "Configure Network Parameters",
                    "description": "Configure IP address, subnet mask, and gateway",
                    "visual_aid": "network_parameters_diagram",
                    "annotation_template": None,
                    "verification": {
                        "type": "user_confirmation"
                    }
                },
                {
                    "name": "Test Network Connection",
                    "description": "Test the network connection",
                    "visual_aid": "network_test_diagram",
                    "annotation_template": None,
                    "verification": {
                        "type": "user_confirmation"
                    }
                }
            ]
        }
    
    def _initialize_visual_aids_library(self):
        """Initialize the visual aids library with predefined visual aids."""
        # USB Connection Visual Aids
        self._visual_aids_library["usb_port_diagram"] = {
            "type": VisualAidType.DIAGRAM,
            "description": "Diagram showing USB port types and locations",
            "content": {
                "image_path": "resources/visual_aids/usb_port_diagram.jpg",
                "caption": "Common USB port types: USB-A, USB-B, USB-C, and Micro USB"
            }
        }
        
        self._visual_aids_library["usb_connector_orientation"] = {
            "type": VisualAidType.DIAGRAM,
            "description": "Diagram showing correct USB connector orientation",
            "content": {
                "image_path": "resources/visual_aids/usb_orientation.jpg",
                "caption": "Correct orientation for USB connector insertion"
            }
        }
        
        self._visual_aids_library["usb_insertion"] = {
            "type": VisualAidType.ANIMATION,
            "description": "Animation showing USB insertion process",
            "content": {
                "animation_path": "resources/visual_aids/usb_insertion.gif",
                "caption": "Gently insert the USB connector until it's fully seated"
            }
        }
        
        self._visual_aids_library["usb_verification"] = {
            "type": VisualAidType.DIAGRAM,
            "description": "Diagram showing USB device verification",
            "content": {
                "image_path": "resources/visual_aids/usb_verification.jpg",
                "caption": "Device manager showing properly connected USB device"
            }
        }
        
        # Display Troubleshooting Visual Aids
        self._visual_aids_library["power_connection_diagram"] = {
            "type": VisualAidType.DIAGRAM,
            "description": "Diagram showing display power connection",
            "content": {
                "image_path": "resources/visual_aids/power_connection.jpg",
                "caption": "Ensure power cable is securely connected to both the display and power outlet"
            }
        }
        
        self._visual_aids_library["video_cable_diagram"] = {
            "type": VisualAidType.DIAGRAM,
            "description": "Diagram showing video cable connections",
            "content": {
                "image_path": "resources/visual_aids/video_cable.jpg",
                "caption": "Common video cable types: HDMI, DisplayPort, DVI, and VGA"
            }
        }
        
        self._visual_aids_library["input_source_diagram"] = {
            "type": VisualAidType.DIAGRAM,
            "description": "Diagram showing display input source selection",
            "content": {
                "image_path": "resources/visual_aids/input_source.jpg",
                "caption": "Use the Input or Source button to cycle through available inputs"
            }
        }
        
        self._visual_aids_library["display_settings_diagram"] = {
            "type": VisualAidType.DIAGRAM,
            "description": "Diagram showing display settings menu",
            "content": {
                "image_path": "resources/visual_aids/display_settings.jpg",
                "caption": "Navigate to display settings to adjust resolution, refresh rate, and color settings"
            }
        }
        
        self._visual_aids_library["display_diagnostic_diagram"] = {
            "type": VisualAidType.DIAGRAM,
            "description": "Diagram showing display diagnostic menu",
            "content": {
                "image_path": "resources/visual_aids/display_diagnostic.jpg",
                "caption": "Access the built-in diagnostic tools through the display menu"
            }
        }
        
        # Network Setup Visual Aids
        self._visual_aids_library["ethernet_connection_diagram"] = {
            "type": VisualAidType.DIAGRAM,
            "description": "Diagram showing ethernet connection",
            "content": {
                "image_path": "resources/visual_aids/ethernet_connection.jpg",
                "caption": "Connect the ethernet cable to the ethernet port on your device"
            }
        }
        
        self._visual_aids_library["network_settings_diagram"] = {
            "type": VisualAidType.DIAGRAM,
            "description": "Diagram showing network settings menu",
            "content": {
                "image_path": "resources/visual_aids/network_settings.jpg",
                "caption": "Navigate to network settings in your device's control panel or settings menu"
            }
        }
        
        self._visual_aids_library["network_parameters_diagram"] = {
            "type": VisualAidType.DIAGRAM,
            "description": "Diagram showing network parameter configuration",
            "content": {
                "image_path": "resources/visual_aids/network_parameters.jpg",
                "caption": "Configure IP address, subnet mask, and gateway settings"
            }
        }
        
        self._visual_aids_library["network_test_diagram"] = {
            "type": VisualAidType.DIAGRAM,
            "description": "Diagram showing network connection testing",
            "content": {
                "image_path": "resources/visual_aids/network_test.jpg",
                "caption": "Use ping or other network diagnostic tools to test the connection"
            }
        }
    
    def _initialize_templates_library(self):
        """Initialize the templates library with predefined annotation templates."""
        # USB Connection Templates
        self.templates["usb_connection"] = [
            {
                "step": 0,
                "annotations": [
                    {
                        "type": AnnotationType.CIRCLE,
                        "coordinates": (320, 240),
                        "radius": 50,
                        "style": AnnotationStyle.HIGHLIGHT,
                        "text": "USB Port"
                    },
                    {
                        "type": AnnotationType.ARROW,
                        "start": (420, 340),
                        "end": (320, 240),
                        "style": AnnotationStyle.STANDARD,
                        "text": "Connect Here"
                    }
                ]
            },
            {
                "step": 1,
                "annotations": [
                    {
                        "type": AnnotationType.RECTANGLE,
                        "top_left": (270, 190),
                        "bottom_right": (370, 290),
                        "style": AnnotationStyle.TECHNICAL,
                        "text": "USB Connector"
                    },
                    {
                        "type": AnnotationType.ARROW,
                        "start": (420, 340),
                        "end": (320, 240),
                        "style": AnnotationStyle.STANDARD,
                        "text": "Align This Way"
                    }
                ]
            },
            {
                "step": 2,
                "annotations": [
                    {
                        "type": AnnotationType.ANIMATED_ARROW,
                        "start": (420, 340),
                        "end": (320, 240),
                        "style": AnnotationStyle.INSTRUCTIONAL,
                        "text": "Insert Gently"
                    }
                ]
            }
        ]
        
        # Power Button Templates
        self.templates["power_button"] = [
            {
                "step": 0,
                "annotations": [
                    {
                        "type": AnnotationType.CIRCLE,
                        "coordinates": (320, 240),
                        "radius": 30,
                        "style": AnnotationStyle.HIGHLIGHT,
                        "text": "Power Button"
                    },
                    {
                        "type": AnnotationType.PULSING_CIRCLE,
                        "coordinates": (320, 240),
                        "radius": 40,
                        "style": AnnotationStyle.HIGHLIGHT,
                        "text": "Press Here"
                    }
                ]
            }
        ]
        
        # Menu Navigation Templates
        self.templates["menu_navigation"] = [
            {
                "step": 0,
                "annotations": [
                    {
                        "type": AnnotationType.RECTANGLE,
                        "top_left": (270, 190),
                        "bottom_right": (370, 290),
                        "style": AnnotationStyle.HIGHLIGHT,
                        "text": "Input Source Menu"
                    },
                    {
                        "type": AnnotationType.ARROW,
                        "start": (420, 340),
                        "end": (320, 240),
                        "style": AnnotationStyle.STANDARD,
                        "text": "Select This Option"
                    }
                ]
            },
            {
                "step": 1,
                "annotations": [
                    {
                        "type": AnnotationType.RECTANGLE,
                        "top_left": (270, 190),
                        "bottom_right": (370, 290),
                        "style": AnnotationStyle.HIGHLIGHT,
                        "text": "Display Settings"
                    },
                    {
                        "type": AnnotationType.PATH,
                        "points": [(420, 340), (370, 310), (320, 240)],
                        "style": AnnotationStyle.STANDARD,
                        "text": "Navigate This Path"
                    }
                ]
            },
            {
                "step": 2,
                "annotations": [
                    {
                        "type": AnnotationType.RECTANGLE,
                        "top_left": (270, 190),
                        "bottom_right": (370, 290),
                        "style": AnnotationStyle.HIGHLIGHT,
                        "text": "Diagnostic Tools"
                    },
                    {
                        "type": AnnotationType.ANIMATED_HIGHLIGHT,
                        "top_left": (270, 190),
                        "bottom_right": (370, 290),
                        "style": AnnotationStyle.INSTRUCTIONAL,
                        "text": "Select This Option"
                    }
                ]
            }
        ]
    
    async def create_procedure(self, procedure_type: str, name: str, description: str, steps: List[Dict[str, Any]]) -> str:
        """
        Create a new procedure and add it to the procedure library.
        
        Args:
            procedure_type: Type of procedure (from ProcedureType enum)
            name: Name of the procedure
            description: Description of the procedure
            steps: List of procedure steps
            
        Returns:
            str: ID of the created procedure
        """
        self.logger.info(f"Creating new procedure: {name}")
        
        try:
            # Generate a unique ID for the procedure
            procedure_id = f"{procedure_type}_{int(time.time())}"
            
            # Create the procedure
            procedure = {
                "name": name,
                "type": procedure_type,
                "description": description,
                "steps": steps
            }
            
            # Add to procedure library
            self._procedure_library[procedure_id] = procedure
            
            self.logger.info(f"Created procedure {procedure_id}: {name}")
            return procedure_id
            
        except Exception as e:
            self.logger.error(f"Error creating procedure: {e}")
            
            # Call the error callback if registered
            if self.on_error:
                try:
                    await self.on_error(str(e))
                except Exception as e:
                    self.logger.error(f"Error in error callback: {e}")
            
            return None
    
    async def generate_visual_aid(self, aid_type: str, description: str, content: Dict[str, Any]) -> str:
        """
        Generate a new visual aid and add it to the visual aids library.
        
        Args:
            aid_type: Type of visual aid (from VisualAidType enum)
            description: Description of the visual aid
            content: Content of the visual aid (varies by type)
            
        Returns:
            str: ID of the created visual aid
        """
        self.logger.info(f"Generating new visual aid: {description}")
        
        try:
            # Generate a unique ID for the visual aid
            aid_id = f"{aid_type}_{int(time.time())}"
            
            # Create the visual aid
            visual_aid = {
                "type": aid_type,
                "description": description,
                "content": content
            }
            
            # Add to visual aids library
            self._visual_aids_library[aid_id] = visual_aid
            
            self.logger.info(f"Generated visual aid {aid_id}: {description}")
            return aid_id
            
        except Exception as e:
            self.logger.error(f"Error generating visual aid: {e}")
            
            # Call the error callback if registered
            if self.on_error:
                try:
                    await self.on_error(str(e))
                except Exception as e:
                    self.logger.error(f"Error in error callback: {e}")
            
            return None
    
    async def start_procedure(self, procedure_id: str) -> bool:
        """
        Start a procedure demonstration.
        
        Args:
            procedure_id: ID of the procedure to start
            
        Returns:
            bool: True if procedure started successfully, False otherwise
        """
        if procedure_id not in self._procedure_library:
            self.logger.warning(f"Procedure {procedure_id} not found")
            return False
        
        self.logger.info(f"Starting procedure: {procedure_id}")
        
        try:
            # Set active procedure
            self._active_procedure = procedure_id
            self._current_step = 0
            
            # Get procedure details
            procedure = self._procedure_library[procedure_id]
            
            # Log procedure start
            self.logger.info(f"Started procedure {procedure_id}: {procedure['name']}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting procedure: {e}")
            
            # Call the error callback if registered
            if self.on_error:
                try:
                    await self.on_error(str(e))
                except Exception as e:
                    self.logger.error(f"Error in error callback: {e}")
            
            return False
    
    async def next_step(self) -> Dict[str, Any]:
        """
        Advance to the next step in the active procedure.
        
        Returns:
            Dict[str, Any]: Details of the next step, or None if no active procedure
                           or end of procedure reached
        """
        if not self._active_procedure:
            self.logger.warning("No active procedure")
            return None
        
        procedure = self._procedure_library[self._active_procedure]
        
        if self._current_step >= len(procedure["steps"]):
            self.logger.info(f"End of procedure {self._active_procedure} reached")
            
            # Call the procedure complete callback if registered
            if self.on_procedure_complete:
                try:
                    await self.on_procedure_complete(self._active_procedure)
                except Exception as e:
                    self.logger.error(f"Error in procedure complete callback: {e}")
            
            # Reset active procedure
            self._active_procedure = None
            self._current_step = 0
            
            return None
        
        self.logger.info(f"Advancing to step {self._current_step} of procedure {self._active_procedure}")
        
        try:
            # Get step details
            step = procedure["steps"][self._current_step]
            
            # Get visual aid if specified
            visual_aid = None
            if "visual_aid" in step and step["visual_aid"] in self._visual_aids_library:
                visual_aid = self._visual_aids_library[step["visual_aid"]]
            
            # Get annotation template if specified
            annotation_template = None
            if "annotation_template" in step and step["annotation_template"] in self.templates:
                template_steps = self.templates[step["annotation_template"]]
                step_index = step.get("step_index", 0)
                
                # Find the template for this step
                for template_step in template_steps:
                    if template_step["step"] == step_index:
                        annotation_template = template_step
                        break
            
            # Prepare step details
            step_details = {
                "step_number": self._current_step,
                "name": step["name"],
                "description": step["description"],
                "visual_aid": visual_aid,
                "annotation_template": annotation_template,
                "verification": step.get("verification", None)
            }
            
            # Increment step counter
            self._current_step += 1
            
            # Call the step complete callback if registered
            if self.on_procedure_step_complete:
                try:
                    await self.on_procedure_step_complete(self._active_procedure, self._current_step - 1)
                except Exception as e:
                    self.logger.error(f"Error in step complete callback: {e}")
            
            return step_details
            
        except Exception as e:
            self.logger.error(f"Error advancing procedure step: {e}")
            
            # Call the error callback if registered
            if self.on_error:
                try:
                    await self.on_error(str(e))
                except Exception as e:
                    self.logger.error(f"Error in error callback: {e}")
            
            return None
    
    async def verify_step(self, verification_result: bool) -> bool:
        """
        Verify the current step in the active procedure.
        
        Args:
            verification_result: Result of the verification (True if verified, False otherwise)
            
        Returns:
            bool: True if verification successful, False otherwise
        """
        if not self._active_procedure:
            self.logger.warning("No active procedure")
            return False
        
        if self._current_step <= 0:
            self.logger.warning("No current step to verify")
            return False
        
        self.logger.info(f"Verifying step {self._current_step - 1} of procedure {self._active_procedure}")
        
        try:
            # Get procedure details
            procedure = self._procedure_library[self._active_procedure]
            
            # Get step details
            step = procedure["steps"][self._current_step - 1]
            
            # Check verification result
            if verification_result:
                self.logger.info(f"Step {self._current_step - 1} verified successfully")
                return True
            else:
                self.logger.warning(f"Step {self._current_step - 1} verification failed")
                
                # Go back to the current step
                self._current_step -= 1
                
                return False
            
        except Exception as e:
            self.logger.error(f"Error verifying procedure step: {e}")
            
            # Call the error callback if registered
            if self.on_error:
                try:
                    await self.on_error(str(e))
                except Exception as e:
                    self.logger.error(f"Error in error callback: {e}")
            
            return False
    
    async def get_procedure_list(self) -> List[Dict[str, Any]]:
        """
        Get a list of all available procedures.
        
        Returns:
            List[Dict[str, Any]]: List of procedure details
        """
        self.logger.info("Getting procedure list")
        
        try:
            # Prepare procedure list
            procedure_list = []
            
            for procedure_id, procedure in self._procedure_library.items():
                procedure_list.append({
                    "id": procedure_id,
                    "name": procedure["name"],
                    "type": procedure["type"],
                    "description": procedure["description"],
                    "step_count": len(procedure["steps"])
                })
            
            return procedure_list
            
        except Exception as e:
            self.logger.error(f"Error getting procedure list: {e}")
            
            # Call the error callback if registered
            if self.on_error:
                try:
                    await self.on_error(str(e))
                except Exception as e:
                    self.logger.error(f"Error in error callback: {e}")
            
            return []
    
    async def get_visual_aid_list(self) -> List[Dict[str, Any]]:
        """
        Get a list of all available visual aids.
        
        Returns:
            List[Dict[str, Any]]: List of visual aid details
        """
        self.logger.info("Getting visual aid list")
        
        try:
            # Prepare visual aid list
            visual_aid_list = []
            
            for aid_id, aid in self._visual_aids_library.items():
                visual_aid_list.append({
                    "id": aid_id,
                    "type": aid["type"],
                    "description": aid["description"]
                })
            
            return visual_aid_list
            
        except Exception as e:
            self.logger.error(f"Error getting visual aid list: {e}")
            
            # Call the error callback if registered
            if self.on_error:
                try:
                    await self.on_error(str(e))
                except Exception as e:
                    self.logger.error(f"Error in error callback: {e}")
            
            return []
    
    async def get_procedure(self, procedure_id: str) -> Dict[str, Any]:
        """
        Get details of a specific procedure.
        
        Args:
            procedure_id: ID of the procedure to get
            
        Returns:
            Dict[str, Any]: Procedure details, or None if not found
        """
        if procedure_id not in self._procedure_library:
            self.logger.warning(f"Procedure {procedure_id} not found")
            return None
        
        self.logger.info(f"Getting procedure: {procedure_id}")
        
        try:
            # Get procedure details
            procedure = self._procedure_library[procedure_id]
            
            # Prepare procedure details
            procedure_details = {
                "id": procedure_id,
                "name": procedure["name"],
                "type": procedure["type"],
                "description": procedure["description"],
                "steps": procedure["steps"]
            }
            
            return procedure_details
            
        except Exception as e:
            self.logger.error(f"Error getting procedure: {e}")
            
            # Call the error callback if registered
            if self.on_error:
                try:
                    await self.on_error(str(e))
                except Exception as e:
                    self.logger.error(f"Error in error callback: {e}")
            
            return None
    
    async def get_visual_aid(self, aid_id: str) -> Dict[str, Any]:
        """
        Get details of a specific visual aid.
        
        Args:
            aid_id: ID of the visual aid to get
            
        Returns:
            Dict[str, Any]: Visual aid details, or None if not found
        """
        if aid_id not in self._visual_aids_library:
            self.logger.warning(f"Visual aid {aid_id} not found")
            return None
        
        self.logger.info(f"Getting visual aid: {aid_id}")
        
        try:
            # Get visual aid details
            aid = self._visual_aids_library[aid_id]
            
            # Prepare visual aid details
            aid_details = {
                "id": aid_id,
                "type": aid["type"],
                "description": aid["description"],
                "content": aid["content"]
            }
            
            return aid_details
            
        except Exception as e:
            self.logger.error(f"Error getting visual aid: {e}")
            
            # Call the error callback if registered
            if self.on_error:
                try:
                    await self.on_error(str(e))
                except Exception as e:
                    self.logger.error(f"Error in error callback: {e}")
            
            return None
    
    async def register_callback(self, event_type: str, callback: Callable):
        """
        Register a callback function for a specific event type.
        
        Args:
            event_type: Type of event to register callback for
                ('on_procedure_step_complete', 'on_procedure_complete', 'on_error')
            callback: Function to call when the event occurs
        """
        if event_type == "on_procedure_step_complete":
            self.on_procedure_step_complete = callback
        elif event_type == "on_procedure_complete":
            self.on_procedure_complete = callback
        elif event_type == "on_error":
            self.on_error = callback
        else:
            self.logger.warning(f"Unknown event type: {event_type}")

async def example_usage():
    """Example usage of the VisualAidsManager class."""
    # Create components
    video_processor = VideoProcessor(device_id=0)
    troubleshooter = VisualTroubleshooter(video_processor)
    enhanced_troubleshooter = EnhancedVisualTroubleshooter(troubleshooter)
    screen_sharing = ScreenSharing()
    annotation_tools = AnnotationTools()
    
    # Create visual aids manager
    visual_aids_manager = VisualAidsManager(
        video_processor=video_processor,
        enhanced_troubleshooter=enhanced_troubleshooter,
        screen_sharing=screen_sharing,
        annotation_tool=annotation_tools
    )
    
    # Get procedure list
    procedures = await visual_aids_manager.get_procedure_list()
    print(f"Available procedures: {len(procedures)}")
    for procedure in procedures:
        print(f"- {procedure['name']}: {procedure['description']}")
    
    # Start a procedure
    if procedures:
        procedure_id = procedures[0]["id"]
        result = await visual_aids_manager.start_procedure(procedure_id)
        if result:
            print(f"Started procedure: {procedures[0]['name']}")
            
            # Get first step
            step = await visual_aids_manager.next_step()
            if step:
                print(f"Step {step['step_number']}: {step['name']}")
                print(f"Description: {step['description']}")
                
                # Verify step
                result = await visual_aids_manager.verify_step(True)
                if result:
                    print("Step verified successfully")
                else:
                    print("Step verification failed")
                
                # Get next step
                step = await visual_aids_manager.next_step()
                if step:
                    print(f"Step {step['step_number']}: {step['name']}")
                    print(f"Description: {step['description']}")

if __name__ == "__main__":
    asyncio.run(example_usage())
