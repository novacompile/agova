#!/bin/bash
###############################################################################
# Agova AI Agent System - Installation Script (Linux/Mac)
# This script installs Agova system-wide and creates the 'agova' command alias
###############################################################################

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="agova"
INSTALL_DIR="$HOME/.agova"
BIN_DIR="/usr/local/bin"
CONFIG_DIR="$HOME/.config/agova"
WORKSPACE_DIR="$HOME/agova_workspace"

# Print colored message
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

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
check_prerequisites() {
    print_message "Checking prerequisites..." "$BLUE"
    
    # Check Python
    if ! command_exists python3; then
        print_message "❌ Python 3 is not installed. Please install Python 3.8 or higher." "$RED"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_message "✅ Python $PYTHON_VERSION found" "$GREEN"
    
    # Check pip
    if ! command_exists pip3; then
        print_message "❌ pip3 is not installed. Please install pip3." "$RED"
        exit 1
    fi
    print_message "✅ pip3 found" "$GREEN"
    
    # Check git
    if ! command_exists git; then
        print_message "❌ Git is not installed. Please install git." "$RED"
        exit 1
    fi
    print_message "✅ Git found" "$GREEN"
}

# Create directories
create_directories() {
    print_message "Creating directories..." "$BLUE"
    
    mkdir -p "$INSTALL_DIR"
    mkdir -p "$CONFIG_DIR"
    mkdir -p "$WORKSPACE_DIR"
    
    print_message "✅ Directories created" "$GREEN"
}

# Clone or update repository
clone_repository() {
    print_message "Setting up Agova..." "$BLUE"
    
    if [ -d "$INSTALL_DIR/.git" ]; then
        print_message "Existing installation found. Updating..." "$YELLOW"
        cd "$INSTALL_DIR"
        git pull origin main 2>/dev/null || git pull origin master 2>/dev/null || true
    else
        # Check if directory is empty
        if [ "$(ls -A $INSTALL_DIR)" ]; then
            print_message "⚠️  Installation directory is not empty. Backing up..." "$YELLOW"
            mv "$INSTALL_DIR" "${INSTALL_DIR}_backup_$(date +%Y%m%d_%H%M%S)"
            mkdir -p "$INSTALL_DIR"
        fi
        
        print_message "Cloning Agova repository..." "$BLUE"
        # Clone from current directory if running from source, otherwise from GitHub
        if [ -f "../main.py" ]; then
            print_message "Installing from local source..." "$YELLOW"
            cp -r ../* "$INSTALL_DIR/" 2>/dev/null || true
            cp -r ../.[!.]* "$INSTALL_DIR/" 2>/dev/null || true
        else
            print_message "Cloning from GitHub..." "$YELLOW"
            git clone https://github.com/yourusername/agova.git "$INSTALL_DIR" 2>/dev/null || {
                print_message "⚠️  Could not clone from GitHub. Please enter repository URL:" "$YELLOW"
                read -p "Repository URL: " REPO_URL
                git clone "$REPO_URL" "$INSTALL_DIR"
            }
        fi
    fi
    
    print_message "✅ Repository set up" "$GREEN"
}

# Install Python dependencies
install_dependencies() {
    print_message "Installing Python dependencies..." "$BLUE"
    
    cd "$INSTALL_DIR"
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_message "✅ Virtual environment created" "$GREEN"
    fi
    
    # Activate and install
    source venv/bin/activate
    pip install --upgrade pip >/dev/null 2>&1
    pip install -r requirements.txt >/dev/null 2>&1
    
    print_message "✅ Dependencies installed" "$GREEN"
}

# Create launcher script
create_launcher() {
    print_message "Creating launcher script..." "$BLUE"
    
    LAUNCHER="$INSTALL_DIR/agova_launcher.sh"
    
    cat > "$LAUNCHER" << 'EOF'
#!/bin/bash
# Agova Launcher Script

AGOVA_HOME="$HOME/.agova"
AGOVA_VENV="$AGOVA_HOME/venv"
AGOVA_MAIN="$AGOVA_HOME/main.py"

# Check if installation exists
if [ ! -f "$AGOVA_MAIN" ]; then
    echo "❌ Agova is not properly installed."
    echo "Please run the install script again."
    exit 1
fi

# Check if virtual environment exists
if [ ! -f "$AGOVA_VENV/bin/activate" ]; then
    echo "❌ Virtual environment not found. Reinstalling dependencies..."
    cd "$AGOVA_HOME"
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
fi

# Activate virtual environment and run
source "$AGOVA_VENV/bin/activate"
python3 "$AGOVA_MAIN" "$@"
EOF
    
    chmod +x "$LAUNCHER"
    print_message "✅ Launcher script created" "$GREEN"
}

# Create system-wide alias
create_alias() {
    print_message "Setting up 'agova' command..." "$BLUE"
    
    # Method 1: Create symlink in /usr/local/bin (requires sudo)
    if [ -w "$BIN_DIR" ] || [ "$EUID" -eq 0 ]; then
        ln -sf "$INSTALL_DIR/agova_launcher.sh" "$BIN_DIR/$APP_NAME"
        print_message "✅ Created system-wide command: agova" "$GREEN"
    else
        print_message "⚠️  Need sudo to create system-wide command." "$YELLOW"
        sudo ln -sf "$INSTALL_DIR/agova_launcher.sh" "$BIN_DIR/$APP_NAME"
        print_message "✅ Created system-wide command: agova" "$GREEN"
    fi
    
    # Method 2: Add alias to shell config files
    SHELL_CONFIG=""
    if [ -n "$ZSH_VERSION" ]; then
        SHELL_CONFIG="$HOME/.zshrc"
    elif [ -n "$BASH_VERSION" ]; then
        if [ -f "$HOME/.bash_profile" ]; then
            SHELL_CONFIG="$HOME/.bash_profile"
        else
            SHELL_CONFIG="$HOME/.bashrc"
        fi
    fi
    
    if [ -n "$SHELL_CONFIG" ]; then
        # Remove old alias if exists
        sed -i '/# Agova AI Agent System/d' "$SHELL_CONFIG" 2>/dev/null || true
        sed -i '/alias agova=/d' "$SHELL_CONFIG" 2>/dev/null || true
        
        # Add new alias
        echo "" >> "$SHELL_CONFIG"
        echo "# Agova AI Agent System" >> "$SHELL_CONFIG"
        echo "alias agova='$INSTALL_DIR/agova_launcher.sh'" >> "$SHELL_CONFIG"
        
        print_message "✅ Added alias to $SHELL_CONFIG" "$GREEN"
    fi
}

# Copy config if exists
setup_config() {
    print_message "Setting up configuration..." "$BLUE"
    
    if [ -f "$INSTALL_DIR/config.json" ]; then
        # Copy default config if user config doesn't exist
        if [ ! -f "$CONFIG_DIR/config.json" ]; then
            cp "$INSTALL_DIR/config.json" "$CONFIG_DIR/config.json"
            print_message "✅ Default configuration created" "$GREEN"
        else
            print_message "✅ Existing configuration preserved" "$GREEN"
        fi
    fi
}

# Create desktop entry (Linux only)
create_desktop_entry() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        print_message "Creating desktop entry..." "$BLUE"
        
        DESKTOP_DIR="$HOME/.local/share/applications"
        mkdir -p "$DESKTOP_DIR"
        
        cat > "$DESKTOP_DIR/agova.desktop" << EOF
[Desktop Entry]
Name=Agova AI Agent System
Comment=Multi-Agent AI System for Terminal
Exec=$INSTALL_DIR/agova_launcher.sh
Icon=terminal
Terminal=true
Type=Application
Categories=Development;ArtificialIntelligence;
Keywords=AI;Agent;Terminal;
EOF
        
        print_message "✅ Desktop entry created" "$GREEN"
    fi
}

# Print completion message
print_completion() {
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}   Installation Complete! 🚀           ${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo -e "${CYAN}To start using Agova:${NC}"
    echo ""
    echo -e "1. ${YELLOW}Restart your terminal${NC} or run:"
    echo -e "   ${GREEN}source ~/.bashrc${NC} (or ~/.zshrc)"
    echo ""
    echo -e "2. ${YELLOW}Run Agova from anywhere:${NC}"
    echo -e "   ${GREEN}agova${NC}"
    echo ""
    echo -e "3. ${YELLOW}First time setup:${NC}"
    echo -e "   • Configure your API key: ${GREEN}agova --setup${NC}"
    echo -e "   • Or edit config: ${GREEN}nano ~/.config/agova/config.json${NC}"
    echo ""
    echo -e "${CYAN}Quick Commands:${NC}"
    echo -e "  ${GREEN}agova${NC}              - Start the application"
    echo -e "  ${GREEN}agova --setup${NC}      - Run configuration wizard"
    echo -e "  ${GREEN}agova --help${NC}       - Show help"
    echo ""
    echo -e "${CYAN}Workspace:${NC} ${YELLOW}$WORKSPACE_DIR${NC}"
    echo -e "${CYAN}Config:${NC} ${YELLOW}$CONFIG_DIR/config.json${NC}"
    echo ""
}

# Main installation process
main() {
    print_header
    
    # Check if running with sudo
    if [ "$EUID" -eq 0 ]; then
        print_message "⚠️  Running as root is not recommended." "$YELLOW"
        print_message "Please run without sudo. The script will ask for sudo when needed." "$YELLOW"
        exit 1
    fi
    
    check_prerequisites
    create_directories
    clone_repository
    install_dependencies
    create_launcher
    create_alias
    setup_config
    create_desktop_entry
    print_completion
    
    # Reload shell
    print_message "Reloading shell configuration..." "$BLUE"
    if [ -n "$BASH_VERSION" ]; then
        exec bash
    elif [ -n "$ZSH_VERSION" ]; then
        exec zsh
    fi
}

# Run main
main "$@"
