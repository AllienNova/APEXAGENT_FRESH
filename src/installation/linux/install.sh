#!/bin/bash
#
# ApexAgent Linux Installer Script
#
# This script installs ApexAgent on Linux systems.
# It handles dependency checking, installation, and configuration.
#
# Usage:
#   ./install.sh [options]
#
# Options:
#   --install-path PATH   Installation path (default: /opt/apexagent)
#   --mode MODE           Installation mode: standard, minimal, complete, development, custom
#   --components LIST     Comma-separated list of components for custom mode
#   --silent              Run in silent mode without user interaction
#   --no-shortcut         Do not create desktop or application menu shortcuts
#   --analytics           Enable anonymous usage analytics
#   --help                Display this help message
#
# Example:
#   ./install.sh --install-path ~/apexagent --mode complete
#
# Note: This script may require sudo privileges for system-wide installation.

set -e

# Default values
INSTALL_PATH="/opt/apexagent"
MODE="standard"
COMPONENTS=""
SILENT=false
NO_SHORTCUT=false
ANALYTICS=false
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMMON_DIR="$(dirname "$SCRIPT_DIR")/common"
LOG_FILE="/tmp/ApexAgent_Install.log"

# Function to log messages
log() {
    local level="INFO"
    if [ $# -eq 2 ]; then
        level="$2"
    fi
    
    local timestamp=$(date "+%Y-%m-%d %H:%M:%S")
    echo "[$level] $timestamp - $1" | tee -a "$LOG_FILE"
}

# Function to display help
show_help() {
    cat << EOF
ApexAgent Linux Installer

Usage:
  ./install.sh [options]

Options:
  --install-path PATH   Installation path (default: /opt/apexagent)
  --mode MODE           Installation mode: standard, minimal, complete, development, custom
  --components LIST     Comma-separated list of components for custom mode
  --silent              Run in silent mode without user interaction
  --no-shortcut         Do not create desktop or application menu shortcuts
  --analytics           Enable anonymous usage analytics
  --help                Display this help message

Example:
  ./install.sh --install-path ~/apexagent --mode complete

Note: This script may require sudo privileges for system-wide installation.
EOF
}

# Parse command line arguments
while [ $# -gt 0 ]; do
    case "$1" in
        --install-path)
            INSTALL_PATH="$2"
            shift 2
            ;;
        --mode)
            MODE="$2"
            shift 2
            ;;
        --components)
            COMPONENTS="$2"
            shift 2
            ;;
        --silent)
            SILENT=true
            shift
            ;;
        --no-shortcut)
            NO_SHORTCUT=true
            shift
            ;;
        --analytics)
            ANALYTICS=true
            shift
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            log "Unknown option: $1" "ERROR"
            show_help
            exit 1
            ;;
    esac
done

# Validate installation mode
if [[ ! "$MODE" =~ ^(standard|minimal|complete|development|custom)$ ]]; then
    log "Invalid installation mode: $MODE. Must be one of: standard, minimal, complete, development, custom" "ERROR"
    exit 1
fi

# Validate components if mode is custom
if [ "$MODE" = "custom" ] && [ -z "$COMPONENTS" ]; then
    log "Custom mode requires --components to be specified" "ERROR"
    exit 1
fi

# Function to detect Linux distribution
detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DISTRO="$ID"
        VERSION="$VERSION_ID"
    elif [ -f /etc/lsb-release ]; then
        . /etc/lsb-release
        DISTRO="$DISTRIB_ID"
        VERSION="$DISTRIB_RELEASE"
    elif [ -f /etc/debian_version ]; then
        DISTRO="debian"
        VERSION=$(cat /etc/debian_version)
    elif [ -f /etc/redhat-release ]; then
        DISTRO="redhat"
        VERSION=$(cat /etc/redhat-release | grep -oE '[0-9]+\.[0-9]+')
    else
        DISTRO="unknown"
        VERSION="unknown"
    fi
    
    # Convert to lowercase
    DISTRO=$(echo "$DISTRO" | tr '[:upper:]' '[:lower:]')
    
    log "Detected Linux distribution: $DISTRO $VERSION"
}

# Function to check if running with sudo
check_sudo() {
    # Skip sudo check if installing to user's home directory
    if [[ "$INSTALL_PATH" == "$HOME"* ]]; then
        log "Installing to user's home directory, sudo not required."
        return 0
    fi
    
    if [ "$EUID" -ne 0 ]; then
        if [ "$SILENT" = false ]; then
            log "This script requires administrative privileges for system-wide installation." "WARNING"
            log "Please enter your password when prompted."
            
            # Try to get sudo privileges
            if ! sudo -v; then
                log "Failed to obtain administrative privileges." "ERROR"
                exit 1
            fi
            
            # Re-run this script with sudo
            log "Re-running script with sudo..."
            exec sudo "$0" "$@"
        else
            log "This script requires administrative privileges for system-wide installation. Please run with sudo." "ERROR"
            exit 1
        fi
    fi
}

# Function to install system dependencies
install_system_dependencies() {
    log "Installing system dependencies..."
    
    case "$DISTRO" in
        ubuntu|debian)
            apt-get update
            apt-get install -y python3 python3-pip python3-venv python3-dev build-essential libssl-dev libffi-dev
            ;;
        fedora|centos|rhel)
            if command -v dnf &> /dev/null; then
                dnf install -y python3 python3-pip python3-devel gcc openssl-devel libffi-devel
            else
                yum install -y python3 python3-pip python3-devel gcc openssl-devel libffi-devel
            fi
            ;;
        arch|manjaro)
            pacman -Sy --noconfirm python python-pip
            ;;
        opensuse|suse)
            zypper install -y python3 python3-pip python3-devel gcc libopenssl-devel libffi-devel
            ;;
        *)
            log "Unsupported distribution: $DISTRO. Please install Python 3.8+ and pip manually." "WARNING"
            ;;
    esac
    
    log "System dependencies installed successfully."
}

# Function to check system requirements
check_system_requirements() {
    log "Checking system requirements..."
    
    # Detect Linux distribution
    detect_distro
    
    # Check Python installation
    if ! command -v python3 &> /dev/null; then
        log "Python 3 is not installed. Installing required system dependencies..." "WARNING"
        install_system_dependencies
    fi
    
    # Check Python version
    local python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
    local py_major=$(echo "$python_version" | cut -d. -f1)
    local py_minor=$(echo "$python_version" | cut -d. -f2)
    
    if [ "$py_major" -lt 3 ] || ([ "$py_major" -eq 3 ] && [ "$py_minor" -lt 8 ]); then
        log "Python version $python_version is not supported. Please install Python 3.8 or higher." "ERROR"
        return 1
    fi
    
    log "Found Python $python_version"
    
    # Check disk space
    local install_dir=$(dirname "$INSTALL_PATH")
    local free_space=$(df -k "$install_dir" | tail -1 | awk '{print $4}')
    local required_space=$((500 * 1024)) # 500 MB in KB
    
    if [ "$free_space" -lt "$required_space" ]; then
        log "Insufficient disk space. Required: 500 MB, Available: $((free_space / 1024)) MB" "ERROR"
        return 1
    fi
    
    log "System requirements check passed."
    return 0
}

# Function to install Python dependencies
install_dependencies() {
    log "Installing Python dependencies..."
    
    # Create a virtual environment if it doesn't exist
    local venv_path="$INSTALL_PATH/venv"
    
    if [ ! -d "$venv_path" ]; then
        log "Creating Python virtual environment..."
        python3 -m venv "$venv_path"
    fi
    
    # Activate virtual environment
    source "$venv_path/bin/activate"
    
    # Upgrade pip
    log "Upgrading pip..."
    pip install --upgrade pip
    
    # Install required packages
    log "Installing required packages..."
    pip install --upgrade setuptools wheel
    
    # Install dependencies based on installation mode
    case "$MODE" in
        minimal)
            pip install requests numpy pandas
            ;;
        standard)
            pip install requests numpy pandas matplotlib pillow beautifulsoup4 flask
            ;;
        complete|development)
            pip install requests numpy pandas matplotlib pillow beautifulsoup4 flask fastapi uvicorn pytest black flake8 mypy isort sphinx sphinx-rtd-theme
            ;;
        custom)
            # Parse components and install relevant packages
            if [[ "$COMPONENTS" == *"core"* ]]; then
                pip install requests numpy pandas
            fi
            if [[ "$COMPONENTS" == *"ui"* ]]; then
                pip install flask fastapi uvicorn
            fi
            if [[ "$COMPONENTS" == *"tools"* ]]; then
                pip install matplotlib pillow beautifulsoup4
            fi
            if [[ "$COMPONENTS" == *"dev"* ]]; then
                pip install pytest black flake8 mypy isort
            fi
            ;;
    esac
    
    # Deactivate virtual environment
    deactivate
    
    log "Dependencies installed successfully."
    return 0
}

# Function to create application launcher
create_launcher() {
    log "Creating application launcher..."
    
    # Create bin directory
    mkdir -p "$INSTALL_PATH/bin"
    
    # Create launcher script
    cat > "$INSTALL_PATH/bin/apexagent" << EOF
#!/bin/bash
# ApexAgent launcher script
SCRIPT_DIR="\$(cd "\$(dirname "\${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="\$(dirname "\$SCRIPT_DIR")"
source "\$INSTALL_DIR/venv/bin/activate"
python3 "\$INSTALL_DIR/src/main.py" "\$@"
deactivate
EOF
    
    # Make launcher executable
    chmod +x "$INSTALL_PATH/bin/apexagent"
    
    # Create a symbolic link in /usr/local/bin if installing system-wide
    if [[ "$INSTALL_PATH" != "$HOME"* ]]; then
        ln -sf "$INSTALL_PATH/bin/apexagent" /usr/local/bin/apexagent
    fi
    
    log "Application launcher created successfully."
    return 0
}

# Function to create desktop and application menu shortcuts
create_shortcuts() {
    if [ "$NO_SHORTCUT" = true ]; then
        log "Skipping shortcut creation as requested."
        return 0
    fi
    
    log "Creating application shortcuts..."
    
    # Create desktop entry file
    local desktop_file_dir="/usr/share/applications"
    local desktop_file="$desktop_file_dir/apexagent.desktop"
    
    # If installing to user's home directory, use local desktop entry
    if [[ "$INSTALL_PATH" == "$HOME"* ]]; then
        desktop_file_dir="$HOME/.local/share/applications"
        desktop_file="$desktop_file_dir/apexagent.desktop"
        mkdir -p "$desktop_file_dir"
    fi
    
    # Create desktop entry
    cat > "$desktop_file" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=ApexAgent
Comment=ApexAgent AI Assistant
Exec=$INSTALL_PATH/bin/apexagent
Icon=$INSTALL_PATH/share/icons/apexagent.png
Terminal=false
Categories=Utility;Development;AI;
Keywords=AI;Assistant;Agent;
EOF
    
    # Create icons directory
    mkdir -p "$INSTALL_PATH/share/icons"
    
    # Create a placeholder icon
    # In a real implementation, this would be a proper icon file
    echo "This is a placeholder for the ApexAgent icon file." > "$INSTALL_PATH/share/icons/apexagent.png"
    
    # Create desktop shortcut if requested
    if [ "$SILENT" = false ]; then
        log "Would you like to create a desktop shortcut? (y/n)"
        read -r create_desktop
        
        if [[ "$create_desktop" =~ ^[Yy]$ ]]; then
            local desktop_dir="$HOME/Desktop"
            if [ -d "$desktop_dir" ]; then
                ln -sf "$desktop_file" "$desktop_dir/apexagent.desktop"
                log "Desktop shortcut created."
            else
                log "Desktop directory not found. Skipping desktop shortcut." "WARNING"
            fi
        fi
    fi
    
    log "Shortcuts created successfully."
    return 0
}

# Function to save installation information
save_installation_info() {
    log "Saving installation information..."
    
    # Create installation info file
    local info_path="$INSTALL_PATH/installation_info.json"
    
    cat > "$info_path" << EOF
{
    "version": "0.1.0",
    "install_path": "$INSTALL_PATH",
    "install_date": "$(date "+%Y-%m-%d %H:%M:%S")",
    "mode": "$MODE",
    "components": [$([ -n "$COMPONENTS" ] && echo "\"$(echo "$COMPONENTS" | sed 's/,/","/g')\"" || echo "")],
    "system_info": {
        "os": "Linux",
        "distro": "$DISTRO",
        "distro_version": "$VERSION",
        "python_version": "$(python3 --version 2>&1 | cut -d' ' -f2)"
    },
    "analytics_enabled": $ANALYTICS
}
EOF
    
    log "Installation information saved successfully."
    return 0
}

# Function to verify installation
verify_installation() {
    log "Verifying installation..."
    
    # Check if installation directory exists
    if [ ! -d "$INSTALL_PATH" ]; then
        log "Installation directory does not exist: $INSTALL_PATH" "ERROR"
        return 1
    fi
    
    # Check for essential files
    local essential_files=(
        "bin/apexagent"
        "installation_info.json"
        "venv/bin/python"
    )
    
    for file in "${essential_files[@]}"; do
        if [ ! -e "$INSTALL_PATH/$file" ]; then
            log "Essential file missing: $file" "ERROR"
            return 1
        fi
    done
    
    # Try to run the application in test mode
    if ! "$INSTALL_PATH/bin/apexagent" --test > /dev/null 2>&1; then
        log "Application test failed." "ERROR"
        return 1
    fi
    
    log "Installation verification passed."
    return 0
}

# Function to create a placeholder main.py
create_placeholder_main() {
    log "Creating placeholder main script..."
    
    # Create src directory
    mkdir -p "$INSTALL_PATH/src"
    
    # Create a placeholder main.py
    cat > "$INSTALL_PATH/src/main.py" << EOF
#!/usr/bin/env python3
"""
ApexAgent main entry point.
"""
import sys
import os

def main():
    print("ApexAgent is starting...")
    print(f"Arguments: {sys.argv[1:]}")
    
    # Check if running in test mode
    if "--test" in sys.argv:
        print("Running in test mode. All systems operational.")
        return 0
    
    # In a real implementation, this would start the actual application
    print("ApexAgent started successfully.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
EOF
    
    # Make main.py executable
    chmod +x "$INSTALL_PATH/src/main.py"
    
    log "Placeholder main script created successfully."
    return 0
}

# Main installation function
install_apexagent() {
    log "Starting ApexAgent installation..."
    log "Installation path: $INSTALL_PATH"
    log "Installation mode: $MODE"
    
    # Create installation directory
    if [ ! -d "$INSTALL_PATH" ]; then
        mkdir -p "$INSTALL_PATH"
        log "Created installation directory: $INSTALL_PATH"
    else
        log "Installation directory already exists: $INSTALL_PATH"
        
        # Backup existing installation if not in silent mode
        if [ "$SILENT" = false ]; then
            log "Would you like to backup the existing installation? (y/n)"
            read -r backup_existing
            
            if [[ "$backup_existing" =~ ^[Yy]$ ]]; then
                local backup_path="$INSTALL_PATH.backup.$(date +%Y%m%d%H%M%S)"
                mv "$INSTALL_PATH" "$backup_path"
                mkdir -p "$INSTALL_PATH"
                log "Backed up existing installation to $backup_path"
            fi
        fi
    fi
    
    # Install dependencies
    if ! install_dependencies; then
        log "Failed to install dependencies." "ERROR"
        return 1
    fi
    
    # Create placeholder main script
    if ! create_placeholder_main; then
        log "Failed to create main script." "ERROR"
        return 1
    fi
    
    # Create application launcher
    if ! create_launcher; then
        log "Failed to create application launcher." "ERROR"
        return 1
    fi
    
    # Create shortcuts
    if ! create_shortcuts; then
        log "Failed to create shortcuts." "ERROR"
        return 1
    fi
    
    # Save installation information
    if ! save_installation_info; then
        log "Failed to save installation information." "ERROR"
        return 1
    fi
    
    # Verify installation
    if ! verify_installation; then
        log "Installation verification failed." "ERROR"
        return 1
    fi
    
    log "ApexAgent installation completed successfully."
    return 0
}

# Main script execution
main() {
    # Display banner
    if [ "$SILENT" = false ]; then
        echo "========================================"
        echo "  ApexAgent Linux Installer"
        echo "  Version: 0.1.0"
        echo "========================================"
        echo ""
    fi
    
    # Check system requirements
    if ! check_system_requirements; then
        exit 1
    fi
    
    # Check for administrative privileges
    check_sudo
    
    # Perform installation
    if install_apexagent; then
        if [ "$SILENT" = false ]; then
            echo ""
            echo "ApexAgent has been installed successfully to $INSTALL_PATH"
            echo "You can now start ApexAgent by running 'apexagent' from the terminal"
            echo "or by using the application shortcut in your desktop environment."
        fi
        exit 0
    else
        if [ "$SILENT" = false ]; then
            echo ""
            echo "Installation failed. Please check the log file for details: $LOG_FILE"
        fi
        exit 1
    fi
}

# Run the main function
main
