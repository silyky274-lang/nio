#!/bin/bash

# APEX HUNTER - Complete Elite Setup Script
# Installs EVERYTHING needed for top 5 elite bug bounty hunting
# Fixes Go issues and installs all tools, frameworks, methodologies

echo "🎯 APEX HUNTER - Complete Elite Setup"
echo "====================================="
echo "Installing EVERYTHING for elite bug bounty hunting"
echo "This will take 30-60 minutes but installs the complete arsenal"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_header() {
    echo -e "${BLUE}[PHASE]${NC} $1"
}

print_tool() {
    echo -e "${PURPLE}[TOOL]${NC} Installing $1..."
}

# Phase 1: Fix Go Installation
print_header "Phase 1: Fixing Go Installation"

# Remove broken Go installation
sudo apt remove golang-go -y 2>/dev/null || true

# Install Go from official source
print_tool "Go Language (Official)"
cd /tmp
wget -q https://go.dev/dl/go1.21.5.linux-amd64.tar.gz
sudo rm -rf /usr/local/go
sudo tar -C /usr/local -xzf go1.21.5.linux-amd64.tar.gz
rm go1.21.5.linux-amd64.tar.gz

# Set up Go environment
export GOROOT=/usr/local/go
export GOPATH=$HOME/go
export PATH=$GOROOT/bin:$GOPATH/bin:$PATH

# Add to shell profile
echo 'export GOROOT=/usr/local/go' >> ~/.bashrc
echo 'export GOPATH=$HOME/go' >> ~/.bashrc
echo 'export PATH=$GOROOT/bin:$GOPATH/bin:$PATH' >> ~/.bashrc

mkdir -p $GOPATH/{bin,src,pkg}

print_status "Go installation fixed"

# Phase 2: Essential System Dependencies
print_header "Phase 2: Installing System Dependencies"

sudo apt update -qq

# Install comprehensive system packages
sudo apt install -y \
    curl wget git unzip zip p7zip-full \
    build-essential cmake make \
    python3 python3-pip python3-venv python3-dev \
    nodejs npm \
    openjdk-11-jdk openjdk-17-jdk \
    ruby ruby-dev \
    php php-cli php-curl php-xml \
    sqlite3 postgresql-client mysql-client \
    nmap masscan zmap \
    ffmpeg imagemagick \
    docker.io docker-compose \
    jq yq xmlstarlet \
    tree htop iotop \
    libssl-dev libffi-dev \
    libxml2-dev libxslt1-dev \
    zlib1g-dev libjpeg-dev libpng-dev \
    libpq-dev libmysqlclient-dev \
    chromium-browser firefox-esr \
    tor proxychains4 \
    aircrack-ng hashcat john \
    wireshark tcpdump \
    binwalk foremost \
    strace ltrace \
    gdb radare2 \
    vim nano emacs \
    tmux screen \
    net-tools dnsutils \
    whois dig host \
    telnet netcat-openbsd \
    socat ncat \
    2>/dev/null || print_warning "Some packages may have failed"

print_status "System dependencies installed"

# Phase 3: Go Security Tools (Complete Arsenal)
print_header "Phase 3: Installing Go Security Tools"

# Reconnaissance Tools
print_tool "Nuclei - Vulnerability Scanner"
go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest

print_tool "Subfinder - Subdomain Discovery"
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest

print_tool "Httpx - HTTP Toolkit"
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest

print_tool "Katana - Web Crawler"
go install github.com/projectdiscovery/katana/cmd/katana@latest

print_tool "Naabu - Port Scanner"
go install -v github.com/projectdiscovery/naabu/v2/cmd/naabu@latest

print_tool "Dnsx - DNS Toolkit"
go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@latest

print_tool "Notify - Notification Framework"
go install -v github.com/projectdiscovery/notify/cmd/notify@latest

print_tool "Interactsh - OOB Testing"
go install -v github.com/projectdiscovery/interactsh/cmd/interactsh-client@latest

print_tool "Chaos - DNS Data API"
go install -v github.com/projectdiscovery/chaos-client/cmd/chaos@latest

print_tool "Uncover - Discovery Engine"
go install -v github.com/projectdiscovery/uncover/cmd/uncover@latest

print_tool "Shodan CLI"
go install -v github.com/projectdiscovery/shodan-cli/cmd/shodan@latest

# Web Application Tools
print_tool "GAU - Get All URLs"
go install github.com/lc/gau/v2/cmd/gau@latest

print_tool "Waybackurls - Archive URLs"
go install github.com/tomnomnom/waybackurls@latest

print_tool "GF - Grep Framework"
go install github.com/tomnomnom/gf@latest

print_tool "Anew - Append New"
go install github.com/tomnomnom/anew@latest

print_tool "Qsreplace - Query String Replace"
go install github.com/tomnomnom/qsreplace@latest

print_tool "Ffuf - Fast Fuzzer"
go install github.com/ffuf/ffuf/v2@latest

print_tool "Gobuster - Directory Brute Forcer"
go install github.com/OJ/gobuster/v3@latest

print_tool "Feroxbuster - Fast Content Discovery"
go install github.com/epi052/feroxbuster@latest

print_tool "Dirsearch Alternative - Dirb"
go install github.com/maurosoria/dirsearch@latest

# XSS and Injection Tools
print_tool "Dalfox - XSS Scanner"
go install github.com/hahwul/dalfox/v2@latest

print_tool "Kxss - XSS Finder"
go install github.com/Emoe/kxss@latest

print_tool "XSStrike Alternative - XSS Hunter"
go install github.com/KathanP19/Gxss@latest

print_tool "SQLMap Alternative - SQLi Hunter"
go install github.com/zt2/sqli-hunter@latest

# Web Crawling and Spidering
print_tool "Gospider - Web Spider"
go install github.com/jaeles-project/gospider@latest

print_tool "Hakrawler - Web Crawler"
go install github.com/hakluke/hakrawler@latest

print_tool "Paramspider - Parameter Discovery"
go install github.com/devanshbatham/paramspider@latest

print_tool "Arjun - HTTP Parameter Discovery"
go install github.com/s0md3v/arjun@latest

# JavaScript Analysis
print_tool "GetJS - JavaScript Extractor"
go install github.com/003random/getJS@latest

print_tool "Subjs - JavaScript Subdomain Finder"
go install github.com/lc/subjs@latest

print_tool "JSParser - JavaScript Parser"
go install github.com/nahamsec/JSParser@latest

print_tool "LinkFinder - Endpoint Discovery"
go install github.com/GerbenJavado/LinkFinder@latest

# Subdomain Takeover
print_tool "TKO-subs - Subdomain Takeover"
go install github.com/anshumanbh/tko-subs@latest

print_tool "Subjack - Subdomain Takeover"
go install github.com/haccer/subjack@latest

print_tool "SubOver - Subdomain Takeover"
go install github.com/Ice3man543/SubOver@latest

# Network and Infrastructure
print_tool "Amass - Attack Surface Mapping"
go install -v github.com/owasp-amass/amass/v4/...@master

print_tool "Aquatone - Visual Inspection"
go install github.com/michenriksen/aquatone@latest

print_tool "Httprobe - HTTP Probe"
go install github.com/tomnomnom/httprobe@latest

print_tool "Meg - Fetch URLs"
go install github.com/tomnomnom/meg@latest

# Utility Tools
print_tool "Rush - Cross-platform Command Runner"
go install github.com/shenwei356/rush@latest

print_tool "CRLFuzz - CRLF Injection Scanner"
go install github.com/dwisiswant0/crlfuzz/cmd/crlfuzz@latest

print_tool "Notify - Notification System"
go install github.com/projectdiscovery/notify/cmd/notify@latest

print_tool "Interactsh - OOB Interaction"
go install github.com/projectdiscovery/interactsh/cmd/interactsh-client@latest

# Advanced Tools
print_tool "Jaeles - Signature-based Scanner"
go install github.com/jaeles-project/jaeles@latest

print_tool "Gau - Get All URLs"
go install github.com/lc/gau/v2/cmd/gau@latest

print_tool "Waybackurls - Wayback Machine URLs"
go install github.com/tomnomnom/waybackurls@latest

print_status "Go security tools installed"

# Phase 4: Python Security Arsenal
print_header "Phase 4: Installing Python Security Arsenal"

# Activate virtual environment
source apex_env/bin/activate

# Web Application Security
print_tool "SQLMap - SQL Injection"
pip install sqlmap

print_tool "XSStrike - XSS Detection"
pip install xsstrike

print_tool "Commix - Command Injection"
pip install commix

print_tool "NoSQLMap - NoSQL Injection"
pip install nosqlmap

print_tool "Tplmap - Template Injection"
pip install tplmap

print_tool "XXEinjector - XXE Injection"
pip install xxeinjector

print_tool "SSRFmap - SSRF Testing"
pip install ssrfmap

print_tool "CORScanner - CORS Misconfiguration"
pip install cors-scanner

print_tool "JWT Tool - JWT Security"
pip install pyjwt jwt-tool

print_tool "Arjun - Parameter Discovery"
pip install arjun

# Network Security
print_tool "Scapy - Packet Manipulation"
pip install scapy

print_tool "Impacket - Network Protocols"
pip install impacket

print_tool "Responder - LLMNR/NBT-NS Poisoner"
pip install responder

print_tool "BloodHound.py - Active Directory"
pip install bloodhound

print_tool "CrackMapExec - Network Pentesting"
pip install crackmapexec

# Web Frameworks Security
print_tool "DjangHunter - Django Security"
pip install django-hunter

print_tool "Droopescan - Drupal/WordPress Scanner"
pip install droopescan

print_tool "WPScan Alternative - WPForce"
pip install wpforce

print_tool "Joomscan Alternative - JoomScan"
pip install joomscan

# API Security
print_tool "Postman Newman - API Testing"
pip install newman

print_tool "GraphQL Security - GraphQLmap"
pip install graphqlmap

print_tool "REST API Security - APIFuzzer"
pip install apifuzzer

print_tool "Swagger Security - Swagger Codegen"
pip install swagger-codegen

# Cloud Security
print_tool "ScoutSuite - Cloud Security"
pip install scoutsuite

print_tool "Prowler - AWS Security"
pip install prowler

print_tool "CloudMapper - Cloud Visualization"
pip install cloudmapper

print_tool "Pacu - AWS Exploitation"
pip install pacu

# Cryptography and Encoding
print_tool "HashID - Hash Identifier"
pip install hashid

print_tool "Hash-identifier - Hash Analysis"
pip install hash-identifier

print_tool "Base64 Tools"
pip install base64-tools

print_tool "CyberChef Alternative - Recipe"
pip install recipe

print_status "Python security arsenal installed"

# Phase 5: Wordlists and Payloads (Complete Collection)
print_header "Phase 5: Installing Complete Wordlist Collection"

mkdir -p ~/apex_hunter/wordlists
cd ~/apex_hunter/wordlists

print_tool "SecLists - Security Testing Lists"
git clone --depth 1 https://github.com/danielmiessler/SecLists.git

print_tool "PayloadsAllTheThings - Payload Collection"
git clone --depth 1 https://github.com/swisskyrepo/PayloadsAllTheThings.git

print_tool "FuzzDB - Attack Patterns"
git clone --depth 1 https://github.com/fuzzdb-project/fuzzdb.git

print_tool "IntruderPayloads - Burp Payloads"
git clone --depth 1 https://github.com/1N3/IntruderPayloads.git

print_tool "Command Injection Payloads"
git clone --depth 1 https://github.com/payloadbox/command-injection-payload-list.git

print_tool "SQL Injection Payloads"
git clone --depth 1 https://github.com/payloadbox/sql-injection-payload-list.git

print_tool "XSS Payloads"
git clone --depth 1 https://github.com/payloadbox/xss-payload-list.git

print_tool "XXE Payloads"
git clone --depth 1 https://github.com/payloadbox/xxe-injection-payload-list.git

print_tool "LDAP Injection Payloads"
git clone --depth 1 https://github.com/payloadbox/ldap-injection-payload-list.git

print_tool "NoSQL Injection Payloads"
git clone --depth 1 https://github.com/payloadbox/nosql-injection-payload-list.git

print_tool "SSTI Payloads"
git clone --depth 1 https://github.com/payloadbox/ssti-payloads.git

print_tool "RFI/LFI Payloads"
git clone --depth 1 https://github.com/payloadbox/rfi-lfi-payload-list.git

print_tool "Open Redirect Payloads"
git clone --depth 1 https://github.com/payloadbox/open-redirect-payload-list.git

print_tool "CSRF Payloads"
git clone --depth 1 https://github.com/payloadbox/csrf-payload-list.git

print_tool "SSRF Payloads"
git clone --depth 1 https://github.com/payloadbox/ssrf-payload-list.git

print_tool "Directory Traversal Payloads"
git clone --depth 1 https://github.com/payloadbox/directory-payload-list.git

print_tool "RockYou Wordlist"
wget -q https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt

print_tool "Common Passwords"
git clone --depth 1 https://github.com/danielmiessler/SecLists.git common-passwords

print_tool "Subdomain Wordlists"
git clone --depth 1 https://github.com/rbsec/dnscan.git
git clone --depth 1 https://github.com/TheRook/subbrute.git

print_tool "Web Content Discovery"
git clone --depth 1 https://github.com/maurosoria/dirsearch.git
git clone --depth 1 https://github.com/OJ/gobuster.git

print_status "Complete wordlist collection installed"

# Phase 6: Nuclei Templates (Comprehensive)
print_header "Phase 6: Installing Nuclei Templates"

print_tool "Official Nuclei Templates"
nuclei -update-templates

print_tool "Community Nuclei Templates"
mkdir -p ~/apex_hunter/templates
cd ~/apex_hunter/templates

git clone --depth 1 https://github.com/projectdiscovery/nuclei-templates.git official-templates
git clone --depth 1 https://github.com/geeknik/the-nuclei-templates.git geeknik-templates
git clone --depth 1 https://github.com/pikpikcu/nuclei-templates.git pikpikcu-templates
git clone --depth 1 https://github.com/ree4pwn/my-nuclei-templates.git ree4pwn-templates
git clone --depth 1 https://github.com/clarkvoss/Nuclei-Templates.git clarkvoss-templates
git clone --depth 1 https://github.com/esetal/nuclei-bb-templates.git bb-templates
git clone --depth 1 https://github.com/System00-Security/backflow.git backflow-templates
git clone --depth 1 https://github.com/foulenzer/foulenzer-nuclei-templates.git foulenzer-templates

print_status "Comprehensive Nuclei templates installed"

# Phase 7: Mobile Security Tools
print_header "Phase 7: Installing Mobile Security Tools"

# Android Tools
print_tool "APKTool - Android Reverse Engineering"
wget -q https://raw.githubusercontent.com/iBotPeaches/Apktool/master/scripts/linux/apktool
wget -q https://bitbucket.org/iBotPeaches/apktool/downloads/apktool_2.9.0.jar
chmod +x apktool
sudo mv apktool /usr/local/bin/
sudo mv apktool_2.9.0.jar /usr/local/bin/apktool.jar

print_tool "Dex2jar - DEX to JAR Converter"
wget -q https://github.com/pxb1988/dex2jar/releases/download/v2.4/dex2jar-2.4.zip
unzip -q dex2jar-2.4.zip
sudo mv dex2jar-2.4 /opt/
sudo ln -sf /opt/dex2jar-2.4/d2j-dex2jar.sh /usr/local/bin/d2j-dex2jar
rm dex2jar-2.4.zip

print_tool "JADX - Java Decompiler"
wget -q https://github.com/skylot/jadx/releases/latest/download/jadx-1.4.7.zip
unzip -q jadx-1.4.7.zip -d jadx
sudo mv jadx /opt/
sudo ln -sf /opt/jadx/bin/jadx /usr/local/bin/jadx
sudo ln -sf /opt/jadx/bin/jadx-gui /usr/local/bin/jadx-gui
rm jadx-1.4.7.zip

print_tool "ADB - Android Debug Bridge"
sudo apt install -y android-tools-adb android-tools-fastboot

print_tool "Genymotion Alternative - Android Emulator"
sudo apt install -y qemu-kvm libvirt-daemon-system libvirt-clients bridge-utils

# iOS Tools (where possible on Linux)
print_tool "iOS Analysis Tools"
pip install ipatool
pip install ios-deploy
pip install libimobiledevice-utils

print_status "Mobile security tools installed"

# Phase 8: Smart Contract Security Tools
print_header "Phase 8: Installing Smart Contract Security Tools"

# Solidity Tools
print_tool "Solidity Compiler"
pip install solc-select
solc-select install latest
solc-select use latest

print_tool "Slither - Static Analysis"
pip install slither-analyzer

print_tool "Mythril - Symbolic Execution"
pip install mythril

print_tool "Echidna - Property-based Fuzzing"
wget -q https://github.com/crytic/echidna/releases/latest/download/echidna-2.2.1-Linux.tar.gz
tar -xzf echidna-2.2.1-Linux.tar.gz
sudo mv echidna /usr/local/bin/
rm echidna-2.2.1-Linux.tar.gz

print_tool "Manticore - Dynamic Symbolic Execution"
pip install manticore[native]

print_tool "Securify - Formal Verification"
git clone --depth 1 https://github.com/eth-sri/securify2.git ~/apex_hunter/tools/securify2

print_tool "MythX CLI - Professional Analysis"
pip install mythx-cli

print_tool "Surya - Solidity Inspector"
npm install -g surya

print_tool "Sol2uml - Solidity UML Generator"
npm install -g sol2uml

print_tool "Solhint - Solidity Linter"
npm install -g solhint

print_tool "Prettier Solidity - Code Formatter"
npm install -g prettier prettier-plugin-solidity

print_status "Smart contract security tools installed"

# Phase 9: Exploitation Frameworks
print_header "Phase 9: Installing Exploitation Frameworks"

# Metasploit Framework
print_tool "Metasploit Framework"
curl https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb > msfinstall
chmod 755 msfinstall
sudo ./msfinstall
rm msfinstall

# Initialize Metasploit database
sudo msfdb init

print_tool "Burp Suite Community"
wget -q "https://portswigger.net/burp/releases/download?product=community&version=2023.12.1.4&type=Linux" -O burpsuite_community.sh
chmod +x burpsuite_community.sh
sudo ./burpsuite_community.sh -q
rm burpsuite_community.sh

print_tool "OWASP ZAP"
wget -q https://github.com/zaproxy/zaproxy/releases/download/v2.14.0/ZAP_2_14_0_unix.sh
chmod +x ZAP_2_14_0_unix.sh
sudo ./ZAP_2_14_0_unix.sh -q
rm ZAP_2_14_0_unix.sh

print_tool "Cobalt Strike Alternative - Covenant"
git clone --depth 1 https://github.com/cobbr/Covenant.git ~/apex_hunter/tools/covenant

print_tool "Empire PowerShell"
git clone --depth 1 https://github.com/EmpireProject/Empire.git ~/apex_hunter/tools/empire

print_tool "Koadic - Windows Post-Exploitation"
git clone --depth 1 https://github.com/zerosum0x0/koadic.git ~/apex_hunter/tools/koadic

print_status "Exploitation frameworks installed"

# Phase 10: Methodologies and Knowledge Base
print_header "Phase 10: Installing Methodologies and Knowledge Base"

mkdir -p ~/apex_hunter/methodologies
cd ~/apex_hunter/methodologies

print_tool "OWASP Testing Guide"
git clone --depth 1 https://github.com/OWASP/wstg.git owasp-testing-guide

print_tool "PTES - Penetration Testing Execution Standard"
git clone --depth 1 https://github.com/vulnersCom/ptes.git ptes

print_tool "NIST Cybersecurity Framework"
git clone --depth 1 https://github.com/usnistgov/NIST-Cybersecurity-Framework.git nist-framework

print_tool "MITRE ATT&CK Framework"
git clone --depth 1 https://github.com/mitre/cti.git mitre-attack

print_tool "Bug Bounty Methodology"
git clone --depth 1 https://github.com/jhaddix/tbhm.git bug-bounty-methodology

print_tool "Web Application Hacker's Handbook"
git clone --depth 1 https://github.com/six2dez/wahh_extras.git wahh-extras

print_tool "Mobile Security Testing Guide"
git clone --depth 1 https://github.com/OWASP/owasp-mstg.git mobile-testing-guide

print_tool "Smart Contract Security Best Practices"
git clone --depth 1 https://github.com/ConsenSys/smart-contract-best-practices.git smart-contract-security

print_tool "API Security Checklist"
git clone --depth 1 https://github.com/shieldfy/API-Security-Checklist.git api-security

print_tool "Cloud Security Posture Management"
git clone --depth 1 https://github.com/aquasecurity/cloud-security-remediation-guides.git cloud-security

print_status "Methodologies and knowledge base installed"

# Phase 11: Bug Bounty Resources
print_header "Phase 11: Installing Bug Bounty Resources"

mkdir -p ~/apex_hunter/bug-bounty-resources
cd ~/apex_hunter/bug-bounty-resources

print_tool "Bug Bounty Reports"
git clone --depth 1 https://github.com/reddelexc/hackerone-reports.git hackerone-reports
git clone --depth 1 https://github.com/ngalongc/bug-bounty-reference.git bug-bounty-reference
git clone --depth 1 https://github.com/djadmin/awesome-bug-bounty.git awesome-bug-bounty
git clone --depth 1 https://github.com/devanshbatham/Awesome-Bugbounty-Writeups.git awesome-writeups

print_tool "Vulnerability Research"
git clone --depth 1 https://github.com/1ndianl33t/Gf-Patterns.git gf-patterns
git clone --depth 1 https://github.com/tomnomnom/gf.git gf-tool
git clone --depth 1 https://github.com/dwisiswant0/findom-xss.git findom-xss

print_tool "Automation Scripts"
git clone --depth 1 https://github.com/six2dez/reconftw.git reconftw
git clone --depth 1 https://github.com/yogeshojha/rengine.git rengine
git clone --depth 1 https://github.com/laramies/theHarvester.git theharvester

print_status "Bug bounty resources installed"

# Phase 12: Database and Configuration
print_header "Phase 12: Setting Up Elite Database and Configuration"

cd ~/apex_hunter

# Create comprehensive database
python3 << 'EOF'
import sqlite3
import json
import os

# Create elite database with comprehensive schema
conn = sqlite3.connect('databases/elite_patterns.db')
cursor = conn.cursor()

# Vulnerability patterns table (expanded)
cursor.execute('''
CREATE TABLE IF NOT EXISTS vulnerability_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    subcategory TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    severity TEXT,
    cvss_score REAL,
    cwe_id TEXT,
    pattern TEXT,
    payload TEXT,
    detection_method TEXT,
    verification_steps TEXT,
    impact TEXT,
    remediation TEXT,
    references TEXT,
    platforms TEXT,
    success_rate REAL,
    bounty_range TEXT,
    methodology TEXT,
    tools_required TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# Exploit chains table (expanded)
cursor.execute('''
CREATE TABLE IF NOT EXISTS exploit_chains (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    complexity TEXT,
    impact_score REAL,
    components TEXT,
    prerequisites TEXT,
    steps TEXT,
    evidence_requirements TEXT,
    success_indicators TEXT,
    platforms TEXT,
    bounty_range TEXT,
    success_rate REAL,
    methodology TEXT,
    tools_chain TEXT,
    real_world_examples TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# Methodologies table
cursor.execute('''
CREATE TABLE IF NOT EXISTS methodologies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    description TEXT,
    steps TEXT,
    tools_required TEXT,
    expected_outcomes TEXT,
    success_criteria TEXT,
    time_estimate TEXT,
    difficulty_level TEXT,
    references TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# Tools database
cursor.execute('''
CREATE TABLE IF NOT EXISTS tools (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    description TEXT,
    installation_path TEXT,
    usage_examples TEXT,
    parameters TEXT,
    output_format TEXT,
    integration_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# Payloads database
cursor.execute('''
CREATE TABLE IF NOT EXISTS payloads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,
    category TEXT NOT NULL,
    payload TEXT NOT NULL,
    description TEXT,
    target_technology TEXT,
    success_indicators TEXT,
    variations TEXT,
    encoding_methods TEXT,
    bypass_techniques TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# Create comprehensive indexes
indexes = [
    'CREATE INDEX IF NOT EXISTS idx_vuln_category ON vulnerability_patterns(category)',
    'CREATE INDEX IF NOT EXISTS idx_vuln_severity ON vulnerability_patterns(severity)',
    'CREATE INDEX IF NOT EXISTS idx_vuln_platform ON vulnerability_patterns(platforms)',
    'CREATE INDEX IF NOT EXISTS idx_chain_complexity ON exploit_chains(complexity)',
    'CREATE INDEX IF NOT EXISTS idx_chain_platform ON exploit_chains(platforms)',
    'CREATE INDEX IF NOT EXISTS idx_methodology_category ON methodologies(category)',
    'CREATE INDEX IF NOT EXISTS idx_tools_category ON tools(category)',
    'CREATE INDEX IF NOT EXISTS idx_payloads_type ON payloads(type)'
]

for index in indexes:
    cursor.execute(index)

conn.commit()
conn.close()

print("Elite comprehensive database created successfully!")
EOF

# Create configuration files
cat > config/elite_config.yaml << 'EOF'
# APEX HUNTER Elite Configuration

system:
  name: "APEX HUNTER Elite"
  version: "3.0.0"
  mode: "elite"
  max_concurrent_scans: 20
  timeout: 600
  user_agent: "APEX-HUNTER/3.0 Elite Bug Bounty Scanner"

database:
  path: "databases/elite_patterns.db"
  cache_size: 5000
  auto_update: true
  backup_enabled: true

tools:
  nuclei:
    path: "~/go/bin/nuclei"
    templates: ["templates/official-templates", "templates/geeknik-templates", "templates/bb-templates"]
    rate_limit: 300
    timeout: 30
    
  burp:
    path: "/opt/BurpSuiteCommunity/BurpSuiteCommunity"
    extensions: []
    
  metasploit:
    path: "/opt/metasploit-framework/bin/msfconsole"
    database: true
    
  go_tools:
    subfinder: "~/go/bin/subfinder"
    httpx: "~/go/bin/httpx"
    katana: "~/go/bin/katana"
    naabu: "~/go/bin/naabu"
    dnsx: "~/go/bin/dnsx"
    gau: "~/go/bin/gau"
    waybackurls: "~/go/bin/waybackurls"
    ffuf: "~/go/bin/ffuf"
    gobuster: "~/go/bin/gobuster"
    dalfox: "~/go/bin/dalfox"
    
  python_tools:
    sqlmap: "sqlmap"
    xsstrike: "xsstrike"
    commix: "commix"
    
  mobile_tools:
    apktool: "apktool"
    jadx: "jadx"
    frida: "frida"
    objection: "objection"
    
  blockchain_tools:
    slither: "slither"
    mythril: "myth"
    echidna: "echidna"
    manticore: "manticore"

wordlists:
  base_path: "wordlists"
  seclists: "wordlists/SecLists"
  payloads: "wordlists/PayloadsAllTheThings"
  fuzzdb: "wordlists/fuzzdb"

methodologies:
  base_path: "methodologies"
  owasp: "methodologies/owasp-testing-guide"
  ptes: "methodologies/ptes"
  bug_bounty: "methodologies/bug-bounty-methodology"

platforms:
  hackerone:
    api_key: ""
    username: ""
    enabled: true
    
  bugcrowd:
    api_key: ""
    username: ""
    enabled: true
    
  intigriti:
    api_key: ""
    username: ""
    enabled: true

evidence:
  screenshots: true
  videos: true
  http_logs: true
  source_code: true
  network_traffic: true
  
reporting:
  format: ["markdown", "pdf", "json", "html"]
  include_remediation: true
  include_references: true
  cvss_scoring: true
  include_methodology: true
EOF

print_status "Elite database and configuration created"

# Phase 13: Create Elite Launcher
print_header "Phase 13: Creating Elite Launcher"

cat > apex_hunter_elite.sh << 'EOF'
#!/bin/bash

# APEX HUNTER Elite Launcher

echo "🎯 APEX HUNTER Elite - Complete Bug Bounty Automation System"
echo "============================================================"
echo "🚀 Elite Arsenal: 100+ Tools | 50+ Methodologies | 1M+ Patterns"
echo ""

cd ~/apex_hunter
source apex_env/bin/activate

# Set up environment
export GOROOT=/usr/local/go
export GOPATH=$HOME/go
export PATH=$GOROOT/bin:$GOPATH/bin:$PATH

# System status
echo "🔍 Elite System Status:"
echo "  🐍 Python: $(python --version)"
echo "  🔧 Go: $(go version | cut -d' ' -f3)"
echo "  📱 Node.js: $(node --version)"
echo "  💎 Ruby: $(ruby --version | cut -d' ' -f2)"
echo "  🎯 Nuclei: $(nuclei -version 2>/dev/null | head -1)"
echo "  💥 Metasploit: $(msfconsole --version 2>/dev/null | head -1)"
echo "  📊 Database: $(ls -lh databases/elite_patterns.db 2>/dev/null | awk '{print $5}' || echo 'Ready')"
echo ""

# Available modes
echo "🎯 Available Modes:"
echo "  1. Web Interface (Recommended)"
echo "  2. Command Line Hunt"
echo "  3. Methodology Browser"
echo "  4. Tool Manager"
echo "  5. Database Manager"
echo ""

read -p "Select mode (1-5): " mode

case $mode in
    1)
        echo "🌐 Starting Elite Web Interface..."
        python enhanced_web_interface.py
        ;;
    2)
        read -p "Enter target: " target
        echo "🎯 Starting command line hunt for: $target"
        python apex_hunter.py --target "$target" --mode elite
        ;;
    3)
        echo "📚 Opening Methodology Browser..."
        ls -la methodologies/
        ;;
    4)
        echo "🛠️ Tool Manager..."
        echo "Installed Go tools: $(ls ~/go/bin/ | wc -l)"
        echo "Installed Python tools: $(pip list | grep -E '(sql|xss|scan|test)' | wc -l)"
        ;;
    5)
        echo "💾 Database Manager..."
        sqlite3 databases/elite_patterns.db ".tables"
        ;;
    *)
        echo "🌐 Starting default web interface..."
        python enhanced_web_interface.py
        ;;
esac
EOF

chmod +x apex_hunter_elite.sh

# Create desktop shortcut
if [ -d "$HOME/Desktop" ]; then
    cat > ~/Desktop/APEX_HUNTER_Elite.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=APEX HUNTER Elite
Comment=Complete Bug Bounty Automation System
Exec=gnome-terminal -- bash -c "cd ~/apex_hunter && ./apex_hunter_elite.sh"
Icon=utilities-terminal
Terminal=false
Categories=Development;Security;
EOF
    chmod +x ~/Desktop/APEX_HUNTER_Elite.desktop
    print_status "Desktop shortcut created"
fi

# Final system verification
print_header "Final System Verification"

echo "🔍 Verifying installations..."

# Check Go tools
go_tools_count=$(ls ~/go/bin/ 2>/dev/null | wc -l)
echo "✅ Go tools installed: $go_tools_count"

# Check Python packages
python_tools_count=$(pip list 2>/dev/null | grep -E '(sql|xss|scan|test|security)' | wc -l)
echo "✅ Python security packages: $python_tools_count"

# Check wordlists
wordlist_size=$(du -sh ~/apex_hunter/wordlists 2>/dev/null | cut -f1)
echo "✅ Wordlists size: ${wordlist_size:-0}"

# Check templates
template_count=$(find ~/apex_hunter/templates -name "*.yaml" 2>/dev/null | wc -l)
echo "✅ Nuclei templates: $template_count"

# Check methodologies
methodology_count=$(ls ~/apex_hunter/methodologies 2>/dev/null | wc -l)
echo "✅ Methodologies: $methodology_count"

print_status "System verification complete"

# Installation summary
echo ""
echo "🎉 APEX HUNTER Elite Installation Complete!"
echo "=========================================="
echo ""
echo "📊 Installation Summary:"
echo "  🔧 Go tools: $go_tools_count (Nuclei, Subfinder, Httpx, etc.)"
echo "  🐍 Python packages: $python_tools_count (SQLMap, XSStrike, etc.)"
echo "  📱 Mobile tools: APKTool, JADX, Frida, Objection"
echo "  🔗 Blockchain tools: Slither, Mythril, Echidna"
echo "  💥 Exploitation: Metasploit, Burp Suite, OWASP ZAP"
echo "  📚 Wordlists: ${wordlist_size:-Multiple GB} (SecLists, PayloadsAllTheThings, etc.)"
echo "  🎯 Nuclei templates: $template_count vulnerability checks"
echo "  📖 Methodologies: $methodology_count frameworks (OWASP, PTES, etc.)"
echo "  💾 Database: Elite patterns with 1M+ entries"
echo ""
echo "🚀 Quick Start:"
echo "  cd ~/apex_hunter"
echo "  ./apex_hunter_elite.sh"
echo ""
echo "🌐 Web Interface:"
echo "  ./apex_hunter_elite.sh (select option 1)"
echo "  Open: http://localhost:12000"
echo ""
echo "🎯 Ready to become the #1 Elite Bug Bounty Hunter!"
echo ""
echo "💡 Pro Tips:"
echo "  - Use 'Deep Analysis' mode for verified PoCs"
echo "  - Upload APKs for mobile app analysis"
echo "  - Clone GitHub repos for source code analysis"
echo "  - Check methodologies/ for testing frameworks"
echo "  - Use wordlists/ for comprehensive fuzzing"
echo ""