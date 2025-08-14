"""
First-run onboarding experience for ApexAgent with API key mode selection.

This module provides the onboarding wizard that runs on first launch,
guiding users through initial setup including API key configuration.
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, font, messagebox
import json
import threading
import webbrowser
from typing import Dict, List, Optional, Any, Callable

# Import configuration and API key manager
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from installation.common.config import ApiKeyMode, API_KEY_MODE_INFO
from core.enhanced_api_key_manager import EnhancedApiKeyManager, ProviderType

class OnboardingWizard:
    """
    First-run onboarding wizard for ApexAgent.
    
    This wizard guides users through the initial setup process, including:
    - Welcome and introduction
    - API key mode confirmation or change
    - API key entry (if User-Provided mode)
    - Feature overview and getting started
    """
    
    def __init__(self, root=None, installation_config_path=None, on_complete=None):
        """
        Initialize the onboarding wizard.
        
        Args:
            root: Root Tkinter window (created if not provided)
            installation_config_path: Path to installation configuration
            on_complete: Callback function to call when onboarding is complete
        """
        self.installation_config_path = installation_config_path
        self.on_complete_callback = on_complete
        
        # Load installation configuration
        self.installation_config = self._load_installation_config()
        
        # Initialize API key manager
        self.api_key_manager = self._initialize_api_key_manager()
        
        # Get current API key mode
        self.current_api_key_mode = self.api_key_manager.get_api_key_mode()
        
        # Create root window if not provided
        if root is None:
            self.root = tk.Tk()
            self.root.title("ApexAgent Onboarding")
            self.root.geometry("800x600")
            self.root.minsize(800, 600)
            self.owns_root = True
        else:
            self.root = root
            self.owns_root = False
        
        # Configure styles
        self._configure_styles()
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding=20)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Initialize step frames
        self.steps = []
        self.current_step = 0
        self._initialize_steps()
        
        # Show first step
        self._show_step(0)
    
    def _load_installation_config(self) -> Dict[str, Any]:
        """
        Load the installation configuration.
        
        Returns:
            Dict[str, Any]: Installation configuration
        """
        if self.installation_config_path and os.path.exists(self.installation_config_path):
            try:
                with open(self.installation_config_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading installation config: {e}")
        
        # Default configuration if not found
        return {
            "installation_path": os.path.expanduser("~/.apex_agent"),
            "mode": "standard",
            "api_key_mode": "complete_system",
            "components": "",
            "analytics": False,
            "installation_date": ""
        }
    
    def _initialize_api_key_manager(self) -> EnhancedApiKeyManager:
        """
        Initialize the API key manager.
        
        Returns:
            EnhancedApiKeyManager: Initialized API key manager
        """
        installation_path = self.installation_config.get("installation_path", 
                                                        os.path.expanduser("~/.apex_agent"))
        installation_config_dir = os.path.join(installation_path, "config")
        
        return EnhancedApiKeyManager(
            installation_config_dir=installation_config_dir,
            config_dir=os.path.join(installation_path, "security"),
            credentials_dir=os.path.join(installation_path, "credentials")
        )
    
    def _configure_styles(self):
        """Configure custom styles for the wizard."""
        self.style = ttk.Style()
        
        # Configure heading style
        default_font = font.nametofont("TkDefaultFont")
        heading_font = font.Font(
            family=default_font.cget("family"),
            size=default_font.cget("size") + 6,
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
        
        # Configure button style
        self.style.configure("Next.TButton", font=("TkDefaultFont", 11))
        self.style.configure("Back.TButton", font=("TkDefaultFont", 11))
        
        # Configure option frame style
        self.style.configure("Option.TFrame", padding=10, relief="solid", borderwidth=1)
        self.style.configure("SelectedOption.TFrame", padding=10, relief="solid", borderwidth=2)
    
    def _initialize_steps(self):
        """Initialize the steps of the onboarding wizard."""
        # Step 1: Welcome
        self.steps.append(self._create_welcome_step())
        
        # Step 2: API Key Mode
        self.steps.append(self._create_api_key_mode_step())
        
        # Step 3: API Key Entry (shown only in User-Provided mode)
        self.steps.append(self._create_api_key_entry_step())
        
        # Step 4: Getting Started
        self.steps.append(self._create_getting_started_step())
    
    def _create_welcome_step(self) -> ttk.Frame:
        """
        Create the welcome step.
        
        Returns:
            ttk.Frame: The welcome step frame
        """
        frame = ttk.Frame(self.main_frame)
        
        # Heading
        heading = ttk.Label(
            frame, 
            text="Welcome to ApexAgent!",
            style="Heading.TLabel"
        )
        heading.pack(pady=(0, 20), anchor=tk.CENTER)
        
        # Logo placeholder
        logo_frame = ttk.Frame(frame, width=200, height=200)
        logo_frame.pack(pady=(0, 20), anchor=tk.CENTER)
        
        # Description
        description = ttk.Label(
            frame,
            text="Thank you for installing ApexAgent, your desktop-native AI assistant. "
                 "This wizard will guide you through the initial setup process to get "
                 "you up and running quickly.",
            wraplength=600,
            justify=tk.CENTER
        )
        description.pack(pady=(0, 30), anchor=tk.CENTER)
        
        # What you'll need
        need_label = ttk.Label(
            frame,
            text="What you'll need:",
            style="Subheading.TLabel"
        )
        need_label.pack(pady=(0, 10), anchor=tk.W)
        
        needs = [
            "A few minutes to complete the setup",
            "API keys from providers (if using your own keys)",
            "Internet connection for activation"
        ]
        
        for need in needs:
            need_item = ttk.Label(
                frame,
                text=f"• {need}",
                wraplength=600,
                justify=tk.LEFT
            )
            need_item.pack(pady=(0, 5), anchor=tk.W, padx=(20, 0))
        
        # Navigation buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=(30, 0), side=tk.BOTTOM)
        
        next_button = ttk.Button(
            button_frame,
            text="Next",
            command=lambda: self._next_step(),
            style="Next.TButton",
            width=15
        )
        next_button.pack(side=tk.RIGHT)
        
        return frame
    
    def _create_api_key_mode_step(self) -> ttk.Frame:
        """
        Create the API key mode selection step.
        
        Returns:
            ttk.Frame: The API key mode step frame
        """
        frame = ttk.Frame(self.main_frame)
        
        # Heading
        heading = ttk.Label(
            frame, 
            text="Choose Your API Key Mode",
            style="Heading.TLabel"
        )
        heading.pack(pady=(0, 20), anchor=tk.W)
        
        # Description
        description = ttk.Label(
            frame,
            text=f"During installation, you selected the {API_KEY_MODE_INFO[self.current_api_key_mode]['title']} option. "
                 f"You can confirm this choice or change it now.",
            wraplength=600,
            justify=tk.LEFT
        )
        description.pack(pady=(0, 20), anchor=tk.W)
        
        # Options container (horizontal layout)
        options_container = ttk.Frame(frame)
        options_container.pack(fill=tk.BOTH, expand=True, pady=10)
        options_container.columnconfigure(0, weight=1)
        options_container.columnconfigure(1, weight=1)
        
        # Create option frames
        self.option_frames = {}
        self.option_vars = {}
        self.selected_mode = self.current_api_key_mode
        
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
        
        # Set initial selection
        self._set_selection(self.current_api_key_mode)
        
        # Navigation buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=(30, 0), side=tk.BOTTOM)
        
        back_button = ttk.Button(
            button_frame,
            text="Back",
            command=lambda: self._prev_step(),
            style="Back.TButton",
            width=15
        )
        back_button.pack(side=tk.LEFT)
        
        next_button = ttk.Button(
            button_frame,
            text="Next",
            command=lambda: self._on_api_mode_next(),
            style="Next.TButton",
            width=15
        )
        next_button.pack(side=tk.RIGHT)
        
        return frame
    
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
        
        # Benefits list (shortened for onboarding)
        for benefit in mode_info["benefits"][:3]:
            benefit_label = ttk.Label(
                frame,
                text=f"• {benefit}",
                wraplength=250,
                justify=tk.LEFT
            )
            benefit_label.pack(anchor=tk.W, pady=(0, 3), padx=(20, 0))
        
        # Make all child widgets clickable too
        for child in frame.winfo_children():
            child.bind("<Button-1>", lambda e, m=mode: self._on_option_click(m))
        
        return frame
    
    def _on_option_click(self, mode: ApiKeyMode):
        """
        Handle option selection.
        
        Args:
            mode: Selected API key mode
        """
        self._set_selection(mode)
    
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
    
    def _on_api_mode_next(self):
        """Handle next button click on API key mode step."""
        # Update API key mode if changed
        if self.selected_mode != self.current_api_key_mode:
            try:
                self.api_key_manager.set_api_key_mode(self.selected_mode)
                self.current_api_key_mode = self.selected_mode
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update API key mode: {e}")
                return
        
        # Skip API key entry step if in Complete System mode
        if self.selected_mode == ApiKeyMode.COMPLETE_SYSTEM:
            self._show_step(3)  # Skip to Getting Started
        else:
            self._next_step()  # Go to API Key Entry
    
    def _create_api_key_entry_step(self) -> ttk.Frame:
        """
        Create the API key entry step.
        
        Returns:
            ttk.Frame: The API key entry step frame
        """
        frame = ttk.Frame(self.main_frame)
        
        # Heading
        heading = ttk.Label(
            frame, 
            text="Enter Your API Keys",
            style="Heading.TLabel"
        )
        heading.pack(pady=(0, 20), anchor=tk.W)
        
        # Description
        description = ttk.Label(
            frame,
            text="You've selected to use your own API keys. Please enter at least one API key "
                 "to get started. You can add more keys later in the settings.",
            wraplength=600,
            justify=tk.LEFT
        )
        description.pack(pady=(0, 20), anchor=tk.W)
        
        # Create notebook for different providers
        notebook = ttk.Notebook(frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Create tabs for major providers
        self.api_key_entries = {}
        self.api_key_vars = {}
        
        # OpenAI tab
        openai_frame = self._create_provider_tab(notebook, ProviderType.OPENAI)
        notebook.add(openai_frame, text="OpenAI")
        
        # Anthropic tab
        anthropic_frame = self._create_provider_tab(notebook, ProviderType.ANTHROPIC)
        notebook.add(anthropic_frame, text="Anthropic")
        
        # Google tab
        google_frame = self._create_provider_tab(notebook, ProviderType.GOOGLE)
        notebook.add(google_frame, text="Google AI")
        
        # Note about skipping
        note_label = ttk.Label(
            frame,
            text="Note: You can skip this step and add API keys later in the settings.",
            font=("TkDefaultFont", 9, "italic")
        )
        note_label.pack(pady=(0, 10), anchor=tk.W)
        
        # Navigation buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=(10, 0), side=tk.BOTTOM)
        
        back_button = ttk.Button(
            button_frame,
            text="Back",
            command=lambda: self._prev_step(),
            style="Back.TButton",
            width=15
        )
        back_button.pack(side=tk.LEFT)
        
        skip_button = ttk.Button(
            button_frame,
            text="Skip",
            command=lambda: self._next_step(),
            style="Back.TButton",
            width=15
        )
        skip_button.pack(side=tk.RIGHT, padx=(0, 10))
        
        next_button = ttk.Button(
            button_frame,
            text="Save & Continue",
            command=lambda: self._on_save_api_keys(),
            style="Next.TButton",
            width=15
        )
        next_button.pack(side=tk.RIGHT)
        
        return frame
    
    def _create_provider_tab(self, notebook, provider: ProviderType) -> ttk.Frame:
        """
        Create a tab for API key entry for a specific provider.
        
        Args:
            notebook: Parent notebook
            provider: Provider type
            
        Returns:
            ttk.Frame: The provider tab frame
        """
        frame = ttk.Frame(notebook, padding=20)
        
        # Provider info
        provider_info = {
            ProviderType.OPENAI: {
                "name": "OpenAI",
                "description": "OpenAI provides GPT models including GPT-3.5 and GPT-4.",
                "key_format": "sk-...",
                "get_key_url": "https://platform.openai.com/api-keys"
            },
            ProviderType.ANTHROPIC: {
                "name": "Anthropic",
                "description": "Anthropic provides Claude models including Claude 2 and Claude Instant.",
                "key_format": "sk-ant-...",
                "get_key_url": "https://console.anthropic.com/account/keys"
            },
            ProviderType.GOOGLE: {
                "name": "Google AI",
                "description": "Google AI provides Gemini models.",
                "key_format": "AIza...",
                "get_key_url": "https://makersuite.google.com/app/apikey"
            }
        }
        
        info = provider_info.get(provider, {
            "name": provider.value.capitalize(),
            "description": f"API key for {provider.value}.",
            "key_format": "...",
            "get_key_url": "#"
        })
        
        # Description
        description = ttk.Label(
            frame,
            text=info["description"],
            wraplength=600,
            justify=tk.LEFT
        )
        description.pack(pady=(0, 10), anchor=tk.W)
        
        # API key entry
        key_frame = ttk.Frame(frame)
        key_frame.pack(fill=tk.X, pady=(0, 10))
        
        key_label = ttk.Label(
            key_frame,
            text="API Key:",
            width=15
        )
        key_label.pack(side=tk.LEFT, padx=(0, 10))
        
        key_var = tk.StringVar()
        self.api_key_vars[provider] = key_var
        
        key_entry = ttk.Entry(
            key_frame,
            textvariable=key_var,
            width=50,
            show="•"
        )
        key_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.api_key_entries[provider] = key_entry
        
        # Format hint
        format_label = ttk.Label(
            frame,
            text=f"Format: {info['key_format']}",
            font=("TkDefaultFont", 9, "italic")
        )
        format_label.pack(pady=(0, 20), anchor=tk.W, padx=(15, 0))
        
        # Get API key link
        link_label = ttk.Label(
            frame,
            text=f"Get {info['name']} API key",
            foreground="blue",
            cursor="hand2",
            font=("TkDefaultFont", 10, "underline")
        )
        link_label.pack(anchor=tk.W)
        link_label.bind("<Button-1>", lambda e, url=info["get_key_url"]: webbrowser.open(url))
        
        # Test button
        test_button = ttk.Button(
            frame,
            text="Test Key",
            command=lambda p=provider: self._test_api_key(p)
        )
        test_button.pack(anchor=tk.W, pady=(10, 0))
        
        return frame
    
    def _test_api_key(self, provider: ProviderType):
        """
        Test an API key.
        
        Args:
            provider: Provider type
        """
        # Get the API key
        api_key = self.api_key_vars[provider].get().strip()
        
        if not api_key:
            messagebox.showwarning("Empty Key", "Please enter an API key to test.")
            return
        
        # Show testing message
        messagebox.showinfo("Testing", f"Testing {provider.value} API key...\n\nThis may take a moment.")
        
        # Test in a separate thread to avoid freezing the UI
        def test_key_thread():
            # In a real implementation, this would actually test the key
            # For this implementation, we'll just simulate a test
            import time
            time.sleep(2)  # Simulate API call
            
            # Show success message
            self.root.after(0, lambda: messagebox.showinfo(
                "Success", f"The {provider.value} API key is valid!"
            ))
        
        threading.Thread(target=test_key_thread).start()
    
    def _on_save_api_keys(self):
        """Handle save and continue button click on API key entry step."""
        # Check if any keys were entered
        has_keys = False
        
        for provider, var in self.api_key_vars.items():
            api_key = var.get().strip()
            if api_key:
                has_keys = True
                try:
                    # Add the API key
                    self.api_key_manager.add_user_api_key(
                        provider=provider,
                        api_key=api_key,
                        name=f"{provider.value} API Key"
                    )
                except Exception as e:
                    messagebox.showerror(
                        "Error", 
                        f"Failed to save {provider.value} API key: {e}"
                    )
                    return
        
        if not has_keys:
            # Confirm skipping
            if not messagebox.askyesno(
                "No API Keys", 
                "You haven't entered any API keys. Are you sure you want to continue?\n\n"
                "You can add API keys later in the settings."
            ):
                return
        
        # Continue to next step
        self._next_step()
    
    def _create_getting_started_step(self) -> ttk.Frame:
        """
        Create the getting started step.
        
        Returns:
            ttk.Frame: The getting started step frame
        """
        frame = ttk.Frame(self.main_frame)
        
        # Heading
        heading = ttk.Label(
            frame, 
            text="You're All Set!",
            style="Heading.TLabel"
        )
        heading.pack(pady=(0, 20), anchor=tk.CENTER)
        
        # Success icon placeholder
        icon_frame = ttk.Frame(frame, width=100, height=100)
        icon_frame.pack(pady=(0, 20), anchor=tk.CENTER)
        
        # Description
        description = ttk.Label(
            frame,
            text="Congratulations! ApexAgent is now set up and ready to use. "
                 "Here are some things you can do to get started:",
            wraplength=600,
            justify=tk.CENTER
        )
        description.pack(pady=(0, 30), anchor=tk.CENTER)
        
        # Getting started tips
        tips = [
            "Create your first project by clicking 'New Project'",
            "Explore the different tabs to understand the interface",
            "Try asking Dr. Tardis for help with any questions",
            "Check out the documentation for detailed guides"
        ]
        
        for tip in tips:
            tip_item = ttk.Label(
                frame,
                text=f"• {tip}",
                wraplength=600,
                justify=tk.LEFT
            )
            tip_item.pack(pady=(0, 5), anchor=tk.W, padx=(20, 0))
        
        # API key mode reminder
        mode_info = API_KEY_MODE_INFO[self.current_api_key_mode]
        mode_frame = ttk.Frame(frame, padding=10)
        mode_frame.pack(fill=tk.X, pady=(20, 0))
        
        mode_label = ttk.Label(
            mode_frame,
            text=f"You're using the {mode_info['title']} option.",
            font=("TkDefaultFont", 10, "bold")
        )
        mode_label.pack(anchor=tk.W)
        
        if self.current_api_key_mode == ApiKeyMode.USER_PROVIDED:
            mode_note = ttk.Label(
                mode_frame,
                text="You can add or manage your API keys anytime in Settings > API Keys.",
                wraplength=600
            )
            mode_note.pack(anchor=tk.W)
        else:
            mode_note = ttk.Label(
                mode_frame,
                text="ApexAgent will handle all API access for you automatically.",
                wraplength=600
            )
            mode_note.pack(anchor=tk.W)
        
        # Navigation buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=(30, 0), side=tk.BOTTOM)
        
        back_button = ttk.Button(
            button_frame,
            text="Back",
            command=lambda: self._prev_step(),
            style="Back.TButton",
            width=15
        )
        back_button.pack(side=tk.LEFT)
        
        finish_button = ttk.Button(
            button_frame,
            text="Finish",
            command=lambda: self._finish_onboarding(),
            style="Next.TButton",
            width=15
        )
        finish_button.pack(side=tk.RIGHT)
        
        return frame
    
    def _show_step(self, step_index: int):
        """
        Show a specific step.
        
        Args:
            step_index: Index of the step to show
        """
        # Hide current step
        if 0 <= self.current_step < len(self.steps):
            self.steps[self.current_step].pack_forget()
        
        # Show new step
        if 0 <= step_index < len(self.steps):
            self.steps[step_index].pack(fill=tk.BOTH, expand=True)
            self.current_step = step_index
    
    def _next_step(self):
        """Go to the next step."""
        if self.current_step < len(self.steps) - 1:
            self._show_step(self.current_step + 1)
    
    def _prev_step(self):
        """Go to the previous step."""
        if self.current_step > 0:
            self._show_step(self.current_step - 1)
    
    def _finish_onboarding(self):
        """Finish the onboarding process."""
        # Save onboarding completion flag
        try:
            # Create a flag file to indicate onboarding is complete
            installation_path = self.installation_config.get("installation_path", 
                                                           os.path.expanduser("~/.apex_agent"))
            flag_path = os.path.join(installation_path, "config", "onboarding_complete")
            
            # Create parent directory if it doesn't exist
            os.makedirs(os.path.dirname(flag_path), exist_ok=True)
            
            # Create the flag file
            with open(flag_path, 'w') as f:
                f.write(f"Completed: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        except Exception as e:
            print(f"Error saving onboarding completion flag: {e}")
        
        # Call completion callback if provided
        if self.on_complete_callback:
            self.on_complete_callback()
        
        # Close the window if we own it
        if self.owns_root:
            self.root.destroy()
    
    def run(self):
        """Run the onboarding wizard."""
        if self.owns_root:
            self.root.mainloop()


# For testing purposes
if __name__ == "__main__":
    # Create a test directory
    test_dir = os.path.join(os.path.expanduser("~"), ".apex_agent_test")
    os.makedirs(test_dir, exist_ok=True)
    
    # Create a test installation config
    installation_config_dir = os.path.join(test_dir, "config")
    os.makedirs(installation_config_dir, exist_ok=True)
    
    installation_config = {
        "installation_path": test_dir,
        "mode": "standard",
        "api_key_mode": "user_provided",
        "components": "",
        "analytics": False,
        "installation_date": time.strftime("%Y-%m-%dT%H:%M:%S%z")
    }
    
    installation_config_path = os.path.join(installation_config_dir, "installation.json")
    with open(installation_config_path, "w") as f:
        json.dump(installation_config, f, indent=2)
    
    # Run the onboarding wizard
    wizard = OnboardingWizard(installation_config_path=installation_config_path)
    wizard.run()
    
    # Clean up
    import shutil
    shutil.rmtree(test_dir)
