#!/bin/bash
# Build portable version

echo "Creating portable version..."

PORTABLE_NAME="ApexAgent-1.0.0-Portable"

# Create portable directory
mkdir -p "$PORTABLE_NAME"

# Copy launcher
cp "ApexAgent_Portable.py" "$PORTABLE_NAME/"

# Copy application files
cp -r "../../apexagent_optimized/src/"* "$PORTABLE_NAME/"
cp "../../apexagent-standalone/apexagent_launcher.py" "$PORTABLE_NAME/"

# Create README
cat > "$PORTABLE_NAME/README.txt" << 'README_EOF'
ApexAgent Portable Version 1.0.0

This is a portable version of ApexAgent that runs without installation.

REQUIREMENTS:
- Python 3.7 or later
- Internet connection for initial setup

USAGE:
1. Ensure Python 3 is installed on your system
2. Run: python3 ApexAgent_Portable.py
3. The application will start automatically

DATA STORAGE:
All application data is stored in the 'data' folder within this directory.
You can move this entire folder to any location or USB drive.

FIRST RUN:
On first run, the application will automatically install required Python
packages. This requires an internet connection.

SUPPORT:
Visit: https://github.com/AllienNova/ApexAgent
README_EOF

# Create Windows batch file
cat > "$PORTABLE_NAME/ApexAgent.bat" << 'BAT_EOF'
@echo off
echo Starting ApexAgent Portable...
python ApexAgent_Portable.py
pause
BAT_EOF

# Create archive
tar czf "../../dist/portable/$PORTABLE_NAME.tar.gz" "$PORTABLE_NAME"
zip -r "../../dist/portable/$PORTABLE_NAME.zip" "$PORTABLE_NAME"

echo "Portable version created:"
echo "  - dist/portable/$PORTABLE_NAME.tar.gz"
echo "  - dist/portable/$PORTABLE_NAME.zip"
