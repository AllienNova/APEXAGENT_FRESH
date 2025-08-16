"""
Settings UI for API Key Mode management in ApexAgent.

This module provides the UI components for managing API key modes
and API keys in the ApexAgent settings interface.
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

class ApiKeySettingsFrame(ttk.Frame):
    """
    Settings frame for managing API key mode and API keys.
    
    This component allows users to:
    - View and change the current API key mode
    - Add, view, test, and remove API keys
    - See the status of available API providers
    """
    
    def __init__(self, parent, api_key_manager=None, on_mode_change=None, **kwargs):
        """
        Initialize the API key settings frame.
        
        Args:
            parent: Parent widget
            api_key_manager: API key manager instance (created if not provided)
            on_mode_change: Callback function to call when API key mode changes
            **kwargs: Additional arguments to pass to ttk.Frame
        """
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.on_mode_change_callback = on_mode_change
        
        # Initialize API key manager if not provided
        if api_key_manager is None:
            self.api_key_manager = EnhancedApiKeyManager()
        else:
            self.api_key_manager = api_key_manager
        
        # Get current API key mode
        self.current_api_key_mode = self.api_key_manager.get_api_key_mode()
        
        # Configure styles
        self._configure_styles()
        
        # Create widgets
        self._create_widgets()
        
        # Load API keys
        self._load_api_keys()
    
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
        
        # Configure section style
        section_font = font.Font(
            family=default_font.cget("family"),
            size=default_font.cget("size") + 1,
            weight="bold"
        )
        self.style.configure("Section.TLabel", font=section_font)
        
        # Configure option frame style
        self.style.configure("Option.TFrame", padding=10, relief="solid", borderwidth=1)
        self.style.configure("SelectedOption.TFrame", padding=10, relief="solid", borderwidth=2)
        
        # Configure provider frame style
        self.style.configure("Provider.TFrame", padding=10)
        self.style.configure("ProviderHeader.TFrame", padding=(10, 5))
    
    def _create_widgets(self):
        """Create and arrange widgets in the frame."""
        # Main container with padding
        main_container = ttk.Frame(self, padding=20)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Heading
        heading = ttk.Label(
            main_container, 
            text="API Key Settings",
            style="Heading.TLabel"
        )
        heading.pack(pady=(0, 20), anchor=tk.W)
        
        # API Key Mode section
        mode_section = ttk.Label(
            main_container,
            text="API Key Mode",
            style="Section.TLabel"
        )
        mode_section.pack(pady=(0, 10), anchor=tk.W)
        
        # Current mode display
        mode_info = API_KEY_MODE_INFO[self.current_api_key_mode]
        current_mode_frame = ttk.Frame(main_container)
        current_mode_frame.pack(fill=tk.X, pady=(0, 10))
        
        current_mode_label = ttk.Label(
            current_mode_frame,
            text="Current Mode:",
            width=15
        )
        current_mode_label.pack(side=tk.LEFT)
        
        self.current_mode_value = ttk.Label(
            current_mode_frame,
            text=mode_info["title"],
            font=("TkDefaultFont", 10, "bold")
        )
        self.current_mode_value.pack(side=tk.LEFT)
        
        # Change mode button
        change_mode_button = ttk.Button(
            main_container,
            text="Change API Key Mode",
            command=self._show_change_mode_dialog
        )
        change_mode_button.pack(anchor=tk.W, pady=(0, 20))
        
        # API Keys section
        keys_section = ttk.Label(
            main_container,
            text="API Keys",
            style="Section.TLabel"
        )
        keys_section.pack(pady=(0, 10), anchor=tk.W)
        
        # API key management depends on the mode
        if self.current_api_key_mode == ApiKeyMode.USER_PROVIDED:
            # User-Provided mode: Show API key management UI
            self._create_user_api_key_ui(main_container)
        else:
            # Complete System mode: Show ApexAgent proxy info
            self._create_complete_system_ui(main_container)
    
    def _create_user_api_key_ui(self, parent):
        """
        Create UI for managing user-provided API keys.
        
        Args:
            parent: Parent widget
        """
        # Container for API key management
        api_key_container = ttk.Frame(parent)
        api_key_container.pack(fill=tk.BOTH, expand=True)
        
        # Description
        description = ttk.Label(
            api_key_container,
            text="Manage your API keys for different providers. These keys will be used "
                 "to access AI models from each provider.",
            wraplength=600,
            justify=tk.LEFT
        )
        description.pack(pady=(0, 10), anchor=tk.W)
        
        # Add API Key button
        add_key_button = ttk.Button(
            api_key_container,
            text="Add API Key",
            command=self._show_add_key_dialog
        )
        add_key_button.pack(anchor=tk.W, pady=(0, 10))
        
        # Create scrollable frame for API keys
        key_canvas = tk.Canvas(api_key_container, highlightthickness=0)
        key_scrollbar = ttk.Scrollbar(api_key_container, orient="vertical", command=key_canvas.yview)
        key_scrollable_frame = ttk.Frame(key_canvas)
        
        key_scrollable_frame.bind(
            "<Configure>",
            lambda e: key_canvas.configure(scrollregion=key_canvas.bbox("all"))
        )
        
        key_canvas.create_window((0, 0), window=key_scrollable_frame, anchor="nw")
        key_canvas.configure(yscrollcommand=key_scrollbar.set)
        
        key_canvas.pack(side="left", fill="both", expand=True)
        key_scrollbar.pack(side="right", fill="y")
        
        # Store reference to the scrollable frame
        self.key_scrollable_frame = key_scrollable_frame
    
    def _create_complete_system_ui(self, parent):
        """
        Create UI for Complete System mode.
        
        Args:
            parent: Parent widget
        """
        # Container for Complete System info
        complete_system_container = ttk.Frame(parent)
        complete_system_container.pack(fill=tk.BOTH, expand=True)
        
        # Description
        description = ttk.Label(
            complete_system_container,
            text="You're using the Complete System mode. ApexAgent is managing all API "
                 "access for you automatically through our secure proxy service.",
            wraplength=600,
            justify=tk.LEFT
        )
        description.pack(pady=(0, 20), anchor=tk.W)
        
        # Status frame
        status_frame = ttk.LabelFrame(complete_system_container, text="Service Status")
        status_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Status indicators for different providers
        providers = [
            ("OpenAI", "Connected", "green"),
            ("Anthropic", "Connected", "green"),
            ("Google AI", "Connected", "green"),
            ("Mistral AI", "Connected", "green")
        ]
        
        for i, (provider, status, color) in enumerate(providers):
            provider_frame = ttk.Frame(status_frame, padding=5)
            provider_frame.grid(row=i//2, column=i%2, padx=10, pady=5, sticky="w")
            
            provider_label = ttk.Label(
                provider_frame,
                text=f"{provider}:",
                width=15
            )
            provider_label.pack(side=tk.LEFT)
            
            status_label = ttk.Label(
                provider_frame,
                text=status,
                foreground=color
            )
            status_label.pack(side=tk.LEFT)
        
        # Note about switching
        note_frame = ttk.Frame(complete_system_container, padding=10)
        note_frame.pack(fill=tk.X)
        
        note_label = ttk.Label(
            note_frame,
            text="Want to use your own API keys? Click 'Change API Key Mode' above to switch "
                 "to User-Provided mode. Your subscription cost will be reduced, but you'll "
                 "need to provide and manage your own API keys.",
            wraplength=600,
            justify=tk.LEFT
        )
        note_label.pack(anchor=tk.W)
    
    def _load_api_keys(self):
        """Load and display API keys."""
        if self.current_api_key_mode != ApiKeyMode.USER_PROVIDED:
            return
        
        # Clear existing keys
        for widget in self.key_scrollable_frame.winfo_children():
            widget.destroy()
        
        # Get user API keys
        user_keys = self.api_key_manager.list_user_api_keys()
        
        if not user_keys:
            # No keys message
            no_keys_label = ttk.Label(
                self.key_scrollable_frame,
                text="No API keys added yet. Click 'Add API Key' to get started.",
                font=("TkDefaultFont", 10, "italic")
            )
            no_keys_label.pack(pady=20)
            return
        
        # Group keys by provider
        keys_by_provider = {}
        for key in user_keys:
            provider = key.get("provider_type")
            if provider not in keys_by_provider:
                keys_by_provider[provider] = []
            keys_by_provider[provider].append(key)
        
        # Display keys by provider
        for provider, keys in keys_by_provider.items():
            # Provider header
            provider_header = ttk.Frame(self.key_scrollable_frame, style="ProviderHeader.TFrame")
            provider_header.pack(fill=tk.X, pady=(10, 0))
            
            provider_label = ttk.Label(
                provider_header,
                text=provider.capitalize(),
                style="Subheading.TLabel"
            )
            provider_label.pack(anchor=tk.W)
            
            # Provider keys
            for key in keys:
                key_frame = ttk.Frame(self.key_scrollable_frame, style="Provider.TFrame")
                key_frame.pack(fill=tk.X, pady=(0, 5))
                
                # Key info
                key_info_frame = ttk.Frame(key_frame)
                key_info_frame.pack(fill=tk.X)
                
                name_label = ttk.Label(
                    key_info_frame,
                    text=key.get("name") or f"{provider.capitalize()} API Key",
                    font=("TkDefaultFont", 10, "bold")
                )
                name_label.pack(anchor=tk.W)
                
                # Format date
                import datetime
                created_at = key.get("created_at")
                if created_at:
                    created_date = datetime.datetime.fromtimestamp(created_at).strftime("%Y-%m-%d %H:%M")
                else:
                    created_date = "Unknown"
                
                date_label = ttk.Label(
                    key_info_frame,
                    text=f"Added: {created_date}",
                    font=("TkDefaultFont", 9)
                )
                date_label.pack(anchor=tk.W)
                
                # Last used
                last_used = key.get("last_used")
                if last_used:
                    last_used_date = datetime.datetime.fromtimestamp(last_used).strftime("%Y-%m-%d %H:%M")
                    last_used_label = ttk.Label(
                        key_info_frame,
                        text=f"Last used: {last_used_date}",
                        font=("TkDefaultFont", 9)
                    )
                    last_used_label.pack(anchor=tk.W)
                
                # Buttons
                button_frame = ttk.Frame(key_frame)
                button_frame.pack(fill=tk.X, pady=(5, 0))
                
                test_button = ttk.Button(
                    button_frame,
                    text="Test",
                    command=lambda k=key: self._test_key(k),
                    width=8
                )
                test_button.pack(side=tk.LEFT, padx=(0, 5))
                
                remove_button = ttk.Button(
                    button_frame,
                    text="Remove",
                    command=lambda k=key: self._remove_key(k),
                    width=8
                )
                remove_button.pack(side=tk.LEFT)
    
    def _show_change_mode_dialog(self):
        """Show dialog for changing API key mode."""
        # Create dialog window
        dialog = tk.Toplevel(self)
        dialog.title("Change API Key Mode")
        dialog.geometry("600x500")
        dialog.minsize(600, 500)
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Dialog content
        content_frame = ttk.Frame(dialog, padding=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Heading
        heading = ttk.Label(
            content_frame, 
            text="Change API Key Mode",
            style="Heading.TLabel"
        )
        heading.pack(pady=(0, 20), anchor=tk.W)
        
        # Current mode
        current_mode_frame = ttk.Frame(content_frame)
        current_mode_frame.pack(fill=tk.X, pady=(0, 20))
        
        current_mode_label = ttk.Label(
            current_mode_frame,
            text="Current Mode:",
            width=15
        )
        current_mode_label.pack(side=tk.LEFT)
        
        mode_info = API_KEY_MODE_INFO[self.current_api_key_mode]
        current_mode_value = ttk.Label(
            current_mode_frame,
            text=mode_info["title"],
            font=("TkDefaultFont", 10, "bold")
        )
        current_mode_value.pack(side=tk.LEFT)
        
        # Warning
        warning_frame = ttk.Frame(content_frame, padding=10)
        warning_frame.pack(fill=tk.X, pady=(0, 20))
        
        if self.current_api_key_mode == ApiKeyMode.COMPLETE_SYSTEM:
            warning_text = (
                "Warning: Switching to User-Provided mode will require you to provide "
                "your own API keys for each provider you want to use. Your subscription "
                "cost will be reduced, but you'll need to obtain and manage these keys yourself."
            )
        else:
            warning_text = (
                "Warning: Switching to Complete System mode will use ApexAgent's proxy "
                "service for all API access. Your subscription cost will increase, but "
                "you won't need to manage API keys yourself."
            )
        
        warning_label = ttk.Label(
            warning_frame,
            text=warning_text,
            wraplength=550,
            justify=tk.LEFT,
            foreground="red"
        )
        warning_label.pack(anchor=tk.W)
        
        # Options
        options_label = ttk.Label(
            content_frame,
            text="Select new mode:",
            style="Subheading.TLabel"
        )
        options_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Target mode (opposite of current)
        target_mode = (
            ApiKeyMode.USER_PROVIDED 
            if self.current_api_key_mode == ApiKeyMode.COMPLETE_SYSTEM 
            else ApiKeyMode.COMPLETE_SYSTEM
        )
        target_mode_info = API_KEY_MODE_INFO[target_mode]
        
        # Target mode frame
        target_frame = ttk.Frame(content_frame, style="Option.TFrame")
        target_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Title
        title = ttk.Label(
            target_frame,
            text=target_mode_info["title"],
            style="Subheading.TLabel",
            padding=(10, 10, 0, 0)
        )
        title.pack(anchor=tk.W)
        
        # Description
        description = ttk.Label(
            target_frame,
            text=target_mode_info["description"],
            wraplength=550,
            justify=tk.LEFT,
            padding=(10, 0, 10, 10)
        )
        description.pack(anchor=tk.W)
        
        # Benefits heading
        benefits_heading = ttk.Label(
            target_frame,
            text="Benefits:",
            font=("TkDefaultFont", 10, "bold"),
            padding=(10, 0, 0, 5)
        )
        benefits_heading.pack(anchor=tk.W)
        
        # Benefits list
        for benefit in target_mode_info["benefits"]:
            benefit_label = ttk.Label(
                target_frame,
                text=f"• {benefit}",
                wraplength=550,
                justify=tk.LEFT,
                padding=(30, 0, 10, 3)
            )
            benefit_label.pack(anchor=tk.W)
        
        # Confirmation checkbox
        confirm_var = tk.BooleanVar(value=False)
        confirm_check = ttk.Checkbutton(
            content_frame,
            text="I understand the implications of changing the API key mode",
            variable=confirm_var
        )
        confirm_check.pack(anchor=tk.W, pady=(0, 20))
        
        # Buttons
        button_frame = ttk.Frame(content_frame)
        button_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        cancel_button = ttk.Button(
            button_frame,
            text="Cancel",
            command=dialog.destroy,
            width=10
        )
        cancel_button.pack(side=tk.LEFT)
        
        def on_change():
            if not confirm_var.get():
                messagebox.showwarning(
                    "Confirmation Required",
                    "Please confirm that you understand the implications of changing the API key mode."
                )
                return
            
            try:
                # Change the mode
                self.api_key_manager.set_api_key_mode(target_mode)
                
                # Update UI
                self._update_mode_display()
                
                # Call callback if provided
                if self.on_mode_change_callback:
                    self.on_mode_change_callback(target_mode)
                
                # Show success message
                messagebox.showinfo(
                    "Mode Changed",
                    f"API key mode changed to {target_mode_info['title']}."
                )
                
                # Close dialog
                dialog.destroy()
                
                # Refresh the settings UI
                self._refresh_ui()
            except Exception as e:
                messagebox.showerror(
                    "Error",
                    f"Failed to change API key mode: {e}"
                )
        
        change_button = ttk.Button(
            button_frame,
            text="Change Mode",
            command=on_change,
            width=15
        )
        change_button.pack(side=tk.RIGHT)
    
    def _show_add_key_dialog(self):
        """Show dialog for adding a new API key."""
        # Create dialog window
        dialog = tk.Toplevel(self)
        dialog.title("Add API Key")
        dialog.geometry("500x400")
        dialog.minsize(500, 400)
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Dialog content
        content_frame = ttk.Frame(dialog, padding=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Heading
        heading = ttk.Label(
            content_frame, 
            text="Add API Key",
            style="Heading.TLabel"
        )
        heading.pack(pady=(0, 20), anchor=tk.W)
        
        # Provider selection
        provider_frame = ttk.Frame(content_frame)
        provider_frame.pack(fill=tk.X, pady=(0, 10))
        
        provider_label = ttk.Label(
            provider_frame,
            text="Provider:",
            width=15
        )
        provider_label.pack(side=tk.LEFT, padx=(0, 10))
        
        provider_var = tk.StringVar()
        provider_combo = ttk.Combobox(
            provider_frame,
            textvariable=provider_var,
            state="readonly",
            width=30
        )
        provider_combo["values"] = [
            "OpenAI",
            "Anthropic",
            "Google AI",
            "Mistral AI",
            "Cohere",
            "Azure OpenAI"
        ]
        provider_combo.current(0)
        provider_combo.pack(side=tk.LEFT)
        
        # API key entry
        key_frame = ttk.Frame(content_frame)
        key_frame.pack(fill=tk.X, pady=(10, 0))
        
        key_label = ttk.Label(
            key_frame,
            text="API Key:",
            width=15
        )
        key_label.pack(side=tk.LEFT, padx=(0, 10))
        
        key_var = tk.StringVar()
        key_entry = ttk.Entry(
            key_frame,
            textvariable=key_var,
            width=40,
            show="•"
        )
        key_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Key name (optional)
        name_frame = ttk.Frame(content_frame)
        name_frame.pack(fill=tk.X, pady=(10, 0))
        
        name_label = ttk.Label(
            name_frame,
            text="Name (optional):",
            width=15
        )
        name_label.pack(side=tk.LEFT, padx=(0, 10))
        
        name_var = tk.StringVar()
        name_entry = ttk.Entry(
            name_frame,
            textvariable=name_var,
            width=40
        )
        name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Format hint based on provider
        format_frame = ttk.Frame(content_frame)
        format_frame.pack(fill=tk.X, pady=(5, 20))
        
        format_label = ttk.Label(
            format_frame,
            text="Format: sk-...",
            font=("TkDefaultFont", 9, "italic")
        )
        format_label.pack(anchor=tk.W, padx=(15, 0))
        
        # Update format hint when provider changes
        def update_format_hint(*args):
            provider = provider_var.get()
            if provider == "OpenAI":
                format_label.config(text="Format: sk-...")
            elif provider == "Anthropic":
                format_label.config(text="Format: sk-ant-...")
            elif provider == "Google AI":
                format_label.config(text="Format: AIza...")
            elif provider == "Azure OpenAI":
                format_label.config(text="Format: Your Azure OpenAI API key")
            else:
                format_label.config(text="Format: Provider-specific API key")
        
        provider_var.trace_add("write", update_format_hint)
        
        # Get API key link
        link_frame = ttk.Frame(content_frame)
        link_frame.pack(fill=tk.X)
        
        link_label = ttk.Label(
            link_frame,
            text="Get API key",
            foreground="blue",
            cursor="hand2",
            font=("TkDefaultFont", 10, "underline")
        )
        link_label.pack(anchor=tk.W)
        
        # Update link when provider changes
        def update_link(*args):
            provider = provider_var.get()
            if provider == "OpenAI":
                link_label.bind("<Button-1>", lambda e: webbrowser.open("https://platform.openai.com/api-keys"))
            elif provider == "Anthropic":
                link_label.bind("<Button-1>", lambda e: webbrowser.open("https://console.anthropic.com/account/keys"))
            elif provider == "Google AI":
                link_label.bind("<Button-1>", lambda e: webbrowser.open("https://makersuite.google.com/app/apikey"))
            elif provider == "Mistral AI":
                link_label.bind("<Button-1>", lambda e: webbrowser.open("https://console.mistral.ai/api-keys/"))
            elif provider == "Cohere":
                link_label.bind("<Button-1>", lambda e: webbrowser.open("https://dashboard.cohere.com/api-keys"))
            elif provider == "Azure OpenAI":
                link_label.bind("<Button-1>", lambda e: webbrowser.open("https://portal.azure.com/"))
        
        provider_var.trace_add("write", update_link)
        update_link()  # Initialize link
        
        # Buttons
        button_frame = ttk.Frame(content_frame)
        button_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(20, 0))
        
        cancel_button = ttk.Button(
            button_frame,
            text="Cancel",
            command=dialog.destroy,
            width=10
        )
        cancel_button.pack(side=tk.LEFT)
        
        def on_test():
            api_key = key_var.get().strip()
            if not api_key:
                messagebox.showwarning("Empty Key", "Please enter an API key to test.")
                return
            
            provider = provider_var.get()
            messagebox.showinfo("Testing", f"Testing {provider} API key...\n\nThis may take a moment.")
            
            # Test in a separate thread to avoid freezing the UI
            def test_key_thread():
                # In a real implementation, this would actually test the key
                # For this implementation, we'll just simulate a test
                import time
                time.sleep(2)  # Simulate API call
                
                # Show success message
                dialog.after(0, lambda: messagebox.showinfo(
                    "Success", f"The {provider} API key is valid!"
                ))
            
            threading.Thread(target=test_key_thread).start()
        
        test_button = ttk.Button(
            button_frame,
            text="Test Key",
            command=on_test,
            width=10
        )
        test_button.pack(side=tk.RIGHT, padx=(0, 10))
        
        def on_add():
            api_key = key_var.get().strip()
            if not api_key:
                messagebox.showwarning("Empty Key", "Please enter an API key.")
                return
            
            provider_name = provider_var.get()
            key_name = name_var.get().strip() or f"{provider_name} API Key"
            
            # Map provider name to ProviderType
            provider_map = {
                "OpenAI": ProviderType.OPENAI,
                "Anthropic": ProviderType.ANTHROPIC,
                "Google AI": ProviderType.GOOGLE,
                "Mistral AI": ProviderType.MISTRAL,
                "Cohere": ProviderType.COHERE,
                "Azure OpenAI": ProviderType.AZURE_OPENAI
            }
            
            provider_type = provider_map.get(provider_name)
            if not provider_type:
                messagebox.showerror("Error", f"Unknown provider: {provider_name}")
                return
            
            try:
                # Add the API key
                self.api_key_manager.add_user_api_key(
                    provider=provider_type,
                    api_key=api_key,
                    name=key_name
                )
                
                # Show success message
                messagebox.showinfo(
                    "Success",
                    f"Added {provider_name} API key."
                )
                
                # Close dialog
                dialog.destroy()
                
                # Refresh the API key list
                self._load_api_keys()
            except Exception as e:
                messagebox.showerror(
                    "Error",
                    f"Failed to add API key: {e}"
                )
        
        add_button = ttk.Button(
            button_frame,
            text="Add Key",
            command=on_add,
            width=10
        )
        add_button.pack(side=tk.RIGHT)
    
    def _test_key(self, key):
        """
        Test an API key.
        
        Args:
            key: API key metadata
        """
        provider_type = key.get("provider_type")
        if not provider_type:
            messagebox.showerror("Error", "Invalid key metadata")
            return
        
        # Show testing message
        messagebox.showinfo(
            "Testing",
            f"Testing {provider_type} API key...\n\nThis may take a moment."
        )
        
        # Test in a separate thread to avoid freezing the UI
        def test_key_thread():
            # In a real implementation, this would actually test the key
            # For this implementation, we'll just simulate a test
            import time
            time.sleep(2)  # Simulate API call
            
            # Show success message
            self.after(0, lambda: messagebox.showinfo(
                "Success", f"The {provider_type} API key is valid!"
            ))
        
        threading.Thread(target=test_key_thread).start()
    
    def _remove_key(self, key):
        """
        Remove an API key.
        
        Args:
            key: API key metadata
        """
        key_id = key.get("id")
        if not key_id:
            messagebox.showerror("Error", "Invalid key metadata")
            return
        
        # Confirm removal
        if not messagebox.askyesno(
            "Confirm Removal",
            f"Are you sure you want to remove this API key?\n\n"
            f"Provider: {key.get('provider_type')}\n"
            f"Name: {key.get('name')}"
        ):
            return
        
        try:
            # Remove the key
            self.api_key_manager.remove_user_api_key(key_id)
            
            # Show success message
            messagebox.showinfo(
                "Success",
                "API key removed."
            )
            
            # Refresh the API key list
            self._load_api_keys()
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to remove API key: {e}"
            )
    
    def _update_mode_display(self):
        """Update the display of the current API key mode."""
        # Get current mode
        self.current_api_key_mode = self.api_key_manager.get_api_key_mode()
        mode_info = API_KEY_MODE_INFO[self.current_api_key_mode]
        
        # Update display
        self.current_mode_value.config(text=mode_info["title"])
    
    def _refresh_ui(self):
        """Refresh the entire UI."""
        # Clear existing widgets
        for widget in self.winfo_children():
            widget.destroy()
        
        # Recreate widgets
        self._create_widgets()
        
        # Load API keys
        self._load_api_keys()


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
    
    # Initialize API key manager
    api_key_manager = EnhancedApiKeyManager(
        installation_config_dir=installation_config_dir,
        config_dir=os.path.join(test_dir, "security"),
        credentials_dir=os.path.join(test_dir, "credentials")
    )
    
    # Add a test API key
    api_key_manager.add_user_api_key(
        provider=ProviderType.OPENAI,
        api_key="sk-test-key-12345",
        name="Test OpenAI Key"
    )
    
    # Create test window
    root = tk.Tk()
    root.title("API Key Settings")
    root.geometry("800x600")
    
    # Create settings frame
    settings_frame = ApiKeySettingsFrame(root, api_key_manager=api_key_manager)
    settings_frame.pack(fill=tk.BOTH, expand=True)
    
    # Run the application
    root.mainloop()
    
    # Clean up
    import shutil
    shutil.rmtree(test_dir)
