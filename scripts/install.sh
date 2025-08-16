#!/bin/bash
# Universal ApexAgent Installer for Linux

set -e

APP_NAME="ApexAgent"
APP_VERSION="1.0.0"
INSTALL_DIR="/opt/apexagent"
BIN_DIR="/usr/local/bin"
DESKTOP_DIR="/usr/share/applications"

echo "========================================="
echo "  $APP_NAME Universal Installer"
echo "  Version: $APP_VERSION"
echo "========================================="
echo

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "This installer requires root privileges."
    echo "Please run with sudo: sudo $0"
    exit 1
fi

# Detect distribution
if [ -f /etc/os-release ]; then
    . /etc/os-release
    DISTRO=$ID
else
    echo "Cannot detect Linux distribution"
    exit 1
fi

echo "Detected distribution: $DISTRO"

# Install dependencies based on distribution
echo "Installing dependencies..."
case $DISTRO in
    ubuntu|debian)
        apt-get update
        apt-get install -y python3 python3-pip python3-tk
        ;;
    fedora|centos|rhel)
        if command -v dnf &> /dev/null; then
            dnf install -y python3 python3-pip python3-tkinter
        else
            yum install -y python3 python3-pip tkinter
        fi
        ;;
    arch|manjaro)
        pacman -S --noconfirm python python-pip tk
        ;;
    opensuse*)
        zypper install -y python3 python3-pip python3-tk
        ;;
    *)
        echo "Unsupported distribution: $DISTRO"
        echo "Please install Python 3, pip, and tkinter manually"
        ;;
esac

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install flask flask-cors redis requests

# Create installation directory
echo "Creating installation directory..."
mkdir -p "$INSTALL_DIR"

# Extract application files (this would be embedded in the actual installer)
echo "Installing application files..."
# In a real installer, files would be extracted here
# For now, we'll create a placeholder
cat > "$INSTALL_DIR/launcher.py" << 'LAUNCHER_EOF'
#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# Import and run the actual launcher
try:
    from apexagent_launcher import main
    main()
except ImportError:
    print("ApexAgent installation is incomplete.")
    print("Please reinstall ApexAgent.")
    sys.exit(1)
LAUNCHER_EOF

chmod +x "$INSTALL_DIR/launcher.py"

# Create launcher script
echo "Creating launcher script..."
cat > "$BIN_DIR/apexagent" << 'LAUNCHER_SCRIPT_EOF'
#!/bin/bash
cd "$INSTALL_DIR"
python3 launcher.py "$@"
LAUNCHER_SCRIPT_EOF

chmod +x "$BIN_DIR/apexagent"

# Create desktop entry
echo "Creating desktop entry..."
cat > "$DESKTOP_DIR/apexagent.desktop" << 'DESKTOP_EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=ApexAgent
Comment=World's First Hybrid Autonomous AI System
Exec=apexagent
Icon=apexagent
Terminal=false
Categories=Office;Development;
Keywords=AI;Artificial Intelligence;Automation;
StartupNotify=true
DESKTOP_EOF

# Update desktop database
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$DESKTOP_DIR"
fi

echo
echo "========================================="
echo "  Installation completed successfully!"
echo "========================================="
echo
echo "You can now run $APP_NAME by:"
echo "  1. Typing 'apexagent' in terminal"
echo "  2. Finding it in your applications menu"
echo "  3. Running: $BIN_DIR/apexagent"
echo
echo "To uninstall, run: sudo rm -rf $INSTALL_DIR $BIN_DIR/apexagent $DESKTOP_DIR/apexagent.desktop"
echo
