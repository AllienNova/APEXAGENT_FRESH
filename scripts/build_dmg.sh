#!/bin/bash
# Build macOS DMG installer

APP_NAME="ApexAgent"
VERSION="1.0.0"
DMG_NAME="$APP_NAME-$VERSION"

echo "Building macOS DMG installer..."

# Copy application files
cp -r "../../apexagent_optimized/src" "$APP_NAME.app/Contents/Resources/backend"
cp "../../apexagent-standalone/apexagent_launcher.py" "$APP_NAME.app/Contents/Resources/launcher.py"

# Create temporary DMG
hdiutil create -size 200m -fs HFS+ -volname "$APP_NAME" "temp-$DMG_NAME.dmg"

# Mount the DMG
hdiutil attach "temp-$DMG_NAME.dmg" -mountpoint "/Volumes/$APP_NAME"

# Copy app to DMG
cp -R "$APP_NAME.app" "/Volumes/$APP_NAME/"

# Create Applications symlink
ln -s /Applications "/Volumes/$APP_NAME/Applications"

# Add background and styling (optional)
# mkdir "/Volumes/$APP_NAME/.background"
# cp background.png "/Volumes/$APP_NAME/.background/"

# Unmount DMG
hdiutil detach "/Volumes/$APP_NAME"

# Convert to compressed DMG
hdiutil convert "temp-$DMG_NAME.dmg" -format UDZO -o "../../dist/macos/$DMG_NAME.dmg"

# Clean up
rm "temp-$DMG_NAME.dmg"

echo "macOS installer created: dist/macos/$DMG_NAME.dmg"
