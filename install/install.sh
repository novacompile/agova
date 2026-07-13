#!/bin/bash
###############################################################################
# Agova AI Agent System - Simple Installation Script (Linux/Mac)
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
AGOVA_DIR="$(dirname "$SCRIPT_DIR")"

print_header

print_message "📦 Installing Agova from: $AGOVA_DIR" "$BLUE"

# Check Python
if ! command -v python3 &> /dev/null; then
    print_message "❌ Python 3 is not installed. Please install Python 3.8 or higher." "$RED"
    exit 1
fi
print_message "✅ Python 3 found" "$GREEN"

# Check pip
if ! command -v pip3 &> /dev/null; then
    print_message "❌ pip3 is not installed. Please install pip3." "$RED"
    exit 1
fi
print_message "✅ pip3 found" "$GREEN"

# Install dependencies
print_message "📥 Installing dependencies..." "$BLUE"
cd "$AGOVA_DIR"
pip3 install -r requirements.txt > /dev/null 2>&1
print_message "✅ Dependencies installed" "$GREEN"

# Create workspace directory
mkdir -p workspace
print_message "✅ Workspace directory created" "$GREEN"

# Determine which shell config file to use
SHELL_CONFIG=""
if [ -n "$ZSH_VERSION" ] || [ "$SHELL" = "/bin/zsh" ] || [ "$SHELL" = "/usr/bin/zsh" ]; then
    SHELL_CONFIG="$HOME/.zshrc"
elif [ -n "$BASH_VERSION" ] || [ "$SHELL" = "/bin/bash" ] || [ "$SHELL" = "/usr/bin/bash" ]; then
    if [ -f "$HOME/.bashrc" ]; then
        SHELL_CONFIG="$HOME/.bashrc"
    elif [ -f "$HOME/.bash_profile" ]; then
        SHELL_CONFIG="$HOME/.bash_profile"
    else
        SHELL_CONFIG="$HOME/.bashrc"
    fi
else
    # Default to .bashrc
    SHELL_CONFIG="$HOME/.bashrc"
fi

print_message "🔧 Using shell config: $SHELL_CONFIG" "$YELLOW"

# Remove any existing agova alias
if [ -f "$SHELL_CONFIG" ]; then
    # Remove old alias lines
    sed -i '/# Agova AI Agent System/d' "$SHELL_CONFIG" 2>/dev/null || true
    sed -i '/alias agova=/d' "$SHELL_CONFIG" 2>/dev/null || true
fi

# Add the alias
echo "" >> "$SHELL_CONFIG"
echo "# Agova AI Agent System" >> "$SHELL_CONFIG"
echo "alias agova=\"python3 $AGOVA_DIR/main.py\"" >> "$SHELL_CONFIG"

print_message "✅ Added alias to $SHELL_CONFIG" "$GREEN"

# Also create a symlink in /usr/local/bin if possible (for system-wide access)
if [ -d "/usr/local/bin" ]; then
    # Create a wrapper script in the agova directory
    cat > "$AGOVA_DIR/agova" << 'WRAPPER_EOF'
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$SCRIPT_DIR/main.py" "$@"
WRAPPER_EOF
    
    chmod +x "$AGOVA_DIR/agova"
    
    # Try to create symlink (may need sudo)
    if [ -w "/usr/local/bin" ]; then
        ln -sf "$AGOVA_DIR/agova" /usr/local/bin/agova 2>/dev/null || true
        print_message "✅ Created system-wide symlink" "$GREEN"
    else
        print_message "🔒 Creating symlink with sudo..." "$YELLOW"
        sudo ln -sf "$AGOVA_DIR/agova" /usr/local/bin/agova 2>/dev/null || {
            print_message "⚠️  Could not create symlink (will use alias instead)" "$YELLOW"
        }
    fi
fi

# Source the shell config
print_message "🔄 Reloading shell configuration..." "$BLUE"
source "$SHELL_CONFIG" 2>/dev/null || true

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
echo -e "1. ${GREEN}Restart your terminal${NC}"
echo -e "   ${YELLOW}OR${NC}"
echo -e "   Run: ${GREEN}source $SHELL_CONFIG${NC}"
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
