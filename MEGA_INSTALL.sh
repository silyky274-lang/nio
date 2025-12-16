#!/bin/bash
# APEX HUNTER - MEGA INSTALLATION SCRIPT
# Complete one-command installation and launch

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}"
cat << "EOF"
    ___    ____  ________  __  __  ____  ___   ____________ 
   /   |  / __ \/ ____/ |/ / / / / / / |/ / | / /_  __/ __ \
  / /| | / /_/ / __/  |   / / /_/ / /|  /  |/ / / / / /_/ /
 / ___ |/ ____/ /___ /   |  \__  / / |  / /|  / / / / _, _/ 
/_/  |_/_/   /_____//_/|_|  /___/_/  |_/_/ |_/ /_/ /_/ |_|  

🎯 APEX HUNTER - MEGA INSTALLATION
==================================
Complete Bug Bounty Automation System
One command to rule them all!
EOF
echo -e "${NC}"

# Function to check command success
check_success() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ $1${NC}"
    else
        echo -e "${RED}❌ $1 failed${NC}"
        exit 1
    fi
}

# Function to print step headers
print_step() {
    echo -e "\n${BLUE}🔄 Step $1: $2${NC}"
    echo -e "${BLUE}========================================${NC}"
}

# Check if we're in the right directory
if [ ! -f "web_interface.py" ]; then
    echo -e "${YELLOW}📁 Not in APEX HUNTER directory. Cloning repository...${NC}"
    
    # Clone the repository
    if [ -d "mr-mx-lee-" ]; then
        echo -e "${CYAN}Updating existing repository...${NC}"
        cd mr-mx-lee-
        git pull origin feature/apex-hunter-complete-system
    else
        echo -e "${CYAN}Cloning APEX HUNTER repository...${NC}"
        git clone -b feature/apex-hunter-complete-system https://github.com/thyrosu156-ai/mr-mx-lee-.git
        cd mr-mx-lee-
    fi
    check_success "Repository setup"
fi

# Step 1: System Information
print_step "1" "System Analysis"

echo -e "${CYAN}Analyzing system resources...${NC}"
TOTAL_RAM=$(free -m | awk 'NR==2{printf "%.0f", $2}')
AVAILABLE_RAM=$(free -m | awk 'NR==2{printf "%.0f", $7}')
DISK_SPACE=$(df -h . | awk 'NR==2 {print $4}')

echo -e "💾 Total RAM: ${TOTAL_RAM}MB"
echo -e "💾 Available RAM: ${AVAILABLE_RAM}MB"
echo -e "💽 Available Disk: ${DISK_SPACE}"

# Determine memory mode
if [ $TOTAL_RAM -lt 2000 ]; then
    MEMORY_MODE="minimal"
    MAX_RAM=1000
elif [ $TOTAL_RAM -lt 4000 ]; then
    MEMORY_MODE="lightweight"
    MAX_RAM=1800
elif [ $TOTAL_RAM -lt 6000 ]; then
    MEMORY_MODE="optimized"
    MAX_RAM=3000
else
    MEMORY_MODE="full"
    MAX_RAM=5500
fi

echo -e "🧠 Memory Mode: ${MEMORY_MODE} (${MAX_RAM}MB limit)"
check_success "System analysis"

# Step 2: Dependencies Installation
print_step "2" "Installing Dependencies"

echo -e "${CYAN}Updating package lists...${NC}"
sudo apt update -qq

echo -e "${CYAN}Installing essential packages...${NC}"
sudo apt install -y -qq \
    python3 \
    python3-pip \
    python3-venv \
    curl \
    wget \
    git \
    nmap \
    dnsutils \
    whois \
    netcat-traditional \
    sqlite3 \
    ffmpeg

check_success "Essential packages installation"

# Step 3: Python Environment
print_step "3" "Python Environment Setup"

echo -e "${CYAN}Creating Python virtual environment...${NC}"
python3 -m venv apex_env
source apex_env/bin/activate
check_success "Virtual environment creation"

echo -e "${CYAN}Installing Python packages...${NC}"
pip install --quiet --upgrade pip
pip install --quiet \
    flask \
    requests \
    beautifulsoup4 \
    psutil \
    pillow \
    pyyaml \
    cryptography \
    networkx \
    matplotlib \
    pandas

check_success "Python packages installation"

# Step 4: Directory Structure
print_step "4" "Creating Directory Structure"

echo -e "${CYAN}Creating required directories...${NC}"
mkdir -p data sources tools config logs
mkdir -p reports/{evidence,submissions,templates}
mkdir -p tools/{wordlists,scripts}

# Create .gitkeep files
touch data/.gitkeep sources/.gitkeep tools/.gitkeep config/.gitkeep logs/.gitkeep
touch reports/evidence/.gitkeep reports/submissions/.gitkeep reports/templates/.gitkeep

check_success "Directory structure creation"

# Step 5: Knowledge Base
print_step "5" "Building Knowledge Base"

echo -e "${CYAN}Creating comprehensive knowledge base...${NC}"
echo -e "${YELLOW}⏳ This may take 1-2 minutes...${NC}"

python create_knowledge_base.py

KB_SIZE=$(du -sh data/knowledge_base.db 2>/dev/null | cut -f1 || echo "0")
echo -e "${GREEN}✅ Knowledge base created: ${KB_SIZE}${NC}"
check_success "Knowledge base creation"

# Step 6: Configuration
print_step "6" "System Configuration"

echo -e "${CYAN}Creating system configuration...${NC}"

cat > config/system_config.json << EOF
{
    "system": {
        "max_ram_mb": ${MAX_RAM},
        "memory_mode": "${MEMORY_MODE}",
        "max_hunt_time_seconds": 600,
        "max_concurrent_hunts": 1,
        "auto_cleanup": true,
        "log_level": "INFO"
    },
    "engines": {
        "shadowfinder": {
            "enabled": true,
            "max_ram_mb": $((MAX_RAM / 4)),
            "timeout_seconds": 120
        },
        "logichunter": {
            "enabled": true,
            "max_ram_mb": $((MAX_RAM / 3)),
            "timeout_seconds": 180
        },
        "chainengine": {
            "enabled": true,
            "max_ram_mb": $((MAX_RAM / 5)),
            "timeout_seconds": 120
        },
        "ai_engine": {
            "enabled": true,
            "max_ram_mb": $((MAX_RAM / 4)),
            "timeout_seconds": 60
        }
    },
    "web_interface": {
        "host": "0.0.0.0",
        "port": 8080,
        "debug": false,
        "auto_refresh_interval": 2
    }
}
EOF

cat > config/tools.json << EOF
{
    "nmap": {"path": "/usr/bin/nmap", "enabled": true},
    "curl": {"path": "/usr/bin/curl", "enabled": true},
    "wget": {"path": "/usr/bin/wget", "enabled": true},
    "dig": {"path": "/usr/bin/dig", "enabled": true},
    "whois": {"path": "/usr/bin/whois", "enabled": true},
    "nslookup": {"path": "/usr/bin/nslookup", "enabled": true}
}
EOF

check_success "Configuration creation"

# Step 7: Memory Optimization
print_step "7" "Memory Optimization"

echo -e "${CYAN}Optimizing system memory...${NC}"

# Stop unnecessary services
services_to_stop=("apache2" "nginx" "mysql" "postgresql" "mongodb" "docker" "snapd" "bluetooth" "cups")

for service in "${services_to_stop[@]}"; do
    if systemctl is-active --quiet "$service" 2>/dev/null; then
        echo -e "  🛑 Stopping $service..."
        sudo systemctl stop "$service" 2>/dev/null || true
    fi
done

# Clear caches
echo -e "  🧹 Clearing system caches..."
sudo sync
sudo sysctl vm.drop_caches=3 2>/dev/null || true

# Optimize swap
echo -e "  💾 Optimizing swap usage..."
sudo sysctl vm.swappiness=10 2>/dev/null || true

check_success "Memory optimization"

# Step 8: Wordlists
print_step "8" "Essential Wordlists"

echo -e "${CYAN}Downloading essential wordlists...${NC}"
cd tools/wordlists

# Small, effective wordlists
wget -q -O common.txt https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/common.txt || echo "common.txt" > common.txt
wget -q -O directories.txt https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/directory-list-2.3-small.txt || echo "admin\napi\ntest\ndev" > directories.txt
wget -q -O passwords.txt https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/Common-Credentials/10-million-password-list-top-100.txt || echo "password\n123456\nadmin" > passwords.txt

cd ../..
check_success "Wordlists download"

# Step 9: Launcher Scripts
print_step "9" "Creating Launcher Scripts"

echo -e "${CYAN}Creating launcher scripts...${NC}"

# Web interface launcher
cat > start_web.sh << 'EOF'
#!/bin/bash
echo "🎯 Starting APEX HUNTER Web Interface..."
echo "🌐 Access dashboard at: http://localhost:8080"
echo "🔗 Or access via: http://$(hostname -I | awk '{print $1}'):8080"
echo "=" * 50

# Activate virtual environment
source apex_env/bin/activate

# Start web interface
python web_interface.py
EOF

# Command line launcher
cat > start_hunt.sh << 'EOF'
#!/bin/bash
if [ -z "$1" ]; then
    echo "Usage: ./start_hunt.sh <target>"
    echo "Example: ./start_hunt.sh testphp.vulnweb.com"
    exit 1
fi

echo "🎯 Starting hunt against: $1"
source apex_env/bin/activate
python test_hunt.py "$1"
EOF

# Quick test launcher
cat > quick_test.sh << 'EOF'
#!/bin/bash
echo "🎯 Running quick test with safe target..."
source apex_env/bin/activate
python test_hunt.py testphp.vulnweb.com
EOF

chmod +x start_web.sh start_hunt.sh quick_test.sh

check_success "Launcher scripts creation"

# Step 10: Final Setup
print_step "10" "Final Setup"

echo -e "${CYAN}Performing final setup...${NC}"

# Create logs
touch logs/apex_hunter.log
touch logs/hunt_results.log

# Set permissions
chmod +x *.py
chmod 755 data config tools reports logs

# Final memory check
FINAL_RAM=$(free -m | awk 'NR==2{printf "%.0f", $7}')
echo -e "💾 Final available RAM: ${FINAL_RAM}MB"

check_success "Final setup"

# Installation Complete
echo -e "\n${GREEN}🎉 APEX HUNTER INSTALLATION COMPLETE!${NC}"
echo -e "${GREEN}====================================${NC}"

echo -e "\n${CYAN}📊 System Status:${NC}"
echo -e "  💾 Memory Mode: ${MEMORY_MODE} (${MAX_RAM}MB limit)"
echo -e "  🧠 Knowledge Base: ${KB_SIZE}"
echo -e "  🛠️  Tools: Essential penetration testing suite"
echo -e "  📁 Wordlists: Common, directories, passwords"
echo -e "  ⚙️  Configuration: Optimized for your system"

echo -e "\n${YELLOW}🚀 Ready to Hunt! Choose your option:${NC}"
echo -e "\n${CYAN}Option 1 - Web Interface (Recommended):${NC}"
echo -e "  ./start_web.sh"
echo -e "  Then open: http://localhost:8080"

echo -e "\n${CYAN}Option 2 - Quick Test:${NC}"
echo -e "  ./quick_test.sh"

echo -e "\n${CYAN}Option 3 - Custom Target:${NC}"
echo -e "  ./start_hunt.sh your-target.com"

echo -e "\n${CYAN}📚 Documentation:${NC}"
echo -e "  📖 README.md - Complete documentation"
echo -e "  🎯 test_hunt.py - Command-line hunting"
echo -e "  🌐 web_interface.py - Web dashboard"

echo -e "\n${RED}⚠️  IMPORTANT - ETHICAL TESTING ONLY:${NC}"
echo -e "  🔒 Only test targets you own or have permission to test"
echo -e "  🎯 Use testphp.vulnweb.com for safe testing"
echo -e "  📋 Always follow responsible disclosure"

echo -e "\n${GREEN}🎯 APEX HUNTER is ready to find chain exploits!${NC}"
echo -e "${GREEN}Happy hunting! 🚀${NC}"

# Auto-start web interface option
echo -e "\n${YELLOW}Start web interface now? (y/n):${NC}"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    echo -e "${CYAN}🚀 Starting web interface...${NC}"
    ./start_web.sh
fi