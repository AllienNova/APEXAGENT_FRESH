"""
Enhanced Visual Troubleshooting Module for Dr. TARDIS Gemini Live API Integration

This module extends the visual troubleshooting capabilities with advanced diagnostics,
pattern recognition, and comprehensive reporting features.

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
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional, Tuple, Union, Callable, AsyncGenerator

from .video_processor import VideoProcessor, VideoState
from .visual_troubleshooter import VisualTroubleshooter, TroubleshootingState

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class EnhancedTroubleshootingState(Enum):
    """Enum for different states of the enhanced visual troubleshooter."""
    IDLE = "idle"
    ANALYZING = "analyzing"
    PATTERN_MATCHING = "pattern_matching"
    GENERATING_REPORT = "generating_report"
    ARCHIVING = "archiving"
    ERROR = "error"

class DiagnosticLevel(Enum):
    """Enum for different diagnostic levels."""
    BASIC = "basic"
    ADVANCED = "advanced"
    EXPERT = "expert"

class EnhancedVisualTroubleshooter:
    """
    Provides enhanced visual troubleshooting capabilities with advanced diagnostics.
    
    This class extends the base VisualTroubleshooter with advanced pattern recognition,
    historical comparison, and comprehensive reporting features.
    
    Attributes:
        base_troubleshooter (VisualTroubleshooter): Base visual troubleshooter
        state (EnhancedTroubleshootingState): Current state of the troubleshooter
        logger (logging.Logger): Logger for the troubleshooter
    """
    
    def __init__(self, video_processor: VideoProcessor):
        """
        Initialize the Enhanced Visual Troubleshooter.
        
        Args:
            video_processor: Video processor for capturing frames
        """
        self.base_troubleshooter = VisualTroubleshooter(video_processor)
        self.video_processor = video_processor
        self.state = EnhancedTroubleshootingState.IDLE
        self.logger = logging.getLogger("EnhancedVisualTroubleshooter")
        
        # Analysis results
        self._analysis_results = {}
        self._historical_results = {}
        self._pattern_database = {}
        
        # Report generation
        self._report_templates = {}
        
        # Callbacks
        self.on_analysis_complete = None
        self.on_error = None
        self.on_state_change = None
        
        # Initialize pattern database
        self._initialize_pattern_database()
        
        # Initialize report templates
        self._initialize_report_templates()
        
        self.logger.info("EnhancedVisualTroubleshooter initialized")
    
    def _initialize_pattern_database(self):
        """Initialize the pattern database for hardware issue recognition."""
        # Load pattern database for common hardware issues
        # In a production environment, this would load from a file or database
        self._pattern_database = {
            "display": {
                "dead_pixel": {
                    "description": "Dead or stuck pixel on display",
                    "visual_patterns": ["isolated bright spots", "isolated dark spots"],
                    "confidence_threshold": 0.75,
                    "severity": "medium",
                    "recommendation": "For LCD displays, try pixel massage techniques or use pixel repair software"
                },
                "screen_flicker": {
                    "description": "Screen flickering",
                    "visual_patterns": ["temporal brightness variation", "horizontal lines"],
                    "confidence_threshold": 0.8,
                    "severity": "high",
                    "recommendation": "Check display cable connection, update graphics drivers, or replace display"
                },
                "color_distortion": {
                    "description": "Color distortion or tinting",
                    "visual_patterns": ["color imbalance", "color shift"],
                    "confidence_threshold": 0.7,
                    "severity": "medium",
                    "recommendation": "Recalibrate display color settings or check display cable"
                }
            },
            "connection": {
                "loose_connection": {
                    "description": "Loose cable connection",
                    "visual_patterns": ["partial connector insertion", "angled connector"],
                    "confidence_threshold": 0.8,
                    "severity": "medium",
                    "recommendation": "Firmly reconnect cable ensuring proper alignment"
                },
                "bent_pins": {
                    "description": "Bent pins in connector",
                    "visual_patterns": ["misaligned pins", "pin irregularity"],
                    "confidence_threshold": 0.85,
                    "severity": "high",
                    "recommendation": "Carefully straighten bent pins using precision tools or replace cable"
                },
                "corrosion": {
                    "description": "Connector corrosion",
                    "visual_patterns": ["greenish discoloration", "white residue"],
                    "confidence_threshold": 0.75,
                    "severity": "high",
                    "recommendation": "Clean connector with isopropyl alcohol and soft brush"
                }
            },
            "physical_damage": {
                "crack": {
                    "description": "Physical crack in casing",
                    "visual_patterns": ["linear fracture", "irregular edge"],
                    "confidence_threshold": 0.8,
                    "severity": "high",
                    "recommendation": "Apply temporary reinforcement and plan for replacement"
                },
                "liquid_damage": {
                    "description": "Liquid damage indicators",
                    "visual_patterns": ["water stain", "discoloration"],
                    "confidence_threshold": 0.7,
                    "severity": "critical",
                    "recommendation": "Power off device immediately, remove battery if possible, and seek professional repair"
                },
                "impact_damage": {
                    "description": "Impact damage",
                    "visual_patterns": ["dent", "deformation"],
                    "confidence_threshold": 0.75,
                    "severity": "medium",
                    "recommendation": "Assess internal component damage and repair or replace as needed"
                }
            },
            "led_status": {
                "error_code": {
                    "description": "LED error code pattern",
                    "visual_patterns": ["blinking pattern", "color sequence"],
                    "confidence_threshold": 0.9,
                    "severity": "high",
                    "recommendation": "Consult device manual for specific error code meaning"
                },
                "power_issue": {
                    "description": "Power-related LED indication",
                    "visual_patterns": ["amber LED", "flashing power LED"],
                    "confidence_threshold": 0.85,
                    "severity": "high",
                    "recommendation": "Check power supply and connections"
                },
                "status_indicator": {
                    "description": "Normal status LED",
                    "visual_patterns": ["steady green LED", "blue operation LED"],
                    "confidence_threshold": 0.9,
                    "severity": "none",
                    "recommendation": "No action needed, device operating normally"
                }
            }
        }
    
    def _initialize_report_templates(self):
        """Initialize report templates for different diagnostic levels."""
        self._report_templates = {
            DiagnosticLevel.BASIC: {
                "sections": [
                    "summary",
                    "camera_quality",
                    "detected_issues",
                    "basic_recommendations"
                ],
                "format": "simple"
            },
            DiagnosticLevel.ADVANCED: {
                "sections": [
                    "summary",
                    "camera_quality",
                    "detected_issues",
                    "detailed_analysis",
                    "advanced_recommendations",
                    "troubleshooting_steps"
                ],
                "format": "detailed"
            },
            DiagnosticLevel.EXPERT: {
                "sections": [
                    "summary",
                    "camera_quality",
                    "detected_issues",
                    "detailed_analysis",
                    "pattern_matching_results",
                    "historical_comparison",
                    "expert_recommendations",
                    "troubleshooting_steps",
                    "repair_procedures",
                    "technical_specifications"
                ],
                "format": "comprehensive"
            }
        }
    
    def register_callback(self, event_type: str, callback: Callable):
        """
        Register a callback function for a specific event type.
        
        Args:
            event_type: Type of event to register callback for
                ('on_analysis_complete', 'on_error', 'on_state_change')
            callback: Function to call when the event occurs
        """
        if event_type == "on_analysis_complete":
            self.on_analysis_complete = callback
            self.base_troubleshooter.register_callback("on_analysis_complete", callback)
        elif event_type == "on_error":
            self.on_error = callback
            self.base_troubleshooter.register_callback("on_error", callback)
        elif event_type == "on_state_change":
            self.on_state_change = callback
        else:
            self.logger.warning(f"Unknown event type: {event_type}")
    
    def _set_state(self, new_state: EnhancedTroubleshootingState):
        """
        Set the state of the troubleshooter and trigger the state change callback.
        
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
    
    async def analyze_camera(self, store_history: bool = True) -> Dict[str, Any]:
        """
        Perform enhanced camera analysis with advanced metrics.
        
        Args:
            store_history: Whether to store results in history
            
        Returns:
            Dict[str, Any]: Enhanced analysis results
        """
        self._set_state(EnhancedTroubleshootingState.ANALYZING)
        self.logger.info("Performing enhanced camera analysis")
        
        try:
            # Get base analysis results
            base_results = await self.base_troubleshooter.analyze_camera()
            
            if "error" in base_results:
                raise RuntimeError(base_results["error"])
            
            # Enhance with additional metrics
            enhanced_results = await self._enhance_camera_analysis(base_results)
            
            # Store in history if requested
            if store_history:
                timestamp = time.time()
                if "camera" not in self._historical_results:
                    self._historical_results["camera"] = []
                
                self._historical_results["camera"].append({
                    "timestamp": timestamp,
                    "date": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp)),
                    "results": enhanced_results
                })
                
                # Limit history size
                if len(self._historical_results["camera"]) > 10:
                    self._historical_results["camera"].pop(0)
            
            # Store in current results
            self._analysis_results["camera"] = enhanced_results
            
            self._set_state(EnhancedTroubleshootingState.IDLE)
            
            # Call the analysis complete callback if registered
            if self.on_analysis_complete:
                try:
                    await self.on_analysis_complete(enhanced_results)
                except Exception as e:
                    self.logger.error(f"Error in analysis complete callback: {e}")
            
            return enhanced_results
            
        except Exception as e:
            self._set_state(EnhancedTroubleshootingState.ERROR)
            self.logger.error(f"Error in enhanced camera analysis: {e}")
            
            # Call the error callback if registered
            if self.on_error:
                try:
                    await self.on_error(str(e))
                except Exception as e:
                    self.logger.error(f"Error in error callback: {e}")
            
            return {"error": str(e)}
    
    async def analyze_hardware_issue(self, issue_type: str, store_history: bool = True) -> Dict[str, Any]:
        """
        Perform enhanced hardware issue analysis with pattern matching.
        
        Args:
            issue_type: Type of hardware issue to analyze
            store_history: Whether to store results in history
            
        Returns:
            Dict[str, Any]: Enhanced analysis results
        """
        self._set_state(EnhancedTroubleshootingState.ANALYZING)
        self.logger.info(f"Performing enhanced hardware issue analysis: {issue_type}")
        
        try:
            # Get base analysis results
            base_results = await self.base_troubleshooter.analyze_hardware_issue(issue_type)
            
            if "error" in base_results:
                raise RuntimeError(base_results["error"])
            
            # Perform pattern matching
            self._set_state(EnhancedTroubleshootingState.PATTERN_MATCHING)
            pattern_results = await self._match_issue_patterns(issue_type, base_results)
            
            # Enhance with additional metrics and pattern matching results
            enhanced_results = await self._enhance_hardware_analysis(issue_type, base_results, pattern_results)
            
            # Store in history if requested
            if store_history:
                timestamp = time.time()
                if "hardware_issues" not in self._historical_results:
                    self._historical_results["hardware_issues"] = {}
                
                if issue_type not in self._historical_results["hardware_issues"]:
                    self._historical_results["hardware_issues"][issue_type] = []
                
                self._historical_results["hardware_issues"][issue_type].append({
                    "timestamp": timestamp,
                    "date": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp)),
                    "results": enhanced_results
                })
                
                # Limit history size
                if len(self._historical_results["hardware_issues"][issue_type]) > 10:
                    self._historical_results["hardware_issues"][issue_type].pop(0)
            
            # Store in current results
            if "hardware_issues" not in self._analysis_results:
                self._analysis_results["hardware_issues"] = {}
            
            self._analysis_results["hardware_issues"][issue_type] = enhanced_results
            
            self._set_state(EnhancedTroubleshootingState.IDLE)
            
            # Call the analysis complete callback if registered
            if self.on_analysis_complete:
                try:
                    await self.on_analysis_complete(enhanced_results)
                except Exception as e:
                    self.logger.error(f"Error in analysis complete callback: {e}")
            
            return enhanced_results
            
        except Exception as e:
            self._set_state(EnhancedTroubleshootingState.ERROR)
            self.logger.error(f"Error in enhanced hardware issue analysis: {e}")
            
            # Call the error callback if registered
            if self.on_error:
                try:
                    await self.on_error(str(e))
                except Exception as e:
                    self.logger.error(f"Error in error callback: {e}")
            
            return {"error": str(e)}
    
    async def generate_diagnostic_report(self, diagnostic_level: DiagnosticLevel = DiagnosticLevel.ADVANCED) -> Dict[str, Any]:
        """
        Generate a comprehensive diagnostic report with the specified level of detail.
        
        Args:
            diagnostic_level: Level of diagnostic detail to include
            
        Returns:
            Dict[str, Any]: Diagnostic report
        """
        self._set_state(EnhancedTroubleshootingState.GENERATING_REPORT)
        self.logger.info(f"Generating {diagnostic_level.value} diagnostic report")
        
        try:
            # Get report template for the specified level
            template = self._report_templates.get(diagnostic_level, self._report_templates[DiagnosticLevel.BASIC])
            
            # Create report structure
            report = {
                "timestamp": time.time(),
                "date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "diagnostic_level": diagnostic_level.value,
                "format": template["format"],
                "sections": {}
            }
            
            # Generate each section based on template
            for section in template["sections"]:
                if section == "summary":
                    report["sections"]["summary"] = await self._generate_summary_section()
                elif section == "camera_quality":
                    report["sections"]["camera_quality"] = await self._generate_camera_quality_section()
                elif section == "detected_issues":
                    report["sections"]["detected_issues"] = await self._generate_detected_issues_section()
                elif section == "detailed_analysis":
                    report["sections"]["detailed_analysis"] = await self._generate_detailed_analysis_section()
                elif section == "pattern_matching_results":
                    report["sections"]["pattern_matching_results"] = await self._generate_pattern_matching_section()
                elif section == "historical_comparison":
                    report["sections"]["historical_comparison"] = await self._generate_historical_comparison_section()
                elif section in ["basic_recommendations", "advanced_recommendations", "expert_recommendations"]:
                    report["sections"]["recommendations"] = await self._generate_recommendations_section(diagnostic_level)
                elif section == "troubleshooting_steps":
                    report["sections"]["troubleshooting_steps"] = await self._generate_troubleshooting_steps_section()
                elif section == "repair_procedures":
                    report["sections"]["repair_procedures"] = await self._generate_repair_procedures_section()
                elif section == "technical_specifications":
                    report["sections"]["technical_specifications"] = await self._generate_technical_specifications_section()
            
            self._set_state(EnhancedTroubleshootingState.IDLE)
            
            return report
            
        except Exception as e:
            self._set_state(EnhancedTroubleshootingState.ERROR)
            self.logger.error(f"Error generating diagnostic report: {e}")
            
            # Call the error callback if registered
            if self.on_error:
                try:
                    await self.on_error(str(e))
                except Exception as e:
                    self.logger.error(f"Error in error callback: {e}")
            
            return {"error": str(e)}
    
    async def save_diagnostic_report(self, file_path: str, diagnostic_level: DiagnosticLevel = DiagnosticLevel.ADVANCED) -> bool:
        """
        Generate and save a diagnostic report to a file.
        
        Args:
            file_path: Path to save the report
            diagnostic_level: Level of diagnostic detail to include
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Generate report
            report = await self.generate_diagnostic_report(diagnostic_level)
            
            if "error" in report:
                raise RuntimeError(report["error"])
            
            # Save report to file
            with open(file_path, 'w') as f:
                json.dump(report, f, indent=2)
            
            self.logger.info(f"Diagnostic report saved to {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving diagnostic report: {e}")
            
            # Call the error callback if registered
            if self.on_error:
                try:
                    await self.on_error(str(e))
                except Exception as e:
                    self.logger.error(f"Error in error callback: {e}")
            
            return False
    
    async def save_annotated_diagnostic_frame(self, file_path: str) -> bool:
        """
        Save an annotated frame with comprehensive diagnostic information.
        
        Args:
            file_path: Path to save the annotated frame
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get the most recent frame
            frame = await self.video_processor.get_frame()
            
            if frame is None:
                self.logger.warning("No frame available to annotate")
                return False
            
            # Create annotations based on analysis results
            annotations = await self._generate_diagnostic_annotations()
            
            # Save annotated frame
            result = await self.base_troubleshooter.save_annotated_frame(file_path, annotations)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error saving annotated diagnostic frame: {e}")
            
            # Call the error callback if registered
            if self.on_error:
                try:
                    await self.on_error(str(e))
                except Exception as e:
                    self.logger.error(f"Error in error callback: {e}")
            
            return False
    
    async def _enhance_camera_analysis(self, base_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance camera analysis with additional metrics.
        
        Args:
            base_results: Base analysis results
            
        Returns:
            Dict[str, Any]: Enhanced analysis results
        """
        # Start with base results
        enhanced_results = base_results.copy()
        
        # Add enhanced metrics
        enhanced_results["analysis_version"] = "2.0"
        enhanced_results["enhanced"] = True
        
        # Add color balance analysis
        if "frame" in enhanced_results:
            frame = enhanced_results["frame"]
            
            # Calculate color balance
            b, g, r = cv2.split(frame)
            r_mean = np.mean(r)
            g_mean = np.mean(g)
            b_mean = np.mean(b)
            
            total_mean = (r_mean + g_mean + b_mean) / 3
            
            color_balance = {
                "red": r_mean / total_mean if total_mean > 0 else 0,
                "green": g_mean / total_mean if total_mean > 0 else 0,
                "blue": b_mean / total_mean if total_mean > 0 else 0
            }
            
            enhanced_results["color_balance"] = color_balance
            
            # Check for color balance issues
            color_balance_issue = False
            for color, value in color_balance.items():
                if value < 0.8 or value > 1.2:
                    color_balance_issue = True
                    break
            
            if color_balance_issue:
                if "issues" not in enhanced_results:
                    enhanced_results["issues"] = []
                
                enhanced_results["issues"].append({
                    "type": "color_balance",
                    "severity": "medium",
                    "message": "Color balance issue detected"
                })
        
        # Add noise analysis
        if "frame" in enhanced_results:
            frame = enhanced_results["frame"]
            
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Calculate noise level using median filter difference
            median_filtered = cv2.medianBlur(gray, 3)
            noise_diff = cv2.absdiff(gray, median_filtered)
            noise_level = np.mean(noise_diff) / 255.0
            
            enhanced_results["noise_level"] = noise_level
            
            # Check for high noise
            if noise_level > 0.1:
                if "issues" not in enhanced_results:
                    enhanced_results["issues"] = []
                
                enhanced_results["issues"].append({
                    "type": "high_noise",
                    "severity": "medium",
                    "message": "High image noise detected"
                })
        
        # Add stability analysis if historical data is available
        if "camera" in self._historical_results and len(self._historical_results["camera"]) > 1:
            # Get previous analysis
            prev_analysis = self._historical_results["camera"][-2]["results"]
            
            # Calculate stability metrics
            brightness_diff = abs(enhanced_results.get("brightness", 0) - prev_analysis.get("brightness", 0))
            contrast_diff = abs(enhanced_results.get("contrast", 0) - prev_analysis.get("contrast", 0))
            focus_diff = abs(enhanced_results.get("focus_score", 0) - prev_analysis.get("focus_score", 0))
            
            stability = {
                "brightness_stability": 1.0 - min(1.0, brightness_diff / 0.2),
                "contrast_stability": 1.0 - min(1.0, contrast_diff / 0.2),
                "focus_stability": 1.0 - min(1.0, focus_diff / 0.2)
            }
            
            enhanced_results["stability"] = stability
            
            # Check for stability issues
            stability_issue = False
            for metric, value in stability.items():
                if value < 0.7:
                    stability_issue = True
                    break
            
            if stability_issue:
                if "issues" not in enhanced_results:
                    enhanced_results["issues"] = []
                
                enhanced_results["issues"].append({
                    "type": "stability",
                    "severity": "medium",
                    "message": "Camera image stability issue detected"
                })
        
        return enhanced_results
    
    async def _enhance_hardware_analysis(self, issue_type: str, base_results: Dict[str, Any], pattern_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance hardware analysis with additional metrics and pattern matching.
        
        Args:
            issue_type: Type of hardware issue
            base_results: Base analysis results
            pattern_results: Pattern matching results
            
        Returns:
            Dict[str, Any]: Enhanced analysis results
        """
        # Start with base results
        enhanced_results = base_results.copy()
        
        # Add enhanced metrics
        enhanced_results["analysis_version"] = "2.0"
        enhanced_results["enhanced"] = True
        
        # Add pattern matching results
        enhanced_results["pattern_matching"] = pattern_results
        
        # Update detected flag based on pattern matching
        if pattern_results.get("matched_patterns", []):
            enhanced_results["detected"] = True
        
        # Add confidence score
        confidence_scores = [pattern.get("confidence", 0) for pattern in pattern_results.get("matched_patterns", [])]
        if confidence_scores:
            enhanced_results["confidence_score"] = max(confidence_scores)
        else:
            enhanced_results["confidence_score"] = 0.0
        
        # Add detailed recommendations based on pattern matching
        if pattern_results.get("matched_patterns", []):
            enhanced_results["detailed_recommendations"] = []
            
            for pattern in pattern_results["matched_patterns"]:
                pattern_type = pattern.get("pattern_type", "")
                if pattern_type and pattern_type in self._pattern_database.get(issue_type, {}):
                    pattern_info = self._pattern_database[issue_type][pattern_type]
                    
                    enhanced_results["detailed_recommendations"].append({
                        "issue": pattern_info.get("description", ""),
                        "severity": pattern_info.get("severity", "medium"),
                        "recommendation": pattern_info.get("recommendation", ""),
                        "confidence": pattern.get("confidence", 0)
                    })
        
        # Add historical trend analysis if available
        if "hardware_issues" in self._historical_results and issue_type in self._historical_results["hardware_issues"] and len(self._historical_results["hardware_issues"][issue_type]) > 1:
            # Get historical confidence scores
            historical_confidence = [
                entry["results"].get("confidence_score", 0)
                for entry in self._historical_results["hardware_issues"][issue_type]
            ]
            
            # Calculate trend
            if len(historical_confidence) >= 2:
                trend = historical_confidence[-1] - historical_confidence[0]
                
                enhanced_results["historical_trend"] = {
                    "direction": "improving" if trend < 0 else "worsening" if trend > 0 else "stable",
                    "magnitude": abs(trend),
                    "data_points": len(historical_confidence)
                }
        
        return enhanced_results
    
    async def _match_issue_patterns(self, issue_type: str, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Match analysis results against known issue patterns.
        
        Args:
            issue_type: Type of hardware issue
            analysis_results: Analysis results to match
            
        Returns:
            Dict[str, Any]: Pattern matching results
        """
        # Initialize results
        results = {
            "matched_patterns": []
        }
        
        # Check if we have patterns for this issue type
        if issue_type not in self._pattern_database:
            return results
        
        # Get frame if available
        frame = None
        if "frame" in analysis_results:
            frame = analysis_results["frame"]
        
        # Match each pattern
        for pattern_type, pattern_info in self._pattern_database[issue_type].items():
            confidence = 0.0
            
            # Different matching logic based on issue type
            if issue_type == "display":
                confidence = await self._match_display_pattern(pattern_type, analysis_results, frame)
            elif issue_type == "connection":
                confidence = await self._match_connection_pattern(pattern_type, analysis_results, frame)
            elif issue_type == "physical_damage":
                confidence = await self._match_physical_damage_pattern(pattern_type, analysis_results, frame)
            elif issue_type == "led_status":
                confidence = await self._match_led_status_pattern(pattern_type, analysis_results, frame)
            
            # Add to matched patterns if confidence exceeds threshold
            if confidence >= pattern_info.get("confidence_threshold", 0.75):
                results["matched_patterns"].append({
                    "pattern_type": pattern_type,
                    "confidence": confidence,
                    "description": pattern_info.get("description", ""),
                    "severity": pattern_info.get("severity", "medium")
                })
        
        # Sort matched patterns by confidence
        results["matched_patterns"].sort(key=lambda x: x.get("confidence", 0), reverse=True)
        
        return results
    
    async def _match_display_pattern(self, pattern_type: str, analysis_results: Dict[str, Any], frame: Optional[np.ndarray]) -> float:
        """
        Match display issue patterns.
        
        Args:
            pattern_type: Type of display issue pattern
            analysis_results: Analysis results
            frame: Video frame or None
            
        Returns:
            float: Confidence score (0.0 to 1.0)
        """
        confidence = 0.0
        
        if pattern_type == "dead_pixel":
            # Check for bright and dark spots
            bright_spots = analysis_results.get("bright_spots", 0)
            dark_spots = analysis_results.get("dark_spots", 0)
            
            if bright_spots > 5 or dark_spots > 5:
                # Calculate confidence based on number of spots
                confidence = min(1.0, max(bright_spots, dark_spots) / 20.0)
        
        elif pattern_type == "screen_flicker":
            # Screen flicker would require temporal analysis
            # This is a simplified implementation
            if "hardware_issues" in self._historical_results and "display" in self._historical_results["hardware_issues"] and len(self._historical_results["hardware_issues"]["display"]) > 1:
                # Check for brightness variation over time
                brightness_values = [
                    entry["results"].get("brightness", 0)
                    for entry in self._historical_results["hardware_issues"]["display"]
                ]
                
                if len(brightness_values) >= 2:
                    # Calculate brightness variation
                    brightness_variation = np.std(brightness_values)
                    
                    # High variation indicates potential flicker
                    if brightness_variation > 0.1:
                        confidence = min(1.0, brightness_variation / 0.2)
        
        elif pattern_type == "color_distortion":
            # Check for color imbalance
            if "color_distribution" in analysis_results:
                color_dist = analysis_results["color_distribution"]
                
                # Calculate color imbalance
                total = sum(color_dist.values())
                if total > 0:
                    red_ratio = color_dist.get("red", 0) / total
                    green_ratio = color_dist.get("green", 0) / total
                    blue_ratio = color_dist.get("blue", 0) / total
                    
                    # Check for significant imbalance
                    max_ratio = max(red_ratio, green_ratio, blue_ratio)
                    min_ratio = min(red_ratio, green_ratio, blue_ratio)
                    
                    if max_ratio > 0.5 or min_ratio < 0.1:
                        confidence = min(1.0, (max_ratio - min_ratio) / 0.5)
        
        return confidence
    
    async def _match_connection_pattern(self, pattern_type: str, analysis_results: Dict[str, Any], frame: Optional[np.ndarray]) -> float:
        """
        Match connection issue patterns.
        
        Args:
            pattern_type: Type of connection issue pattern
            analysis_results: Analysis results
            frame: Video frame or None
            
        Returns:
            float: Confidence score (0.0 to 1.0)
        """
        # This is a simplified implementation
        # In a real system, this would use more sophisticated image analysis
        
        confidence = 0.0
        
        if pattern_type == "loose_connection":
            # Check for USB port detection
            if analysis_results.get("usb_port_detected", False):
                # This is a very simplified check
                confidence = 0.5
        
        elif pattern_type == "bent_pins":
            # Would require detailed image analysis
            # Simplified implementation
            confidence = 0.0
        
        elif pattern_type == "corrosion":
            # Would require color analysis for greenish/whitish discoloration
            # Simplified implementation
            confidence = 0.0
        
        return confidence
    
    async def _match_physical_damage_pattern(self, pattern_type: str, analysis_results: Dict[str, Any], frame: Optional[np.ndarray]) -> float:
        """
        Match physical damage patterns.
        
        Args:
            pattern_type: Type of physical damage pattern
            analysis_results: Analysis results
            frame: Video frame or None
            
        Returns:
            float: Confidence score (0.0 to 1.0)
        """
        confidence = 0.0
        
        if pattern_type == "crack":
            # Check for potential cracks
            potential_cracks = analysis_results.get("potential_cracks", 0)
            
            if potential_cracks > 0:
                # Calculate confidence based on number of potential cracks
                confidence = min(1.0, potential_cracks / 5.0)
        
        elif pattern_type == "liquid_damage" or pattern_type == "impact_damage":
            # Would require more sophisticated image analysis
            # Simplified implementation
            confidence = 0.0
        
        return confidence
    
    async def _match_led_status_pattern(self, pattern_type: str, analysis_results: Dict[str, Any], frame: Optional[np.ndarray]) -> float:
        """
        Match LED status patterns.
        
        Args:
            pattern_type: Type of LED status pattern
            analysis_results: Analysis results
            frame: Video frame or None
            
        Returns:
            float: Confidence score (0.0 to 1.0)
        """
        confidence = 0.0
        
        if pattern_type == "error_code":
            # Check for red LED
            if analysis_results.get("red_led_detected", False):
                confidence = 0.8
        
        elif pattern_type == "power_issue":
            # Check for red LED
            if analysis_results.get("red_led_detected", False):
                confidence = 0.7
        
        elif pattern_type == "status_indicator":
            # Check for green LED
            if analysis_results.get("green_led_detected", False):
                confidence = 0.9
        
        return confidence
    
    async def _generate_diagnostic_annotations(self) -> Dict[str, Any]:
        """
        Generate annotations for diagnostic visualization.
        
        Returns:
            Dict[str, Any]: Annotations for visualization
        """
        annotations = {
            "text": [],
            "rectangles": [],
            "circles": [],
            "lines": []
        }
        
        # Add camera quality information
        if "camera" in self._analysis_results:
            camera_results = self._analysis_results["camera"]
            
            quality_score = camera_results.get("quality_score", 0)
            quality_text = "Excellent" if quality_score > 0.8 else "Good" if quality_score > 0.6 else "Fair" if quality_score > 0.4 else "Poor"
            
            annotations["text"].append({
                "text": f"Camera Quality: {quality_text} ({quality_score:.2f})",
                "x": 10,
                "y": 30,
                "color": (0, 255, 0) if quality_score > 0.6 else (0, 165, 255) if quality_score > 0.4 else (0, 0, 255),
                "scale": 0.8
            })
            
            # Add brightness, contrast, focus information
            brightness = camera_results.get("brightness", 0)
            contrast = camera_results.get("contrast", 0)
            focus = camera_results.get("focus_score", 0)
            
            annotations["text"].append({
                "text": f"Brightness: {brightness:.2f}",
                "x": 10,
                "y": 60,
                "color": (0, 255, 0) if 0.3 <= brightness <= 0.7 else (0, 165, 255),
                "scale": 0.7
            })
            
            annotations["text"].append({
                "text": f"Contrast: {contrast:.2f}",
                "x": 10,
                "y": 90,
                "color": (0, 255, 0) if contrast > 0.4 else (0, 165, 255),
                "scale": 0.7
            })
            
            annotations["text"].append({
                "text": f"Focus: {focus:.2f}",
                "x": 10,
                "y": 120,
                "color": (0, 255, 0) if focus > 0.5 else (0, 165, 255),
                "scale": 0.7
            })
        
        # Add detected issues
        y_pos = 160
        if "hardware_issues" in self._analysis_results:
            for issue_type, results in self._analysis_results["hardware_issues"].items():
                if results.get("detected", False):
                    annotations["text"].append({
                        "text": f"Issue Detected: {issue_type.replace('_', ' ').title()}",
                        "x": 10,
                        "y": y_pos,
                        "color": (0, 0, 255),
                        "scale": 0.8
                    })
                    y_pos += 30
                    
                    # Add confidence score if available
                    if "confidence_score" in results:
                        annotations["text"].append({
                            "text": f"Confidence: {results['confidence_score']:.2f}",
                            "x": 30,
                            "y": y_pos,
                            "color": (0, 165, 255),
                            "scale": 0.7
                        })
                        y_pos += 30
                    
                    # Add pattern matching results
                    if "pattern_matching" in results and "matched_patterns" in results["pattern_matching"]:
                        for i, pattern in enumerate(results["pattern_matching"]["matched_patterns"]):
                            if i >= 2:  # Limit to top 2 patterns
                                break
                                
                            annotations["text"].append({
                                "text": f"- {pattern.get('description', '')}",
                                "x": 30,
                                "y": y_pos,
                                "color": (0, 165, 255),
                                "scale": 0.7
                            })
                            y_pos += 30
        
        # Add timestamp
        annotations["text"].append({
            "text": f"Analysis: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            "x": 10,
            "y": y_pos + 30,
            "color": (255, 255, 255),
            "scale": 0.6
        })
        
        return annotations
    
    async def _generate_summary_section(self) -> Dict[str, Any]:
        """Generate summary section for diagnostic report."""
        summary = {
            "overview": "Dr. TARDIS Visual Diagnostic Report",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "issues_detected": 0,
            "camera_quality": "Unknown",
            "critical_issues": 0,
            "high_severity_issues": 0,
            "medium_severity_issues": 0,
            "low_severity_issues": 0
        }
        
        # Count issues by severity
        all_issues = []
        
        # Add camera issues
        if "camera" in self._analysis_results and "issues" in self._analysis_results["camera"]:
            all_issues.extend(self._analysis_results["camera"]["issues"])
        
        # Add hardware issues
        if "hardware_issues" in self._analysis_results:
            for issue_type, results in self._analysis_results["hardware_issues"].items():
                if "issues" in results:
                    all_issues.extend(results["issues"])
        
        # Count by severity
        for issue in all_issues:
            severity = issue.get("severity", "medium")
            if severity == "critical":
                summary["critical_issues"] += 1
            elif severity == "high":
                summary["high_severity_issues"] += 1
            elif severity == "medium":
                summary["medium_severity_issues"] += 1
            elif severity == "low":
                summary["low_severity_issues"] += 1
        
        summary["issues_detected"] = len(all_issues)
        
        # Set camera quality
        if "camera" in self._analysis_results:
            quality_score = self._analysis_results["camera"].get("quality_score", 0)
            summary["camera_quality"] = "Excellent" if quality_score > 0.8 else "Good" if quality_score > 0.6 else "Fair" if quality_score > 0.4 else "Poor"
        
        return summary
    
    async def _generate_camera_quality_section(self) -> Dict[str, Any]:
        """Generate camera quality section for diagnostic report."""
        camera_quality = {
            "metrics": {},
            "issues": []
        }
        
        if "camera" in self._analysis_results:
            camera_results = self._analysis_results["camera"]
            
            # Add metrics
            for key, value in camera_results.items():
                if key not in ["issues", "frame", "resolution"]:
                    camera_quality["metrics"][key] = value
            
            # Add resolution
            if "resolution" in camera_results:
                camera_quality["resolution"] = camera_results["resolution"]
            
            # Add issues
            if "issues" in camera_results:
                camera_quality["issues"] = camera_results["issues"]
        
        return camera_quality
    
    async def _generate_detected_issues_section(self) -> Dict[str, Any]:
        """Generate detected issues section for diagnostic report."""
        detected_issues = {
            "camera_issues": [],
            "hardware_issues": {}
        }
        
        # Add camera issues
        if "camera" in self._analysis_results and "issues" in self._analysis_results["camera"]:
            detected_issues["camera_issues"] = self._analysis_results["camera"]["issues"]
        
        # Add hardware issues
        if "hardware_issues" in self._analysis_results:
            for issue_type, results in self._analysis_results["hardware_issues"].items():
                if "issues" in results:
                    detected_issues["hardware_issues"][issue_type] = results["issues"]
        
        return detected_issues
    
    async def _generate_detailed_analysis_section(self) -> Dict[str, Any]:
        """Generate detailed analysis section for diagnostic report."""
        detailed_analysis = {
            "camera_analysis": {},
            "hardware_analysis": {}
        }
        
        # Add camera analysis
        if "camera" in self._analysis_results:
            detailed_analysis["camera_analysis"] = self._analysis_results["camera"]
        
        # Add hardware analysis
        if "hardware_issues" in self._analysis_results:
            for issue_type, results in self._analysis_results["hardware_issues"].items():
                detailed_analysis["hardware_analysis"][issue_type] = results
        
        return detailed_analysis
    
    async def _generate_pattern_matching_section(self) -> Dict[str, Any]:
        """Generate pattern matching section for diagnostic report."""
        pattern_matching = {
            "matched_patterns": []
        }
        
        # Add matched patterns from hardware issues
        if "hardware_issues" in self._analysis_results:
            for issue_type, results in self._analysis_results["hardware_issues"].items():
                if "pattern_matching" in results and "matched_patterns" in results["pattern_matching"]:
                    for pattern in results["pattern_matching"]["matched_patterns"]:
                        pattern_info = pattern.copy()
                        pattern_info["issue_type"] = issue_type
                        pattern_matching["matched_patterns"].append(pattern_info)
        
        # Sort by confidence
        pattern_matching["matched_patterns"].sort(key=lambda x: x.get("confidence", 0), reverse=True)
        
        return pattern_matching
    
    async def _generate_historical_comparison_section(self) -> Dict[str, Any]:
        """Generate historical comparison section for diagnostic report."""
        historical_comparison = {
            "camera_history": [],
            "hardware_history": {}
        }
        
        # Add camera history
        if "camera" in self._historical_results:
            for entry in self._historical_results["camera"]:
                historical_comparison["camera_history"].append({
                    "timestamp": entry["timestamp"],
                    "date": entry["date"],
                    "quality_score": entry["results"].get("quality_score", 0),
                    "brightness": entry["results"].get("brightness", 0),
                    "contrast": entry["results"].get("contrast", 0),
                    "focus_score": entry["results"].get("focus_score", 0)
                })
        
        # Add hardware history
        if "hardware_issues" in self._historical_results:
            for issue_type, entries in self._historical_results["hardware_issues"].items():
                historical_comparison["hardware_history"][issue_type] = []
                
                for entry in entries:
                    historical_comparison["hardware_history"][issue_type].append({
                        "timestamp": entry["timestamp"],
                        "date": entry["date"],
                        "detected": entry["results"].get("detected", False),
                        "confidence_score": entry["results"].get("confidence_score", 0)
                    })
        
        return historical_comparison
    
    async def _generate_recommendations_section(self, diagnostic_level: DiagnosticLevel) -> Dict[str, Any]:
        """
        Generate recommendations section for diagnostic report.
        
        Args:
            diagnostic_level: Level of diagnostic detail
            
        Returns:
            Dict[str, Any]: Recommendations section
        """
        recommendations = {
            "camera_recommendations": [],
            "hardware_recommendations": [],
            "general_recommendations": []
        }
        
        # Add camera recommendations
        if "camera" in self._analysis_results and "issues" in self._analysis_results["camera"]:
            for issue in self._analysis_results["camera"]["issues"]:
                issue_type = issue.get("type", "")
                
                if issue_type == "low_brightness":
                    recommendations["camera_recommendations"].append({
                        "issue": "Low lighting conditions",
                        "recommendation": "Increase lighting in the environment for better visibility",
                        "severity": issue.get("severity", "medium")
                    })
                elif issue_type == "low_contrast":
                    recommendations["camera_recommendations"].append({
                        "issue": "Low image contrast",
                        "recommendation": "Adjust lighting to increase contrast or adjust camera settings",
                        "severity": issue.get("severity", "medium")
                    })
                elif issue_type == "poor_focus":
                    recommendations["camera_recommendations"].append({
                        "issue": "Poor camera focus",
                        "recommendation": "Adjust camera focus or clean lens",
                        "severity": issue.get("severity", "high")
                    })
                elif issue_type == "high_noise":
                    recommendations["camera_recommendations"].append({
                        "issue": "High image noise",
                        "recommendation": "Improve lighting conditions or use a higher quality camera",
                        "severity": issue.get("severity", "medium")
                    })
                elif issue_type == "color_balance":
                    recommendations["camera_recommendations"].append({
                        "issue": "Color balance issue",
                        "recommendation": "Adjust white balance settings or use neutral lighting",
                        "severity": issue.get("severity", "medium")
                    })
                elif issue_type == "stability":
                    recommendations["camera_recommendations"].append({
                        "issue": "Camera stability issue",
                        "recommendation": "Use a stable mount or tripod for the camera",
                        "severity": issue.get("severity", "medium")
                    })
        
        # Add hardware recommendations
        if "hardware_issues" in self._analysis_results:
            for issue_type, results in self._analysis_results["hardware_issues"].items():
                if "detailed_recommendations" in results:
                    for rec in results["detailed_recommendations"]:
                        recommendations["hardware_recommendations"].append(rec)
                elif results.get("detected", False) and "issues" in results:
                    for issue in results["issues"]:
                        recommendations["hardware_recommendations"].append({
                            "issue": f"{issue_type.replace('_', ' ').title()}: {issue.get('message', '')}",
                            "recommendation": "Contact technical support for assistance",
                            "severity": issue.get("severity", "medium")
                        })
        
        # Add general recommendations based on diagnostic level
        if diagnostic_level == DiagnosticLevel.BASIC:
            recommendations["general_recommendations"].append({
                "issue": "Basic diagnostic completed",
                "recommendation": "For more detailed analysis, run an advanced diagnostic",
                "severity": "low"
            })
        elif diagnostic_level == DiagnosticLevel.ADVANCED:
            if not recommendations["hardware_recommendations"] and not recommendations["camera_recommendations"]:
                recommendations["general_recommendations"].append({
                    "issue": "No significant issues detected",
                    "recommendation": "Regular maintenance is recommended for optimal performance",
                    "severity": "low"
                })
        elif diagnostic_level == DiagnosticLevel.EXPERT:
            if not recommendations["hardware_recommendations"] and not recommendations["camera_recommendations"]:
                recommendations["general_recommendations"].append({
                    "issue": "No significant issues detected",
                    "recommendation": "Schedule periodic expert diagnostics for preventive maintenance",
                    "severity": "low"
                })
            else:
                recommendations["general_recommendations"].append({
                    "issue": "Multiple issues detected",
                    "recommendation": "Consider consulting with a technical specialist for comprehensive resolution",
                    "severity": "medium"
                })
        
        return recommendations
    
    async def _generate_troubleshooting_steps_section(self) -> Dict[str, Any]:
        """Generate troubleshooting steps section for diagnostic report."""
        troubleshooting_steps = {
            "camera_troubleshooting": [],
            "hardware_troubleshooting": {}
        }
        
        # Add camera troubleshooting steps
        if "camera" in self._analysis_results and "issues" in self._analysis_results["camera"]:
            for issue in self._analysis_results["camera"]["issues"]:
                issue_type = issue.get("type", "")
                
                if issue_type == "low_brightness":
                    troubleshooting_steps["camera_troubleshooting"].append({
                        "issue": "Low lighting conditions",
                        "steps": [
                            "Increase ambient lighting in the environment",
                            "Add additional light sources facing the subject",
                            "Adjust camera exposure settings if available",
                            "Move to a better lit location"
                        ]
                    })
                elif issue_type == "poor_focus":
                    troubleshooting_steps["camera_troubleshooting"].append({
                        "issue": "Poor camera focus",
                        "steps": [
                            "Clean camera lens with a microfiber cloth",
                            "Adjust manual focus if available",
                            "Ensure adequate lighting for autofocus to work properly",
                            "Maintain appropriate distance from subject (not too close)",
                            "Check for physical damage to lens"
                        ]
                    })
        
        # Add hardware troubleshooting steps
        if "hardware_issues" in self._analysis_results:
            for issue_type, results in self._analysis_results["hardware_issues"].items():
                if results.get("detected", False):
                    if issue_type == "display":
                        troubleshooting_steps["hardware_troubleshooting"]["display"] = {
                            "steps": [
                                "Check display cable connections",
                                "Update graphics drivers",
                                "Test with external monitor if possible",
                                "Run display diagnostic software",
                                "Check for physical damage to display"
                            ]
                        }
                    elif issue_type == "connection":
                        troubleshooting_steps["hardware_troubleshooting"]["connection"] = {
                            "steps": [
                                "Disconnect and reconnect all cables",
                                "Inspect connectors for damage or bent pins",
                                "Clean connectors with compressed air",
                                "Try alternative ports if available",
                                "Test with known working cables"
                            ]
                        }
                    elif issue_type == "physical_damage":
                        troubleshooting_steps["hardware_troubleshooting"]["physical_damage"] = {
                            "steps": [
                                "Document damage with photos",
                                "Avoid using damaged components",
                                "Check for internal damage",
                                "Consult repair service",
                                "Use temporary protective measures to prevent further damage"
                            ]
                        }
                    elif issue_type == "led_status":
                        troubleshooting_steps["hardware_troubleshooting"]["led_status"] = {
                            "steps": [
                                "Consult device manual for LED code meaning",
                                "Power cycle the device",
                                "Check power supply",
                                "Reset device to factory settings if possible",
                                "Contact technical support with LED pattern information"
                            ]
                        }
        
        return troubleshooting_steps
    
    async def _generate_repair_procedures_section(self) -> Dict[str, Any]:
        """Generate repair procedures section for diagnostic report."""
        # This would contain detailed repair procedures for expert level diagnostics
        # Simplified implementation for demonstration
        repair_procedures = {
            "disclaimer": "The following repair procedures should only be performed by qualified technicians.",
            "procedures": {}
        }
        
        # Add procedures based on detected issues
        if "hardware_issues" in self._analysis_results:
            for issue_type, results in self._analysis_results["hardware_issues"].items():
                if results.get("detected", False):
                    if issue_type == "display" and "pattern_matching" in results:
                        for pattern in results["pattern_matching"].get("matched_patterns", []):
                            if pattern.get("pattern_type") == "dead_pixel":
                                repair_procedures["procedures"]["dead_pixel_repair"] = {
                                    "title": "Dead Pixel Repair Procedure",
                                    "difficulty": "Medium",
                                    "tools_required": ["Microfiber cloth", "Pixel repair software"],
                                    "steps": [
                                        "Run pixel repair software that cycles through colors",
                                        "Apply gentle pressure with microfiber cloth on affected area",
                                        "Run color cycling for at least 10 minutes",
                                        "For persistent issues, consult display manufacturer"
                                    ]
                                }
        
        return repair_procedures
    
    async def _generate_technical_specifications_section(self) -> Dict[str, Any]:
        """Generate technical specifications section for diagnostic report."""
        # This would contain detailed technical specifications for expert level diagnostics
        # Simplified implementation for demonstration
        technical_specifications = {
            "camera_specifications": {},
            "analysis_parameters": {},
            "software_versions": {
                "enhanced_visual_troubleshooter": "2.0",
                "opencv": cv2.__version__
            }
        }
        
        # Add camera specifications
        if "camera" in self._analysis_results and "resolution" in self._analysis_results["camera"]:
            technical_specifications["camera_specifications"]["resolution"] = self._analysis_results["camera"]["resolution"]
        
        # Add analysis parameters
        technical_specifications["analysis_parameters"] = {
            "brightness_threshold": 0.3,
            "focus_threshold": 0.5,
            "pattern_matching_confidence_threshold": 0.75
        }
        
        return technical_specifications

# Example usage
async def example_usage():
    # Create a video processor
    processor = VideoProcessor(device_id=0, width=640, height=480, fps=30)
    
    # Create an enhanced visual troubleshooter
    troubleshooter = EnhancedVisualTroubleshooter(processor)
    
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
        
        # Analyze hardware issues
        print("Analyzing display issues...")
        display_results = await troubleshooter.analyze_hardware_issue("display")
        print(f"Display analysis results: {display_results}")
        
        # Generate diagnostic report
        print("Generating diagnostic report...")
        report = await troubleshooter.generate_diagnostic_report(DiagnosticLevel.ADVANCED)
        print(f"Diagnostic report: {report}")
        
        # Save diagnostic report
        await troubleshooter.save_diagnostic_report("diagnostic_report.json", DiagnosticLevel.ADVANCED)
        
        # Save annotated diagnostic frame
        await troubleshooter.save_annotated_diagnostic_frame("diagnostic_frame.jpg")
        
    finally:
        # Clean up
        processor.close()

if __name__ == "__main__":
    asyncio.run(example_usage())
