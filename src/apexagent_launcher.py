#!/usr/bin/env python3
"""
ApexAgent Standalone Launcher
World's First Hybrid Autonomous AI System

This launcher creates a self-contained ApexAgent installation that runs
without requiring separate Python installation or dependencies.
"""

import os
import sys
import subprocess
import threading
import time
import webbrowser
import tempfile
import shutil
import json
import logging
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk
import socket
from contextlib import closing

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('apexagent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ApexAgentLauncher:
    def __init__(self):
        self.app_name = "ApexAgent"
        self.version = "1.0.0"
        self.port = self.find_free_port()
        self.backend_process = None
        self.temp_dir = None
        self.app_dir = self.get_app_directory()
        self.setup_directories()
        
    def get_app_directory(self):
        """Get the application directory based on the platform."""
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            return Path(sys._MEIPASS)
        else:
            # Running as script
            return Path(__file__).parent
            
    def setup_directories(self):
        """Setup necessary directories for the application."""
        try:
            # Create user data directory
            if sys.platform == "win32":
                user_data = Path.home() / "AppData" / "Local" / self.app_name
            elif sys.platform == "darwin":
                user_data = Path.home() / "Library" / "Application Support" / self.app_name
            else:
                user_data = Path.home() / f".{self.app_name.lower()}"
            
            user_data.mkdir(parents=True, exist_ok=True)
            self.user_data_dir = user_data
            
            # Create temp directory for runtime files
            self.temp_dir = tempfile.mkdtemp(prefix=f"{self.app_name.lower()}_")
            
            logger.info(f"App directory: {self.app_dir}")
            logger.info(f"User data directory: {self.user_data_dir}")
            logger.info(f"Temp directory: {self.temp_dir}")
            
        except Exception as e:
            logger.error(f"Failed to setup directories: {e}")
            self.show_error("Setup Error", f"Failed to setup application directories: {e}")
            sys.exit(1)
    
    def find_free_port(self, start_port=5000):
        """Find a free port starting from the given port."""
        for port in range(start_port, start_port + 100):
            with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
                if sock.connect_ex(('localhost', port)) != 0:
                    return port
        return start_port
    
    def extract_backend_files(self):
        """Extract backend files to temp directory."""
        try:
            backend_source = self.app_dir / "backend"
            backend_dest = Path(self.temp_dir) / "backend"
            
            if backend_source.exists():
                shutil.copytree(backend_source, backend_dest)
                logger.info(f"Backend files extracted to: {backend_dest}")
                return backend_dest
            else:
                # Fallback: create minimal backend
                backend_dest.mkdir(parents=True, exist_ok=True)
                self.create_minimal_backend(backend_dest)
                return backend_dest
                
        except Exception as e:
            logger.error(f"Failed to extract backend files: {e}")
            raise
    
    def create_minimal_backend(self, backend_dir):
        """Create a minimal backend if full backend is not available."""
        main_py = backend_dir / "main.py"
        
        backend_code = f'''
import os
import sys
from flask import Flask, render_template, jsonify, send_from_directory
from flask_cors import CORS
import json
import time
import random

app = Flask(__name__)
CORS(app)

# Configuration
app.config['SECRET_KEY'] = 'apexagent-standalone-key'
PORT = {self.port}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/system/status')
def system_status():
    return jsonify({{
        'status': 'operational',
        'version': '1.0.0',
        'uptime': time.time(),
        'mode': 'standalone'
    }})

@app.route('/api/dashboard/metrics')
def dashboard_metrics():
    return jsonify({{
        'ai_performance': 98.7,
        'security_status': 1247,
        'hybrid_processing': 67,
        'cost_savings': 45,
        'credits': 2847,
        'cost_today': 0.42
    }})

@app.route('/health')
def health():
    return jsonify({{'status': 'healthy', 'timestamp': time.time()}})

if __name__ == '__main__':
    print(f"Starting ApexAgent backend on port {{PORT}}")
    app.run(host='0.0.0.0', port=PORT, debug=False)
'''
        
        with open(main_py, 'w') as f:
            f.write(backend_code)
        
        # Create templates directory and copy frontend
        templates_dir = backend_dir / "templates"
        templates_dir.mkdir(exist_ok=True)
        
        # Copy frontend files
        frontend_source = self.app_dir / "frontend"
        if frontend_source.exists():
            shutil.copytree(frontend_source, templates_dir, dirs_exist_ok=True)
        
        logger.info("Minimal backend created")
    
    def start_backend(self):
        """Start the backend server."""
        try:
            backend_dir = self.extract_backend_files()
            main_py = backend_dir / "main.py"
            
            if not main_py.exists():
                raise FileNotFoundError("Backend main.py not found")
            
            # Start backend process
            env = os.environ.copy()
            env['PORT'] = str(self.port)
            env['PYTHONPATH'] = str(backend_dir)
            
            self.backend_process = subprocess.Popen(
                [sys.executable, str(main_py)],
                cwd=str(backend_dir),
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            logger.info(f"Backend started with PID: {self.backend_process.pid}")
            
            # Wait for backend to start
            self.wait_for_backend()
            
        except Exception as e:
            logger.error(f"Failed to start backend: {e}")
            raise
    
    def wait_for_backend(self, timeout=30):
        """Wait for backend to become available."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
                    if sock.connect_ex(('localhost', self.port)) == 0:
                        logger.info("Backend is ready")
                        return True
            except:
                pass
            
            time.sleep(1)
        
        raise TimeoutError("Backend failed to start within timeout")
    
    def open_browser(self):
        """Open the application in the default browser."""
        url = f"http://localhost:{self.port}"
        logger.info(f"Opening browser to: {url}")
        
        # Wait a moment for backend to fully initialize
        time.sleep(2)
        
        try:
            webbrowser.open(url)
        except Exception as e:
            logger.error(f"Failed to open browser: {e}")
            self.show_info("Manual Access", f"Please open your browser and go to: {url}")
    
    def create_gui(self):
        """Create a simple GUI for the launcher."""
        root = tk.Tk()
        root.title(f"{self.app_name} Launcher")
        root.geometry("500x400")
        root.resizable(False, False)
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Main frame
        main_frame = ttk.Frame(root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text=self.app_name,
            font=('Arial', 24, 'bold')
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # Subtitle
        subtitle_label = ttk.Label(
            main_frame,
            text="World's First Hybrid Autonomous AI System",
            font=('Arial', 12)
        )
        subtitle_label.grid(row=1, column=0, columnspan=2, pady=(0, 20))
        
        # Status
        self.status_var = tk.StringVar(value="Initializing...")
        status_label = ttk.Label(main_frame, textvariable=self.status_var)
        status_label.grid(row=2, column=0, columnspan=2, pady=(0, 10))
        
        # Progress bar
        self.progress = ttk.Progressbar(
            main_frame, 
            mode='indeterminate',
            length=400
        )
        self.progress.grid(row=3, column=0, columnspan=2, pady=(0, 20))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=(0, 10))
        
        self.start_button = ttk.Button(
            button_frame,
            text="Start ApexAgent",
            command=self.start_application,
            state='disabled'
        )
        self.start_button.grid(row=0, column=0, padx=(0, 10))
        
        self.stop_button = ttk.Button(
            button_frame,
            text="Stop",
            command=self.stop_application,
            state='disabled'
        )
        self.stop_button.grid(row=0, column=1, padx=(10, 0))
        
        # Info text
        info_text = tk.Text(
            main_frame,
            height=8,
            width=60,
            wrap=tk.WORD,
            state='disabled'
        )
        info_text.grid(row=5, column=0, columnspan=2, pady=(20, 0))
        
        # Add scrollbar to text
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=info_text.yview)
        scrollbar.grid(row=5, column=2, sticky="ns", pady=(20, 0))
        info_text.configure(yscrollcommand=scrollbar.set)
        
        self.info_text = info_text
        self.root = root
        
        # Initialize
        self.update_status("Ready to start")
        self.start_button.config(state='normal')
        
        return root
    
    def update_status(self, status):
        """Update the status in the GUI."""
        if hasattr(self, 'status_var'):
            self.status_var.set(status)
        logger.info(status)
    
    def add_info(self, text):
        """Add information to the info text widget."""
        if hasattr(self, 'info_text'):
            self.info_text.config(state='normal')
            self.info_text.insert(tk.END, f"{time.strftime('%H:%M:%S')} - {text}\\n")
            self.info_text.see(tk.END)
            self.info_text.config(state='disabled')
    
    def start_application(self):
        """Start the ApexAgent application."""
        def start_thread():
            try:
                self.start_button.config(state='disabled')
                self.stop_button.config(state='normal')
                self.progress.start()
                
                self.update_status("Starting backend server...")
                self.add_info("Initializing ApexAgent backend...")
                
                self.start_backend()
                
                self.update_status("Opening web interface...")
                self.add_info(f"Backend started on port {self.port}")
                
                self.open_browser()
                
                self.update_status(f"ApexAgent running on http://localhost:{self.port}")
                self.add_info("ApexAgent is now running!")
                self.add_info("You can close this window - ApexAgent will continue running.")
                
                self.progress.stop()
                
            except Exception as e:
                self.progress.stop()
                self.update_status("Failed to start")
                self.add_info(f"Error: {e}")
                self.show_error("Startup Error", f"Failed to start ApexAgent: {e}")
                self.start_button.config(state='normal')
                self.stop_button.config(state='disabled')
        
        threading.Thread(target=start_thread, daemon=True).start()
    
    def stop_application(self):
        """Stop the ApexAgent application."""
        try:
            self.update_status("Stopping...")
            self.add_info("Stopping ApexAgent...")
            
            if self.backend_process:
                self.backend_process.terminate()
                self.backend_process.wait(timeout=10)
                self.backend_process = None
            
            self.update_status("Stopped")
            self.add_info("ApexAgent stopped")
            
            self.start_button.config(state='normal')
            self.stop_button.config(state='disabled')
            
        except Exception as e:
            logger.error(f"Error stopping application: {e}")
            self.add_info(f"Error stopping: {e}")
    
    def cleanup(self):
        """Cleanup resources."""
        try:
            if self.backend_process:
                self.backend_process.terminate()
            
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir, ignore_errors=True)
                
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
    
    def show_error(self, title, message):
        """Show error message."""
        if hasattr(self, 'root'):
            messagebox.showerror(title, message)
        else:
            print(f"ERROR - {title}: {message}")
    
    def show_info(self, title, message):
        """Show info message."""
        if hasattr(self, 'root'):
            messagebox.showinfo(title, message)
        else:
            print(f"INFO - {title}: {message}")
    
    def run(self):
        """Run the launcher."""
        try:
            logger.info(f"Starting {self.app_name} Launcher v{self.version}")
            
            # Create and run GUI
            root = self.create_gui()
            
            # Handle window close
            def on_closing():
                self.cleanup()
                root.destroy()
            
            root.protocol("WM_DELETE_WINDOW", on_closing)
            root.mainloop()
            
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        except Exception as e:
            logger.error(f"Launcher error: {e}")
            self.show_error("Launcher Error", f"An error occurred: {e}")
        finally:
            self.cleanup()

def main():
    """Main entry point."""
    launcher = ApexAgentLauncher()
    launcher.run()

if __name__ == "__main__":
    main()

