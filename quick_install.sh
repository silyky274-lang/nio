#!/bin/bash
# APEX HUNTER - Quick Installation (2-3 minutes)
# Gets you hunting immediately without heavy frameworks

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}"
cat << "EOF"
⚡ APEX HUNTER - Quick Installation
==================================
Fast setup for immediate hunting (2-3 minutes)
EOF
echo -e "${NC}"

# Create required directories
echo -e "${BLUE}📁 Creating directories...${NC}"
mkdir -p data sources tools config logs reports/{evidence,submissions,templates}

# Fix the missing sources directory issue
echo -e "${BLUE}🔧 Fixing system paths...${NC}"
touch sources/.gitkeep
touch tools/.gitkeep
touch config/.gitkeep
touch logs/.gitkeep

# Install only essential tools (fast)
echo -e "${BLUE}🛠️  Installing essential tools...${NC}"
sudo apt update -qq
sudo apt install -y -qq \
    nmap \
    curl \
    wget \
    git \
    python3-requests \
    python3-bs4 \
    dnsutils \
    whois \
    netcat-traditional \
    masscan \
    gobuster \
    dirb \
    nikto \
    sqlmap

echo -e "${GREEN}✅ Essential tools installed${NC}"

# Create lightweight tool configuration
echo -e "${BLUE}⚙️  Creating tool configuration...${NC}"
cat > config/tools.json << 'EOF'
{
    "nmap": {"path": "/usr/bin/nmap", "enabled": true},
    "masscan": {"path": "/usr/bin/masscan", "enabled": true},
    "gobuster": {"path": "/usr/bin/gobuster", "enabled": true},
    "dirb": {"path": "/usr/bin/dirb", "enabled": true},
    "nikto": {"path": "/usr/bin/nikto", "enabled": true},
    "sqlmap": {"path": "/usr/bin/sqlmap", "enabled": true},
    "curl": {"path": "/usr/bin/curl", "enabled": true},
    "wget": {"path": "/usr/bin/wget", "enabled": true}
}
EOF

# Create system configuration for your RAM
echo -e "${BLUE}⚙️  Creating system configuration...${NC}"
cat > config/system_config.json << 'EOF'
{
    "system": {
        "max_ram_mb": 1800,
        "memory_mode": "lightweight",
        "max_hunt_time_seconds": 600,
        "max_concurrent_hunts": 1,
        "auto_cleanup": true,
        "log_level": "INFO"
    },
    "engines": {
        "shadowfinder": {"enabled": true, "max_ram_mb": 400, "timeout_seconds": 120},
        "logichunter": {"enabled": true, "max_ram_mb": 600, "timeout_seconds": 180},
        "chainengine": {"enabled": true, "max_ram_mb": 300, "timeout_seconds": 120},
        "ai_engine": {"enabled": true, "max_ram_mb": 400, "timeout_seconds": 60},
        "evidence_collector": {"enabled": true, "max_ram_mb": 100, "timeout_seconds": 60}
    },
    "web_interface": {
        "host": "0.0.0.0",
        "port": 8080,
        "debug": false,
        "auto_refresh_interval": 5
    }
}
EOF

# Create platform configuration
cat > config/platform_config.json << 'EOF'
{
    "platforms": {
        "hackerone": {
            "report_format": "markdown",
            "max_video_size_mb": 25,
            "evidence_requirements": ["poc_video", "technical_writeup"],
            "average_response_time_days": 3
        },
        "bugcrowd": {
            "report_format": "markdown",
            "max_video_size_mb": 50,
            "evidence_requirements": ["poc_video", "business_impact"],
            "average_response_time_days": 5
        },
        "intigriti": {
            "report_format": "markdown",
            "max_video_size_mb": 30,
            "evidence_requirements": ["detailed_poc", "remediation_advice"],
            "average_response_time_days": 2
        }
    }
}
EOF

# Download essential wordlists (small ones)
echo -e "${BLUE}📚 Downloading essential wordlists...${NC}"
mkdir -p tools/wordlists
cd tools/wordlists

# Small, effective wordlists
wget -q https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/common.txt
wget -q https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/directory-list-2.3-small.txt
wget -q https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/Common-Credentials/10-million-password-list-top-100.txt

cd ../..
echo -e "${GREEN}✅ Wordlists downloaded${NC}"

# Create quick start script
echo -e "${BLUE}🚀 Creating quick start script...${NC}"
cat > start_apex.sh << 'EOF'
#!/bin/bash
# APEX HUNTER Quick Start

echo "🎯 Starting APEX HUNTER..."

# Check if knowledge base exists
if [ ! -f "data/knowledge_base.db" ]; then
    echo "🧠 Creating knowledge base..."
    python create_knowledge_base.py
fi

# Start the system
echo "🚀 Launching APEX HUNTER..."
python apex_hunter.py --web --port 8080 --max-ram 1800
EOF

chmod +x start_apex.sh

# Create test target script
cat > test_target.sh << 'EOF'
#!/bin/bash
# Test APEX HUNTER with a safe target

echo "🎯 Testing APEX HUNTER with testphp.vulnweb.com..."
python apex_hunter.py --target testphp.vulnweb.com --mode lightweight --timeout 300
EOF

chmod +x test_target.sh

echo -e "\n${GREEN}🎉 APEX HUNTER Quick Installation Complete!${NC}"
echo -e "${GREEN}===========================================${NC}"

echo -e "\n${CYAN}🚀 Ready to Hunt! Choose your option:${NC}"
echo -e "\n${YELLOW}Option 1 - Web Interface:${NC}"
echo -e "  ./start_apex.sh"
echo -e "  Then open: http://localhost:8080"

echo -e "\n${YELLOW}Option 2 - Command Line Test:${NC}"
echo -e "  ./test_target.sh"

echo -e "\n${YELLOW}Option 3 - Custom Target:${NC}"
echo -e "  python apex_hunter.py --target your-target.com --mode lightweight"

echo -e "\n${CYAN}📊 System Status:${NC}"
echo -e "  💾 RAM Mode: Lightweight (1.8GB max)"
echo -e "  🧠 Knowledge Base: 8.11MB (10,000+ templates)"
echo -e "  🛠️  Tools: Essential penetration testing suite"
echo -e "  ⏱️  Hunt Time: 10 minutes max per target"

echo -e "\n${GREEN}Ready to find your first chain exploit! 🎯${NC}"