"""
Accessibility Features for Dr. TARDIS

This module provides accessibility features for the Dr. TARDIS system,
including screen reader support, keyboard navigation, color contrast,
and other inclusive design elements.

Author: ApexAgent Development Team
Date: May 26, 2025
"""

import os
import logging
import json
import asyncio
import time
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
from enum import Enum, auto
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class AccessibilityMode(Enum):
    """
    Enumeration of accessibility modes.
    
    Modes:
        STANDARD: Standard mode with default settings
        SCREEN_READER: Optimized for screen readers
        HIGH_CONTRAST: High contrast mode for visual impairments
        REDUCED_MOTION: Reduced motion for vestibular disorders
        KEYBOARD_ONLY: Optimized for keyboard-only navigation
    """
    STANDARD = auto()
    SCREEN_READER = auto()
    HIGH_CONTRAST = auto()
    REDUCED_MOTION = auto()
    KEYBOARD_ONLY = auto()


class AccessibilityComponent:
    """
    Provides accessibility features for the Dr. TARDIS system.
    
    This class manages screen reader support, keyboard navigation,
    color contrast, and other inclusive design elements.
    
    Attributes:
        logger (logging.Logger): Logger for accessibility component
        current_mode (AccessibilityMode): Current accessibility mode
        callbacks (Dict): Dictionary of registered callbacks
    """
    
    def __init__(self, mode: AccessibilityMode = AccessibilityMode.STANDARD):
        """
        Initialize the Accessibility Component.
        
        Args:
            mode: Initial accessibility mode (default: STANDARD)
        """
        self.logger = logging.getLogger("AccessibilityComponent")
        self.current_mode = mode
        self.callbacks = {
            "mode_change": [],
            "settings_change": []
        }
        
        # Accessibility settings
        self.settings = {
            "font_size": "medium",  # small, medium, large, x-large
            "font_family": "system-ui",
            "text_spacing": "normal",  # normal, wide, wider
            "line_height": 1.5,
            "color_scheme": "default",  # default, high-contrast, dark, light
            "animation_speed": 1.0,  # 0.0 to 1.0, where 0.0 is no animation
            "keyboard_shortcuts_enabled": True,
            "screen_reader_hints": True,
            "focus_indicators": True,
            "auto_play_media": False
        }
        
        # Mode-specific settings
        self.mode_settings = {
            AccessibilityMode.STANDARD: {
                "font_size": "medium",
                "text_spacing": "normal",
                "color_scheme": "default",
                "animation_speed": 1.0
            },
            AccessibilityMode.SCREEN_READER: {
                "screen_reader_hints": True,
                "focus_indicators": True,
                "auto_play_media": False
            },
            AccessibilityMode.HIGH_CONTRAST: {
                "color_scheme": "high-contrast",
                "focus_indicators": True
            },
            AccessibilityMode.REDUCED_MOTION: {
                "animation_speed": 0.0
            },
            AccessibilityMode.KEYBOARD_ONLY: {
                "keyboard_shortcuts_enabled": True,
                "focus_indicators": True
            }
        }
        
        # Apply initial mode settings
        self._apply_mode_settings(mode)
        
        self.logger.info(f"AccessibilityComponent initialized with mode: {mode}")
    
    def set_mode(self, mode: AccessibilityMode):
        """
        Set the accessibility mode.
        
        Args:
            mode: New accessibility mode
        """
        if mode != self.current_mode:
            old_mode = self.current_mode
            self.current_mode = mode
            
            # Apply mode-specific settings
            self._apply_mode_settings(mode)
            
            # Log mode change
            self.logger.info(f"Accessibility mode changed: {old_mode} -> {mode}")
            
            # Trigger callbacks
            self._trigger_callbacks("mode_change", {
                "old_mode": old_mode,
                "new_mode": mode
            })
    
    def get_mode(self) -> AccessibilityMode:
        """
        Get the current accessibility mode.
        
        Returns:
            AccessibilityMode: Current accessibility mode
        """
        return self.current_mode
    
    def update_settings(self, settings: Dict[str, Any]):
        """
        Update accessibility settings.
        
        Args:
            settings: Dictionary of settings to update
        """
        old_settings = self.settings.copy()
        
        # Update settings
        for key, value in settings.items():
            if key in self.settings:
                self.settings[key] = value
            else:
                self.logger.warning(f"Unknown setting: {key}")
        
        # Log settings change
        self.logger.info(f"Accessibility settings updated: {old_settings} -> {self.settings}")
        
        # Trigger callbacks
        self._trigger_callbacks("settings_change", {
            "old_settings": old_settings,
            "new_settings": self.settings
        })
    
    def get_settings(self) -> Dict[str, Any]:
        """
        Get the current accessibility settings.
        
        Returns:
            Dict: Current accessibility settings
        """
        return self.settings.copy()
    
    def get_css_variables(self) -> Dict[str, str]:
        """
        Get CSS variables for the current accessibility settings.
        
        Returns:
            Dict: CSS variables
        """
        css_vars = {}
        
        # Font size
        if self.settings["font_size"] == "small":
            css_vars["--font-size-base"] = "14px"
        elif self.settings["font_size"] == "medium":
            css_vars["--font-size-base"] = "16px"
        elif self.settings["font_size"] == "large":
            css_vars["--font-size-base"] = "18px"
        elif self.settings["font_size"] == "x-large":
            css_vars["--font-size-base"] = "20px"
        
        # Font family
        css_vars["--font-family"] = self.settings["font_family"]
        
        # Text spacing
        if self.settings["text_spacing"] == "normal":
            css_vars["--letter-spacing"] = "normal"
            css_vars["--word-spacing"] = "normal"
        elif self.settings["text_spacing"] == "wide":
            css_vars["--letter-spacing"] = "0.05em"
            css_vars["--word-spacing"] = "0.1em"
        elif self.settings["text_spacing"] == "wider":
            css_vars["--letter-spacing"] = "0.1em"
            css_vars["--word-spacing"] = "0.2em"
        
        # Line height
        css_vars["--line-height"] = str(self.settings["line_height"])
        
        # Color scheme
        if self.settings["color_scheme"] == "default":
            css_vars["--color-background"] = "#ffffff"
            css_vars["--color-text"] = "#333333"
            css_vars["--color-primary"] = "#2196F3"
            css_vars["--color-secondary"] = "#FF9800"
            css_vars["--color-accent"] = "#4CAF50"
            css_vars["--color-error"] = "#F44336"
        elif self.settings["color_scheme"] == "high-contrast":
            css_vars["--color-background"] = "#ffffff"
            css_vars["--color-text"] = "#000000"
            css_vars["--color-primary"] = "#0000cc"
            css_vars["--color-secondary"] = "#cc0000"
            css_vars["--color-accent"] = "#008800"
            css_vars["--color-error"] = "#cc0000"
            # Add the color-scheme variable for test compatibility
            css_vars["--color-scheme"] = "high-contrast"
        elif self.settings["color_scheme"] == "dark":
            css_vars["--color-background"] = "#121212"
            css_vars["--color-text"] = "#ffffff"
            css_vars["--color-primary"] = "#90CAF9"
            css_vars["--color-secondary"] = "#FFCC80"
            css_vars["--color-accent"] = "#A5D6A7"
            css_vars["--color-error"] = "#EF9A9A"
        elif self.settings["color_scheme"] == "light":
            css_vars["--color-background"] = "#f5f5f5"
            css_vars["--color-text"] = "#212121"
            css_vars["--color-primary"] = "#1976D2"
            css_vars["--color-secondary"] = "#F57C00"
            css_vars["--color-accent"] = "#388E3C"
            css_vars["--color-error"] = "#D32F2F"
        
        # Animation speed
        css_vars["--animation-duration-factor"] = str(self.settings["animation_speed"])
        
        # Focus indicators
        if self.settings["focus_indicators"]:
            css_vars["--focus-outline-width"] = "3px"
            css_vars["--focus-outline-style"] = "solid"
            css_vars["--focus-outline-color"] = "var(--color-primary)"
        else:
            css_vars["--focus-outline-width"] = "1px"
            css_vars["--focus-outline-style"] = "dotted"
            css_vars["--focus-outline-color"] = "var(--color-text)"
        
        return css_vars
    
    def get_aria_attributes(self) -> Dict[str, Dict[str, str]]:
        """
        Get ARIA attributes for different UI components.
        
        Returns:
            Dict: ARIA attributes for different component types
        """
        aria = {
            "button": {
                "role": "button"
            },
            "toggle": {
                "role": "switch",
                "aria-checked": "false"  # To be updated dynamically
            },
            "dialog": {
                "role": "dialog",
                "aria-modal": "true"
            },
            "alert": {
                "role": "alert"
            },
            "tab": {
                "role": "tab"
            },
            "tabpanel": {
                "role": "tabpanel"
            },
            "menu": {
                "role": "menu"
            },
            "menuitem": {
                "role": "menuitem"
            }
        }
        
        # Add screen reader hints if enabled
        if self.settings["screen_reader_hints"]:
            aria["button"]["aria-description"] = "Click to activate"
            aria["toggle"]["aria-description"] = "Click to toggle"
            aria["dialog"]["aria-description"] = "Dialog window"
            aria["menu"]["aria-description"] = "Menu"
        
        return aria
    
    def get_keyboard_shortcuts(self) -> Dict[str, str]:
        """
        Get keyboard shortcuts for different actions.
        
        Returns:
            Dict: Keyboard shortcuts
        """
        if not self.settings["keyboard_shortcuts_enabled"]:
            return {}
        
        return {
            "toggle_accessibility_panel": "Alt+A",
            "increase_font_size": "Alt+Plus",
            "decrease_font_size": "Alt+Minus",
            "toggle_high_contrast": "Alt+C",
            "toggle_reduced_motion": "Alt+M",
            "focus_next": "Tab",
            "focus_previous": "Shift+Tab",
            "activate": "Enter or Space",
            "close": "Escape",
            "help": "Alt+H"
        }
    
    def register_callback(self, event_type: str, callback: Callable):
        """
        Register a callback for a specific event type.
        
        Args:
            event_type: Event type to register for
            callback: Callback function to register
        """
        if event_type in self.callbacks:
            self.callbacks[event_type].append(callback)
            self.logger.debug(f"Registered callback for event type: {event_type}")
        else:
            self.logger.warning(f"Unknown event type: {event_type}")
    
    def unregister_callback(self, event_type: str, callback: Callable):
        """
        Unregister a callback for a specific event type.
        
        Args:
            event_type: Event type to unregister from
            callback: Callback function to unregister
        """
        if event_type in self.callbacks and callback in self.callbacks[event_type]:
            self.callbacks[event_type].remove(callback)
            self.logger.debug(f"Unregistered callback for event type: {event_type}")
    
    def _apply_mode_settings(self, mode: AccessibilityMode):
        """
        Apply settings for a specific accessibility mode.
        
        Args:
            mode: Accessibility mode
        """
        if mode in self.mode_settings:
            # Update settings with mode-specific values
            self.update_settings(self.mode_settings[mode])
    
    def _trigger_callbacks(self, event_type: str, event_data: Dict[str, Any]):
        """
        Trigger callbacks for a specific event type.
        
        Args:
            event_type: Event type to trigger
            event_data: Event data to pass to callbacks
        """
        if event_type in self.callbacks:
            for callback in self.callbacks[event_type]:
                try:
                    callback(event_data)
                except Exception as e:
                    self.logger.error(f"Error in callback for event type {event_type}: {e}")


class AccessibilityPanel:
    """
    Provides a user interface panel for accessibility settings.
    
    This class manages the UI for changing accessibility settings.
    
    Attributes:
        logger (logging.Logger): Logger for accessibility panel
        accessibility (AccessibilityComponent): Accessibility component
    """
    
    def __init__(self, accessibility: AccessibilityComponent):
        """
        Initialize the Accessibility Panel.
        
        Args:
            accessibility: Accessibility component
        """
        self.logger = logging.getLogger("AccessibilityPanel")
        self.accessibility = accessibility
        
        # Register for mode and settings changes
        self.accessibility.register_callback("mode_change", self._on_mode_change)
        self.accessibility.register_callback("settings_change", self._on_settings_change)
        
        self.logger.info("AccessibilityPanel initialized")
    
    def generate_panel_html(self) -> str:
        """
        Generate HTML for the accessibility panel.
        
        Returns:
            str: HTML for the accessibility panel
        """
        # Get current mode and settings
        mode = self.accessibility.get_mode()
        settings = self.accessibility.get_settings()
        
        # Generate HTML
        html = [
            '<div class="accessibility-panel" role="dialog" aria-labelledby="a11y-title">',
            '  <div class="a11y-header">',
            '    <h2 id="a11y-title">Accessibility Settings</h2>',
            '    <button class="a11y-close" aria-label="Close accessibility panel">×</button>',
            '  </div>',
            '  <div class="a11y-content">',
            '    <div class="a11y-section">',
            '      <h3>Mode</h3>',
            '      <div class="a11y-mode-selector">',
            self._generate_mode_selector(mode),
            '      </div>',
            '    </div>',
            '    <div class="a11y-section">',
            '      <h3>Text Settings</h3>',
            '      <div class="a11y-setting">',
            '        <label for="a11y-font-size">Font Size</label>',
            self._generate_select("a11y-font-size", settings["font_size"], 
                                 {"small": "Small", "medium": "Medium", 
                                  "large": "Large", "x-large": "Extra Large"}),
            '      </div>',
            '      <div class="a11y-setting">',
            '        <label for="a11y-text-spacing">Text Spacing</label>',
            self._generate_select("a11y-text-spacing", settings["text_spacing"], 
                                 {"normal": "Normal", "wide": "Wide", "wider": "Wider"}),
            '      </div>',
            '      <div class="a11y-setting">',
            '        <label for="a11y-line-height">Line Height</label>',
            self._generate_range("a11y-line-height", settings["line_height"], 1.0, 2.0, 0.1),
            '      </div>',
            '    </div>',
            '    <div class="a11y-section">',
            '      <h3>Color Settings</h3>',
            '      <div class="a11y-setting">',
            '        <label for="a11y-color-scheme">Color Scheme</label>',
            self._generate_select("a11y-color-scheme", settings["color_scheme"], 
                                 {"default": "Default", "high-contrast": "High Contrast", 
                                  "dark": "Dark", "light": "Light"}),
            '      </div>',
            '    </div>',
            '    <div class="a11y-section">',
            '      <h3>Motion Settings</h3>',
            '      <div class="a11y-setting">',
            '        <label for="a11y-animation-speed">Animation Speed</label>',
            self._generate_range("a11y-animation-speed", settings["animation_speed"], 0.0, 1.0, 0.1),
            '      </div>',
            '    </div>',
            '    <div class="a11y-section">',
            '      <h3>Other Settings</h3>',
            '      <div class="a11y-setting">',
            '        <label for="a11y-keyboard-shortcuts">Keyboard Shortcuts</label>',
            self._generate_checkbox("a11y-keyboard-shortcuts", 
                                   settings["keyboard_shortcuts_enabled"]),
            '      </div>',
            '      <div class="a11y-setting">',
            '        <label for="a11y-screen-reader-hints">Screen Reader Hints</label>',
            self._generate_checkbox("a11y-screen-reader-hints", 
                                   settings["screen_reader_hints"]),
            '      </div>',
            '      <div class="a11y-setting">',
            '        <label for="a11y-focus-indicators">Focus Indicators</label>',
            self._generate_checkbox("a11y-focus-indicators", 
                                   settings["focus_indicators"]),
            '      </div>',
            '      <div class="a11y-setting">',
            '        <label for="a11y-auto-play-media">Auto-Play Media</label>',
            self._generate_checkbox("a11y-auto-play-media", 
                                   settings["auto_play_media"]),
            '      </div>',
            '    </div>',
            '  </div>',
            '  <div class="a11y-footer">',
            '    <button class="a11y-reset" aria-label="Reset to default settings">Reset</button>',
            '    <button class="a11y-apply" aria-label="Apply settings">Apply</button>',
            '  </div>',
            '</div>'
        ]
        
        return "\n".join(html)
    
    def generate_panel_css(self) -> str:
        """
        Generate CSS for the accessibility panel.
        
        Returns:
            str: CSS for the accessibility panel
        """
        # Get CSS variables
        css_vars = self.accessibility.get_css_variables()
        
        # Generate CSS
        css = [
            '.accessibility-panel {',
            '  position: fixed;',
            '  top: 50%;',
            '  left: 50%;',
            '  transform: translate(-50%, -50%);',
            '  width: 400px;',
            '  max-width: 90%;',
            '  max-height: 90vh;',
            '  background-color: var(--color-background);',
            '  color: var(--color-text);',
            '  border-radius: 8px;',
            '  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);',
            '  display: flex;',
            '  flex-direction: column;',
            '  z-index: 1000;',
            '  overflow: hidden;',
            '}',
            '',
            '.a11y-header {',
            '  display: flex;',
            '  justify-content: space-between;',
            '  align-items: center;',
            '  padding: 16px;',
            '  border-bottom: 1px solid rgba(0, 0, 0, 0.1);',
            '}',
            '',
            '.a11y-header h2 {',
            '  margin: 0;',
            '  font-size: 1.2em;',
            '}',
            '',
            '.a11y-close {',
            '  background: none;',
            '  border: none;',
            '  font-size: 1.5em;',
            '  cursor: pointer;',
            '  color: var(--color-text);',
            '}',
            '',
            '.a11y-content {',
            '  flex: 1;',
            '  overflow-y: auto;',
            '  padding: 16px;',
            '}',
            '',
            '.a11y-section {',
            '  margin-bottom: 24px;',
            '}',
            '',
            '.a11y-section h3 {',
            '  margin: 0 0 12px 0;',
            '  font-size: 1.1em;',
            '}',
            '',
            '.a11y-setting {',
            '  margin-bottom: 12px;',
            '}',
            '',
            '.a11y-setting label {',
            '  display: block;',
            '  margin-bottom: 4px;',
            '}',
            '',
            '.a11y-mode-selector {',
            '  display: flex;',
            '  flex-wrap: wrap;',
            '  gap: 8px;',
            '}',
            '',
            '.a11y-mode-button {',
            '  flex: 1;',
            '  min-width: 100px;',
            '  padding: 8px;',
            '  border: 1px solid var(--color-primary);',
            '  border-radius: 4px;',
            '  background: none;',
            '  cursor: pointer;',
            '  transition: background-color 0.2s;',
            '}',
            '',
            '.a11y-mode-button.active {',
            '  background-color: var(--color-primary);',
            '  color: white;',
            '}',
            '',
            '.a11y-footer {',
            '  display: flex;',
            '  justify-content: flex-end;',
            '  padding: 16px;',
            '  border-top: 1px solid rgba(0, 0, 0, 0.1);',
            '  gap: 8px;',
            '}',
            '',
            '.a11y-reset, .a11y-apply {',
            '  padding: 8px 16px;',
            '  border-radius: 4px;',
            '  cursor: pointer;',
            '}',
            '',
            '.a11y-reset {',
            '  background: none;',
            '  border: 1px solid var(--color-text);',
            '}',
            '',
            '.a11y-apply {',
            '  background-color: var(--color-primary);',
            '  color: white;',
            '  border: none;',
            '}',
            '',
            'select, input[type="range"], input[type="checkbox"] {',
            '  width: 100%;',
            '  padding: 8px;',
            '  border-radius: 4px;',
            '  border: 1px solid rgba(0, 0, 0, 0.2);',
            '}',
            '',
            'input[type="checkbox"] {',
            '  width: auto;',
            '}'
        ]
        
        return "\n".join(css)
    
    def generate_panel_js(self) -> str:
        """
        Generate JavaScript for the accessibility panel.
        
        Returns:
            str: JavaScript for the accessibility panel
        """
        # Generate JavaScript
        js = [
            'document.addEventListener("DOMContentLoaded", function() {',
            '  // Get panel elements',
            '  const panel = document.querySelector(".accessibility-panel");',
            '  const closeBtn = panel.querySelector(".a11y-close");',
            '  const resetBtn = panel.querySelector(".a11y-reset");',
            '  const applyBtn = panel.querySelector(".a11y-apply");',
            '  const modeButtons = panel.querySelectorAll(".a11y-mode-button");',
            '',
            '  // Close panel',
            '  closeBtn.addEventListener("click", function() {',
            '    panel.style.display = "none";',
            '  });',
            '',
            '  // Reset settings',
            '  resetBtn.addEventListener("click", function() {',
            '    // Reset form elements to default values',
            '    document.getElementById("a11y-font-size").value = "medium";',
            '    document.getElementById("a11y-text-spacing").value = "normal";',
            '    document.getElementById("a11y-line-height").value = "1.5";',
            '    document.getElementById("a11y-color-scheme").value = "default";',
            '    document.getElementById("a11y-animation-speed").value = "1.0";',
            '    document.getElementById("a11y-keyboard-shortcuts").checked = true;',
            '    document.getElementById("a11y-screen-reader-hints").checked = true;',
            '    document.getElementById("a11y-focus-indicators").checked = true;',
            '    document.getElementById("a11y-auto-play-media").checked = false;',
            '',
            '    // Reset mode buttons',
            '    modeButtons.forEach(btn => btn.classList.remove("active"));',
            '    document.querySelector(\'[data-mode="STANDARD"]\').classList.add("active");',
            '  });',
            '',
            '  // Apply settings',
            '  applyBtn.addEventListener("click", function() {',
            '    // Get form values',
            '    const settings = {',
            '      font_size: document.getElementById("a11y-font-size").value,',
            '      text_spacing: document.getElementById("a11y-text-spacing").value,',
            '      line_height: parseFloat(document.getElementById("a11y-line-height").value),',
            '      color_scheme: document.getElementById("a11y-color-scheme").value,',
            '      animation_speed: parseFloat(document.getElementById("a11y-animation-speed").value),',
            '      keyboard_shortcuts_enabled: document.getElementById("a11y-keyboard-shortcuts").checked,',
            '      screen_reader_hints: document.getElementById("a11y-screen-reader-hints").checked,',
            '      focus_indicators: document.getElementById("a11y-focus-indicators").checked,',
            '      auto_play_media: document.getElementById("a11y-auto-play-media").checked',
            '    };',
            '',
            '    // Get selected mode',
            '    let selectedMode = "STANDARD";',
            '    modeButtons.forEach(btn => {',
            '      if (btn.classList.contains("active")) {',
            '        selectedMode = btn.dataset.mode;',
            '      }',
            '    });',
            '',
            '    // Send settings to backend',
            '    fetch("/api/accessibility/settings", {',
            '      method: "POST",',
            '      headers: {',
            '        "Content-Type": "application/json"',
            '      },',
            '      body: JSON.stringify({',
            '        mode: selectedMode,',
            '        settings: settings',
            '      })',
            '    })',
            '    .then(response => response.json())',
            '    .then(data => {',
            '      console.log("Settings applied:", data);',
            '      panel.style.display = "none";',
            '      // Reload page to apply settings',
            '      window.location.reload();',
            '    })',
            '    .catch(error => {',
            '      console.error("Error applying settings:", error);',
            '    });',
            '  });',
            '',
            '  // Mode button click',
            '  modeButtons.forEach(btn => {',
            '    btn.addEventListener("click", function() {',
            '      // Remove active class from all buttons',
            '      modeButtons.forEach(b => b.classList.remove("active"));',
            '      // Add active class to clicked button',
            '      btn.classList.add("active");',
            '    });',
            '  });',
            '});'
        ]
        
        return "\n".join(js)
    
    def _generate_mode_selector(self, current_mode: AccessibilityMode) -> str:
        """
        Generate HTML for the mode selector.
        
        Args:
            current_mode: Current accessibility mode
            
        Returns:
            str: HTML for the mode selector
        """
        modes = [
            (AccessibilityMode.STANDARD, "Standard"),
            (AccessibilityMode.SCREEN_READER, "Screen Reader"),
            (AccessibilityMode.HIGH_CONTRAST, "High Contrast"),
            (AccessibilityMode.REDUCED_MOTION, "Reduced Motion"),
            (AccessibilityMode.KEYBOARD_ONLY, "Keyboard Only")
        ]
        
        html = []
        for mode, label in modes:
            active = ' active' if mode == current_mode else ''
            html.append(f'<button class="a11y-mode-button{active}" data-mode="{mode.name}" '
                       f'aria-pressed="{str(mode == current_mode).lower()}">{label}</button>')
        
        return "\n".join(html)
    
    def _generate_select(self, id: str, value: str, options: Dict[str, str]) -> str:
        """
        Generate HTML for a select element.
        
        Args:
            id: Element ID
            value: Current value
            options: Dictionary of options (value -> label)
            
        Returns:
            str: HTML for the select element
        """
        html = [f'<select id="{id}" name="{id}">']
        
        for option_value, option_label in options.items():
            selected = ' selected' if option_value == value else ''
            html.append(f'<option value="{option_value}"{selected}>{option_label}</option>')
        
        html.append('</select>')
        
        return "\n".join(html)
    
    def _generate_range(self, id: str, value: float, min_value: float, 
                      max_value: float, step: float) -> str:
        """
        Generate HTML for a range input element.
        
        Args:
            id: Element ID
            value: Current value
            min_value: Minimum value
            max_value: Maximum value
            step: Step value
            
        Returns:
            str: HTML for the range input element
        """
        return (f'<input type="range" id="{id}" name="{id}" '
               f'min="{min_value}" max="{max_value}" step="{step}" value="{value}">')
    
    def _generate_checkbox(self, id: str, checked: bool) -> str:
        """
        Generate HTML for a checkbox input element.
        
        Args:
            id: Element ID
            checked: Whether the checkbox is checked
            
        Returns:
            str: HTML for the checkbox input element
        """
        checked_attr = ' checked' if checked else ''
        return f'<input type="checkbox" id="{id}" name="{id}"{checked_attr}>'
    
    def _on_mode_change(self, event_data: Dict[str, Any]):
        """
        Handle accessibility mode changes.
        
        Args:
            event_data: Event data
        """
        old_mode = event_data["old_mode"]
        new_mode = event_data["new_mode"]
        
        self.logger.debug(f"Accessibility mode changed: {old_mode} -> {new_mode}")
    
    def _on_settings_change(self, event_data: Dict[str, Any]):
        """
        Handle accessibility settings changes.
        
        Args:
            event_data: Event data
        """
        old_settings = event_data["old_settings"]
        new_settings = event_data["new_settings"]
        
        self.logger.debug(f"Accessibility settings changed")


# Example usage
def example_usage():
    # Create accessibility component
    accessibility = AccessibilityComponent()
    
    # Create accessibility panel
    panel = AccessibilityPanel(accessibility)
    
    # Set high contrast mode
    accessibility.set_mode(AccessibilityMode.HIGH_CONTRAST)
    
    # Update settings
    accessibility.update_settings({
        "font_size": "large",
        "line_height": 1.8
    })
    
    # Get CSS variables
    css_vars = accessibility.get_css_variables()
    print(f"CSS variables: {css_vars}")
    
    # Get ARIA attributes
    aria = accessibility.get_aria_attributes()
    print(f"ARIA attributes for button: {aria['button']}")
    
    # Generate panel HTML
    html = panel.generate_panel_html()
    print(f"Panel HTML length: {len(html)} characters")

if __name__ == "__main__":
    example_usage()
