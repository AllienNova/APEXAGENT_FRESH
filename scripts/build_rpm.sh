#!/bin/bash
# Build RPM package

echo "Building RPM package..."

# Create source tarball
mkdir -p "apexagent-1.0.0"
cp -r "../../../apexagent_optimized/src" "apexagent-1.0.0/"
cp "../../../apexagent-standalone/apexagent_launcher.py" "apexagent-1.0.0/launcher.py"

tar czf "apexagent-1.0.0.tar.gz" "apexagent-1.0.0"

# Build RPM
rpmbuild -ta "apexagent-1.0.0.tar.gz" --define "_topdir $(pwd)/rpmbuild"

# Move to dist
mkdir -p "../../../dist/linux"
cp rpmbuild/RPMS/noarch/apexagent-1.0.0-1.*.rpm "../../../dist/linux/"

echo "RPM package created in dist/linux/"
