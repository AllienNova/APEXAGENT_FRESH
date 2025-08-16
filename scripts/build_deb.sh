#!/bin/bash
# Build DEB package

echo "Building DEB package..."

# Copy application files
cp -r "../../../apexagent_optimized/src/"* "apexagent-1.0.0/usr/share/apexagent/"
cp "../../../apexagent-standalone/apexagent_launcher.py" "apexagent-1.0.0/usr/share/apexagent/launcher.py"

# Build package
dpkg-deb --build "apexagent-1.0.0"

# Move to dist
mv "apexagent-1.0.0.deb" "../../../dist/linux/"

echo "DEB package created: dist/linux/apexagent-1.0.0.deb"
