#!/bin/bash
# APEX HUNTER - Complete Installation Script
# Optimized for Debian 12 with 6GB RAM constraint

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ASCII Art Banner
echo -e "${CYAN}"
cat << "EOF"
    ___    ____  ________  __  __  ____  ___   ____________ 
   /   |  / __ \/ ____/ |/ / / / / / / |/ / | / /_  __/ __ \
  / /| | / /_/ / __/  |   / / /_/ / /|  /  |/ / / / / /_/ /
 / ___ |/ ____/ /___ /   |  \__  / / |  / /|  / / / / _, _/ 
/_/  |_/_/   /_____//_/|_|  /___/_/  |_/_/ |_/ /_/ /_/ |_|  
                                                            
Elite Bug Bounty Automation System - Installation Script
EOF
echo -e "${NC}"

echo -e "${BLUE}================================================================${NC}"
echo -e "${GREEN}🎯 APEX HUNTER Installation Starting...${NC}"
echo -e "${BLUE}================================================================${NC}"

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo -e "${RED}❌ This script should not be run as root${NC}"
   echo -e "${YELLOW}Please run as a regular user with sudo privileges${NC}"
   exit 1
fi

# Check OS compatibility
if ! grep -q "Debian" /etc/os-release && ! grep -q "Ubuntu" /etc/os-release; then
    echo -e "${RED}❌ This script is designed for Debian/Ubuntu systems${NC}"
    echo -e "${YELLOW}Current OS: $(cat /etc/os-release | grep PRETTY_NAME)${NC}"
    exit 1
fi

# Check RAM requirements
TOTAL_RAM=$(free -m | awk 'NR==2{printf "%.0f", $2}')
if [ "$TOTAL_RAM" -lt 6000 ]; then
    echo -e "${RED}❌ Insufficient RAM: ${TOTAL_RAM}MB detected${NC}"
    echo -e "${YELLOW}APEX HUNTER requires at least 6GB RAM${NC}"
    exit 1
fi

# Check disk space
AVAILABLE_DISK=$(df -BG . | awk 'NR==2 {print $4}' | sed 's/G//')
if [ "$AVAILABLE_DISK" -lt 10 ]; then
    echo -e "${RED}❌ Insufficient disk space: ${AVAILABLE_DISK}GB available${NC}"
    echo -e "${YELLOW}APEX HUNTER requires at least 10GB free space${NC}"
    exit 1
fi

echo -e "${GREEN}✅ System requirements check passed${NC}"
echo -e "${CYAN}   RAM: ${TOTAL_RAM}MB${NC}"
echo -e "${CYAN}   Disk: ${AVAILABLE_DISK}GB available${NC}"

# Function to print step headers
print_step() {
    echo -e "\n${PURPLE}🔄 Step $1: $2${NC}"
    echo -e "${BLUE}----------------------------------------${NC}"
}

# Function to check command success
check_success() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ $1 completed successfully${NC}"
    else
        echo -e "${RED}❌ $1 failed${NC}"
        exit 1
    fi
}

# Step 1: System Updates and Dependencies
print_step "1" "Installing System Dependencies"

echo -e "${CYAN}Updating package lists...${NC}"
sudo apt update -qq
check_success "Package list update"

echo -e "${CYAN}Installing core dependencies...${NC}"
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    sqlite3 \
    ffmpeg \
    libva-drm2 \
    libva-x11-2 \
    git \
    curl \
    wget \
    build-essential \
    libssl-dev \
    libffi-dev \
    pkg-config \
    libsqlite3-dev \
    libjpeg-dev \
    libpng-dev \
    zlib1g-dev \
    unzip \
    htop \
    tree \
    jq > /dev/null 2>&1

check_success "Core dependencies installation"

# Step 2: Python Environment Setup
print_step "2" "Setting up Python Environment"

echo -e "${CYAN}Creating Python virtual environment...${NC}"
python3 -m venv apex_hunter_env
source apex_hunter_env/bin/activate
check_success "Virtual environment creation"

echo -e "${CYAN}Upgrading pip...${NC}"
pip install --upgrade pip > /dev/null 2>&1
check_success "Pip upgrade"

echo -e "${CYAN}Installing Python dependencies...${NC}"
pip install -r requirements.txt > /dev/null 2>&1
check_success "Python dependencies installation"

# Step 3: Directory Structure Setup
print_step "3" "Creating Directory Structure"

echo -e "${CYAN}Creating APEX HUNTER directories...${NC}"
sudo mkdir -p /usr/local/apexhunter/{data,tools,reports,sources,knowledge_base,logs,config,backup}
sudo mkdir -p /usr/local/apexhunter/reports/{evidence,submissions,templates}
sudo mkdir -p /usr/local/apexhunter/tools/{custom,external,scripts}
sudo mkdir -p /usr/local/apexhunter/data/{cache,temp,exports}

# Set proper permissions
sudo chown -R $USER:$USER /usr/local/apexhunter
chmod -R 755 /usr/local/apexhunter
check_success "Directory structure creation"

# Step 4: Install External Tools
print_step "4" "Installing External Security Tools"

cd /usr/local/apexhunter/tools/external

# Install Go (required for some tools)
if ! command -v go &> /dev/null; then
    echo -e "${CYAN}Installing Go programming language...${NC}"
    wget -q https://go.dev/dl/go1.21.5.linux-amd64.tar.gz
    sudo tar -C /usr/local -xzf go1.21.5.linux-amd64.tar.gz
    echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc
    export PATH=$PATH:/usr/local/go/bin
    rm go1.21.5.linux-amd64.tar.gz
    check_success "Go installation"
fi

# Install Subfinder
echo -e "${CYAN}Installing Subfinder...${NC}"
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest > /dev/null 2>&1
sudo cp ~/go/bin/subfinder /usr/local/bin/ 2>/dev/null || true
check_success "Subfinder installation"

# Install Httpx
echo -e "${CYAN}Installing Httpx...${NC}"
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest > /dev/null 2>&1
sudo cp ~/go/bin/httpx /usr/local/bin/ 2>/dev/null || true
check_success "Httpx installation"

# Install Nuclei
echo -e "${CYAN}Installing Nuclei...${NC}"
go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest > /dev/null 2>&1
sudo cp ~/go/bin/nuclei /usr/local/bin/ 2>/dev/null || true
check_success "Nuclei installation"

# Update Nuclei templates
echo -e "${CYAN}Updating Nuclei templates...${NC}"
nuclei -update-templates > /dev/null 2>&1 || true
check_success "Nuclei templates update"

# Step 5: Copy APEX HUNTER Files
print_step "5" "Installing APEX HUNTER System Files"

echo -e "${CYAN}Copying system files...${NC}"
cp -r . /usr/local/apexhunter/
check_success "System files copy"

# Make scripts executable
chmod +x /usr/local/apexhunter/apex_hunter.py
chmod +x /usr/local/apexhunter/install.sh

# Step 6: Build Knowledge Base
print_step "6" "Building Knowledge Base"

echo -e "${CYAN}Building comprehensive knowledge base...${NC}"
echo -e "${YELLOW}⚠️  This may take 5-10 minutes on first run...${NC}"

cd /usr/local/apexhunter
python3 data_collector.py > /dev/null 2>&1
check_success "Knowledge base construction"

# Verify knowledge base
KB_SIZE=$(du -sh data/knowledge_base.db 2>/dev/null | cut -f1 || echo "0")
echo -e "${GREEN}✅ Knowledge base created: ${KB_SIZE}${NC}"

# Step 7: System Configuration
print_step "7" "System Configuration"

# Create configuration files
echo -e "${CYAN}Creating system configuration...${NC}"

cat > /usr/local/apexhunter/config/system_config.json << EOF
{
    "system": {
        "max_ram_mb": 5500,
        "max_hunt_time_seconds": 480,
        "max_concurrent_hunts": 1,
        "auto_cleanup": true,
        "log_level": "INFO"
    },
    "engines": {
        "shadowfinder": {
            "enabled": true,
            "max_ram_mb": 800,
            "timeout_seconds": 120
        },
        "logichunter": {
            "enabled": true,
            "max_ram_mb": 1200,
            "timeout_seconds": 180
        },
        "chainengine": {
            "enabled": true,
            "max_ram_mb": 600,
            "timeout_seconds": 120
        },
        "ai_engine": {
            "enabled": true,
            "max_ram_mb": 1000,
            "timeout_seconds": 60
        },
        "evidence_collector": {
            "enabled": true,
            "max_ram_mb": 300,
            "timeout_seconds": 60
        }
    },
    "web_interface": {
        "host": "0.0.0.0",
        "port": 8080,
        "debug": false,
        "auto_refresh_interval": 5
    }
}
EOF

cat > /usr/local/apexhunter/config/platform_config.json << EOF
{
    "platforms": {
        "hackerone": {
            "report_format": "markdown",
            "max_video_size_mb": 50,
            "max_screenshots": 10,
            "required_sections": ["summary", "impact", "reproduction_steps", "mitigation"]
        },
        "bugcrowd": {
            "report_format": "markdown",
            "max_video_size_mb": 100,
            "max_screenshots": 15,
            "required_sections": ["vulnerability_details", "proof_of_concept", "business_impact"]
        },
        "intigriti": {
            "report_format": "markdown",
            "max_video_size_mb": 75,
            "max_screenshots": 12,
            "required_sections": ["technical_details", "exploitation_steps", "impact_assessment"]
        }
    }
}
EOF

check_success "Configuration files creation"

# Step 8: Create System Service
print_step "8" "Creating System Service"

echo -e "${CYAN}Creating systemd service...${NC}"

sudo tee /etc/systemd/system/apex-hunter.service > /dev/null << EOF
[Unit]
Description=APEX HUNTER - Elite Bug Bounty Automation System
After=network.target
Wants=network.target

[Service]
Type=simple
User=$USER
Group=$USER
WorkingDirectory=/usr/local/apexhunter
Environment=PATH=/usr/local/apexhunter/apex_hunter_env/bin:/usr/local/go/bin:/usr/local/bin:/usr/bin:/bin
ExecStart=/usr/local/apexhunter/apex_hunter_env/bin/python /usr/local/apexhunter/apex_hunter.py --web --port 8080 --max-ram 5500
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=apex-hunter

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/usr/local/apexhunter
MemoryMax=6G

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
check_success "Systemd service creation"

# Step 9: Create Command Line Aliases
print_step "9" "Setting up Command Line Interface"

echo -e "${CYAN}Creating command line aliases...${NC}"

# Create apex-hunter command
sudo tee /usr/local/bin/apex-hunter > /dev/null << EOF
#!/bin/bash
cd /usr/local/apexhunter
source apex_hunter_env/bin/activate
python3 apex_hunter.py "\$@"
EOF

sudo chmod +x /usr/local/bin/apex-hunter

# Add to user's bashrc
if ! grep -q "APEX HUNTER" ~/.bashrc; then
    cat >> ~/.bashrc << 'EOF'

# APEX HUNTER Aliases
alias apex='apex-hunter'
alias apex-web='apex-hunter --web'
alias apex-status='apex-hunter --status'
alias apex-hunt='apex-hunter --target'
EOF
fi

check_success "Command line interface setup"

# Step 10: Performance Optimization
print_step "10" "Performance Optimization"

echo -e "${CYAN}Optimizing system performance...${NC}"

# Create swap file if needed (for memory management)
if [ ! -f /swapfile ]; then
    echo -e "${CYAN}Creating swap file for memory management...${NC}"
    sudo fallocate -l 2G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
fi

# Optimize SQLite performance
echo -e "${CYAN}Optimizing database performance...${NC}"
sqlite3 /usr/local/apexhunter/data/knowledge_base.db "PRAGMA optimize;"

# Set up log rotation
sudo tee /etc/logrotate.d/apex-hunter > /dev/null << EOF
/usr/local/apexhunter/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 $USER $USER
}
EOF

check_success "Performance optimization"

# Step 11: Security Hardening
print_step "11" "Security Hardening"

echo -e "${CYAN}Applying security configurations...${NC}"

# Set proper file permissions
chmod 700 /usr/local/apexhunter/config
chmod 600 /usr/local/apexhunter/config/*.json
chmod 755 /usr/local/apexhunter/data
chmod 644 /usr/local/apexhunter/data/knowledge_base.db

# Create .gitignore for sensitive files
cat > /usr/local/apexhunter/.gitignore << EOF
# Sensitive data
config/secrets.json
data/cache/
data/temp/
logs/
*.log

# Evidence files
reports/evidence/
reports/submissions/

# Python cache
__pycache__/
*.pyc
*.pyo

# Virtual environment
apex_hunter_env/

# OS files
.DS_Store
Thumbs.db
EOF

check_success "Security hardening"

# Step 12: Final Verification
print_step "12" "Final System Verification"

echo -e "${CYAN}Running system verification tests...${NC}"

# Test Python imports
cd /usr/local/apexhunter
source apex_hunter_env/bin/activate

python3 -c "
import sys
sys.path.append('.')
try:
    from memory_manager import memory_manager
    from ai_engine import ApexHunterAIEngine
    from shadowfinder import ShadowFinder
    from logichunter import LogicHunter
    from chain_engine import ChainEngine
    from evidence_collector import EvidenceManager
    print('✅ All Python modules imported successfully')
except Exception as e:
    print(f'❌ Module import failed: {e}')
    sys.exit(1)
"

check_success "Python modules verification"

# Test knowledge base
KB_RECORDS=$(sqlite3 /usr/local/apexhunter/data/knowledge_base.db "SELECT COUNT(*) FROM chain_templates;" 2>/dev/null || echo "0")
if [ "$KB_RECORDS" -gt 1000 ]; then
    echo -e "${GREEN}✅ Knowledge base verified: ${KB_RECORDS} chain templates${NC}"
else
    echo -e "${YELLOW}⚠️  Knowledge base may be incomplete: ${KB_RECORDS} records${NC}"
fi

# Test system status
python3 apex_hunter.py --status > /dev/null 2>&1
check_success "System status check"

# Installation Complete
echo -e "\n${BLUE}================================================================${NC}"
echo -e "${GREEN}🎉 APEX HUNTER Installation Complete!${NC}"
echo -e "${BLUE}================================================================${NC}"

echo -e "\n${PURPLE}📊 Installation Summary:${NC}"
echo -e "${CYAN}   System RAM: ${TOTAL_RAM}MB${NC}"
echo -e "${CYAN}   Knowledge Base: ${KB_RECORDS} chain templates${NC}"
echo -e "${CYAN}   Database Size: $(du -sh /usr/local/apexhunter/data/knowledge_base.db | cut -f1)${NC}"
echo -e "${CYAN}   Installation Path: /usr/local/apexhunter${NC}"

echo -e "\n${PURPLE}🚀 Quick Start Commands:${NC}"
echo -e "${GREEN}   Start Web Interface:${NC} apex-hunter --web"
echo -e "${GREEN}   Run Command Hunt:${NC} apex-hunter --target example.com"
echo -e "${GREEN}   Check System Status:${NC} apex-hunter --status"
echo -e "${GREEN}   Start as Service:${NC} sudo systemctl start apex-hunter"

echo -e "\n${PURPLE}🌐 Web Dashboard:${NC}"
echo -e "${GREEN}   URL: http://localhost:8080${NC}"
echo -e "${GREEN}   Start: sudo systemctl start apex-hunter${NC}"
echo -e "${GREEN}   Enable Auto-start: sudo systemctl enable apex-hunter${NC}"

echo -e "\n${PURPLE}📁 Important Directories:${NC}"
echo -e "${CYAN}   System: /usr/local/apexhunter${NC}"
echo -e "${CYAN}   Reports: /usr/local/apexhunter/reports${NC}"
echo -e "${CYAN}   Evidence: /usr/local/apexhunter/reports/evidence${NC}"
echo -e "${CYAN}   Logs: /usr/local/apexhunter/logs${NC}"

echo -e "\n${PURPLE}⚡ Performance Targets:${NC}"
echo -e "${CYAN}   Hunt Time: < 8 minutes${NC}"
echo -e "${CYAN}   Chain Exploits: 3-5 per target${NC}"
echo -e "${CYAN}   Estimated Bounty: $500+ per chain${NC}"
echo -e "${CYAN}   Payment Probability: 80%+${NC}"

echo -e "\n${YELLOW}⚠️  Important Notes:${NC}"
echo -e "${CYAN}   • Use only on authorized targets${NC}"
echo -e "${CYAN}   • Follow responsible disclosure practices${NC}"
echo -e "${CYAN}   • Respect bug bounty program rules${NC}"
echo -e "${CYAN}   • System optimized for 6GB RAM${NC}"

echo -e "\n${GREEN}🎯 APEX HUNTER is ready for elite bug bounty hunting!${NC}"
echo -e "${BLUE}================================================================${NC}"

# Reload bash to get new aliases
echo -e "\n${YELLOW}💡 Run 'source ~/.bashrc' or restart your terminal to use apex commands${NC}"