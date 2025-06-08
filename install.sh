#!/bin/bash

# VulnScanner v2.0 Installation Script
# For authorized testing and educational use only

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                    VulnScanner v2.0 Installer                   ║"
echo "║              Advanced Penetration Testing Toolkit               ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}[*] Starting installation...${NC}"

# Check if running as root for nmap installation
if [[ $EUID -eq 0 ]]; then
   echo -e "${YELLOW}[!] Running as root - will install system dependencies${NC}"
   ROOT_ACCESS=true
else
   echo -e "${YELLOW}[!] Not running as root - will skip system dependency installation${NC}"
   ROOT_ACCESS=false
fi

# Install system dependencies
echo -e "${BLUE}[*] Installing system dependencies...${NC}"

if [ "$ROOT_ACCESS" = true ]; then
    # Detect package manager and install nmap
    if command -v apt-get &> /dev/null; then
        echo -e "${GREEN}[✓] Detected apt package manager${NC}"
        apt-get update
        apt-get install -y nmap python3-pip python3-venv
    elif command -v yum &> /dev/null; then
        echo -e "${GREEN}[✓] Detected yum package manager${NC}"
        yum install -y nmap python3-pip python3-venv
    elif command -v dnf &> /dev/null; then
        echo -e "${GREEN}[✓] Detected dnf package manager${NC}"
        dnf install -y nmap python3-pip python3-venv
    elif command -v pacman &> /dev/null; then
        echo -e "${GREEN}[✓] Detected pacman package manager${NC}"
        pacman -S --noconfirm nmap python-pip python-virtualenv
    else
        echo -e "${RED}[✗] Could not detect package manager. Please install nmap manually.${NC}"
    fi
else
    echo -e "${YELLOW}[!] Skipping system dependency installation (requires root)${NC}"
    echo -e "${BLUE}[i] Please ensure nmap is installed: sudo apt install nmap${NC}"
fi

# Check Python version
echo -e "${BLUE}[*] Checking Python version...${NC}"
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}[✓] Python version: $python_version${NC}"

# Create virtual environment
echo -e "${BLUE}[*] Creating virtual environment...${NC}"
if [ -d "venv" ]; then
    echo -e "${YELLOW}[!] Virtual environment already exists${NC}"
else
    python3 -m venv venv
    echo -e "${GREEN}[✓] Virtual environment created${NC}"
fi

# Activate virtual environment and install dependencies
echo -e "${BLUE}[*] Installing Python dependencies...${NC}"
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

echo -e "${GREEN}[✓] Python dependencies installed${NC}"

# Make scripts executable
echo -e "${BLUE}[*] Setting up permissions...${NC}"
chmod +x main.py
chmod +x gui.py

# Create launcher scripts
echo -e "${BLUE}[*] Creating launcher scripts...${NC}"

# CLI launcher
cat > vulnscan << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
python main.py "$@"
EOF

# GUI launcher
cat > vulnscan-gui << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
python gui.py "$@"
EOF

chmod +x vulnscan vulnscan-gui

echo -e "${GREEN}[✓] Launcher scripts created${NC}"

# Test installation
echo -e "${BLUE}[*] Testing installation...${NC}"
if python -c "import nmap, requests, bs4, colorama, tqdm" 2>/dev/null; then
    echo -e "${GREEN}[✓] All dependencies imported successfully${NC}"
else
    echo -e "${RED}[✗] Some dependencies failed to import${NC}"
    exit 1
fi

# Create desktop entry for GUI (optional)
if command -v desktop-file-install &> /dev/null; then
    echo -e "${BLUE}[*] Creating desktop entry...${NC}"
    cat > vulnscanner.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=VulnScanner v2.0
Comment=Advanced Penetration Testing Toolkit
Exec=$(pwd)/vulnscan-gui
Icon=security-high
Terminal=false
Categories=Security;Network;
EOF
    
    if [ "$ROOT_ACCESS" = true ]; then
        desktop-file-install vulnscanner.desktop
        echo -e "${GREEN}[✓] Desktop entry installed${NC}"
    else
        echo -e "${YELLOW}[!] Desktop entry created but not installed (requires root)${NC}"
    fi
fi

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════════╗"
echo -e "║                     Installation Complete!                      ║"
echo -e "╚══════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Usage:${NC}"
echo -e "  CLI Mode:  ${GREEN}./vulnscan --url https://example.com${NC}"
echo -e "  GUI Mode:  ${GREEN}./vulnscan-gui${NC}"
echo ""
echo -e "${BLUE}Examples:${NC}"
echo -e "  ${GREEN}./vulnscan --url https://example.com --threads 10 --enable-portscan${NC}"
echo -e "  ${GREEN}./vulnscan --url https://testsite.com --output json --max-pages 20${NC}"
echo ""
echo -e "${YELLOW}⚠️  Important: This tool is for authorized testing only!${NC}"
echo -e "${YELLOW}   Ensure you have permission to test the target systems.${NC}"
echo "" 