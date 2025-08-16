#!/usr/bin/env python3
"""
ApexAgent Installer Builder
Creates platform-specific installers for Windows, macOS, and Linux
"""

import os
import sys
import shutil
import subprocess
import tempfile
import json
from pathlib import Path
import argparse

class InstallerBuilder:
    def __init__(self):
        self.app_name = "ApexAgent"
        self.version = "1.0.0"
        self.description = "World's First Hybrid Autonomous AI System"
        self.author = "ApexAgent Team"
        self.url = "https://github.com/AllienNova/ApexAgent"
        
        self.build_dir = Path("build")
        self.dist_dir = Path("dist")
        self.source_dir = Path("../apexagent_optimized")
        
        self.setup_directories()
    
    def setup_directories(self):
        """Setup build directories."""
        self.build_dir.mkdir(exist_ok=True)
        self.dist_dir.mkdir(exist_ok=True)
        
        # Create platform-specific directories
        for platform in ['windows', 'macos', 'linux']:
            (self.build_dir / platform).mkdir(exist_ok=True)
            (self.dist_dir / platform).mkdir(exist_ok=True)
    
    def create_windows_installer(self):
        """Create Windows MSI installer using WiX Toolset."""
        print("Creating Windows installer...")
        
        windows_dir = self.build_dir / "windows"
        
        # Create WiX configuration
        wxs_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<Wix xmlns="http://schemas.microsoft.com/wix/2006/wi">
    <Product Id="*" 
             Name="{self.app_name}" 
             Language="1033" 
             Version="{self.version}" 
             Manufacturer="{self.author}" 
             UpgradeCode="{{12345678-1234-1234-1234-123456789012}}">
        
        <Package InstallerVersion="200" 
                 Compressed="yes" 
                 InstallScope="perMachine" 
                 Description="{self.description}" />
        
        <MajorUpgrade DowngradeErrorMessage="A newer version of {self.app_name} is already installed." />
        
        <MediaTemplate EmbedCab="yes" />
        
        <Feature Id="ProductFeature" Title="{self.app_name}" Level="1">
            <ComponentGroupRef Id="ProductComponents" />
        </Feature>
        
        <Directory Id="TARGETDIR" Name="SourceDir">
            <Directory Id="ProgramFilesFolder">
                <Directory Id="INSTALLFOLDER" Name="{self.app_name}" />
            </Directory>
            <Directory Id="ProgramMenuFolder">
                <Directory Id="ApplicationProgramsFolder" Name="{self.app_name}" />
            </Directory>
            <Directory Id="DesktopFolder" Name="Desktop" />
        </Directory>
        
        <ComponentGroup Id="ProductComponents" Directory="INSTALLFOLDER">
            <Component Id="MainExecutable" Guid="{{87654321-4321-4321-4321-210987654321}}">
                <File Id="ApexAgentExe" 
                      Source="ApexAgent.exe" 
                      KeyPath="yes" 
                      Checksum="yes">
                    <Shortcut Id="ApplicationStartMenuShortcut" 
                              Directory="ApplicationProgramsFolder" 
                              Name="{self.app_name}" 
                              WorkingDirectory="INSTALLFOLDER" 
                              Icon="ApexAgent.exe" 
                              IconIndex="0" 
                              Advertise="yes" />
                    <Shortcut Id="ApplicationDesktopShortcut" 
                              Directory="DesktopFolder" 
                              Name="{self.app_name}" 
                              WorkingDirectory="INSTALLFOLDER" 
                              Icon="ApexAgent.exe" 
                              IconIndex="0" 
                              Advertise="yes" />
                </File>
            </Component>
            
            <Component Id="BackendFiles" Guid="{{11111111-2222-3333-4444-555555555555}}">
                <File Id="BackendMain" Source="backend/main_production.py" KeyPath="yes" />
                <!-- Add more backend files here -->
            </Component>
        </ComponentGroup>
        
        <Icon Id="ApexAgent.exe" SourceFile="ApexAgent.exe" />
        <Property Id="ARPPRODUCTICON" Value="ApexAgent.exe" />
        <Property Id="ARPHELPLINK" Value="{self.url}" />
        <Property Id="ARPURLINFOABOUT" Value="{self.url}" />
        <Property Id="ARPNOREPAIR" Value="1" />
        <Property Id="ARPNOMODIFY" Value="1" />
        
        <UI>
            <UIRef Id="WixUI_InstallDir" />
        </UI>
        
        <WixVariable Id="WixUILicenseRtf" Value="License.rtf" />
        
    </Product>
</Wix>'''
        
        with open(windows_dir / "ApexAgent.wxs", "w") as f:
            f.write(wxs_content)
        
        # Create license file
        license_content = f'''{{\\rtf1\\ansi\\deff0 {{\\fonttbl {{\\f0 Times New Roman;}}}}
\\f0\\fs24 {self.app_name} License Agreement\\par
\\par
This software is provided "as is" without warranty of any kind.\\par
\\par
© 2025 {self.author}\\par
}}'''
        
        with open(windows_dir / "License.rtf", "w") as f:
            f.write(license_content)
        
        # Create batch script to build MSI
        batch_script = f'''@echo off
echo Building {self.app_name} Windows Installer...

REM Check if WiX is installed
where candle >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo WiX Toolset not found. Please install WiX Toolset v3.11 or later.
    echo Download from: https://wixtoolset.org/releases/
    pause
    exit /b 1
)

REM Copy application files
copy "..\\..\\apexagent-standalone\\dist\\ApexAgent.exe" .
xcopy "..\\..\\apexagent_optimized\\src" backend\\ /E /I /Y

REM Build the installer
candle ApexAgent.wxs
if %ERRORLEVEL% NEQ 0 (
    echo Failed to compile WiX source
    pause
    exit /b 1
)

light -ext WixUIExtension ApexAgent.wixobj -out "..\\..\\dist\\windows\\{self.app_name}-{self.version}.msi"
if %ERRORLEVEL% NEQ 0 (
    echo Failed to link MSI
    pause
    exit /b 1
)

echo Windows installer created successfully!
echo Location: dist\\windows\\{self.app_name}-{self.version}.msi
pause
'''
        
        with open(windows_dir / "build_msi.bat", "w") as f:
            f.write(batch_script)
        
        print(f"Windows installer configuration created in {windows_dir}")
        print("To build: Run build_msi.bat on Windows with WiX Toolset installed")
    
    def create_macos_installer(self):
        """Create macOS DMG installer."""
        print("Creating macOS installer...")
        
        macos_dir = self.build_dir / "macos"
        
        # Create app bundle structure
        app_bundle = macos_dir / f"{self.app_name}.app"
        contents_dir = app_bundle / "Contents"
        macos_bin_dir = contents_dir / "MacOS"
        resources_dir = contents_dir / "Resources"
        
        for dir_path in [contents_dir, macos_bin_dir, resources_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Create Info.plist
        info_plist = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>{self.app_name}</string>
    <key>CFBundleIdentifier</key>
    <string>com.apexagent.desktop</string>
    <key>CFBundleName</key>
    <string>{self.app_name}</string>
    <key>CFBundleVersion</key>
    <string>{self.version}</string>
    <key>CFBundleShortVersionString</key>
    <string>{self.version}</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleSignature</key>
    <string>APEX</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.14</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>NSAppTransportSecurity</key>
    <dict>
        <key>NSAllowsArbitraryLoads</key>
        <true/>
    </dict>
</dict>
</plist>'''
        
        with open(contents_dir / "Info.plist", "w") as f:
            f.write(info_plist)
        
        # Create launcher script
        launcher_script = f'''#!/bin/bash
# {self.app_name} macOS Launcher

SCRIPT_DIR="$( cd "$( dirname "${{BASH_SOURCE[0]}}" )" &> /dev/null && pwd )"
APP_DIR="$SCRIPT_DIR/../Resources"

# Set up environment
export PYTHONPATH="$APP_DIR/backend:$PYTHONPATH"

# Start the application
cd "$APP_DIR"
python3 launcher.py
'''
        
        launcher_path = macos_bin_dir / self.app_name
        with open(launcher_path, "w") as f:
            f.write(launcher_script)
        
        # Make launcher executable
        os.chmod(launcher_path, 0o755)
        
        # Create DMG build script
        dmg_script = f'''#!/bin/bash
# Build macOS DMG installer

APP_NAME="{self.app_name}"
VERSION="{self.version}"
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
'''
        
        with open(macos_dir / "build_dmg.sh", "w") as f:
            f.write(dmg_script)
        
        os.chmod(macos_dir / "build_dmg.sh", 0o755)
        
        print(f"macOS installer configuration created in {macos_dir}")
        print("To build: Run build_dmg.sh on macOS")
    
    def create_linux_installers(self):
        """Create Linux installers (DEB, RPM, AppImage)."""
        print("Creating Linux installers...")
        
        linux_dir = self.build_dir / "linux"
        
        # Create DEB package structure
        self.create_deb_package(linux_dir)
        
        # Create RPM spec file
        self.create_rpm_spec(linux_dir)
        
        # Create AppImage
        self.create_appimage(linux_dir)
        
        # Create universal install script
        self.create_universal_installer(linux_dir)
    
    def create_deb_package(self, linux_dir):
        """Create Debian package structure."""
        deb_dir = linux_dir / "deb"
        
        # Create package structure
        pkg_dir = deb_dir / f"{self.app_name.lower()}-{self.version}"
        debian_dir = pkg_dir / "DEBIAN"
        usr_dir = pkg_dir / "usr"
        bin_dir = usr_dir / "bin"
        share_dir = usr_dir / "share"
        app_dir = share_dir / self.app_name.lower()
        desktop_dir = share_dir / "applications"
        
        for dir_path in [debian_dir, bin_dir, app_dir, desktop_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Create control file
        control_content = f'''Package: {self.app_name.lower()}
Version: {self.version}
Section: utils
Priority: optional
Architecture: amd64
Depends: python3, python3-tk, python3-pip
Maintainer: {self.author} <support@apexagent.com>
Description: {self.description}
 ApexAgent is the world's first hybrid autonomous AI system that combines
 local and cloud processing for unprecedented performance, security, and
 cost efficiency.
 .
 Features:
  * Hybrid AI processing (local + cloud)
  * Enterprise-grade security
  * Real-time monitoring
  * Professional interface
  * Multi-provider AI integration
Homepage: {self.url}
'''
        
        with open(debian_dir / "control", "w") as f:
            f.write(control_content)
        
        # Create postinst script
        postinst_content = f'''#!/bin/bash
# Post-installation script for {self.app_name}

set -e

# Install Python dependencies
pip3 install flask flask-cors redis requests

# Create desktop entry
update-desktop-database /usr/share/applications

# Set permissions
chmod +x /usr/bin/{self.app_name.lower()}

echo "{self.app_name} installed successfully!"
echo "Run '{self.app_name.lower()}' to start the application."
'''
        
        postinst_path = debian_dir / "postinst"
        with open(postinst_path, "w") as f:
            f.write(postinst_content)
        os.chmod(postinst_path, 0o755)
        
        # Create launcher script
        launcher_content = f'''#!/bin/bash
# {self.app_name} Launcher Script

APP_DIR="/usr/share/{self.app_name.lower()}"
cd "$APP_DIR"
python3 launcher.py "$@"
'''
        
        with open(bin_dir / self.app_name.lower(), "w") as f:
            f.write(launcher_content)
        
        # Create desktop entry
        desktop_content = f'''[Desktop Entry]
Version=1.0
Type=Application
Name={self.app_name}
Comment={self.description}
Exec={self.app_name.lower()}
Icon={self.app_name.lower()}
Terminal=false
Categories=Office;Development;
Keywords=AI;Artificial Intelligence;Automation;
StartupNotify=true
'''
        
        with open(desktop_dir / f"{self.app_name.lower()}.desktop", "w") as f:
            f.write(desktop_content)
        
        # Create build script
        build_script = f'''#!/bin/bash
# Build DEB package

echo "Building DEB package..."

# Copy application files
cp -r "../../../apexagent_optimized/src/"* "{self.app_name.lower()}-{self.version}/usr/share/{self.app_name.lower()}/"
cp "../../../apexagent-standalone/apexagent_launcher.py" "{self.app_name.lower()}-{self.version}/usr/share/{self.app_name.lower()}/launcher.py"

# Build package
dpkg-deb --build "{self.app_name.lower()}-{self.version}"

# Move to dist
mv "{self.app_name.lower()}-{self.version}.deb" "../../../dist/linux/"

echo "DEB package created: dist/linux/{self.app_name.lower()}-{self.version}.deb"
'''
        
        with open(deb_dir / "build_deb.sh", "w") as f:
            f.write(build_script)
        os.chmod(deb_dir / "build_deb.sh", 0o755)
    
    def create_rpm_spec(self, linux_dir):
        """Create RPM spec file."""
        rpm_dir = linux_dir / "rpm"
        rpm_dir.mkdir(exist_ok=True)
        
        spec_content = f'''Name:           {self.app_name.lower()}
Version:        {self.version}
Release:        1%{{?dist}}
Summary:        {self.description}

License:        MIT
URL:            {self.url}
Source0:        %{{name}}-%{{version}}.tar.gz

BuildArch:      noarch
Requires:       python3, python3-tkinter, python3-pip

%description
ApexAgent is the world's first hybrid autonomous AI system that combines
local and cloud processing for unprecedented performance, security, and
cost efficiency.

Features:
- Hybrid AI processing (local + cloud)
- Enterprise-grade security
- Real-time monitoring
- Professional interface
- Multi-provider AI integration

%prep
%setup -q

%build
# Nothing to build

%install
rm -rf $RPM_BUILD_ROOT

# Create directories
mkdir -p $RPM_BUILD_ROOT/usr/bin
mkdir -p $RPM_BUILD_ROOT/usr/share/{self.app_name.lower()}
mkdir -p $RPM_BUILD_ROOT/usr/share/applications

# Install files
cp -r src/* $RPM_BUILD_ROOT/usr/share/{self.app_name.lower()}/
cp launcher.py $RPM_BUILD_ROOT/usr/share/{self.app_name.lower()}/

# Install launcher
cat > $RPM_BUILD_ROOT/usr/bin/{self.app_name.lower()} << 'EOF'
#!/bin/bash
APP_DIR="/usr/share/{self.app_name.lower()}"
cd "$APP_DIR"
python3 launcher.py "$@"
EOF

chmod +x $RPM_BUILD_ROOT/usr/bin/{self.app_name.lower()}

# Install desktop entry
cat > $RPM_BUILD_ROOT/usr/share/applications/{self.app_name.lower()}.desktop << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name={self.app_name}
Comment={self.description}
Exec={self.app_name.lower()}
Icon={self.app_name.lower()}
Terminal=false
Categories=Office;Development;
Keywords=AI;Artificial Intelligence;Automation;
StartupNotify=true
EOF

%files
/usr/bin/{self.app_name.lower()}
/usr/share/{self.app_name.lower()}/*
/usr/share/applications/{self.app_name.lower()}.desktop

%post
# Install Python dependencies
pip3 install flask flask-cors redis requests

# Update desktop database
update-desktop-database /usr/share/applications

echo "{self.app_name} installed successfully!"
echo "Run '{self.app_name.lower()}' to start the application."

%changelog
* Wed Jan 01 2025 {self.author} <support@apexagent.com> - {self.version}-1
- Initial release
'''
        
        with open(rpm_dir / f"{self.app_name.lower()}.spec", "w") as f:
            f.write(spec_content)
        
        # Create RPM build script
        build_script = f'''#!/bin/bash
# Build RPM package

echo "Building RPM package..."

# Create source tarball
mkdir -p "{self.app_name.lower()}-{self.version}"
cp -r "../../../apexagent_optimized/src" "{self.app_name.lower()}-{self.version}/"
cp "../../../apexagent-standalone/apexagent_launcher.py" "{self.app_name.lower()}-{self.version}/launcher.py"

tar czf "{self.app_name.lower()}-{self.version}.tar.gz" "{self.app_name.lower()}-{self.version}"

# Build RPM
rpmbuild -ta "{self.app_name.lower()}-{self.version}.tar.gz" --define "_topdir $(pwd)/rpmbuild"

# Move to dist
mkdir -p "../../../dist/linux"
cp rpmbuild/RPMS/noarch/{self.app_name.lower()}-{self.version}-1.*.rpm "../../../dist/linux/"

echo "RPM package created in dist/linux/"
'''
        
        with open(rpm_dir / "build_rpm.sh", "w") as f:
            f.write(build_script)
        os.chmod(rpm_dir / "build_rpm.sh", 0o755)
    
    def create_appimage(self, linux_dir):
        """Create AppImage."""
        appimage_dir = linux_dir / "appimage"
        appdir = appimage_dir / f"{self.app_name}.AppDir"
        
        # Create AppDir structure
        usr_dir = appdir / "usr"
        bin_dir = usr_dir / "bin"
        share_dir = usr_dir / "share"
        app_share_dir = share_dir / self.app_name.lower()
        
        for dir_path in [appdir, bin_dir, app_share_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Create AppRun
        apprun_content = f'''#!/bin/bash
# AppImage launcher for {self.app_name}

HERE="$(dirname "$(readlink -f "${{0}}")")"
export PATH="$HERE/usr/bin:$PATH"
export LD_LIBRARY_PATH="$HERE/usr/lib:$LD_LIBRARY_PATH"

cd "$HERE/usr/share/{self.app_name.lower()}"
python3 launcher.py "$@"
'''
        
        apprun_path = appdir / "AppRun"
        with open(apprun_path, "w") as f:
            f.write(apprun_content)
        os.chmod(apprun_path, 0o755)
        
        # Create desktop file
        desktop_content = f'''[Desktop Entry]
Version=1.0
Type=Application
Name={self.app_name}
Comment={self.description}
Exec=AppRun
Icon={self.app_name.lower()}
Terminal=false
Categories=Office;Development;
'''
        
        with open(appdir / f"{self.app_name.lower()}.desktop", "w") as f:
            f.write(desktop_content)
        
        # Create AppImage build script
        build_script = f'''#!/bin/bash
# Build AppImage

echo "Building AppImage..."

# Copy application files
cp -r "../../../apexagent_optimized/src/"* "{self.app_name}.AppDir/usr/share/{self.app_name.lower()}/"
cp "../../../apexagent-standalone/apexagent_launcher.py" "{self.app_name}.AppDir/usr/share/{self.app_name.lower()}/launcher.py"

# Download appimagetool if not exists
if [ ! -f "appimagetool-x86_64.AppImage" ]; then
    wget "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
    chmod +x appimagetool-x86_64.AppImage
fi

# Build AppImage
./appimagetool-x86_64.AppImage "{self.app_name}.AppDir" "../../../dist/linux/{self.app_name}-{self.version}-x86_64.AppImage"

echo "AppImage created: dist/linux/{self.app_name}-{self.version}-x86_64.AppImage"
'''
        
        with open(appimage_dir / "build_appimage.sh", "w") as f:
            f.write(build_script)
        os.chmod(appimage_dir / "build_appimage.sh", 0o755)
    
    def create_universal_installer(self, linux_dir):
        """Create universal Linux installer script."""
        installer_content = f'''#!/bin/bash
# Universal {self.app_name} Installer for Linux

set -e

APP_NAME="{self.app_name}"
APP_VERSION="{self.version}"
INSTALL_DIR="/opt/{self.app_name.lower()}"
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
cat > "$BIN_DIR/{self.app_name.lower()}" << 'LAUNCHER_SCRIPT_EOF'
#!/bin/bash
cd "$INSTALL_DIR"
python3 launcher.py "$@"
LAUNCHER_SCRIPT_EOF

chmod +x "$BIN_DIR/{self.app_name.lower()}"

# Create desktop entry
echo "Creating desktop entry..."
cat > "$DESKTOP_DIR/{self.app_name.lower()}.desktop" << 'DESKTOP_EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name={self.app_name}
Comment={self.description}
Exec={self.app_name.lower()}
Icon={self.app_name.lower()}
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
echo "  1. Typing '{self.app_name.lower()}' in terminal"
echo "  2. Finding it in your applications menu"
echo "  3. Running: $BIN_DIR/{self.app_name.lower()}"
echo
echo "To uninstall, run: sudo rm -rf $INSTALL_DIR $BIN_DIR/{self.app_name.lower()} $DESKTOP_DIR/{self.app_name.lower()}.desktop"
echo
'''
        
        with open(linux_dir / "install.sh", "w") as f:
            f.write(installer_content)
        os.chmod(linux_dir / "install.sh", 0o755)
        
        print(f"Linux installers configuration created in {linux_dir}")
    
    def create_portable_version(self):
        """Create portable version that runs without installation."""
        print("Creating portable version...")
        
        portable_dir = self.build_dir / "portable"
        portable_dir.mkdir(exist_ok=True)
        
        # Create portable launcher
        portable_launcher = f'''#!/usr/bin/env python3
"""
{self.app_name} Portable Launcher
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
    print(f"Error: {{e}}")
    print("ApexAgent portable installation is incomplete.")
    input("Press Enter to exit...")
    sys.exit(1)
except Exception as e:
    print(f"Error starting ApexAgent: {{e}}")
    input("Press Enter to exit...")
    sys.exit(1)
'''
        
        with open(portable_dir / "ApexAgent_Portable.py", "w") as f:
            f.write(portable_launcher)
        
        # Create portable build script
        build_script = f'''#!/bin/bash
# Build portable version

echo "Creating portable version..."

PORTABLE_NAME="{self.app_name}-{self.version}-Portable"

# Create portable directory
mkdir -p "$PORTABLE_NAME"

# Copy launcher
cp "ApexAgent_Portable.py" "$PORTABLE_NAME/"

# Copy application files
cp -r "../../apexagent_optimized/src/"* "$PORTABLE_NAME/"
cp "../../apexagent-standalone/apexagent_launcher.py" "$PORTABLE_NAME/"

# Create README
cat > "$PORTABLE_NAME/README.txt" << 'README_EOF'
{self.app_name} Portable Version {self.version}

This is a portable version of {self.app_name} that runs without installation.

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
Visit: {self.url}
README_EOF

# Create Windows batch file
cat > "$PORTABLE_NAME/ApexAgent.bat" << 'BAT_EOF'
@echo off
echo Starting {self.app_name} Portable...
python ApexAgent_Portable.py
pause
BAT_EOF

# Create archive
tar czf "../../dist/portable/$PORTABLE_NAME.tar.gz" "$PORTABLE_NAME"
zip -r "../../dist/portable/$PORTABLE_NAME.zip" "$PORTABLE_NAME"

echo "Portable version created:"
echo "  - dist/portable/$PORTABLE_NAME.tar.gz"
echo "  - dist/portable/$PORTABLE_NAME.zip"
'''
        
        with open(portable_dir / "build_portable.sh", "w") as f:
            f.write(build_script)
        os.chmod(portable_dir / "build_portable.sh", 0o755)
        
        # Create portable dist directory
        (self.dist_dir / "portable").mkdir(exist_ok=True)
    
    def build_all(self):
        """Build all installer types."""
        print(f"Building all installers for {self.app_name} v{self.version}")
        print("=" * 50)
        
        self.create_windows_installer()
        self.create_macos_installer()
        self.create_linux_installers()
        self.create_portable_version()
        
        print("\\n" + "=" * 50)
        print("All installer configurations created!")
        print("\\nTo build installers:")
        print("- Windows: Run build/windows/build_msi.bat on Windows")
        print("- macOS: Run build/macos/build_dmg.sh on macOS")
        print("- Linux DEB: Run build/linux/deb/build_deb.sh")
        print("- Linux RPM: Run build/linux/rpm/build_rpm.sh")
        print("- Linux AppImage: Run build/linux/appimage/build_appimage.sh")
        print("- Portable: Run build/portable/build_portable.sh")
        print(f"\\nAll installers will be created in the 'dist' directory.")

def main():
    parser = argparse.ArgumentParser(description="Build ApexAgent installers")
    parser.add_argument("--platform", choices=["windows", "macos", "linux", "portable", "all"], 
                       default="all", help="Platform to build for")
    
    args = parser.parse_args()
    
    builder = InstallerBuilder()
    
    if args.platform == "all":
        builder.build_all()
    elif args.platform == "windows":
        builder.create_windows_installer()
    elif args.platform == "macos":
        builder.create_macos_installer()
    elif args.platform == "linux":
        builder.create_linux_installers()
    elif args.platform == "portable":
        builder.create_portable_version()

if __name__ == "__main__":
    main()

