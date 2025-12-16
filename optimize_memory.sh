#!/bin/bash
# APEX HUNTER - Memory Optimization Script
# Optimizes system for maximum available RAM

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}"
cat << "EOF"
🧠 APEX HUNTER - Memory Optimization
===================================
Optimizing system for maximum RAM availability
EOF
echo -e "${NC}"

# Function to check command success
check_success() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ $1${NC}"
    else
        echo -e "${YELLOW}⚠️  $1 (non-critical)${NC}"
    fi
}

# Get current memory info
echo -e "${BLUE}📊 Current Memory Status:${NC}"
free -h
echo ""

# Stop unnecessary services
echo -e "${BLUE}🛑 Stopping unnecessary services...${NC}"

services_to_stop=(
    "apache2"
    "nginx" 
    "mysql"
    "mariadb"
    "postgresql"
    "mongodb"
    "redis-server"
    "memcached"
    "elasticsearch"
    "docker"
    "snapd"
    "bluetooth"
    "cups"
    "cups-browsed"
    "avahi-daemon"
    "whoopsie"
    "kerneloops"
    "apport"
    "speech-dispatcher"
    "pulseaudio"
    "gdm3"
    "lightdm"
    "sddm"
    "NetworkManager"
    "ModemManager"
    "wpa_supplicant"
    "packagekit"
    "udisks2"
    "accounts-daemon"
    "colord"
    "geoclue"
    "thermald"
    "irqbalance"
)

for service in "${services_to_stop[@]}"; do
    if systemctl is-active --quiet "$service" 2>/dev/null; then
        echo -e "  🛑 Stopping $service..."
        sudo systemctl stop "$service" 2>/dev/null
        check_success "$service stopped"
    fi
done

# Disable unnecessary services from starting
echo -e "\n${BLUE}🚫 Disabling unnecessary services...${NC}"

services_to_disable=(
    "snapd"
    "bluetooth"
    "cups"
    "cups-browsed"
    "avahi-daemon"
    "whoopsie"
    "kerneloops"
    "apport"
    "speech-dispatcher"
    "ModemManager"
    "packagekit"
    "accounts-daemon"
    "colord"
    "geoclue"
    "thermald"
)

for service in "${services_to_disable[@]}"; do
    if systemctl is-enabled --quiet "$service" 2>/dev/null; then
        echo -e "  🚫 Disabling $service..."
        sudo systemctl disable "$service" 2>/dev/null
        check_success "$service disabled"
    fi
done

# Clear system caches
echo -e "\n${BLUE}🧹 Clearing system caches...${NC}"

echo -e "  🧹 Clearing package cache..."
sudo apt clean
sudo apt autoclean
check_success "Package cache cleared"

echo -e "  🧹 Clearing system page cache..."
sudo sync
sudo sysctl vm.drop_caches=1
check_success "Page cache cleared"

echo -e "  🧹 Clearing dentries and inodes..."
sudo sysctl vm.drop_caches=2
check_success "Dentries and inodes cleared"

echo -e "  🧹 Clearing all caches..."
sudo sysctl vm.drop_caches=3
check_success "All caches cleared"

# Optimize swap usage
echo -e "\n${BLUE}💾 Optimizing swap usage...${NC}"

echo -e "  💾 Setting swappiness to 10..."
sudo sysctl vm.swappiness=10
echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf >/dev/null
check_success "Swappiness optimized"

echo -e "  💾 Setting cache pressure to 50..."
sudo sysctl vm.vfs_cache_pressure=50
echo 'vm.vfs_cache_pressure=50' | sudo tee -a /etc/sysctl.conf >/dev/null
check_success "Cache pressure optimized"

# Remove unnecessary packages
echo -e "\n${BLUE}📦 Removing unnecessary packages...${NC}"

echo -e "  📦 Removing orphaned packages..."
sudo apt autoremove -y >/dev/null 2>&1
check_success "Orphaned packages removed"

echo -e "  📦 Removing unnecessary language packs..."
sudo apt purge -y language-pack-* >/dev/null 2>&1 || true
check_success "Language packs removed"

echo -e "  📦 Removing documentation packages..."
sudo apt purge -y *-doc *-docs >/dev/null 2>&1 || true
check_success "Documentation packages removed"

# Optimize kernel parameters
echo -e "\n${BLUE}⚙️  Optimizing kernel parameters...${NC}"

# Create optimized sysctl configuration
sudo tee /etc/sysctl.d/99-apex-hunter.conf >/dev/null << EOF
# APEX HUNTER Memory Optimizations

# Memory management
vm.swappiness=10
vm.vfs_cache_pressure=50
vm.dirty_ratio=15
vm.dirty_background_ratio=5
vm.overcommit_memory=1
vm.overcommit_ratio=50

# Network optimizations
net.core.rmem_max=16777216
net.core.wmem_max=16777216
net.ipv4.tcp_rmem=4096 87380 16777216
net.ipv4.tcp_wmem=4096 65536 16777216

# File system optimizations
fs.file-max=2097152
fs.inotify.max_user_watches=524288
EOF

sudo sysctl -p /etc/sysctl.d/99-apex-hunter.conf >/dev/null 2>&1
check_success "Kernel parameters optimized"

# Kill memory-heavy processes
echo -e "\n${BLUE}🔪 Terminating memory-heavy processes...${NC}"

memory_heavy_processes=(
    "firefox"
    "chrome"
    "chromium"
    "thunderbird"
    "libreoffice"
    "gimp"
    "inkscape"
    "blender"
    "vlc"
    "steam"
    "discord"
    "slack"
    "teams"
    "zoom"
    "skype"
)

for process in "${memory_heavy_processes[@]}"; do
    if pgrep "$process" >/dev/null 2>&1; then
        echo -e "  🔪 Terminating $process..."
        sudo pkill -f "$process" 2>/dev/null || true
        check_success "$process terminated"
    fi
done

# Optimize systemd services
echo -e "\n${BLUE}⚙️  Optimizing systemd services...${NC}"

echo -e "  ⚙️  Masking unnecessary services..."
services_to_mask=(
    "snapd.service"
    "snapd.socket"
    "snapd.seeded.service"
    "bluetooth.service"
    "cups.service"
    "cups-browsed.service"
    "avahi-daemon.service"
    "whoopsie.service"
    "kerneloops.service"
    "apport.service"
)

for service in "${services_to_mask[@]}"; do
    sudo systemctl mask "$service" 2>/dev/null || true
done
check_success "Unnecessary services masked"

# Create memory monitoring script
echo -e "\n${BLUE}📊 Creating memory monitoring script...${NC}"

sudo tee /usr/local/bin/apex-memory-monitor >/dev/null << 'EOF'
#!/bin/bash
# APEX HUNTER Memory Monitor

while true; do
    clear
    echo "🧠 APEX HUNTER - Memory Monitor"
    echo "==============================="
    echo ""
    
    # Memory usage
    echo "📊 Memory Usage:"
    free -h
    echo ""
    
    # Top memory consumers
    echo "🔝 Top Memory Consumers:"
    ps aux --sort=-%mem | head -10
    echo ""
    
    # APEX HUNTER processes
    echo "🎯 APEX HUNTER Processes:"
    ps aux | grep -E "(apex_hunter|python.*apex)" | grep -v grep || echo "No APEX HUNTER processes running"
    echo ""
    
    echo "Press Ctrl+C to exit"
    sleep 5
done
EOF

sudo chmod +x /usr/local/bin/apex-memory-monitor
check_success "Memory monitor created"

# Final memory status
echo -e "\n${GREEN}🎉 Memory Optimization Complete!${NC}"
echo -e "${GREEN}================================${NC}"

echo -e "\n${BLUE}📊 Final Memory Status:${NC}"
free -h

echo -e "\n${CYAN}Optimizations Applied:${NC}"
echo -e "  ✅ Stopped unnecessary services"
echo -e "  ✅ Disabled startup services"
echo -e "  ✅ Cleared system caches"
echo -e "  ✅ Optimized swap usage"
echo -e "  ✅ Removed unnecessary packages"
echo -e "  ✅ Optimized kernel parameters"
echo -e "  ✅ Terminated memory-heavy processes"
echo -e "  ✅ Masked unnecessary systemd services"

echo -e "\n${CYAN}Available Commands:${NC}"
echo -e "  📊 Monitor memory: apex-memory-monitor"
echo -e "  🧹 Clear caches: sudo sysctl vm.drop_caches=3"
echo -e "  🔄 Restart optimization: ./optimize_memory.sh"

echo -e "\n${YELLOW}Note: Some optimizations require a reboot to take full effect${NC}"
echo -e "${GREEN}System is now optimized for APEX HUNTER! 🚀${NC}"