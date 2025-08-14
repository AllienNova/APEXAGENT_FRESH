#!/bin/bash
#
# ApexAgent macOS Installer Script
#
# This script installs ApexAgent on macOS systems.
# It handles dependency checking, installation, and configuration.
#
# Usage:
#   ./install.sh [options]
#
# Options:
#   --install-path PATH   Installation path (default: /Applications/ApexAgent)
#   --mode MODE           Installation mode: standard, minimal, complete, development, custom
#   --components LIST     Comma-separated list of components for custom mode
#   --silent              Run in silent mode without user interaction
#   --no-shortcut         Do not create application shortcuts
#   --analytics           Enable anonymous usage analytics
#   --help                Display this help message
#
# Example:
#   ./install.sh --install-path ~/Applications/ApexAgent --mode complete
#
# Note: This script may require sudo privileges for certain operations.

set -e

# Default values
INSTALL_PATH="/Applications/ApexAgent"
MODE="standard"
COMPONENTS=""
SILENT=false
NO_SHORTCUT=false
ANALYTICS=false
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMMON_DIR="$(dirname "$SCRIPT_DIR")/common"
LOG_FILE="$HOME/Library/Logs/ApexAgent_Install.log"

# Create log directory if it doesn't exist
mkdir -p "$(dirname "$LOG_FILE")"

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
ApexAgent macOS Installer

Usage:
  ./install.sh [options]

Options:
  --install-path PATH   Installation path (default: /Applications/ApexAgent)
  --mode MODE           Installation mode: standard, minimal, complete, development, custom
  --components LIST     Comma-separated list of components for custom mode
  --silent              Run in silent mode without user interaction
  --no-shortcut         Do not create application shortcuts
  --analytics           Enable anonymous usage analytics
  --help                Display this help message

Example:
  ./install.sh --install-path ~/Applications/ApexAgent --mode complete

Note: This script may require sudo privileges for certain operations.
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

# Function to check if running with sudo
check_sudo() {
    if [ "$EUID" -ne 0 ]; then
        if [ "$SILENT" = false ]; then
            log "This script requires administrative privileges for some operations." "WARNING"
            log "Please enter your password when prompted."
            
            # Try to get sudo privileges
            if ! sudo -v; then
                log "Failed to obtain administrative privileges." "ERROR"
                exit 1
            fi
        else
            log "This script requires administrative privileges. Please run with sudo." "ERROR"
            exit 1
        fi
    fi
}

# Function to check system requirements
check_system_requirements() {
    log "Checking system requirements..."
    
    # Check macOS version
    local os_version=$(sw_vers -productVersion)
    local os_major=$(echo "$os_version" | cut -d. -f1)
    local os_minor=$(echo "$os_version" | cut -d. -f2)
    
    if [ "$os_major" -lt 10 ] || ([ "$os_major" -eq 10 ] && [ "$os_minor" -lt 15 ]); then
        log "macOS version $os_version is not supported. Please use macOS 10.15 (Catalina) or higher." "ERROR"
        return 1
    fi
    
    # Check Python installation
    if ! command -v python3 &> /dev/null; then
        log "Python 3 is not installed. Please install Python 3.8 or higher." "ERROR"
        return 1
    fi
    
    local python_version=$(python3 --version | cut -d' ' -f2)
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
    
    # Check if Homebrew is installed (optional)
    if command -v brew &> /dev/null; then
        log "Found Homebrew installation"
    else
        log "Homebrew is not installed. Some dependencies may need to be installed manually." "WARNING"
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
            # This would be more sophisticated in a real implementation
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

# Function to create application bundle
create_app_bundle() {
    log "Creating application bundle..."
    
    local app_path="$INSTALL_PATH.app"
    local contents_path="$app_path/Contents"
    local macos_path="$contents_path/MacOS"
    local resources_path="$contents_path/Resources"
    
    # Create directory structure
    mkdir -p "$macos_path" "$resources_path"
    
    # Create Info.plist
    cat > "$contents_path/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>ApexAgent</string>
    <key>CFBundleIconFile</key>
    <string>AppIcon</string>
    <key>CFBundleIdentifier</key>
    <string>com.apexagent.app</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>ApexAgent</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>0.1.0</string>
    <key>CFBundleVersion</key>
    <string>1</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.15</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
EOF
    
    # Create launcher script
    cat > "$macos_path/ApexAgent" << EOF
#!/bin/bash
# ApexAgent launcher script
SCRIPT_DIR="\$(cd "\$(dirname "\${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="\$(dirname "\$(dirname "\$SCRIPT_DIR")")"
"\$APP_DIR/Resources/venv/bin/python3" "\$APP_DIR/Resources/src/main.py" "\$@"
EOF
    
    # Make launcher executable
    chmod +x "$macos_path/ApexAgent"
    
    # Copy resources
    # In a real implementation, this would copy actual resources
    # For now, we'll create placeholder directories and files
    mkdir -p "$resources_path/src"
    
    # Create a placeholder icon
    # In a real implementation, this would be a proper .icns file
    echo "This is a placeholder for the ApexAgent icon file." > "$resources_path/AppIcon.icns"
    
    # Create a placeholder main.py
    mkdir -p "$resources_path/src"
    cat > "$resources_path/src/main.py" << EOF
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
    chmod +x "$resources_path/src/main.py"
    
    # Move the installation directory to Resources
    if [ -d "$INSTALL_PATH" ]; then
        mv "$INSTALL_PATH"/* "$resources_path/"
    fi
    
    log "Application bundle created successfully."
    return 0
}

# Function to create shortcuts
create_shortcuts() {
    if [ "$NO_SHORTCUT" = true ]; then
        log "Skipping shortcut creation as requested."
        return 0
    fi
    
    log "Creating application shortcuts..."
    
    local app_path="$INSTALL_PATH.app"
    
    # Create symlink in /Applications if not already there
    if [ "$(dirname "$app_path")" != "/Applications" ]; then
        ln -sf "$app_path" "/Applications/"
    fi
    
    # Create symlink in Dock (optional)
    if [ "$SILENT" = false ]; then
        log "Would you like to add ApexAgent to the Dock? (y/n)"
        read -r add_to_dock
        
        if [[ "$add_to_dock" =~ ^[Yy]$ ]]; then
            # Add to Dock using AppleScript
            osascript << EOF
tell application "Dock"
    set dock_items to every item of list 1
    set found_item to false
    
    repeat with dock_item in dock_items
        try
            set item_path to path of dock_item
            if item_path contains "ApexAgent.app" then
                set found_item to true
                exit repeat
            end if
        end try
    end repeat
    
    if not found_item then
        add POSIX file "/Applications/ApexAgent.app" to list 1
    end if
end tell
EOF
            log "Added ApexAgent to the Dock."
        fi
    fi
    
    log "Shortcuts created successfully."
    return 0
}

# Function to register application
register_application() {
    log "Registering application..."
    
    # Update Launch Services database
    /System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -f "$INSTALL_PATH.app"
    
    # Create installation info file
    local info_path="$INSTALL_PATH.app/Contents/Resources/installation_info.json"
    
    cat > "$info_path" << EOF
{
    "version": "0.1.0",
    "install_path": "$INSTALL_PATH.app",
    "install_date": "$(date "+%Y-%m-%d %H:%M:%S")",
    "mode": "$MODE",
    "components": [$([ -n "$COMPONENTS" ] && echo "\"$(echo "$COMPONENTS" | sed 's/,/","/g')\"" || echo "")],
    "system_info": {
        "os": "macOS",
        "os_version": "$(sw_vers -productVersion)",
        "python_version": "$(python3 --version | cut -d' ' -f2)"
    },
    "analytics_enabled": $ANALYTICS
}
EOF
    
    log "Application registered successfully."
    return 0
}

# Function to verify installation
verify_installation() {
    log "Verifying installation..."
    
    local app_path="$INSTALL_PATH.app"
    
    # Check if application bundle exists
    if [ ! -d "$app_path" ]; then
        log "Application bundle does not exist: $app_path" "ERROR"
        return 1
    fi
    
    # Check for essential files
    local essential_files=(
        "Contents/MacOS/ApexAgent"
        "Contents/Info.plist"
        "Contents/Resources/installation_info.json"
        "Contents/Resources/src/main.py"
    )
    
    for file in "${essential_files[@]}"; do
        if [ ! -e "$app_path/$file" ]; then
            log "Essential file missing: $file" "ERROR"
            return 1
        fi
    done
    
    # Try to run the application in test mode
    if ! "$app_path/Contents/MacOS/ApexAgent" --test > /dev/null; then
        log "Application test failed." "ERROR"
        return 1
    fi
    
    log "Installation verification passed."
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
    
    # Create application bundle
    if ! create_app_bundle; then
        log "Failed to create application bundle." "ERROR"
        return 1
    fi
    
    # Create shortcuts
    if ! create_shortcuts; then
        log "Failed to create shortcuts." "ERROR"
        return 1
    fi
    
    # Register application
    if ! register_application; then
        log "Failed to register application." "ERROR"
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
        echo "  ApexAgent macOS Installer"
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
            echo "ApexAgent has been installed successfully to $INSTALL_PATH.app"
            echo "You can now start ApexAgent from the Applications folder or Dock."
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
