<#
.SYNOPSIS
    ApexAgent Windows Installer Script
.DESCRIPTION
    This PowerShell script installs ApexAgent on Windows systems.
    It handles dependency checking, installation, and configuration.
.PARAMETER InstallPath
    The path where ApexAgent should be installed. Defaults to C:\Program Files\ApexAgent.
.PARAMETER Mode
    Installation mode: standard, minimal, complete, development, or custom. Defaults to standard.
.PARAMETER Components
    List of components to install when using custom mode. Ignored for other modes.
.PARAMETER Silent
    Run the installer in silent mode without user interaction.
.PARAMETER NoShortcut
    Do not create desktop or start menu shortcuts.
.PARAMETER Analytics
    Enable anonymous usage analytics.
.EXAMPLE
    .\install.ps1 -InstallPath "D:\ApexAgent" -Mode complete
.NOTES
    Requires PowerShell 5.1 or higher and administrative privileges.
#>

param (
    [string]$InstallPath = "C:\Program Files\ApexAgent",
    [ValidateSet("standard", "minimal", "complete", "development", "custom")]
    [string]$Mode = "standard",
    [string[]]$Components = @(),
    [switch]$Silent = $false,
    [switch]$NoShortcut = $false,
    [switch]$Analytics = $false
)

# Script constants
$ErrorActionPreference = "Stop"
$ScriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$CommonPath = Join-Path (Split-Path -Parent $ScriptPath) "common"
$LogFile = Join-Path $env:TEMP "ApexAgent_Install.log"

# Initialize logging
function Write-Log {
    param (
        [string]$Message,
        [ValidateSet("INFO", "WARNING", "ERROR")]
        [string]$Level = "INFO"
    )
    
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogMessage = "$Timestamp [$Level] $Message"
    
    # Write to console
    if ($Level -eq "ERROR") {
        Write-Host $LogMessage -ForegroundColor Red
    } elseif ($Level -eq "WARNING") {
        Write-Host $LogMessage -ForegroundColor Yellow
    } else {
        Write-Host $LogMessage
    }
    
    # Write to log file
    Add-Content -Path $LogFile -Value $LogMessage
}

# Check if running as administrator
function Test-Administrator {
    $currentUser = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    return $currentUser.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Check system requirements
function Test-SystemRequirements {
    Write-Log "Checking system requirements..."
    
    # Check PowerShell version
    $psVersion = $PSVersionTable.PSVersion
    if ($psVersion.Major -lt 5 -or ($psVersion.Major -eq 5 -and $psVersion.Minor -lt 1)) {
        Write-Log "PowerShell version $($psVersion.ToString()) is not supported. Please use PowerShell 5.1 or higher." "ERROR"
        return $false
    }
    
    # Check Python installation
    try {
        $pythonVersion = python --version 2>&1
        if ($pythonVersion -match "Python (\d+)\.(\d+)\.(\d+)") {
            $major = [int]$Matches[1]
            $minor = [int]$Matches[2]
            
            if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 8)) {
                Write-Log "Python version $major.$minor is not supported. Please install Python 3.8 or higher." "ERROR"
                return $false
            }
            
            Write-Log "Found Python $major.$minor"
        } else {
            Write-Log "Could not determine Python version." "ERROR"
            return $false
        }
    } catch {
        Write-Log "Python is not installed or not in PATH. Please install Python 3.8 or higher." "ERROR"
        return $false
    }
    
    # Check disk space
    $drive = Split-Path -Qualifier $InstallPath
    $freeSpace = (Get-PSDrive -Name $drive.Replace(":", "")).Free
    $requiredSpace = 500MB
    
    if ($freeSpace -lt $requiredSpace) {
        Write-Log "Insufficient disk space. Required: $([math]::Round($requiredSpace/1MB)) MB, Available: $([math]::Round($freeSpace/1MB)) MB" "ERROR"
        return $false
    }
    
    Write-Log "System requirements check passed."
    return $true
}

# Install Python dependencies
function Install-Dependencies {
    param (
        [string[]]$Packages
    )
    
    Write-Log "Installing Python dependencies: $($Packages -join ', ')"
    
    try {
        $process = Start-Process -FilePath "python" -ArgumentList "-m", "pip", "install", "--upgrade", $Packages -NoNewWindow -Wait -PassThru
        if ($process.ExitCode -ne 0) {
            Write-Log "Failed to install dependencies. Exit code: $($process.ExitCode)" "ERROR"
            return $false
        }
    } catch {
        Write-Log "Error installing dependencies: $_" "ERROR"
        return $false
    }
    
    Write-Log "Dependencies installed successfully."
    return $true
}

# Create shortcuts
function Create-Shortcuts {
    if ($NoShortcut) {
        Write-Log "Skipping shortcut creation as requested."
        return $true
    }
    
    Write-Log "Creating shortcuts..."
    
    $executablePath = Join-Path $InstallPath "bin\apexagent.exe"
    
    # Create desktop shortcut
    $desktopPath = [Environment]::GetFolderPath("Desktop")
    $desktopShortcut = Join-Path $desktopPath "ApexAgent.lnk"
    
    $WshShell = New-Object -ComObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut($desktopShortcut)
    $Shortcut.TargetPath = $executablePath
    $Shortcut.Description = "ApexAgent AI Assistant"
    $Shortcut.WorkingDirectory = Split-Path -Parent $executablePath
    $Shortcut.IconLocation = "$executablePath,0"
    $Shortcut.Save()
    
    # Create start menu shortcut
    $startMenuPath = [Environment]::GetFolderPath("StartMenu")
    $programsPath = Join-Path $startMenuPath "Programs"
    $apexAgentFolder = Join-Path $programsPath "ApexAgent"
    
    if (-not (Test-Path $apexAgentFolder)) {
        New-Item -Path $apexAgentFolder -ItemType Directory | Out-Null
    }
    
    $startMenuShortcut = Join-Path $apexAgentFolder "ApexAgent.lnk"
    
    $Shortcut = $WshShell.CreateShortcut($startMenuShortcut)
    $Shortcut.TargetPath = $executablePath
    $Shortcut.Description = "ApexAgent AI Assistant"
    $Shortcut.WorkingDirectory = Split-Path -Parent $executablePath
    $Shortcut.IconLocation = "$executablePath,0"
    $Shortcut.Save()
    
    Write-Log "Shortcuts created successfully."
    return $true
}

# Register application in Windows registry
function Register-Application {
    Write-Log "Registering application in Windows registry..."
    
    $registryPath = "HKLM:\SOFTWARE\ApexAgent"
    
    if (-not (Test-Path $registryPath)) {
        New-Item -Path $registryPath -Force | Out-Null
    }
    
    # Set registry values
    New-ItemProperty -Path $registryPath -Name "InstallPath" -Value $InstallPath -PropertyType String -Force | Out-Null
    New-ItemProperty -Path $registryPath -Name "Version" -Value "0.1.0" -PropertyType String -Force | Out-Null
    New-ItemProperty -Path $registryPath -Name "InstallDate" -Value (Get-Date -Format "yyyy-MM-dd") -PropertyType String -Force | Out-Null
    
    # Add uninstall information
    $uninstallPath = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\ApexAgent"
    
    if (-not (Test-Path $uninstallPath)) {
        New-Item -Path $uninstallPath -Force | Out-Null
    }
    
    $uninstallString = "powershell.exe -ExecutionPolicy Bypass -File `"$InstallPath\uninstall.ps1`""
    
    New-ItemProperty -Path $uninstallPath -Name "DisplayName" -Value "ApexAgent" -PropertyType String -Force | Out-Null
    New-ItemProperty -Path $uninstallPath -Name "DisplayVersion" -Value "0.1.0" -PropertyType String -Force | Out-Null
    New-ItemProperty -Path $uninstallPath -Name "Publisher" -Value "ApexAgent Team" -PropertyType String -Force | Out-Null
    New-ItemProperty -Path $uninstallPath -Name "UninstallString" -Value $uninstallString -PropertyType String -Force | Out-Null
    New-ItemProperty -Path $uninstallPath -Name "InstallLocation" -Value $InstallPath -PropertyType String -Force | Out-Null
    New-ItemProperty -Path $uninstallPath -Name "DisplayIcon" -Value "$InstallPath\bin\apexagent.exe,0" -PropertyType String -Force | Out-Null
    New-ItemProperty -Path $uninstallPath -Name "NoModify" -Value 1 -PropertyType DWord -Force | Out-Null
    New-ItemProperty -Path $uninstallPath -Name "NoRepair" -Value 1 -PropertyType DWord -Force | Out-Null
    
    Write-Log "Application registered successfully."
    return $true
}

# Verify installation
function Test-Installation {
    Write-Log "Verifying installation..."
    
    # Check if installation directory exists
    if (-not (Test-Path $InstallPath)) {
        Write-Log "Installation directory does not exist: $InstallPath" "ERROR"
        return $false
    }
    
    # Check for essential files
    $essentialFiles = @(
        "bin\apexagent.exe",
        "installation_info.json",
        "src\core\plugin_system.py",
        "src\core\error_handling\errors.py"
    )
    
    foreach ($file in $essentialFiles) {
        $filePath = Join-Path $InstallPath $file
        if (-not (Test-Path $filePath)) {
            Write-Log "Essential file missing: $file" "ERROR"
            return $false
        }
    }
    
    # Try to run the application in test mode
    try {
        $testPath = Join-Path $InstallPath "bin\apexagent.exe"
        $process = Start-Process -FilePath $testPath -ArgumentList "--test" -NoNewWindow -Wait -PassThru
        if ($process.ExitCode -ne 0) {
            Write-Log "Application test failed. Exit code: $($process.ExitCode)" "ERROR"
            return $false
        }
    } catch {
        Write-Log "Error testing application: $_" "ERROR"
        return $false
    }
    
    Write-Log "Installation verification passed."
    return $true
}

# Main installation function
function Install-ApexAgent {
    Write-Log "Starting ApexAgent installation..."
    Write-Log "Installation path: $InstallPath"
    Write-Log "Installation mode: $Mode"
    
    # Create installation directory
    if (-not (Test-Path $InstallPath)) {
        try {
            New-Item -Path $InstallPath -ItemType Directory -Force | Out-Null
            Write-Log "Created installation directory: $InstallPath"
        } catch {
            Write-Log "Failed to create installation directory: $_" "ERROR"
            return $false
        }
    } else {
        Write-Log "Installation directory already exists: $InstallPath"
    }
    
    # Copy files to installation directory
    Write-Log "Copying files to installation directory..."
    
    try {
        # In a real implementation, this would copy files from the installation package
        # For now, we'll create placeholder directories and files
        
        $directories = @(
            "bin",
            "src\core",
            "src\core\error_handling",
            "src\installation",
            "docs",
            "plugins"
        )
        
        foreach ($dir in $directories) {
            $dirPath = Join-Path $InstallPath $dir
            if (-not (Test-Path $dirPath)) {
                New-Item -Path $dirPath -ItemType Directory -Force | Out-Null
            }
        }
        
        # Create placeholder executable
        $binPath = Join-Path $InstallPath "bin"
        $exePath = Join-Path $binPath "apexagent.exe"
        
        if (-not (Test-Path $exePath)) {
            # In a real implementation, this would be a copy of the actual executable
            # For now, we'll create a placeholder file
            Set-Content -Path $exePath -Value "This is a placeholder for the ApexAgent executable."
        }
        
        # Create installation info file
        $infoPath = Join-Path $InstallPath "installation_info.json"
        $installInfo = @{
            version = "0.1.0"
            install_path = $InstallPath
            install_date = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
            mode = $Mode
            components = if ($Mode -eq "custom") { $Components } else { @() }
            system_info = @{
                os = "Windows"
                os_version = [Environment]::OSVersion.Version.ToString()
                powershell_version = $PSVersionTable.PSVersion.ToString()
                python_version = (python --version 2>&1)
            }
            analytics_enabled = $Analytics.IsPresent
        }
        
        $installInfoJson = ConvertTo-Json $installInfo -Depth 4
        Set-Content -Path $infoPath -Value $installInfoJson
        
        Write-Log "Files copied successfully."
    } catch {
        Write-Log "Failed to copy files: $_" "ERROR"
        return $false
    }
    
    # Create shortcuts
    if (-not (Create-Shortcuts)) {
        return $false
    }
    
    # Register application
    if (-not (Register-Application)) {
        return $false
    }
    
    # Verify installation
    if (-not (Test-Installation)) {
        Write-Log "Installation verification failed. Rolling back..." "ERROR"
        # In a real implementation, this would call a cleanup function
        return $false
    }
    
    Write-Log "ApexAgent installation completed successfully."
    return $true
}

# Main script execution
try {
    # Check if running as administrator
    if (-not (Test-Administrator)) {
        Write-Log "This script requires administrative privileges. Please run as Administrator." "ERROR"
        exit 1
    }
    
    # Check system requirements
    if (-not (Test-SystemRequirements)) {
        exit 1
    }
    
    # Perform installation
    if (Install-ApexAgent) {
        Write-Log "Installation completed successfully."
        
        if (-not $Silent) {
            Write-Host "`nApexAgent has been installed successfully to $InstallPath" -ForegroundColor Green
            Write-Host "You can now start ApexAgent from the Start Menu or Desktop shortcut."
        }
        
        exit 0
    } else {
        Write-Log "Installation failed." "ERROR"
        
        if (-not $Silent) {
            Write-Host "`nInstallation failed. Please check the log file for details: $LogFile" -ForegroundColor Red
        }
        
        exit 1
    }
} catch {
    Write-Log "Unhandled exception: $_" "ERROR"
    Write-Log $_.ScriptStackTrace "ERROR"
    
    if (-not $Silent) {
        Write-Host "`nAn error occurred during installation. Please check the log file for details: $LogFile" -ForegroundColor Red
    }
    
    exit 1
}
