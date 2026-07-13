#!/bin/bash
###############################################################################
# Agova AI Agent System - Uninstall Script (Linux/Mac)
###############################################################################

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
    echo -e "${CYAN}    Agova AI Agent System Uninstaller   ${NC}"
    echo -e "${CYAN}========================================${NC}"
    echo ""
}

# Get the agova directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGOVA_DIR="$(dirname "$SCRIPT_DIR")"

print_header

print_message "⚠️  This will remove Agova from your system." "$YELLOW"
print_message "Agova directory: $AGOVA_DIR" "$YELLOW"
echo ""
read -p "Are you sure you want to continue? (y/N): " CONFIRM

if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
    print_message "Uninstall cancelled." "$GREEN"
    exit 0
fi

# Remove symlink
print_message "Removing system command..." "$BLUE"
sudo rm -f /usr/local/bin/agova 2>/dev/null || true
print_message "✅ Removed system command" "$GREEN"

# Remove alias from shell configs
for SHELL_CONFIG in "$HOME/.bashrc" "$HOME/.bash_profile" "$HOME/.zshrc"; do
    if [ -f "$SHELL_CONFIG" ]; then
        grep -v "alias agova=" "$SHELL_CONFIG" > "${SHELL_CONFIG}.tmp" 2>/dev/null || true
        grep -v "Agova AI Agent System" "${SHELL_CONFIG}.tmp" > "$SHELL_CONFIG" 2>/dev/null || true
        rm -f "${SHELL_CONFIG}.tmp"
    fi
done
print_message "✅ Removed shell aliases" "$GREEN"

# Ask about removing the directory
read -p "Do you want to remove the Agova directory? ($AGOVA_DIR) (y/N): " REMOVE_DIR
if [[ "$REMOVE_DIR" =~ ^[Yy]$ ]]; then
    rm -rf "$AGOVA_DIR"
    print_message "✅ Removed Agova directory" "$GREEN"
else
    print_message "✅ Kept Agova directory" "$GREEN"
fi

echo ""
print_message "========================================" "$GREEN"
print_message "   Uninstall Complete!                 " "$GREEN"
print_message "========================================" "$GREEN"
echo ""
print_message "Please restart your terminal for changes to take effect." "$YELLOW"
