#!/bin/bash
# EsTodo Linux Build Script

set -e

echo "========================================"
echo "  EsTodo Linux Build Script"
echo "========================================"
echo ""

# Check Python
if command -v python3 &> /dev/null; then
    echo "✓ Python found: $(python3 --version)"
else
    echo "✗ Python not found! Please install Python 3.12+"
    exit 1
fi

# Check virtual environment
if [ -d ".venv" ]; then
    echo "✓ Virtual environment found"
    source .venv/bin/activate
else
    echo "⚠ Virtual environment not found, using current Python"
fi

# Install/upgrade dependencies
echo ""
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install --upgrade pyinstaller

# Clean previous builds
echo ""
echo "Cleaning previous builds..."
rm -rf build dist

# Build with PyInstaller
echo ""
echo "Building with PyInstaller..."

if [ -f "assets/icon.ico" ]; then
    echo "✓ Using icon: assets/icon.ico"
    pyinstaller \
        --name "EsTodo" \
        --windowed \
        --onefile \
        --clean \
        --icon "assets/icon.ico" \
        --add-data "src/estodo:estodo" \
        src/estodo/main.py
else
    echo "⚠ Icon not found at assets/icon.ico, building without icon"
    pyinstaller \
        --name "EsTodo" \
        --windowed \
        --onefile \
        --clean \
        --add-data "src/estodo:estodo" \
        src/estodo/main.py
fi

echo ""
echo "✓ Build successful!"
echo ""

if [ -f "dist/EsTodo" ]; then
    chmod +x dist/EsTodo
    SIZE=$(du -h dist/EsTodo | cut -f1)
    echo "Executable: dist/EsTodo"
    echo "Size: $SIZE"
    echo ""

    # Create tar.gz
    echo "Creating tar.gz archive..."
    cd dist
    tar -czf ../EsTodo-linux.tar.gz EsTodo
    cd ..
    echo "✓ Archive created: EsTodo-linux.tar.gz"
fi

echo ""
echo "========================================"
echo "  Build complete!"
echo "========================================"
