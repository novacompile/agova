#!/bin/bash
###############################################################################
# Agova AI Agent System - Installation Script (Linux/Mac)
# Simple, reliable installation that just works
###############################################################################

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

print_message() {
    echo -e "${2}${1}${NC}"
}

print_header() {
    echo ""
    echo -e "${CYAN}========================================${NC}"
    echo -e "${CYAN}    Agova AI Agent System Installer     ${NC}"
    echo -e "${CYAN}========================================${NC}"
    echo ""
}

# Get the directory where the install script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Agova directory is one level up from install/
AGOVA_DIR="$(dirname "$SCRIPT_DIR")"

print_header

print_message "📦 Agova directory: $AGOVA_DIR" "$BLUE"

# Check Python
if ! command -v python3 &> /dev/null; then
    print_message "❌ Python 3 is not installed. Please install Python 3.8 or higher." "$RED"
    exit 1
fi
print_message "✅ Python 3 found: $(python3 --version)" "$GREEN"

# Check pip
if ! command -v pip3 &> /dev/null; then
    print_message "❌ pip3 is not installed. Please install pip3." "$RED"
    exit 1
fi
print_message "✅ pip3 found" "$GREEN"

# Install dependencies
print_message "📥 Installing dependencies..." "$BLUE"
cd "$AGOVA_DIR"
pip3 install -r requirements.txt
print_message "✅ Dependencies installed" "$GREEN"

# Create workspace directory if it doesn't exist
mkdir -p "$AGOVA_DIR/workspace"
print_message "✅ Workspace directory ready" "$GREEN"

# Determine shell config file
SHELL_CONFIG=""
if [ -n "$ZSH_VERSION" ] || [[ "$SHELL" == *"zsh"* ]]; then
    SHELL_CONFIG="$HOME/.zshrc"
elif [ -n "$BASH_VERSION" ] || [[ "$SHELL" == *"bash"* ]]; then
    SHELL_CONFIG="$HOME/.bashrc"
else
    # Default to .bashrc
    SHELL_CONFIG="$HOME/.bashrc"
fi

print_message "🔧 Shell config: $SHELL_CONFIG" "$YELLOW"

# Remove any existing agova aliases
if [ -f "$SHELL_CONFIG" ]; then
    # Create temp file without old agova lines
    grep -v "alias agova=" "$SHELL_CONFIG" > "${SHELL_CONFIG}.tmp" 2>/dev/null || true
    grep -v "Agova AI Agent System" "${SHELL_CONFIG}.tmp" > "$SHELL_CONFIG" 2>/dev/null || true
    rm -f "${SHELL_CONFIG}.tmp"
fi

# Add the correct alias
echo "" >> "$SHELL_CONFIG"
echo "# Agova AI Agent System" >> "$SHELL_CONFIG"
echo "alias agova=\"python3 $AGOVA_DIR/main.py\"" >> "$SHELL_CONFIG"

print_message "✅ Alias added to $SHELL_CONFIG" "$GREEN"

# Also create symlink in /usr/local/bin for system-wide access
print_message "🔗 Creating system-wide command..." "$BLUE"
if [ -d "/usr/local/bin" ]; then
    sudo ln -sf "$AGOVA_DIR/agova.sh" /usr/local/bin/agova 2>/dev/null && {
        print_message "✅ System-wide 'agova' command created" "$GREEN"
    } || {
        print_message "⚠️  Skipping symlink (will use alias instead)" "$YELLOW"
    }
fi

# Create agova.sh wrapper in agova directory
cat > "$AGOVA_DIR/agova.sh" << 'EOF'
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$SCRIPT_DIR/main.py" "$@"
EOF
chmod +x "$AGOVA_DIR/agova.sh"

# Print completion
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   ✅ Installation Complete!            ${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${CYAN}Agova is now installed!${NC}"
echo ""
echo -e "${YELLOW}To start using Agova:${NC}"
echo ""
echo -e "1. ${GREEN}Reload your shell:${NC}"
echo -e "   ${CYAN}source $SHELL_CONFIG${NC}"
echo ""
echo -e "2. ${GREEN}Start Agova:${NC}"
echo -e "   ${CYAN}agova${NC}"
echo ""
echo -e "${YELLOW}Quick commands:${NC}"
echo -e "  ${GREEN}agova${NC}              - Start the application"
echo -e "  ${GREEN}agova --setup${NC}      - Run configuration wizard"
echo -e ""
echo -e "${CYAN}Installation directory:${NC} $AGOVA_DIR"
echo -e "${CYAN}Config file:${NC} $AGOVA_DIR/config.json"
echo ""

# Try to source the shell config
source "$SHELL_CONFIG" 2>/dev/null || true
