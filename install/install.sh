#!/bin/bash
# Agova Installer - Always installs to ~/agova

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

print_message() { echo -e "${2}${1}${NC}"; }

print_header() {
    echo ""
    echo -e "${CYAN}========================================${NC}"
    echo -e "${CYAN}    Agova AI Agent System Installer     ${NC}"
    echo -e "${CYAN}========================================${NC}"
    echo ""
}

AGOVA_DIR="$HOME/agova"

print_header
print_message "📦 Installing Agova to: $AGOVA_DIR" "$BLUE"

# Check Python
if ! command -v python3 &> /dev/null; then
    print_message "❌ Python 3 not installed" "$RED"
    exit 1
fi
print_message "✅ Python 3 found" "$GREEN"

# Install dependencies
print_message "📥 Installing dependencies..." "$BLUE"
cd "$AGOVA_DIR"
pip install -r requirements.txt
print_message "✅ Dependencies installed" "$GREEN"

# Create workspace
mkdir -p "$AGOVA_DIR/workspace"

# Remove old alias
sed -i '/alias agova=/d' ~/.bashrc 2>/dev/null
sed -i '/# Agova/d' ~/.bashrc 2>/dev/null

# Add fixed alias
echo "" >> ~/.bashrc
echo "# Agova AI Agent System" >> ~/.bashrc
echo "alias agova='python3 $HOME/agova/main.py'" >> ~/.bashrc

print_message "✅ Alias added to ~/.bashrc" "$GREEN"

source ~/.bashrc 2>/dev/null

echo ""
echo -e "${GREEN}✅ Installation Complete!${NC}"
echo ""
echo "Run: source ~/.bashrc"
echo "Then: agova"
