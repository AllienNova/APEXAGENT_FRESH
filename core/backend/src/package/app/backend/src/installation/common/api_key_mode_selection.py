"""
Setup Wizard UI Component for API Key Mode Selection.

This module provides the UI component for selecting between Complete System
and User-Provided API Keys during the ApexAgent installation process.
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, font
from PIL import Image, ImageTk
import json
from typing import Callable, Dict, Any, Optional

# Import configuration
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from installation.common.config import ApiKeyMode, API_KEY_MODE_INFO

class ApiKeyModeSelectionFrame(ttk.Frame):
    """
    Frame for selecting the API Key Mode during installation.
    
    This component presents users with a choice between Complete System
    (ApexAgent-provided API keys) and User-Provided API Keys, with
    clear explanations of each option.
    """
    
    def __init__(self, parent, callback: Callable[[ApiKeyMode], None], 
                 initial_mode: ApiKeyMode = ApiKeyMode.COMPLETE_SYSTEM,
                 **kwargs):
        """
        Initialize the API Key Mode selection frame.
        
        Args:
            parent: Parent widget
            callback: Function to call when a mode is selected
            initial_mode: Initially selected mode
            **kwargs: Additional arguments to pass to ttk.Frame
        """
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.callback = callback
        self.selected_mode = initial_mode
        
        # Configure styles
        self._configure_styles()
        
        # Create widgets
        self._create_widgets()
        
        # Set initial selection
        self._set_selection(initial_mode)
    
    def _configure_styles(self):
        """Configure custom styles for the frame."""
        self.style = ttk.Style()
        
        # Configure heading style
        default_font = font.nametofont("TkDefaultFont")
        heading_font = font.Font(
            family=default_font.cget("family"),
            size=default_font.cget("size") + 4,
            weight="bold"
        )
        self.style.configure("Heading.TLabel", font=heading_font)
        
        # Configure subheading style
        subheading_font = font.Font(
            family=default_font.cget("family"),
            size=default_font.cget("size") + 2,
            weight="bold"
        )
        self.style.configure("Subheading.TLabel", font=subheading_font)
        
        # Configure option frame style
        self.style.configure("Option.TFrame", padding=10, relief="solid", borderwidth=1)
        self.style.configure("SelectedOption.TFrame", padding=10, relief="solid", borderwidth=2)
        
        # Configure benefit list style
        self.style.configure("Benefit.TLabel", padding=(20, 2, 0, 2))
    
    def _create_widgets(self):
        """Create and arrange widgets in the frame."""
        # Main container with padding
        main_container = ttk.Frame(self, padding=20)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Heading
        heading = ttk.Label(
            main_container, 
            text="Choose Your API Key Mode",
            style="Heading.TLabel"
        )
        heading.pack(pady=(0, 20), anchor=tk.W)
        
        # Description
        description = ttk.Label(
            main_container,
            text="ApexAgent offers two ways to access AI models. Choose the option that best fits your needs:",
            wraplength=600,
            justify=tk.LEFT
        )
        description.pack(pady=(0, 20), anchor=tk.W)
        
        # Options container (horizontal layout)
        options_container = ttk.Frame(main_container)
        options_container.pack(fill=tk.BOTH, expand=True, pady=10)
        options_container.columnconfigure(0, weight=1)
        options_container.columnconfigure(1, weight=1)
        
        # Create option frames
        self.option_frames = {}
        self.option_vars = {}
        
        # Complete System option
        self.option_frames[ApiKeyMode.COMPLETE_SYSTEM] = self._create_option_frame(
            options_container,
            ApiKeyMode.COMPLETE_SYSTEM,
            0  # Grid column 0
        )
        
        # User-Provided option
        self.option_frames[ApiKeyMode.USER_PROVIDED] = self._create_option_frame(
            options_container,
            ApiKeyMode.USER_PROVIDED,
            1  # Grid column 1
        )
        
        # Comparison table
        comparison_label = ttk.Label(
            main_container,
            text="Pricing Comparison:",
            style="Subheading.TLabel"
        )
        comparison_label.pack(pady=(20, 10), anchor=tk.W)
        
        # Create comparison table
        self._create_comparison_table(main_container)
        
        # Note about changing later
        note_label = ttk.Label(
            main_container,
            text="Note: You can change this selection later in the ApexAgent settings.",
            font=("TkDefaultFont", 9, "italic")
        )
        note_label.pack(pady=(20, 0), anchor=tk.W)
    
    def _create_option_frame(self, parent, mode: ApiKeyMode, column: int) -> ttk.Frame:
        """
        Create a frame for an API key mode option.
        
        Args:
            parent: Parent widget
            mode: API key mode
            column: Grid column for placement
            
        Returns:
            ttk.Frame: The created option frame
        """
        # Get mode info
        mode_info = API_KEY_MODE_INFO[mode]
        
        # Create frame
        frame = ttk.Frame(parent, style="Option.TFrame")
        frame.grid(row=0, column=column, padx=10, pady=10, sticky="nsew")
        
        # Make the frame clickable
        frame.bind("<Button-1>", lambda e, m=mode: self._on_option_click(m))
        
        # Radio button for selection
        var = tk.BooleanVar(value=False)
        self.option_vars[mode] = var
        radio = ttk.Radiobutton(
            frame,
            text="",
            variable=var,
            value=True,
            command=lambda m=mode: self._on_option_click(m)
        )
        radio.pack(anchor=tk.W, pady=(0, 5))
        
        # Title
        title = ttk.Label(
            frame,
            text=mode_info["title"],
            style="Subheading.TLabel"
        )
        title.pack(anchor=tk.W, pady=(0, 5))
        
        # Description
        description = ttk.Label(
            frame,
            text=mode_info["description"],
            wraplength=250,
            justify=tk.LEFT
        )
        description.pack(anchor=tk.W, pady=(0, 10))
        
        # Benefits heading
        benefits_heading = ttk.Label(
            frame,
            text="Benefits:",
            font=("TkDefaultFont", 10, "bold")
        )
        benefits_heading.pack(anchor=tk.W, pady=(0, 5))
        
        # Benefits list
        for benefit in mode_info["benefits"]:
            benefit_label = ttk.Label(
                frame,
                text=f"• {benefit}",
                wraplength=250,
                justify=tk.LEFT,
                style="Benefit.TLabel"
            )
            benefit_label.pack(anchor=tk.W, pady=(0, 3))
        
        # Ideal for heading
        ideal_heading = ttk.Label(
            frame,
            text="Ideal for:",
            font=("TkDefaultFont", 10, "bold")
        )
        ideal_heading.pack(anchor=tk.W, pady=(10, 5))
        
        # Ideal for list
        for ideal in mode_info["ideal_for"]:
            ideal_label = ttk.Label(
                frame,
                text=f"• {ideal}",
                wraplength=250,
                justify=tk.LEFT,
                style="Benefit.TLabel"
            )
            ideal_label.pack(anchor=tk.W, pady=(0, 3))
        
        # Make all child widgets clickable too
        for child in frame.winfo_children():
            child.bind("<Button-1>", lambda e, m=mode: self._on_option_click(m))
        
        return frame
    
    def _create_comparison_table(self, parent):
        """
        Create a pricing comparison table.
        
        Args:
            parent: Parent widget
        """
        # Create frame for table
        table_frame = ttk.Frame(parent)
        table_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Table headers
        headers = ["Tier", "Complete System", "User-Provided API Keys", "Monthly Savings"]
        for i, header in enumerate(headers):
            label = ttk.Label(
                table_frame,
                text=header,
                font=("TkDefaultFont", 10, "bold"),
                anchor=tk.CENTER
            )
            label.grid(row=0, column=i, padx=5, pady=5, sticky="ew")
        
        # Table data
        data = [
            ["Basic", "$24.99/month", "$19.99/month", "$5.00 (20%)"],
            ["Pro", "$89.99/month", "$49.99/month", "$40.00 (44%)"],
            ["Expert", "$149.99/month", "$99.99/month", "$50.00 (33%)"],
            ["Enterprise", "Custom pricing", "Custom pricing", "Varies"]
        ]
        
        for i, row in enumerate(data):
            for j, cell in enumerate(row):
                label = ttk.Label(
                    table_frame,
                    text=cell,
                    anchor=tk.CENTER
                )
                label.grid(row=i+1, column=j, padx=5, pady=5, sticky="ew")
        
        # Configure column weights
        for i in range(len(headers)):
            table_frame.columnconfigure(i, weight=1)
    
    def _on_option_click(self, mode: ApiKeyMode):
        """
        Handle option selection.
        
        Args:
            mode: Selected API key mode
        """
        self._set_selection(mode)
        self.callback(mode)
    
    def _set_selection(self, mode: ApiKeyMode):
        """
        Set the selected option.
        
        Args:
            mode: API key mode to select
        """
        self.selected_mode = mode
        
        # Update radio buttons
        for m, var in self.option_vars.items():
            var.set(m == mode)
        
        # Update frame styles
        for m, frame in self.option_frames.items():
            if m == mode:
                frame.configure(style="SelectedOption.TFrame")
            else:
                frame.configure(style="Option.TFrame")
    
    def get_selected_mode(self) -> ApiKeyMode:
        """
        Get the currently selected API key mode.
        
        Returns:
            ApiKeyMode: The selected mode
        """
        return self.selected_mode


# For testing purposes
if __name__ == "__main__":
    root = tk.Tk()
    root.title("API Key Mode Selection")
    root.geometry("800x600")
    
    def on_mode_selected(mode):
        print(f"Selected mode: {mode.value}")
    
    frame = ApiKeyModeSelectionFrame(root, on_mode_selected)
    frame.pack(fill=tk.BOTH, expand=True)
    
    root.mainloop()
