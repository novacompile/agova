#!/bin/bash
###############################################################################
# Agova AI Agent System - Uninstall Script (Linux/Mac)
###############################################################################

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

APP_NAME="agova"
INSTALL_DIR="$HOME/.agova"
BIN_DIR="/usr/local/bin"
CONFIG_DIR="$HOME/.config/agova"

print_message() {
    echo -e "${2}${1}${NC}"
}

print_message "========================================" "$BLUE"
print_message "   Agova AI Agent System Uninstaller    " "$BLUE"
print_message "========================================" "$BLUE"
echo ""

# Confirm uninstall
print_message "⚠️  This will remove Agova from your system." "$YELLOW"
print_message "This includes:" "$YELLOW"
echo "  - Application files in $INSTALL_DIR"
echo "  - System command: $APP_NAME"
echo "  - Configuration in $CONFIG_DIR"
echo ""
read -p "Are you sure you want to continue? (y/N): " CONFIRM

if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
    print_message "Uninstall cancelled." "$GREEN"
    exit 0
fi

# Remove system command
print_message "Removing system command..." "$BLUE"
if [ -f "$BIN_DIR/$APP_NAME" ]; then
    if [ -w "$BIN_DIR" ]; then
        rm -f "$BIN_DIR/$APP_NAME"
    else
        sudo rm -f "$BIN_DIR/$APP_NAME"
    fi
    print_message "✅ Removed system command" "$GREEN"
fi

# Remove alias from shell config
for SHELL_CONFIG in "$HOME/.bashrc" "$HOME/.bash_profile" "$HOME/.zshrc"; do
    if [ -f "$SHELL_CONFIG" ]; then
        sed -i '/# Agova AI Agent System/d' "$SHELL_CONFIG" 2>/dev/null || true
        sed -i '/alias agova=/d' "$SHELL_CONFIG" 2>/dev/null || true
    fi
done
print_message "✅ Removed shell aliases" "$GREEN"

# Remove desktop entry
DESKTOP_FILE="$HOME/.local/share/applications/agova.desktop"
if [ -f "$DESKTOP_FILE" ]; then
    rm -f "$DESKTOP_FILE"
    print_message "✅ Removed desktop entry" "$GREEN"
fi

# Backup and remove config
if [ -d "$CONFIG_DIR" ]; then
    read -p "Do you want to backup your configuration? (y/N): " BACKUP_CONFIG
    if [[ "$BACKUP_CONFIG" =~ ^[Yy]$ ]]; then
        BACKUP_DIR="$HOME/agova_backup_$(date +%Y%m%d_%H%M%S)"
        mkdir -p "$BACKUP_DIR"
        cp -r "$CONFIG_DIR" "$BACKUP_DIR/"
        print_message "✅ Configuration backed up to $BACKUP_DIR" "$GREEN"
    fi
    rm -rf "$CONFIG_DIR"
    print_message "✅ Removed configuration" "$GREEN"
fi

# Remove installation directory
if [ -d "$INSTALL_DIR" ]; then
    read -p "Do you want to keep the virtual environment? (y/N): " KEEP_VENV
    if [[ ! "$KEEP_VENV" =~ ^[Yy]$ ]]; then
        rm -rf "$INSTALL_DIR"
        print_message "✅ Removed installation directory" "$GREEN"
    else
        print_message "✅ Kept virtual environment" "$GREEN"
    fi
fi

# Ask about workspace
WORKSPACE_DIR="$HOME/agova_workspace"
if [ -d "$WORKSPACE_DIR" ]; then
    read -p "Do you want to remove the workspace? This will delete all generated files! (y/N): " REMOVE_WORKSPACE
    if [[ "$REMOVE_WORKSPACE" =~ ^[Yy]$ ]]; then
        rm -rf "$WORKSPACE_DIR"
        print_message "✅ Removed workspace" "$GREEN"
    else
        print_message "✅ Kept workspace at $WORKSPACE_DIR" "$GREEN"
    fi
fi

echo ""
print_message "========================================" "$GREEN"
print_message "   Uninstall Complete!                 " "$GREEN"
print_message "========================================" "$GREEN"
echo ""
print_message "Please restart your terminal for changes to take effect." "$YELLOW"
