# Poppler Installation Script for Windows
# This script downloads and installs Poppler for PDF processing

Write-Host "=== Poppler Installation Script ===" -ForegroundColor Cyan
Write-Host ""

# Configuration
$popplerVersion = "24.08.0-0"
$downloadUrl = "https://github.com/oschwartz10612/poppler-windows/releases/download/v$popplerVersion/Release-$popplerVersion.zip"
$installPath = "C:\Program Files\poppler"
$tempZip = "$env:TEMP\poppler.zip"

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "[ERROR] This script requires Administrator privileges to install to Program Files." -ForegroundColor Yellow
    Write-Host "Please run PowerShell as Administrator and try again." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To run as Administrator:" -ForegroundColor Cyan
    Write-Host "1. Right-click PowerShell" -ForegroundColor White
    Write-Host "2. Select 'Run as Administrator'" -ForegroundColor White
    Write-Host "3. Navigate to: cd E:\doc_intelligence" -ForegroundColor White
    Write-Host "4. Run: .\install_poppler.ps1" -ForegroundColor White
    Write-Host ""
    pause
    exit 1
}

# Check if already installed
if (Test-Path "$installPath\Library\bin\pdfinfo.exe") {
    Write-Host "[OK] Poppler is already installed at: $installPath" -ForegroundColor Green
    
    # Check if in PATH
    $currentPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
    $popplerBinPath = "$installPath\Library\bin"
    
    if ($currentPath -like "*$popplerBinPath*") {
        Write-Host "[OK] Poppler is already in system PATH" -ForegroundColor Green
        Write-Host ""
        Write-Host "Poppler is ready to use! Restart your backend server." -ForegroundColor Cyan
        pause
        exit 0
    } else {
        Write-Host "[WARN] Poppler found but not in PATH. Adding to PATH..." -ForegroundColor Yellow
        [Environment]::SetEnvironmentVariable("Path", "$currentPath;$popplerBinPath", "Machine")
        Write-Host "[OK] Added Poppler to system PATH" -ForegroundColor Green
        Write-Host ""
        Write-Host "[OK] Installation complete! Please restart your terminal and backend server." -ForegroundColor Green
        pause
        exit 0
    }
}

Write-Host "[INFO] Downloading Poppler $popplerVersion..." -ForegroundColor Cyan
Write-Host "URL: $downloadUrl" -ForegroundColor Gray
Write-Host ""

try {
    # Download Poppler
    Invoke-WebRequest -Uri $downloadUrl -OutFile $tempZip -UseBasicParsing
    Write-Host "[OK] Download complete!" -ForegroundColor Green
    Write-Host ""
    
    # Extract to Program Files
    Write-Host "[INFO] Extracting to $installPath..." -ForegroundColor Cyan
    
    if (Test-Path $installPath) {
        Remove-Item -Path $installPath -Recurse -Force
    }
    
    Expand-Archive -Path $tempZip -DestinationPath "C:\Program Files\" -Force
    
    # The zip extracts to a folder with version number, rename it
    $extractedFolder = Get-ChildItem "C:\Program Files\" | Where-Object { $_.Name -like "poppler-*" } | Select-Object -First 1
    if ($extractedFolder) {
        Rename-Item -Path $extractedFolder.FullName -NewName "poppler" -Force
    }
    
    Write-Host "[OK] Extraction complete!" -ForegroundColor Green
    Write-Host ""
    
    # Add to PATH
    Write-Host "[INFO] Adding Poppler to system PATH..." -ForegroundColor Cyan
    $popplerBinPath = "$installPath\Library\bin"
    $currentPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
    
    if ($currentPath -notlike "*$popplerBinPath*") {
        [Environment]::SetEnvironmentVariable("Path", "$currentPath;$popplerBinPath", "Machine")
        Write-Host "[OK] Added to system PATH: $popplerBinPath" -ForegroundColor Green
    } else {
        Write-Host "[OK] Already in system PATH" -ForegroundColor Green
    }
    
    # Cleanup
    Remove-Item -Path $tempZip -Force
    Write-Host ""
    Write-Host "================================================" -ForegroundColor Green
    Write-Host "[SUCCESS] Poppler Installation Complete!" -ForegroundColor Green
    Write-Host "================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "[INFO] Installed to: $installPath" -ForegroundColor Cyan
    Write-Host "[INFO] Binary path: $popplerBinPath" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "[IMPORTANT] Please restart your terminal and backend server" -ForegroundColor Yellow
    Write-Host "            for PATH changes to take effect." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To verify installation, run:" -ForegroundColor Cyan
    Write-Host "  pdfinfo -v" -ForegroundColor White
    Write-Host ""
    
} catch {
    Write-Host "[ERROR] Installation failed: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Manual installation steps:" -ForegroundColor Yellow
    Write-Host "1. Download from: https://github.com/oschwartz10612/poppler-windows/releases" -ForegroundColor White
    Write-Host "2. Extract to: C:\Program Files\poppler" -ForegroundColor White
    Write-Host "3. Add to PATH: C:\Program Files\poppler\Library\bin" -ForegroundColor White
    Write-Host ""
    exit 1
}

pause
