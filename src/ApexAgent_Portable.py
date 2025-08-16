#!/usr/bin/env python3
"""
ApexAgent Portable Launcher
No installation required - runs from any directory
"""

import os
import sys
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Set portable mode
os.environ['APEXAGENT_PORTABLE'] = '1'
os.environ['APEXAGENT_DATA_DIR'] = str(current_dir / 'data')

# Create data directory
data_dir = current_dir / 'data'
data_dir.mkdir(exist_ok=True)

# Import and run the launcher
try:
    from apexagent_launcher import ApexAgentLauncher
    
    class PortableLauncher(ApexAgentLauncher):
        def get_app_directory(self):
            return current_dir
        
        def setup_directories(self):
            super().setup_directories()
            # Override user data directory for portable mode
            self.user_data_dir = data_dir
    
    launcher = PortableLauncher()
    launcher.run()
    
except ImportError as e:
    print(f"Error: {e}")
    print("ApexAgent portable installation is incomplete.")
    input("Press Enter to exit...")
    sys.exit(1)
except Exception as e:
    print(f"Error starting ApexAgent: {e}")
    input("Press Enter to exit...")
    sys.exit(1)
