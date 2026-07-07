# Master Build Script for OMNI Engine Installer
$ErrorActionPreference = "Stop"

# Get absolute path to the directory where the script is located
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location -Path $ScriptDir
Write-Host "Current Directory Set To: $ScriptDir" -ForegroundColor Cyan

# Step 1: Ensure PyInstaller is installed
Write-Host "`n[1/3] Checking PyInstaller..." -ForegroundColor Yellow
if (!(Get-Command pyinstaller -ErrorAction SilentlyContinue)) {
    Write-Host "PyInstaller not found. Installing via pip..."
    pip install pyinstaller
}

# Step 2: Build the Executable via PyInstaller
Write-Host "`n[2/3] Compiling OMNI Engine..." -ForegroundColor Yellow
if (Test-Path -Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path -Path "dist") { Remove-Item -Recurse -Force "dist" }

python -m PyInstaller --noconfirm omni.spec
if ($LASTEXITCODE -ne 0) {
    Write-Error "PyInstaller failed with code $LASTEXITCODE"
    Exit $LASTEXITCODE
}
Write-Host "PyInstaller Compilation Successful." -ForegroundColor Green

# Step 3: Package with Inno Setup
Write-Host "`n[3/3] Creating Windows Installer Setup..." -ForegroundColor Yellow

$InnoSetupPath = "$env:USERPROFILE\Documents\InnoSetup\ISCC.exe"

if (!(Test-Path -Path $InnoSetupPath)) {
    Write-Error "Inno Setup Compiler (ISCC.exe) not found. Please install Inno Setup 6."
    Exit 1
}

& $InnoSetupPath "omni.iss"
if ($LASTEXITCODE -ne 0) {
    Write-Error "Inno Setup Compiler failed with code $LASTEXITCODE"
    Exit $LASTEXITCODE
}

Write-Host "`n===============================================" -ForegroundColor Cyan
Write-Host "BUILD COMPLETE!" -ForegroundColor Green
Write-Host "Installer generated at: $(Join-Path $ScriptDir 'installer\OMNI_Setup.exe')" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
