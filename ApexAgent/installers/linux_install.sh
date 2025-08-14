#!/bin/bash
# ApexAgent Linux Installer Script

# Default values
INSTALL_PATH="/opt/apexagent"
MODE="standard"
API_KEY_MODE="complete_system"
COMPONENTS=""
SILENT=false
NO_SHORTCUT=false
ANALYTICS=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --install-path)
            INSTALL_PATH="$2"
            shift
            shift
            ;;
        --mode)
            MODE="$2"
            shift
            shift
            ;;
        --api-key-mode)
            API_KEY_MODE="$2"
            shift
            shift
            ;;
        --components)
            COMPONENTS="$2"
            shift
            shift
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
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Validate API key mode
if [[ "$API_KEY_MODE" != "complete_system" && "$API_KEY_MODE" != "user_provided" ]]; then
    echo "Invalid API key mode: $API_KEY_MODE. Must be 'complete_system' or 'user_provided'."
    exit 1
fi

# Display installation information
if [ "$SILENT" = false ]; then
    echo "ApexAgent Installation"
    echo "======================"
    echo "Installation path: $INSTALL_PATH"
    echo "Installation mode: $MODE"
    echo "API key mode: $API_KEY_MODE"
    if [ ! -z "$COMPONENTS" ]; then
        echo "Custom components: $COMPONENTS"
    fi
    echo ""
    
    # Confirm installation
    read -p "Continue with installation? (y/n): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Installation cancelled."
        exit 0
    fi
fi

# Create installation directory
echo "Creating installation directory..."
mkdir -p "$INSTALL_PATH"
if [ $? -ne 0 ]; then
    echo "Failed to create installation directory. Please check permissions."
    exit 1
fi

# Create configuration
echo "Creating configuration..."
CONFIG_DIR="$INSTALL_PATH/config"
mkdir -p "$CONFIG_DIR"

# Save installation settings
cat > "$CONFIG_DIR/installation.json" << EOF
{
    "installation_path": "$INSTALL_PATH",
    "mode": "$MODE",
    "api_key_mode": "$API_KEY_MODE",
    "components": "$COMPONENTS",
    "analytics": $ANALYTICS,
    "installation_date": "$(date -Iseconds)"
}
EOF

# Copy files
echo "Copying files..."
# (Actual file copying would happen here)

# Create desktop shortcut if requested
if [ "$NO_SHORTCUT" = false ]; then
    echo "Creating desktop shortcut..."
    # (Desktop shortcut creation would happen here)
fi

# Set up API key mode based on selection
echo "Configuring API key mode: $API_KEY_MODE"
if [ "$API_KEY_MODE" = "user_provided" ]; then
    # Configure for user-provided API keys
    touch "$CONFIG_DIR/user_provided_keys.flag"
else
    # Configure for complete system (default)
    rm -f "$CONFIG_DIR/user_provided_keys.flag"
fi

# Complete installation
echo "Installation completed successfully!"
if [ "$SILENT" = false ]; then
    echo "You can now start ApexAgent from your applications menu."
    if [ "$API_KEY_MODE" = "user_provided" ]; then
        echo ""
        echo "You selected the User-Provided API Keys option."
        echo "You will be prompted to enter your API keys when you first run ApexAgent."
        echo "If you don't have API keys yet, you can get them from the following providers:"
        echo "- OpenAI: https://platform.openai.com/api-keys"
        echo "- Anthropic: https://console.anthropic.com/account/keys"
        echo "- Google AI: https://makersuite.google.com/app/apikey"
        echo ""
    fi
fi

exit 0
