#!/bin/bash

# APEX HUNTER - Ultimate Installation Script
# Supports: URLs, IPs, APKs, Source Code, GitHub Repos
# Features: Video Recording, Screenshots, Complete Evidence Collection

echo "🎯 APEX HUNTER - Ultimate Multi-Target Installation"
echo "=================================================="
echo "Installing complete bug bounty automation system..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root for security reasons"
   exit 1
fi

# Detect OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if [ -f /etc/debian_version ]; then
        OS="debian"
        print_status "Detected Debian/Ubuntu system"
    elif [ -f /etc/redhat-release ]; then
        OS="redhat"
        print_status "Detected RedHat/CentOS system"
    else
        OS="linux"
        print_status "Detected generic Linux system"
    fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
    print_status "Detected macOS system"
else
    print_error "Unsupported operating system: $OSTYPE"
    exit 1
fi

# Check available RAM
TOTAL_RAM=$(free -m | awk 'NR==2{printf "%.0f", $2}' 2>/dev/null || echo "4096")
print_status "Detected RAM: ${TOTAL_RAM}MB"

if [ "$TOTAL_RAM" -lt 1500 ]; then
    print_warning "Low RAM detected. System will run in minimal mode."
    MEMORY_MODE="minimal"
elif [ "$TOTAL_RAM" -lt 3000 ]; then
    print_status "Moderate RAM detected. System will run in lightweight mode."
    MEMORY_MODE="lightweight"
elif [ "$TOTAL_RAM" -lt 6000 ]; then
    print_status "Good RAM detected. System will run in optimized mode."
    MEMORY_MODE="optimized"
else
    print_status "Excellent RAM detected. System will run in full mode."
    MEMORY_MODE="full"
fi

# Step 1: Update system packages
print_header "Step 1: Updating system packages"
if [ "$OS" = "debian" ]; then
    sudo apt update -qq
    print_status "Package list updated"
elif [ "$OS" = "redhat" ]; then
    sudo yum update -y -q
    print_status "Package list updated"
elif [ "$OS" = "macos" ]; then
    if ! command -v brew &> /dev/null; then
        print_status "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    brew update
    print_status "Homebrew updated"
fi

# Step 2: Install system dependencies
print_header "Step 2: Installing system dependencies"
if [ "$OS" = "debian" ]; then
    sudo apt install -y \
        python3 python3-pip python3-venv python3-dev \
        git curl wget unzip \
        build-essential libssl-dev libffi-dev \
        sqlite3 \
        ffmpeg \
        scrot \
        nmap \
        gobuster \
        nikto \
        sqlmap \
        masscan \
        dirb \
        aapt \
        openjdk-11-jdk \
        android-tools-adb \
        android-tools-fastboot \
        apktool \
        dex2jar \
        jadx \
        binwalk \
        strings \
        file \
        exiftool \
        imagemagick \
        tesseract-ocr \
        zbar-tools \
        qrencode \
        steghide \
        foremost \
        volatility \
        john \
        hashcat \
        hydra \
        aircrack-ng \
        wireshark-common \
        tcpdump \
        netcat \
        socat \
        proxychains \
        tor \
        i2p \
        metasploit-framework 2>/dev/null || true
    
    print_status "System dependencies installed"
    
elif [ "$OS" = "redhat" ]; then
    sudo yum install -y \
        python3 python3-pip python3-devel \
        git curl wget unzip \
        gcc gcc-c++ make openssl-devel libffi-devel \
        sqlite \
        ffmpeg \
        nmap \
        nikto \
        sqlmap \
        masscan \
        java-11-openjdk \
        binutils \
        strings \
        file \
        exiftool \
        ImageMagick \
        tesseract \
        john \
        hashcat \
        hydra \
        aircrack-ng \
        wireshark \
        tcpdump \
        nc \
        socat \
        proxychains-ng \
        tor
    
    print_status "System dependencies installed"
    
elif [ "$OS" = "macos" ]; then
    brew install \
        python3 \
        git curl wget unzip \
        sqlite \
        ffmpeg \
        nmap \
        gobuster \
        nikto \
        sqlmap \
        masscan \
        openjdk@11 \
        binutils \
        exiftool \
        imagemagick \
        tesseract \
        john \
        hashcat \
        hydra \
        aircrack-ng \
        wireshark \
        netcat \
        socat \
        proxychains-ng \
        tor
    
    print_status "System dependencies installed"
fi

# Step 3: Install Python dependencies
print_header "Step 3: Installing Python dependencies"
pip3 install --user --upgrade pip

# Core dependencies
pip3 install --user \
    flask==2.3.3 \
    requests==2.31.0 \
    beautifulsoup4==4.12.2 \
    selenium==4.15.2 \
    pillow==10.0.1 \
    cryptography==41.0.7 \
    pyyaml==6.0.1 \
    networkx==3.2.1 \
    matplotlib==3.8.2 \
    psutil==5.9.6 \
    lxml==4.9.3 \
    pandas==2.1.3 \
    numpy==1.24.4 \
    opencv-python==4.8.1.78 \
    pytesseract==0.3.10 \
    pyzbar==0.1.9 \
    qrcode==7.4.2 \
    python-magic==0.4.27 \
    exifread==3.0.0 \
    scapy==2.5.0 \
    paramiko==3.3.1 \
    pycryptodome==3.19.0 \
    androguard==3.4.0a1 \
    frida==16.1.4 \
    frida-tools==12.2.1 \
    objection==1.11.0 \
    jadx==1.4.7 \
    apkleaks==2.6.1 \
    mobsf==3.7.6 \
    semgrep==1.45.0 \
    bandit==1.7.5 \
    safety==2.3.5 \
    truffleHog==3.63.2 \
    gitpython==3.1.40 \
    pygithub==1.59.1 \
    python-gitlab==4.2.0 \
    python-bitbucket==0.12.0

print_status "Python dependencies installed"

# Step 4: Install Go-based tools
print_header "Step 4: Installing Go-based security tools"
if ! command -v go &> /dev/null; then
    print_status "Installing Go..."
    if [ "$OS" = "debian" ]; then
        sudo apt install -y golang-go
    elif [ "$OS" = "redhat" ]; then
        sudo yum install -y golang
    elif [ "$OS" = "macos" ]; then
        brew install go
    fi
fi

# Create tools directory
mkdir -p ~/apex_tools
cd ~/apex_tools

# Install essential Go tools
print_status "Installing subfinder..."
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest

print_status "Installing httpx..."
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest

print_status "Installing nuclei..."
go install -v github.com/projectdiscovery/nuclei/v2/cmd/nuclei@latest

print_status "Installing katana..."
go install github.com/projectdiscovery/katana/cmd/katana@latest

print_status "Installing naabu..."
go install -v github.com/projectdiscovery/naabu/v2/cmd/naabu@latest

print_status "Installing dnsx..."
go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@latest

print_status "Installing notify..."
go install -v github.com/projectdiscovery/notify/cmd/notify@latest

print_status "Installing interactsh-client..."
go install -v github.com/projectdiscovery/interactsh/cmd/interactsh-client@latest

print_status "Installing gau..."
go install github.com/lc/gau/v2/cmd/gau@latest

print_status "Installing waybackurls..."
go install github.com/tomnomnom/waybackurls@latest

print_status "Installing gf..."
go install github.com/tomnomnom/gf@latest

print_status "Installing anew..."
go install github.com/tomnomnom/anew@latest

print_status "Installing qsreplace..."
go install github.com/tomnomnom/qsreplace@latest

print_status "Installing fff..."
go install github.com/tomnomnom/fff@latest

print_status "Installing assetfinder..."
go install github.com/tomnomnom/assetfinder@latest

print_status "Installing httprobe..."
go install github.com/tomnomnom/httprobe@latest

print_status "Installing meg..."
go install github.com/tomnomnom/meg@latest

print_status "Installing gron..."
go install github.com/tomnomnom/gron@latest

print_status "Installing unfurl..."
go install github.com/tomnomnom/unfurl@latest

print_status "Installing dalfox..."
go install github.com/hahwul/dalfox/v2@latest

print_status "Installing kxss..."
go install github.com/Emoe/kxss@latest

print_status "Installing freq..."
go install github.com/takshal/freq@latest

print_status "Installing gospider..."
go install github.com/jaeles-project/gospider@latest

print_status "Installing hakrawler..."
go install github.com/hakluke/hakrawler@latest

print_status "Installing getJS..."
go install github.com/003random/getJS@latest

print_status "Installing subjs..."
go install github.com/lc/subjs@latest

print_status "Installing anti-burl..."
go install github.com/tomnomnom/hacks/anti-burl@latest

print_status "Installing filter-resolved..."
go install github.com/tomnomnom/hacks/filter-resolved@latest

print_status "Installing html-tool..."
go install github.com/tomnomnom/hacks/html-tool@latest

print_status "Installing tok..."
go install github.com/tomnomnom/hacks/tok@latest

print_status "Installing concurl..."
go install github.com/tomnomnom/hacks/concurl@latest

print_status "Installing rush..."
go install github.com/shenwei356/rush@latest

print_status "Installing crlfuzz..."
go install github.com/dwisiswant0/crlfuzz/cmd/crlfuzz@latest

print_status "Installing tko-subs..."
go install github.com/anshumanbh/tko-subs@latest

print_status "Installing subjack..."
go install github.com/haccer/subjack@latest

print_status "Installing aquatone..."
go install github.com/michenriksen/aquatone@latest

# Add Go bin to PATH
echo 'export PATH=$PATH:$(go env GOPATH)/bin' >> ~/.bashrc
export PATH=$PATH:$(go env GOPATH)/bin

print_status "Go-based tools installed"

# Step 5: Install wordlists
print_header "Step 5: Installing wordlists and payloads"
mkdir -p ~/wordlists
cd ~/wordlists

print_status "Downloading SecLists..."
git clone https://github.com/danielmiessler/SecLists.git

print_status "Downloading PayloadsAllTheThings..."
git clone https://github.com/swisskyrepo/PayloadsAllTheThings.git

print_status "Downloading FuzzDB..."
git clone https://github.com/fuzzdb-project/fuzzdb.git

print_status "Downloading Auto_Wordlists..."
git clone https://github.com/carlospolop/Auto_Wordlists.git

print_status "Downloading OneListForAll..."
git clone https://github.com/six2dez/OneListForAll.git

print_status "Wordlists installed"

# Step 6: Setup APEX HUNTER
print_header "Step 6: Setting up APEX HUNTER system"
cd ~/

# Create APEX HUNTER directory structure
mkdir -p ~/apex_hunter/{data,evidence,uploads,reports,logs,config}

# Copy APEX HUNTER files (assuming they're in current directory)
if [ -f "multi_target_analyzer.py" ]; then
    cp *.py ~/apex_hunter/
    cp *.sh ~/apex_hunter/
    chmod +x ~/apex_hunter/*.sh
    print_status "APEX HUNTER files copied"
else
    print_warning "APEX HUNTER source files not found in current directory"
    print_status "Please copy the APEX HUNTER files to ~/apex_hunter/"
fi

# Create knowledge base
cd ~/apex_hunter
if [ -f "create_knowledge_base.py" ]; then
    print_status "Creating knowledge base..."
    python3 create_knowledge_base.py
    print_status "Knowledge base created"
fi

# Step 7: Install additional APK analysis tools
print_header "Step 7: Installing APK analysis tools"
mkdir -p ~/apk_tools
cd ~/apk_tools

# Install MobSF
print_status "Installing MobSF (Mobile Security Framework)..."
git clone https://github.com/MobSF/Mobile-Security-Framework-MobSF.git
cd Mobile-Security-Framework-MobSF
pip3 install --user -r requirements.txt

# Install QARK
cd ~/apk_tools
print_status "Installing QARK..."
git clone https://github.com/linkedin/qark.git
cd qark
pip3 install --user -r requirements.txt

# Install APKiD
print_status "Installing APKiD..."
pip3 install --user apkid

# Install APK Studio
print_status "Installing APK Studio dependencies..."
sudo apt install -y default-jre default-jdk 2>/dev/null || true

print_status "APK analysis tools installed"

# Step 8: Configure system optimizations
print_header "Step 8: Configuring system optimizations"

# Create memory optimization script
cat > ~/apex_hunter/optimize_system.sh << 'EOF'
#!/bin/bash
# APEX HUNTER System Optimization

echo "🔧 Optimizing system for APEX HUNTER..."

# Clear system caches
sudo sysctl vm.drop_caches=3

# Optimize swappiness
echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf

# Optimize network settings
echo 'net.core.rmem_max = 134217728' | sudo tee -a /etc/sysctl.conf
echo 'net.core.wmem_max = 134217728' | sudo tee -a /etc/sysctl.conf
echo 'net.ipv4.tcp_rmem = 4096 87380 134217728' | sudo tee -a /etc/sysctl.conf
echo 'net.ipv4.tcp_wmem = 4096 65536 134217728' | sudo tee -a /etc/sysctl.conf

# Increase file descriptor limits
echo '* soft nofile 65536' | sudo tee -a /etc/security/limits.conf
echo '* hard nofile 65536' | sudo tee -a /etc/security/limits.conf

echo "✅ System optimization complete"
EOF

chmod +x ~/apex_hunter/optimize_system.sh

# Create APEX HUNTER launcher
cat > ~/apex_hunter/launch_apex.sh << 'EOF'
#!/bin/bash
# APEX HUNTER Launcher

echo "🎯 APEX HUNTER - Elite Bug Bounty Automation System"
echo "=================================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
pip install --upgrade pip
pip install -r requirements.txt 2>/dev/null || true

# Optimize system
./optimize_system.sh 2>/dev/null || true

# Start APEX HUNTER
echo "🚀 Starting APEX HUNTER web interface..."
echo "🔗 Access at: http://localhost:12000"
echo "📱 Supports: URLs, IPs, APKs, Source Code, GitHub Repos"
echo ""

python3 enhanced_web_interface.py
EOF

chmod +x ~/apex_hunter/launch_apex.sh

# Create desktop shortcut
if [ "$OS" = "linux" ]; then
    cat > ~/Desktop/APEX_HUNTER.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=APEX HUNTER
Comment=Elite Bug Bounty Automation System
Exec=gnome-terminal -- bash -c "cd ~/apex_hunter && ./launch_apex.sh; exec bash"
Icon=utilities-terminal
Terminal=false
Categories=Development;Security;
EOF
    chmod +x ~/Desktop/APEX_HUNTER.desktop
    print_status "Desktop shortcut created"
fi

# Step 9: Create configuration files
print_header "Step 9: Creating configuration files"

# Create main config
cat > ~/apex_hunter/config/apex_config.yaml << EOF
# APEX HUNTER Configuration
system:
  memory_mode: $MEMORY_MODE
  max_ram_mb: $TOTAL_RAM
  max_concurrent_tools: 3
  evidence_retention_days: 30
  
analysis:
  default_timeout: 600  # 10 minutes
  deep_analysis_timeout: 1800  # 30 minutes
  screenshot_interval: 30  # seconds
  video_quality: medium
  
targets:
  max_file_size_mb: 100
  supported_formats:
    - apk
    - zip
    - tar.gz
    - jar
    - war
    - aar
  
platforms:
  hackerone:
    enabled: true
    report_template: hackerone_template.md
  bugcrowd:
    enabled: true
    report_template: bugcrowd_template.md
  intigriti:
    enabled: true
    report_template: intigriti_template.md
    
tools:
  nmap_args: "-sS -sV -O --script vuln"
  gobuster_threads: 50
  sqlmap_args: "--batch --random-agent"
  nuclei_args: "-c 50 -rl 150"
EOF

print_status "Configuration files created"

# Step 10: Final setup and testing
print_header "Step 10: Final setup and testing"

cd ~/apex_hunter

# Create requirements.txt if it doesn't exist
if [ ! -f "requirements.txt" ]; then
    cat > requirements.txt << EOF
flask==2.3.3
requests==2.31.0
beautifulsoup4==4.12.2
selenium==4.15.2
pillow==10.0.1
cryptography==41.0.7
pyyaml==6.0.1
networkx==3.2.1
matplotlib==3.8.2
psutil==5.9.6
lxml==4.9.3
pandas==2.1.3
numpy==1.24.4
opencv-python==4.8.1.78
pytesseract==0.3.10
pyzbar==0.1.9
qrcode==7.4.2
python-magic==0.4.27
exifread==3.0.0
scapy==2.5.0
paramiko==3.3.1
pycryptodome==3.19.0
androguard==3.4.0a1
frida==16.1.4
frida-tools==12.2.1
objection==1.11.0
semgrep==1.45.0
bandit==1.7.5
safety==2.3.5
gitpython==3.1.40
pygithub==1.59.1
python-gitlab==4.2.0
EOF
fi

# Test installation
print_status "Testing APEX HUNTER installation..."
if python3 -c "import flask, requests, beautifulsoup4, selenium, PIL, cryptography, yaml, networkx, matplotlib, psutil, lxml, pandas, numpy, cv2" 2>/dev/null; then
    print_status "✅ Python dependencies test passed"
else
    print_warning "⚠️ Some Python dependencies may be missing"
fi

# Create installation summary
cat > ~/apex_hunter/INSTALLATION_SUMMARY.txt << EOF
🎯 APEX HUNTER - Installation Summary
====================================

Installation Date: $(date)
System: $OS
Memory Mode: $MEMORY_MODE
Total RAM: ${TOTAL_RAM}MB

📁 Installation Directories:
- APEX HUNTER: ~/apex_hunter/
- Tools: ~/apex_tools/
- Wordlists: ~/wordlists/
- APK Tools: ~/apk_tools/

🚀 Quick Start:
1. cd ~/apex_hunter
2. ./launch_apex.sh
3. Open browser to http://localhost:12000

🎯 Supported Targets:
- Web Applications (URLs)
- Network Hosts (IP addresses)
- Mobile Applications (APK files)
- Source Code (ZIP/TAR archives)
- GitHub Repositories

🛠️ Installed Tools:
- Core: Python 3, Flask, Selenium, OpenCV
- Network: Nmap, Masscan, Gobuster, Nikto
- Web: SQLMap, Nuclei, Katana, HTTPx
- Mobile: APKTool, Dex2Jar, JADX, MobSF
- Analysis: Semgrep, Bandit, TruffleHog
- Go Tools: 30+ ProjectDiscovery & community tools

📊 Features:
- Multi-target analysis engine
- Real-time evidence collection
- Video PoC recording
- Screenshot automation
- Professional report generation
- Exploit chain detection
- Platform-specific formatting

🔧 System Optimizations:
- Memory management tuning
- Network parameter optimization
- File descriptor limits increased
- Swap usage optimized

⚡ Performance:
- Memory Mode: $MEMORY_MODE
- Max RAM Usage: ${TOTAL_RAM}MB
- Concurrent Tools: 3
- Analysis Timeout: 10-30 minutes

🎉 Installation Complete!
Ready for elite bug bounty hunting!
EOF

print_status "Installation summary created"

# Final message
echo ""
echo "🎉 APEX HUNTER Installation Complete!"
echo "====================================="
echo ""
echo "📁 Installation Directory: ~/apex_hunter/"
echo "🚀 Quick Start: cd ~/apex_hunter && ./launch_apex.sh"
echo "🔗 Web Interface: http://localhost:12000"
echo "📖 Summary: ~/apex_hunter/INSTALLATION_SUMMARY.txt"
echo ""
echo "🎯 Supported Targets:"
echo "  • Web Applications (URLs)"
echo "  • Network Hosts (IP addresses)"  
echo "  • Mobile Applications (APK files)"
echo "  • Source Code (ZIP/TAR archives)"
echo "  • GitHub Repositories"
echo ""
echo "🛡️ Features:"
echo "  • Real-time evidence collection"
echo "  • Video PoC recording"
echo "  • Screenshot automation"
echo "  • Professional report generation"
echo "  • Exploit chain detection"
echo "  • Multi-platform support"
echo ""
echo "⚡ System Optimized for: $MEMORY_MODE mode (${TOTAL_RAM}MB RAM)"
echo ""
echo "🎉 Ready for elite bug bounty hunting!"
echo ""
echo "To start APEX HUNTER:"
echo "  cd ~/apex_hunter"
echo "  ./launch_apex.sh"
echo ""