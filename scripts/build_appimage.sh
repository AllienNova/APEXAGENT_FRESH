#!/bin/bash
# Build AppImage

echo "Building AppImage..."

# Copy application files
cp -r "../../../apexagent_optimized/src/"* "ApexAgent.AppDir/usr/share/apexagent/"
cp "../../../apexagent-standalone/apexagent_launcher.py" "ApexAgent.AppDir/usr/share/apexagent/launcher.py"

# Download appimagetool if not exists
if [ ! -f "appimagetool-x86_64.AppImage" ]; then
    wget "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
    chmod +x appimagetool-x86_64.AppImage
fi

# Build AppImage
./appimagetool-x86_64.AppImage "ApexAgent.AppDir" "../../../dist/linux/ApexAgent-1.0.0-x86_64.AppImage"

echo "AppImage created: dist/linux/ApexAgent-1.0.0-x86_64.AppImage"
