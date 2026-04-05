# EsTodo Windows Build Script
# Run this in PowerShell on Windows

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  EsTodo Windows Build Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is available
try {
    $pythonVersion = python --version
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found! Please install Python 3.12+" -ForegroundColor Red
    exit 1
}

# Check if virtual environment exists
$venvDir = ".venv"
if (Test-Path $venvDir) {
    Write-Host "✓ Virtual environment found" -ForegroundColor Green
    $activateScript = Join-Path $venvDir "Scripts" "Activate.ps1"
    . $activateScript
} else {
    Write-Host "⚠ Virtual environment not found, using current Python" -ForegroundColor Yellow
}

# Install/upgrade dependencies
Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Cyan
pip install --upgrade pip
pip install -r requirements.txt
pip install --upgrade pyinstaller

# Clean previous builds
Write-Host ""
Write-Host "Cleaning previous builds..." -ForegroundColor Cyan
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }

# Build with PyInstaller
Write-Host ""
Write-Host "Building with PyInstaller..." -ForegroundColor Cyan

# Simple one-file build
pyinstaller `
    --name "EsTodo" `
    --windowed `
    --onefile `
    --clean `
    --add-data "src/estodo;estodo" `
    src/estodo/main.py

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✓ Build successful!" -ForegroundColor Green
    Write-Host ""

    $exePath = "dist/EsTodo.exe"
    if (Test-Path $exePath) {
        $size = (Get-Item $exePath).Length / 1MB
        Write-Host "Executable: $exePath" -ForegroundColor Cyan
        Write-Host "Size: $([math]::Round($size, 2)) MB" -ForegroundColor Cyan
        Write-Host ""

        # Create zip
        Write-Host "Creating zip archive..." -ForegroundColor Cyan
        Compress-Archive -Path "dist/EsTodo.exe" -DestinationPath "EsTodo-windows.zip" -Force
        Write-Host "✓ Zip created: EsTodo-windows.zip" -ForegroundColor Green
    }
} else {
    Write-Host ""
    Write-Host "✗ Build failed!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Build complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
