#!/bin/bash

# APEX HUNTER - Fixed Installation Script
# Handles Python virtual environments, Go installation, and dependency issues

echo "🎯 APEX HUNTER - Fixed Installation Script"
echo "=========================================="
echo "Fixing installation issues and setting up properly..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check available RAM
TOTAL_RAM=$(free -m | awk 'NR==2{printf "%.0f", $2}' 2>/dev/null || echo "4096")
print_status "Detected RAM: ${TOTAL_RAM}MB"

if [ "$TOTAL_RAM" -lt 2000 ]; then
    MEMORY_MODE="minimal"
    print_status "System will run in minimal mode"
elif [ "$TOTAL_RAM" -lt 4000 ]; then
    MEMORY_MODE="lightweight"
    print_status "System will run in lightweight mode"
else
    MEMORY_MODE="optimized"
    print_status "System will run in optimized mode"
fi

# Step 1: Kill any conflicting processes
print_header "Step 1: Cleaning up conflicting processes"
sudo pkill -f apt-get 2>/dev/null || true
sudo pkill -f dpkg 2>/dev/null || true
sleep 2
print_status "Cleanup complete"

# Step 2: Install essential system packages only
print_header "Step 2: Installing essential system packages"
sudo apt update -qq
sudo apt install -y \
    python3 python3-pip python3-venv python3-full \
    git curl wget unzip \
    build-essential libssl-dev libffi-dev \
    sqlite3 \
    nmap \
    default-jre \
    libopencv-dev python3-opencv \
    scrot \
    ffmpeg

print_status "Essential packages installed"

# Step 3: Create Python virtual environment
print_header "Step 3: Setting up Python virtual environment"
cd ~/nio

# Remove existing venv if it exists
if [ -d "venv" ]; then
    rm -rf venv
    print_status "Removed existing virtual environment"
fi

# Create new virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

print_status "Virtual environment created and activated"

# Step 4: Install Python dependencies in virtual environment
print_header "Step 4: Installing Python dependencies"

# Install core dependencies first
pip install \
    flask==2.3.3 \
    requests==2.31.0 \
    beautifulsoup4==4.12.2 \
    pillow==10.0.1 \
    psutil==5.9.6 \
    pyyaml==6.0.1

# Install OpenCV without building from source
pip install opencv-python-headless==4.8.1.78

print_status "Core Python dependencies installed"

# Step 5: Create knowledge base
print_header "Step 5: Creating knowledge base"
if [ -f "create_knowledge_base.py" ]; then
    python create_knowledge_base.py
    print_status "Knowledge base created"
else
    print_warning "Knowledge base script not found, skipping"
fi

# Step 6: Install minimal Go tools (optional)
print_header "Step 6: Installing minimal Go tools (optional)"
if command -v go &> /dev/null; then
    print_status "Go found, installing essential tools..."
    go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest 2>/dev/null || print_warning "Subfinder install failed"
    go install github.com/projectdiscovery/httpx/cmd/httpx@latest 2>/dev/null || print_warning "Httpx install failed"
    go install github.com/projectdiscovery/nuclei/v2/cmd/nuclei@latest 2>/dev/null || print_warning "Nuclei install failed"
    print_status "Essential Go tools installed"
else
    print_warning "Go not found, skipping Go tools (system will work without them)"
fi

# Step 7: Create simplified launcher
print_header "Step 7: Creating launcher scripts"

# Create activation script
cat > activate_apex.sh << 'EOF'
#!/bin/bash
# APEX HUNTER Activation Script

echo "🎯 Activating APEX HUNTER Environment"
echo "====================================="

cd ~/nio
source venv/bin/activate

echo "✅ Virtual environment activated"
echo "🐍 Python: $(python --version)"
echo "📦 Pip: $(pip --version)"
echo ""
echo "Available commands:"
echo "  python enhanced_web_interface.py    # Start web interface"
echo "  python multi_target_analyzer.py     # Command line analysis"
echo "  python create_knowledge_base.py     # Rebuild knowledge base"
echo ""
EOF

chmod +x activate_apex.sh

# Create web launcher
cat > start_web.sh << 'EOF'
#!/bin/bash
# APEX HUNTER Web Interface Launcher

cd ~/nio
source venv/bin/activate

echo "🎯 Starting APEX HUNTER Web Interface"
echo "====================================="
echo "🌐 Access at: http://localhost:12000"
echo "📱 Supports: URLs, IPs, APKs, Source Code, GitHub Repos"
echo "🛑 Press Ctrl+C to stop"
echo ""

python enhanced_web_interface.py
EOF

chmod +x start_web.sh

# Create command line launcher
cat > start_cli.sh << 'EOF'
#!/bin/bash
# APEX HUNTER Command Line Launcher

cd ~/nio
source venv/bin/activate

echo "🎯 APEX HUNTER Command Line Interface"
echo "====================================="
echo ""

if [ $# -eq 0 ]; then
    echo "Usage: ./start_cli.sh <target> [target_type]"
    echo ""
    echo "Examples:"
    echo "  ./start_cli.sh https://example.com"
    echo "  ./start_cli.sh 192.168.1.1 ip"
    echo "  ./start_cli.sh app.apk apk"
    echo "  ./start_cli.sh /path/to/source source_code"
    echo "  ./start_cli.sh https://github.com/user/repo github"
    echo ""
    exit 1
fi

python multi_target_analyzer.py "$@"
EOF

chmod +x start_cli.sh

print_status "Launcher scripts created"

# Step 8: Create desktop shortcut
print_header "Step 8: Creating desktop shortcut"
if [ -d "$HOME/Desktop" ]; then
    cat > ~/Desktop/APEX_HUNTER.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=APEX HUNTER
Comment=Elite Bug Bounty Automation System
Exec=gnome-terminal -- bash -c "cd ~/nio && ./start_web.sh; exec bash"
Icon=utilities-terminal
Terminal=false
Categories=Development;Security;
EOF
    chmod +x ~/Desktop/APEX_HUNTER.desktop
    print_status "Desktop shortcut created"
fi

# Step 9: Test installation
print_header "Step 9: Testing installation"
source venv/bin/activate

# Test Python imports
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
    print('✅ Core dependencies: OK')
except ImportError as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)

try:
    import cv2
    print('✅ OpenCV: OK')
except ImportError:
    print('⚠️ OpenCV: Not available (optional)')

print('✅ Installation test passed!')
"

if [ $? -eq 0 ]; then
    print_status "✅ Installation test passed!"
else
    print_error "❌ Installation test failed"
    exit 1
fi

# Step 10: Create installation summary
print_header "Step 10: Creating installation summary"

cat > INSTALLATION_STATUS.txt << EOF
🎯 APEX HUNTER - Installation Status
===================================

Installation Date: $(date)
Memory Mode: $MEMORY_MODE
Total RAM: ${TOTAL_RAM}MB

📁 Installation Directory: ~/nio/
🐍 Python Environment: ~/nio/venv/

🚀 Quick Start Commands:
  ./activate_apex.sh          # Activate environment
  ./start_web.sh              # Start web interface
  ./start_cli.sh <target>     # Command line analysis

🌐 Web Interface: http://localhost:12000

🎯 Supported Targets:
- Web Applications (URLs)
- Network Hosts (IP addresses)
- Mobile Applications (APK files)
- Source Code (ZIP/TAR archives)
- GitHub Repositories

✅ Core Features Available:
- Multi-target analysis engine
- Real-time evidence collection
- Professional report generation
- Exploit chain detection
- Web dashboard interface

⚠️ Optional Features:
- Go-based tools (install Go for full functionality)
- Advanced wordlists (download separately if needed)
- Video recording (requires additional setup)

🎉 Installation Complete!
Ready for bug bounty hunting!
EOF

print_status "Installation summary created"

# Final message
echo ""
echo "🎉 APEX HUNTER Installation Complete!"
echo "====================================="
echo ""
echo "📁 Installation Directory: ~/nio/"
echo "🚀 Quick Start:"
echo "  cd ~/nio"
echo "  ./start_web.sh"
echo ""
echo "🌐 Web Interface: http://localhost:12000"
echo "📖 Status: ~/nio/INSTALLATION_STATUS.txt"
echo ""
echo "🎯 Ready for elite bug bounty hunting!"
echo ""
echo "Next steps:"
echo "1. cd ~/nio"
echo "2. ./start_web.sh"
echo "3. Open browser to http://localhost:12000"
echo "4. Start hunting!"
echo ""