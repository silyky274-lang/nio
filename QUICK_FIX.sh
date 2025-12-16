#!/bin/bash

echo "🔧 APEX HUNTER - Quick Fix for Installation Issues"
echo "================================================="

# Navigate to the project directory
cd ~/nio

# Activate virtual environment
echo "[INFO] Activating virtual environment..."
source venv/bin/activate

# Install missing Python packages
echo "[INFO] Installing missing Python packages..."
pip install beautifulsoup4==4.12.2
pip install lxml==4.9.3
pip install selenium==4.15.2

# Test the installation
echo "[INFO] Testing installation..."
python -c "
import sys
print(f'Python version: {sys.version}')

try:
    import flask
    import requests
    import beautifulsoup4
    import PIL
    import psutil
    import yaml
    import cv2
    print('✅ All dependencies: OK')
except ImportError as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)

print('✅ Installation test passed!')
"

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 APEX HUNTER - Quick Fix Complete!"
    echo "===================================="
    echo ""
    echo "✅ All dependencies installed successfully"
    echo "🚀 Ready to start hunting!"
    echo ""
    echo "Start commands:"
    echo "  cd ~/nio"
    echo "  source venv/bin/activate"
    echo "  python enhanced_web_interface.py"
    echo ""
    echo "🌐 Access at: http://localhost:12000"
    echo ""
else
    echo ""
    echo "❌ Quick fix failed. Using simple interface instead..."
    echo ""
    echo "Alternative start command:"
    echo "  cd ~/nio"
    echo "  python simple_web_interface.py"
    echo ""
fi