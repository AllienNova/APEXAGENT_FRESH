#!/usr/bin/env python3
"""
Accessibility Framework for ApexAgent

This module provides a comprehensive framework for ensuring accessibility
compliance, including screen reader support, keyboard navigation, color
contrast checking, and other accessibility features to make ApexAgent
usable by people with disabilities.
"""

import os
import sys
import json
import uuid
import logging
import threading
import re
import time
import math
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union, Callable, Set, TypeVar
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
import queue
from PIL import Image, ImageDraw, ImageFont
import colorsys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("accessibility.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("accessibility")

# Type variables for generic functions
T = TypeVar("T")

class AccessibilityStandard(Enum):
    """Enumeration of accessibility standards."""
    WCAG_2_0_A = "wcag_2_0_a"
    WCAG_2_0_AA = "wcag_2_0_aa"
    WCAG_2_0_AAA = "wcag_2_0_aaa"
    WCAG_2_1_A = "wcag_2_1_a"
    WCAG_2_1_AA = "wcag_2_1_aa"
    WCAG_2_1_AAA = "wcag_2_1_aaa"
    SECTION_508 = "section_508"
    EN_301_549 = "en_301_549"
    ADA = "ada"

class AccessibilityRole(Enum):
    """Enumeration of ARIA roles."""
    ALERT = "alert"
    ALERTDIALOG = "alertdialog"
    BUTTON = "button"
    CHECKBOX = "checkbox"
    DIALOG = "dialog"
    GRIDCELL = "gridcell"
    LINK = "link"
    LOG = "log"
    MARQUEE = "marquee"
    MENUITEM = "menuitem"
    MENUITEMCHECKBOX = "menuitemcheckbox"
    MENUITEMRADIO = "menuitemradio"
    OPTION = "option"
    PROGRESSBAR = "progressbar"
    RADIO = "radio"
    SCROLLBAR = "scrollbar"
    SEARCHBOX = "searchbox"
    SLIDER = "slider"
    SPINBUTTON = "spinbutton"
    STATUS = "status"
    SWITCH = "switch"
    TAB = "tab"
    TABPANEL = "tabpanel"
    TEXTBOX = "textbox"
    TIMER = "timer"
    TOOLTIP = "tooltip"
    TREEITEM = "treeitem"
    COMBOBOX = "combobox"
    GRID = "grid"
    LISTBOX = "listbox"
    MENU = "menu"
    MENUBAR = "menubar"
    RADIOGROUP = "radiogroup"
    TABLIST = "tablist"
    TREE = "tree"
    TREEGRID = "treegrid"
    ARTICLE = "article"
    COLUMNHEADER = "columnheader"
    DEFINITION = "definition"
    DIRECTORY = "directory"
    DOCUMENT = "document"
    FEED = "feed"
    FIGURE = "figure"
    HEADING = "heading"
    IMG = "img"
    LIST = "list"
    LISTITEM = "listitem"
    MATH = "math"
    NAVIGATION = "navigation"
    REGION = "region"
    ROW = "row"
    ROWGROUP = "rowgroup"
    ROWHEADER = "rowheader"
    SEPARATOR = "separator"
    TOOLBAR = "toolbar"
    APPLICATION = "application"
    BANNER = "banner"
    COMPLEMENTARY = "complementary"
    CONTENTINFO = "contentinfo"
    FORM = "form"
    MAIN = "main"
    NONE = "none"
    NOTE = "note"
    PRESENTATION = "presentation"
    SEARCH = "search"

class AccessibilityViolationType(Enum):
    """Enumeration of accessibility violation types."""
    CONTRAST = "contrast"
    KEYBOARD = "keyboard"
    SCREEN_READER = "screen_reader"
    STRUCTURE = "structure"
    SEMANTICS = "semantics"
    FOCUS = "focus"
    TIMING = "timing"
    LANGUAGE = "language"
    ALTERNATIVE = "alternative"
    ARIA = "aria"
    CUSTOM = "custom"

class AccessibilityViolationSeverity(Enum):
    """Enumeration of accessibility violation severities."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

@dataclass
class AccessibilityConfig:
    """Configuration for the accessibility system."""
    enabled: bool = True
    target_standards: List[AccessibilityStandard] = field(default_factory=lambda: [AccessibilityStandard.WCAG_2_1_AA])
    screen_reader_support: bool = True
    keyboard_navigation: bool = True
    high_contrast_mode: bool = True
    text_to_speech: bool = True
    speech_recognition: bool = False
    motion_reduction: bool = True
    font_size_adjustment: bool = True
    color_blind_support: bool = True
    violations_storage_path: str = "accessibility_violations"
    reports_storage_path: str = "accessibility_reports"
    min_contrast_ratio: float = 4.5  # WCAG 2.1 AA requires 4.5:1 for normal text
    min_large_text_contrast_ratio: float = 3.0  # WCAG 2.1 AA requires 3:1 for large text
    focus_visible: bool = True
    skip_links: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the configuration to a dictionary."""
        return {
            "enabled": self.enabled,
            "target_standards": [std.value for std in self.target_standards],
            "screen_reader_support": self.screen_reader_support,
            "keyboard_navigation": self.keyboard_navigation,
            "high_contrast_mode": self.high_contrast_mode,
            "text_to_speech": self.text_to_speech,
            "speech_recognition": self.speech_recognition,
            "motion_reduction": self.motion_reduction,
            "font_size_adjustment": self.font_size_adjustment,
            "color_blind_support": self.color_blind_support,
            "violations_storage_path": self.violations_storage_path,
            "reports_storage_path": self.reports_storage_path,
            "min_contrast_ratio": self.min_contrast_ratio,
            "min_large_text_contrast_ratio": self.min_large_text_contrast_ratio,
            "focus_visible": self.focus_visible,
            "skip_links": self.skip_links
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AccessibilityConfig":
        """Create a configuration from a dictionary."""
        return cls(
            enabled=data.get("enabled", True),
            target_standards=[AccessibilityStandard(std) for std in data.get("target_standards", ["wcag_2_1_aa"])],
            screen_reader_support=data.get("screen_reader_support", True),
            keyboard_navigation=data.get("keyboard_navigation", True),
            high_contrast_mode=data.get("high_contrast_mode", True),
            text_to_speech=data.get("text_to_speech", True),
            speech_recognition=data.get("speech_recognition", False),
            motion_reduction=data.get("motion_reduction", True),
            font_size_adjustment=data.get("font_size_adjustment", True),
            color_blind_support=data.get("color_blind_support", True),
            violations_storage_path=data.get("violations_storage_path", "accessibility_violations"),
            reports_storage_path=data.get("reports_storage_path", "accessibility_reports"),
            min_contrast_ratio=data.get("min_contrast_ratio", 4.5),
            min_large_text_contrast_ratio=data.get("min_large_text_contrast_ratio", 3.0),
            focus_visible=data.get("focus_visible", True),
            skip_links=data.get("skip_links", True)
        )

@dataclass
class AccessibilityViolation:
    """An accessibility violation."""
    violation_id: str
    type: AccessibilityViolationType
    severity: AccessibilityViolationSeverity
    standard: AccessibilityStandard
    element_id: Optional[str]
    element_type: Optional[str]
    element_role: Optional[AccessibilityRole]
    description: str
    recommendation: str
    screenshot_path: Optional[str] = None
    code_snippet: Optional[str] = None
    page_url: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    fixed_at: Optional[datetime] = None
    fixed: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "violation_id": self.violation_id,
            "type": self.type.value,
            "severity": self.severity.value,
            "standard": self.standard.value,
            "element_id": self.element_id,
            "element_type": self.element_type,
            "element_role": self.element_role.value if self.element_role else None,
            "description": self.description,
            "recommendation": self.recommendation,
            "screenshot_path": self.screenshot_path,
            "code_snippet": self.code_snippet,
            "page_url": self.page_url,
            "created_at": self.created_at.isoformat(),
            "fixed_at": self.fixed_at.isoformat() if self.fixed_at else None,
            "fixed": self.fixed
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AccessibilityViolation":
        """Create from dictionary."""
        return cls(
            violation_id=data["violation_id"],
            type=AccessibilityViolationType(data["type"]),
            severity=AccessibilityViolationSeverity(data["severity"]),
            standard=AccessibilityStandard(data["standard"]),
            element_id=data.get("element_id"),
            element_type=data.get("element_type"),
            element_role=AccessibilityRole(data["element_role"]) if data.get("element_role") else None,
            description=data["description"],
            recommendation=data["recommendation"],
            screenshot_path=data.get("screenshot_path"),
            code_snippet=data.get("code_snippet"),
            page_url=data.get("page_url"),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
            fixed_at=datetime.fromisoformat(data["fixed_at"]) if data.get("fixed_at") else None,
            fixed=data.get("fixed", False)
        )

@dataclass
class AccessibilityReport:
    """An accessibility audit report."""
    report_id: str
    title: str
    target_standards: List[AccessibilityStandard]
    violations: List[AccessibilityViolation]
    pass_count: int
    fail_count: int
    warning_count: int
    info_count: int
    total_elements_checked: int
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "report_id": self.report_id,
            "title": self.title,
            "target_standards": [std.value for std in self.target_standards],
            "violations": [v.to_dict() for v in self.violations],
            "pass_count": self.pass_count,
            "fail_count": self.fail_count,
            "warning_count": self.warning_count,
            "info_count": self.info_count,
            "total_elements_checked": self.total_elements_checked,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AccessibilityReport":
        """Create from dictionary."""
        return cls(
            report_id=data["report_id"],
            title=data["title"],
            target_standards=[AccessibilityStandard(std) for std in data["target_standards"]],
            violations=[AccessibilityViolation.from_dict(v) for v in data["violations"]],
            pass_count=data["pass_count"],
            fail_count=data["fail_count"],
            warning_count=data["warning_count"],
            info_count=data["info_count"],
            total_elements_checked=data["total_elements_checked"],
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
            updated_at=datetime.fromisoformat(data.get("updated_at", datetime.now().isoformat()))
        )

@dataclass
class ElementAccessibilityAttributes:
    """Accessibility attributes for an element."""
    element_id: str
    element_type: str
    role: Optional[AccessibilityRole] = None
    label: Optional[str] = None
    description: Optional[str] = None
    has_keyboard_focus: bool = False
    is_focusable: bool = False
    tab_index: Optional[int] = None
    is_visible: bool = True
    is_enabled: bool = True
    has_alt_text: bool = False
    alt_text: Optional[str] = None
    has_aria_label: bool = False
    aria_label: Optional[str] = None
    has_aria_describedby: bool = False
    aria_describedby: Optional[str] = None
    has_aria_labelledby: bool = False
    aria_labelledby: Optional[str] = None
    has_title: bool = False
    title: Optional[str] = None
    foreground_color: Optional[str] = None
    background_color: Optional[str] = None
    font_size: Optional[float] = None
    is_bold: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "element_id": self.element_id,
            "element_type": self.element_type,
            "role": self.role.value if self.role else None,
            "label": self.label,
            "description": self.description,
            "has_keyboard_focus": self.has_keyboard_focus,
            "is_focusable": self.is_focusable,
            "tab_index": self.tab_index,
            "is_visible": self.is_visible,
            "is_enabled": self.is_enabled,
            "has_alt_text": self.has_alt_text,
            "alt_text": self.alt_text,
            "has_aria_label": self.has_aria_label,
            "aria_label": self.aria_label,
            "has_aria_describedby": self.has_aria_describedby,
            "aria_describedby": self.aria_describedby,
            "has_aria_labelledby": self.has_aria_labelledby,
            "aria_labelledby": self.aria_labelledby,
            "has_title": self.has_title,
            "title": self.title,
            "foreground_color": self.foreground_color,
            "background_color": self.background_color,
            "font_size": self.font_size,
            "is_bold": self.is_bold
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ElementAccessibilityAttributes":
        """Create from dictionary."""
        return cls(
            element_id=data["element_id"],
            element_type=data["element_type"],
            role=AccessibilityRole(data["role"]) if data.get("role") else None,
            label=data.get("label"),
            description=data.get("description"),
            has_keyboard_focus=data.get("has_keyboard_focus", False),
            is_focusable=data.get("is_focusable", False),
            tab_index=data.get("tab_index"),
            is_visible=data.get("is_visible", True),
            is_enabled=data.get("is_enabled", True),
            has_alt_text=data.get("has_alt_text", False),
            alt_text=data.get("alt_text"),
            has_aria_label=data.get("has_aria_label", False),
            aria_label=data.get("aria_label"),
            has_aria_describedby=data.get("has_aria_describedby", False),
            aria_describedby=data.get("aria_describedby"),
            has_aria_labelledby=data.get("has_aria_labelledby", False),
            aria_labelledby=data.get("aria_labelledby"),
            has_title=data.get("has_title", False),
            title=data.get("title"),
            foreground_color=data.get("foreground_color"),
            background_color=data.get("background_color"),
            font_size=data.get("font_size"),
            is_bold=data.get("is_bold", False)
        )

class ColorContrastChecker:
    """Checks color contrast for accessibility."""
    
    @staticmethod
    def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    @staticmethod
    def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
        """Convert RGB to hex color."""
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
    
    @staticmethod
    def relative_luminance(rgb: Tuple[int, int, int]) -> float:
        """Calculate relative luminance of a color."""
        r, g, b = [c / 255 for c in rgb]
        
        # Convert to sRGB
        r = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
        g = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
        b = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4
        
        # Calculate luminance
        return 0.2126 * r + 0.7152 * g + 0.0722 * b
    
    @staticmethod
    def contrast_ratio(color1: str, color2: str) -> float:
        """Calculate contrast ratio between two colors."""
        rgb1 = ColorContrastChecker.hex_to_rgb(color1)
        rgb2 = ColorContrastChecker.hex_to_rgb(color2)
        
        lum1 = ColorContrastChecker.relative_luminance(rgb1)
        lum2 = ColorContrastChecker.relative_luminance(rgb2)
        
        # Ensure lighter color is first
        if lum1 < lum2:
            lum1, lum2 = lum2, lum1
        
        # Calculate contrast ratio
        return (lum1 + 0.05) / (lum2 + 0.05)
    
    @staticmethod
    def meets_wcag_aa(color1: str, color2: str, is_large_text: bool = False) -> bool:
        """Check if colors meet WCAG 2.1 AA contrast requirements."""
        ratio = ColorContrastChecker.contrast_ratio(color1, color2)
        min_ratio = 3.0 if is_large_text else 4.5
        return ratio >= min_ratio
    
    @staticmethod
    def meets_wcag_aaa(color1: str, color2: str, is_large_text: bool = False) -> bool:
        """Check if colors meet WCAG 2.1 AAA contrast requirements."""
        ratio = ColorContrastChecker.contrast_ratio(color1, color2)
        min_ratio = 4.5 if is_large_text else 7.0
        return ratio >= min_ratio
    
    @staticmethod
    def suggest_accessible_color(target_color: str, background_color: str, 
                               min_ratio: float = 4.5) -> str:
        """Suggest an accessible color that meets the minimum contrast ratio."""
        target_rgb = ColorContrastChecker.hex_to_rgb(target_color)
        bg_rgb = ColorContrastChecker.hex_to_rgb(background_color)
        
        # Convert to HSL for better adjustments
        h, l, s = colorsys.rgb_to_hls(target_rgb[0]/255, target_rgb[1]/255, target_rgb[2]/255)
        
        # Try adjusting lightness
        best_color = target_color
        best_ratio = ColorContrastChecker.contrast_ratio(target_color, background_color)
        
        if best_ratio >= min_ratio:
            return best_color
        
        # Try increasing and decreasing lightness
        for l_adjust in [l * 0.8, l * 0.6, l * 0.4, l * 0.2, 
                         min(1.0, l * 1.2), min(1.0, l * 1.4), 
                         min(1.0, l * 1.6), min(1.0, l * 1.8)]:
            r, g, b = colorsys.hls_to_rgb(h, l_adjust, s)
            new_color = ColorContrastChecker.rgb_to_hex((int(r*255), int(g*255), int(b*255)))
            new_ratio = ColorContrastChecker.contrast_ratio(new_color, background_color)
            
            if new_ratio > best_ratio:
                best_ratio = new_ratio
                best_color = new_color
                
                if best_ratio >= min_ratio:
                    break
        
        # If still not meeting requirements, try black or white
        if best_ratio < min_ratio:
            white_ratio = ColorContrastChecker.contrast_ratio("#FFFFFF", background_color)
            black_ratio = ColorContrastChecker.contrast_ratio("#000000", background_color)
            
            if white_ratio >= black_ratio and white_ratio >= min_ratio:
                return "#FFFFFF"
            elif black_ratio >= min_ratio:
                return "#000000"
        
        return best_color
    
    @staticmethod
    def simulate_color_blindness(color: str, color_blind_type: str) -> str:
        """Simulate how a color would appear to someone with color blindness."""
        rgb = ColorContrastChecker.hex_to_rgb(color)
        r, g, b = rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0
        
        if color_blind_type == "protanopia":  # Red-blind
            # Simulation matrix for protanopia
            sim_r = 0.567 * r + 0.433 * g + 0.0 * b
            sim_g = 0.558 * r + 0.442 * g + 0.0 * b
            sim_b = 0.0 * r + 0.242 * g + 0.758 * b
        elif color_blind_type == "deuteranopia":  # Green-blind
            # Simulation matrix for deuteranopia
            sim_r = 0.625 * r + 0.375 * g + 0.0 * b
            sim_g = 0.7 * r + 0.3 * g + 0.0 * b
            sim_b = 0.0 * r + 0.3 * g + 0.7 * b
        elif color_blind_type == "tritanopia":  # Blue-blind
            # Simulation matrix for tritanopia
            sim_r = 0.95 * r + 0.05 * g + 0.0 * b
            sim_g = 0.0 * r + 0.433 * g + 0.567 * b
            sim_b = 0.0 * r + 0.475 * g + 0.525 * b
        else:
            return color
        
        # Convert back to RGB
        sim_r = max(0, min(1, sim_r)) * 255
        sim_g = max(0, min(1, sim_g)) * 255
        sim_b = max(0, min(1, sim_b)) * 255
        
        return ColorContrastChecker.rgb_to_hex((int(sim_r), int(sim_g), int(sim_b)))

class AccessibilityChecker:
    """Checks elements for accessibility violations."""
    
    def __init__(self, config: AccessibilityConfig):
        """Initialize the accessibility checker."""
        self.config = config
        self.color_checker = ColorContrastChecker()
    
    def check_element(self, element: ElementAccessibilityAttributes) -> List[AccessibilityViolation]:
        """Check an element for accessibility violations."""
        violations = []
        
        # Check for various accessibility issues
        violations.extend(self._check_alt_text(element))
        violations.extend(self._check_aria_attributes(element))
        violations.extend(self._check_color_contrast(element))
        violations.extend(self._check_keyboard_accessibility(element))
        
        return violations
    
    def _check_alt_text(self, element: ElementAccessibilityAttributes) -> List[AccessibilityViolation]:
        """Check for alt text on images and other elements that need it."""
        violations = []
        
        # Check if element is an image or has image role
        if element.element_type == "img" or element.role == AccessibilityRole.IMG:
            if not element.has_alt_text and not element.has_aria_label:
                violations.append(AccessibilityViolation(
                    violation_id=str(uuid.uuid4()),
                    type=AccessibilityViolationType.ALTERNATIVE,
                    severity=AccessibilityViolationSeverity.HIGH,
                    standard=AccessibilityStandard.WCAG_2_1_A,
                    element_id=element.element_id,
                    element_type=element.element_type,
                    element_role=element.role,
                    description="Image missing alternative text",
                    recommendation="Add alt attribute or aria-label to provide alternative text for screen readers"
                ))
            elif element.has_alt_text and element.alt_text == "":
                # Empty alt text is valid for decorative images, but let's flag it as info
                violations.append(AccessibilityViolation(
                    violation_id=str(uuid.uuid4()),
                    type=AccessibilityViolationType.ALTERNATIVE,
                    severity=AccessibilityViolationSeverity.INFO,
                    standard=AccessibilityStandard.WCAG_2_1_A,
                    element_id=element.element_id,
                    element_type=element.element_type,
                    element_role=element.role,
                    description="Image has empty alt text",
                    recommendation="Ensure this is intentional for decorative images"
                ))
        
        return violations
    
    def _check_aria_attributes(self, element: ElementAccessibilityAttributes) -> List[AccessibilityViolation]:
        """Check for proper ARIA attributes."""
        violations = []
        
        # Check for interactive elements without accessible names
        interactive_roles = [
            AccessibilityRole.BUTTON, AccessibilityRole.LINK, AccessibilityRole.CHECKBOX,
            AccessibilityRole.RADIO, AccessibilityRole.COMBOBOX, AccessibilityRole.LISTBOX,
            AccessibilityRole.MENU, AccessibilityRole.MENUITEM, AccessibilityRole.SLIDER,
            AccessibilityRole.SWITCH, AccessibilityRole.TAB
        ]
        
        if element.role in interactive_roles:
            has_accessible_name = (
                element.has_aria_label or 
                element.has_aria_labelledby or 
                element.label is not None or
                element.has_title
            )
            
            if not has_accessible_name:
                violations.append(AccessibilityViolation(
                    violation_id=str(uuid.uuid4()),
                    type=AccessibilityViolationType.ARIA,
                    severity=AccessibilityViolationSeverity.HIGH,
                    standard=AccessibilityStandard.WCAG_2_1_A,
                    element_id=element.element_id,
                    element_type=element.element_type,
                    element_role=element.role,
                    description=f"Interactive element ({element.role.value}) missing accessible name",
                    recommendation="Add aria-label, aria-labelledby, or visible text label"
                ))
        
        # Check for invalid ARIA role combinations
        if element.role == AccessibilityRole.BUTTON and element.element_type == "a":
            violations.append(AccessibilityViolation(
                violation_id=str(uuid.uuid4()),
                type=AccessibilityViolationType.ARIA,
                severity=AccessibilityViolationSeverity.MEDIUM,
                standard=AccessibilityStandard.WCAG_2_1_A,
                element_id=element.element_id,
                element_type=element.element_type,
                element_role=element.role,
                description="Link element with button role",
                recommendation="Use a button element instead of a link with role='button'"
            ))
        
        return violations
    
    def _check_color_contrast(self, element: ElementAccessibilityAttributes) -> List[AccessibilityViolation]:
        """Check for sufficient color contrast."""
        violations = []
        
        if element.foreground_color and element.background_color:
            # Determine if this is large text
            is_large_text = False
            if element.font_size:
                is_large_text = (element.font_size >= 18) or (element.font_size >= 14 and element.is_bold)
            
            # Check contrast ratio
            try:
                ratio = self.color_checker.contrast_ratio(
                    element.foreground_color, element.background_color
                )
                
                min_ratio = self.config.min_large_text_contrast_ratio if is_large_text else self.config.min_contrast_ratio
                
                if ratio < min_ratio:
                    # Suggest a better color
                    suggested_color = self.color_checker.suggest_accessible_color(
                        element.foreground_color, element.background_color, min_ratio
                    )
                    
                    violations.append(AccessibilityViolation(
                        violation_id=str(uuid.uuid4()),
                        type=AccessibilityViolationType.CONTRAST,
                        severity=AccessibilityViolationSeverity.HIGH,
                        standard=AccessibilityStandard.WCAG_2_1_AA,
                        element_id=element.element_id,
                        element_type=element.element_type,
                        element_role=element.role,
                        description=f"Insufficient color contrast ratio: {ratio:.2f}:1 (minimum required: {min_ratio}:1)",
                        recommendation=f"Increase contrast. Suggested color: {suggested_color}"
                    ))
            except Exception as e:
                logger.error(f"Error checking color contrast: {str(e)}")
        
        return violations
    
    def _check_keyboard_accessibility(self, element: ElementAccessibilityAttributes) -> List[AccessibilityViolation]:
        """Check for keyboard accessibility issues."""
        violations = []
        
        # Interactive elements should be focusable
        interactive_elements = ["a", "button", "input", "select", "textarea"]
        interactive_roles = [
            AccessibilityRole.BUTTON, AccessibilityRole.LINK, AccessibilityRole.CHECKBOX,
            AccessibilityRole.RADIO, AccessibilityRole.COMBOBOX, AccessibilityRole.LISTBOX,
            AccessibilityRole.MENU, AccessibilityRole.MENUITEM, AccessibilityRole.SLIDER,
            AccessibilityRole.SWITCH, AccessibilityRole.TAB
        ]
        
        if (element.element_type in interactive_elements or element.role in interactive_roles) and element.is_visible and element.is_enabled:
            if not element.is_focusable:
                violations.append(AccessibilityViolation(
                    violation_id=str(uuid.uuid4()),
                    type=AccessibilityViolationType.KEYBOARD,
                    severity=AccessibilityViolationSeverity.HIGH,
                    standard=AccessibilityStandard.WCAG_2_1_A,
                    element_id=element.element_id,
                    element_type=element.element_type,
                    element_role=element.role,
                    description="Interactive element not keyboard focusable",
                    recommendation="Ensure element can receive keyboard focus"
                ))
        
        # Check for negative tabindex
        if element.tab_index is not None and element.tab_index < 0:
            violations.append(AccessibilityViolation(
                violation_id=str(uuid.uuid4()),
                type=AccessibilityViolationType.KEYBOARD,
                severity=AccessibilityViolationSeverity.MEDIUM,
                standard=AccessibilityStandard.WCAG_2_1_A,
                element_id=element.element_id,
                element_type=element.element_type,
                element_role=element.role,
                description="Element with negative tabindex",
                recommendation="Avoid using negative tabindex as it removes element from keyboard navigation"
            ))
        
        return violations

class ViolationManager:
    """Manages accessibility violations."""
    
    def __init__(self, config: AccessibilityConfig):
        """Initialize the violation manager."""
        self.config = config
        self.violations: Dict[str, AccessibilityViolation] = {}
        self._lock = threading.RLock()
        self._load_violations()
    
    def _load_violations(self) -> None:
        """Load violations from storage."""
        with self._lock:
            self.violations = {}
            violations_dir = Path(self.config.violations_storage_path)
            violations_dir.mkdir(parents=True, exist_ok=True)
            
            for file_path in violations_dir.glob("*.json"):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        violation_data = json.load(f)
                    
                    violation = AccessibilityViolation.from_dict(violation_data)
                    self.violations[violation.violation_id] = violation
                except Exception as e:
                    logger.error(f"Failed to load violation from {file_path}: {str(e)}")
    
    def _save_violation(self, violation: AccessibilityViolation) -> None:
        """Save a violation to storage."""
        violations_dir = Path(self.config.violations_storage_path)
        violations_dir.mkdir(parents=True, exist_ok=True)
        file_path = violations_dir / f"{violation.violation_id}.json"
        
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(violation.to_dict(), f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save violation {violation.violation_id}: {str(e)}")
    
    def add_violation(self, violation: AccessibilityViolation) -> None:
        """Add a new violation."""
        with self._lock:
            self.violations[violation.violation_id] = violation
            self._save_violation(violation)
            logger.info(f"Added new violation: {violation.violation_id} ({violation.type.value})")
    
    def get_violation(self, violation_id: str) -> Optional[AccessibilityViolation]:
        """Get a violation by ID."""
        with self._lock:
            return self.violations.get(violation_id)
    
    def get_violations(self, fixed: Optional[bool] = None, 
                      type: Optional[AccessibilityViolationType] = None,
                      severity: Optional[AccessibilityViolationSeverity] = None,
                      standard: Optional[AccessibilityStandard] = None) -> List[AccessibilityViolation]:
        """Get violations filtered by criteria."""
        with self._lock:
            filtered_violations = list(self.violations.values())
            
            if fixed is not None:
                filtered_violations = [v for v in filtered_violations if v.fixed == fixed]
            
            if type:
                filtered_violations = [v for v in filtered_violations if v.type == type]
            
            if severity:
                filtered_violations = [v for v in filtered_violations if v.severity == severity]
            
            if standard:
                filtered_violations = [v for v in filtered_violations if v.standard == standard]
            
            return filtered_violations
    
    def mark_as_fixed(self, violation_id: str) -> bool:
        """Mark a violation as fixed."""
        with self._lock:
            if violation_id not in self.violations:
                logger.error(f"Violation not found: {violation_id}")
                return False
            
            violation = self.violations[violation_id]
            violation.fixed = True
            violation.fixed_at = datetime.now()
            
            self._save_violation(violation)
            logger.info(f"Marked violation as fixed: {violation_id}")
            return True
    
    def delete_violation(self, violation_id: str) -> bool:
        """Delete a violation."""
        with self._lock:
            if violation_id not in self.violations:
                logger.error(f"Violation not found: {violation_id}")
                return False
            
            violations_dir = Path(self.config.violations_storage_path)
            file_path = violations_dir / f"{violation_id}.json"
            
            try:
                if file_path.exists():
                    file_path.unlink()
                
                del self.violations[violation_id]
                logger.info(f"Deleted violation: {violation_id}")
                return True
            except Exception as e:
                logger.error(f"Failed to delete violation {violation_id}: {str(e)}")
                return False

class ReportGenerator:
    """Generates accessibility reports."""
    
    def __init__(self, config: AccessibilityConfig):
        """Initialize the report generator."""
        self.config = config
    
    def generate_report(self, title: str, violations: List[AccessibilityViolation], 
                       total_elements_checked: int) -> AccessibilityReport:
        """Generate an accessibility report."""
        report_id = str(uuid.uuid4())
        
        # Count violations by severity
        pass_count = total_elements_checked - len(violations)
        fail_count = len([v for v in violations if v.severity in [
            AccessibilityViolationSeverity.CRITICAL, AccessibilityViolationSeverity.HIGH
        ]])
        warning_count = len([v for v in violations if v.severity == AccessibilityViolationSeverity.MEDIUM])
        info_count = len([v for v in violations if v.severity in [
            AccessibilityViolationSeverity.LOW, AccessibilityViolationSeverity.INFO
        ]])
        
        report = AccessibilityReport(
            report_id=report_id,
            title=title,
            target_standards=self.config.target_standards,
            violations=violations,
            pass_count=pass_count,
            fail_count=fail_count,
            warning_count=warning_count,
            info_count=info_count,
            total_elements_checked=total_elements_checked
        )
        
        self._save_report(report)
        logger.info(f"Generated report: {report_id} ({title})")
        
        return report
    
    def _save_report(self, report: AccessibilityReport) -> None:
        """Save a report to storage."""
        reports_dir = Path(self.config.reports_storage_path)
        reports_dir.mkdir(parents=True, exist_ok=True)
        file_path = reports_dir / f"{report.report_id}.json"
        
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(report.to_dict(), f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save report {report.report_id}: {str(e)}")
    
    def get_report(self, report_id: str) -> Optional[AccessibilityReport]:
        """Get a report by ID."""
        reports_dir = Path(self.config.reports_storage_path)
        file_path = reports_dir / f"{report_id}.json"
        
        if not file_path.exists():
            logger.error(f"Report not found: {report_id}")
            return None
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                report_data = json.load(f)
            
            return AccessibilityReport.from_dict(report_data)
        except Exception as e:
            logger.error(f"Failed to load report {report_id}: {str(e)}")
            return None
    
    def get_reports(self) -> List[AccessibilityReport]:
        """Get all reports."""
        reports = []
        reports_dir = Path(self.config.reports_storage_path)
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        for file_path in reports_dir.glob("*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    report_data = json.load(f)
                
                reports.append(AccessibilityReport.from_dict(report_data))
            except Exception as e:
                logger.error(f"Failed to load report from {file_path}: {str(e)}")
        
        # Sort by creation date (newest first)
        reports.sort(key=lambda r: r.created_at, reverse=True)
        
        return reports
    
    def export_report_to_html(self, report: AccessibilityReport, output_file: str) -> bool:
        """Export a report to HTML format."""
        try:
            # Simple HTML template
            html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Accessibility Report: {report.title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; color: #333; }}
        h1, h2, h3 {{ color: #2c3e50; }}
        .summary {{ display: flex; justify-content: space-between; margin-bottom: 20px; }}
        .summary-item {{ padding: 15px; border-radius: 5px; text-align: center; flex: 1; margin: 0 10px; }}
        .pass {{ background-color: #d4edda; color: #155724; }}
        .fail {{ background-color: #f8d7da; color: #721c24; }}
        .warning {{ background-color: #fff3cd; color: #856404; }}
        .info {{ background-color: #d1ecf1; color: #0c5460; }}
        table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
        th, td {{ padding: 12px 15px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #f8f9fa; }}
        tr:hover {{ background-color: #f1f1f1; }}
        .critical {{ color: #721c24; font-weight: bold; }}
        .high {{ color: #e74c3c; }}
        .medium {{ color: #f39c12; }}
        .low {{ color: #3498db; }}
        .info-severity {{ color: #2ecc71; }}
        .fixed {{ text-decoration: line-through; opacity: 0.7; }}
    </style>
</head>
<body>
    <h1>Accessibility Report: {report.title}</h1>
    <p>Generated on: {report.created_at.strftime('%Y-%m-%d %H:%M:%S')}</p>
    <p>Standards: {', '.join([std.value for std in report.target_standards])}</p>
    
    <div class="summary">
        <div class="summary-item pass">
            <h3>Pass</h3>
            <p>{report.pass_count}</p>
        </div>
        <div class="summary-item fail">
            <h3>Fail</h3>
            <p>{report.fail_count}</p>
        </div>
        <div class="summary-item warning">
            <h3>Warning</h3>
            <p>{report.warning_count}</p>
        </div>
        <div class="summary-item info">
            <h3>Info</h3>
            <p>{report.info_count}</p>
        </div>
    </div>
    
    <h2>Violations</h2>
    <table>
        <thead>
            <tr>
                <th>Type</th>
                <th>Severity</th>
                <th>Element</th>
                <th>Description</th>
                <th>Recommendation</th>
                <th>Status</th>
            </tr>
        </thead>
        <tbody>
"""
            
            # Add violations
            for violation in report.violations:
                severity_class = {
                    AccessibilityViolationSeverity.CRITICAL: "critical",
                    AccessibilityViolationSeverity.HIGH: "high",
                    AccessibilityViolationSeverity.MEDIUM: "medium",
                    AccessibilityViolationSeverity.LOW: "low",
                    AccessibilityViolationSeverity.INFO: "info-severity"
                }.get(violation.severity, "")
                
                fixed_class = "fixed" if violation.fixed else ""
                
                element_info = f"{violation.element_type}"
                if violation.element_id:
                    element_info += f" (ID: {violation.element_id})"
                if violation.element_role:
                    element_info += f" [Role: {violation.element_role.value}]"
                
                html += f"""
            <tr class="{fixed_class}">
                <td>{violation.type.value}</td>
                <td class="{severity_class}">{violation.severity.value}</td>
                <td>{element_info}</td>
                <td>{violation.description}</td>
                <td>{violation.recommendation}</td>
                <td>{"Fixed" if violation.fixed else "Open"}</td>
            </tr>"""
            
            html += """
        </tbody>
    </table>
</body>
</html>"""
            
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(html)
            
            logger.info(f"Exported report to HTML: {output_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to export report to HTML: {str(e)}")
            return False
    
    def export_report_to_csv(self, report: AccessibilityReport, output_file: str) -> bool:
        """Export a report to CSV format."""
        try:
            import csv
            
            with open(output_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                
                # Write header
                writer.writerow([
                    "Type", "Severity", "Standard", "Element Type", "Element ID", 
                    "Element Role", "Description", "Recommendation", "Fixed"
                ])
                
                # Write violations
                for violation in report.violations:
                    writer.writerow([
                        violation.type.value,
                        violation.severity.value,
                        violation.standard.value,
                        violation.element_type,
                        violation.element_id or "",
                        violation.element_role.value if violation.element_role else "",
                        violation.description,
                        violation.recommendation,
                        "Yes" if violation.fixed else "No"
                    ])
            
            logger.info(f"Exported report to CSV: {output_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to export report to CSV: {str(e)}")
            return False

class AccessibilitySystem:
    """Main accessibility system class."""
    
    _instance = None
    
    @classmethod
    def get_instance(cls) -> "AccessibilitySystem":
        """Get the singleton instance."""
        if cls._instance is None:
            cls._instance = AccessibilitySystem()
        return cls._instance
    
    def __init__(self):
        """Initialize the accessibility system."""
        self.config = AccessibilityConfig()
        self.checker = None
        self.violation_manager = None
        self.report_generator = None
        self._initialized = False
        self._lock = threading.RLock()
    
    def initialize(self, config_path: Optional[str] = None) -> None:
        """Initialize the system with configuration."""
        with self._lock:
            if self._initialized:
                return
            
            if config_path and Path(config_path).exists():
                try:
                    with open(config_path, "r") as f:
                        config_data = json.load(f)
                    self.config = AccessibilityConfig.from_dict(config_data)
                except Exception as e:
                    logger.error(f"Failed to load accessibility config from {config_path}: {str(e)}. Using defaults.")
                    self.config = AccessibilityConfig()
            else:
                logger.warning("Accessibility config file not found. Using defaults.")
                self.config = AccessibilityConfig()
            
            # Initialize components
            self.checker = AccessibilityChecker(self.config)
            self.violation_manager = ViolationManager(self.config)
            self.report_generator = ReportGenerator(self.config)
            
            self._initialized = True
            logger.info("Accessibility system initialized")
    
    def shutdown(self) -> None:
        """Shutdown the system."""
        with self._lock:
            if not self._initialized:
                return
            
            self._initialized = False
            logger.info("Accessibility system shutdown")
    
    def ensure_initialized(self) -> None:
        """Ensure the system is initialized."""
        if not self._initialized:
            self.initialize()
    
    def check_element(self, element: ElementAccessibilityAttributes) -> List[AccessibilityViolation]:
        """Check an element for accessibility violations."""
        self.ensure_initialized()
        
        violations = self.checker.check_element(element)
        
        # Add violations to manager
        for violation in violations:
            self.violation_manager.add_violation(violation)
        
        return violations
    
    def check_elements(self, elements: List[ElementAccessibilityAttributes]) -> List[AccessibilityViolation]:
        """Check multiple elements for accessibility violations."""
        self.ensure_initialized()
        
        all_violations = []
        for element in elements:
            violations = self.check_element(element)
            all_violations.extend(violations)
        
        return all_violations
    
    def generate_report(self, title: str, elements: List[ElementAccessibilityAttributes]) -> AccessibilityReport:
        """Generate an accessibility report for a set of elements."""
        self.ensure_initialized()
        
        violations = self.check_elements(elements)
        return self.report_generator.generate_report(title, violations, len(elements))
    
    def get_report(self, report_id: str) -> Optional[AccessibilityReport]:
        """Get a report by ID."""
        self.ensure_initialized()
        
        return self.report_generator.get_report(report_id)
    
    def get_reports(self) -> List[AccessibilityReport]:
        """Get all reports."""
        self.ensure_initialized()
        
        return self.report_generator.get_reports()
    
    def export_report_to_html(self, report_id: str, output_file: str) -> bool:
        """Export a report to HTML format."""
        self.ensure_initialized()
        
        report = self.get_report(report_id)
        if not report:
            return False
        
        return self.report_generator.export_report_to_html(report, output_file)
    
    def export_report_to_csv(self, report_id: str, output_file: str) -> bool:
        """Export a report to CSV format."""
        self.ensure_initialized()
        
        report = self.get_report(report_id)
        if not report:
            return False
        
        return self.report_generator.export_report_to_csv(report, output_file)
    
    def get_violations(self, fixed: Optional[bool] = None, 
                      type: Optional[AccessibilityViolationType] = None,
                      severity: Optional[AccessibilityViolationSeverity] = None,
                      standard: Optional[AccessibilityStandard] = None) -> List[AccessibilityViolation]:
        """Get violations filtered by criteria."""
        self.ensure_initialized()
        
        return self.violation_manager.get_violations(fixed, type, severity, standard)
    
    def mark_violation_as_fixed(self, violation_id: str) -> bool:
        """Mark a violation as fixed."""
        self.ensure_initialized()
        
        return self.violation_manager.mark_as_fixed(violation_id)
    
    def check_color_contrast(self, foreground_color: str, background_color: str, 
                           is_large_text: bool = False) -> Tuple[float, bool]:
        """Check color contrast ratio."""
        self.ensure_initialized()
        
        ratio = ColorContrastChecker.contrast_ratio(foreground_color, background_color)
        min_ratio = self.config.min_large_text_contrast_ratio if is_large_text else self.config.min_contrast_ratio
        passes = ratio >= min_ratio
        
        return ratio, passes
    
    def suggest_accessible_color(self, target_color: str, background_color: str, 
                               is_large_text: bool = False) -> str:
        """Suggest an accessible color that meets contrast requirements."""
        self.ensure_initialized()
        
        min_ratio = self.config.min_large_text_contrast_ratio if is_large_text else self.config.min_contrast_ratio
        return ColorContrastChecker.suggest_accessible_color(target_color, background_color, min_ratio)
    
    def simulate_color_blindness(self, color: str, color_blind_type: str) -> str:
        """Simulate how a color would appear to someone with color blindness."""
        self.ensure_initialized()
        
        return ColorContrastChecker.simulate_color_blindness(color, color_blind_type)
    
    def create_element_attributes(self, element_id: str, element_type: str, **kwargs) -> ElementAccessibilityAttributes:
        """Create accessibility attributes for an element."""
        return ElementAccessibilityAttributes(element_id=element_id, element_type=element_type, **kwargs)

# Global instance for easy access
accessibility_system = AccessibilitySystem.get_instance()

# --- Helper Functions --- #

def initialize_accessibility(config_path: Optional[str] = None) -> None:
    """Initialize the accessibility system."""
    accessibility_system.initialize(config_path)

def shutdown_accessibility() -> None:
    """Shutdown the accessibility system."""
    accessibility_system.shutdown()

def check_element_accessibility(element_id: str, element_type: str, **kwargs) -> List[AccessibilityViolation]:
    """Check accessibility for an element."""
    element = accessibility_system.create_element_attributes(element_id, element_type, **kwargs)
    return accessibility_system.check_element(element)

def check_color_contrast(foreground_color: str, background_color: str, is_large_text: bool = False) -> Tuple[float, bool]:
    """Check color contrast ratio."""
    return accessibility_system.check_color_contrast(foreground_color, background_color, is_large_text)

def suggest_accessible_color(target_color: str, background_color: str, is_large_text: bool = False) -> str:
    """Suggest an accessible color that meets contrast requirements."""
    return accessibility_system.suggest_accessible_color(target_color, background_color, is_large_text)

# Example usage
if __name__ == "__main__":
    # Initialize
    initialize_accessibility()
    
    # Check color contrast
    foreground = "#777777"
    background = "#FFFFFF"
    ratio, passes = check_color_contrast(foreground, background)
    print(f"Contrast ratio: {ratio:.2f}:1 - {'Passes' if passes else 'Fails'} WCAG 2.1 AA")
    
    if not passes:
        suggested_color = suggest_accessible_color(foreground, background)
        print(f"Suggested accessible color: {suggested_color}")
    
    # Check element accessibility
    violations = check_element_accessibility(
        element_id="header-logo",
        element_type="img",
        role=AccessibilityRole.IMG,
        has_alt_text=False,
        is_visible=True,
        is_enabled=True
    )
    
    for violation in violations:
        print(f"Violation: {violation.type.value} - {violation.description}")
        print(f"Recommendation: {violation.recommendation}")
    
    # Simulate color blindness
    original_color = "#FF0000"  # Red
    protanopia_color = accessibility_system.simulate_color_blindness(original_color, "protanopia")
    print(f"Original color: {original_color}, As seen with protanopia: {protanopia_color}")
    
    # Generate a report
    elements = [
        accessibility_system.create_element_attributes(
            element_id="header-logo",
            element_type="img",
            role=AccessibilityRole.IMG,
            has_alt_text=False,
            is_visible=True,
            is_enabled=True
        ),
        accessibility_system.create_element_attributes(
            element_id="submit-button",
            element_type="button",
            role=AccessibilityRole.BUTTON,
            has_aria_label=True,
            aria_label="Submit Form",
            is_focusable=True,
            is_visible=True,
            is_enabled=True,
            foreground_color="#FFFFFF",
            background_color="#0066CC"
        ),
        accessibility_system.create_element_attributes(
            element_id="terms-link",
            element_type="a",
            role=AccessibilityRole.LINK,
            has_aria_label=False,
            is_focusable=False,
            is_visible=True,
            is_enabled=True
        )
    ]
    
    report = accessibility_system.generate_report("Sample Accessibility Audit", elements)
    print(f"Report generated: {report.report_id}")
    print(f"Pass: {report.pass_count}, Fail: {report.fail_count}, Warning: {report.warning_count}, Info: {report.info_count}")
    
    # Export report
    accessibility_system.export_report_to_html(report.report_id, "accessibility_report.html")
    print("Report exported to accessibility_report.html")
    
    # Shutdown
    shutdown_accessibility()
