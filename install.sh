#!/bin/bash
# install_agova.sh - Install Agova and add alias to shell config

echo "========================================"
echo "  Agova Installer"
echo "========================================"
echo ""

# Check if agova directory exists
if [ ! -f "$HOME/agova/main.py" ]; then
    echo "Error: main.py not found at ~/agova/main.py"
    echo "Please clone agova first:"
    echo "  git clone https://github.com/novacompile/agova.git ~/agova"
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
pip3 install -r ~/agova/requirements.txt --quiet 2>/dev/null || pip install -r ~/agova/requirements.txt --quiet 2>/dev/null

# Remove any existing agova alias
sed -i '/# Agova/d' ~/.bashrc 2>/dev/null
sed -i '/alias agova=/d' ~/.bashrc 2>/dev/null

# Add the alias
echo "" >> ~/.bashrc
echo "# Agova AI Agent System" >> ~/.bashrc
echo "alias agova='python3 \$HOME/agova/main.py'" >> ~/.bashrc

# Also add to .zshrc if it exists
if [ -f ~/.zshrc ]; then
    sed -i '/# Agova/d' ~/.zshrc 2>/dev/null
    sed -i '/alias agova=/d' ~/.zshrc 2>/dev/null
    echo "" >> ~/.zshrc
    echo "# Agova AI Agent System" >> ~/.zshrc
    echo "alias agova='python3 \$HOME/agova/main.py'" >> ~/.zshrc
fi

# Also add to .bash_profile if it exists
if [ -f ~/.bash_profile ]; then
    sed -i '/# Agova/d' ~/.bash_profile 2>/dev/null
    sed -i '/alias agova=/d' ~/.bash_profile 2>/dev/null
    echo "" >> ~/.bash_profile
    echo "# Agova AI Agent System" >> ~/.bash_profile
    echo "alias agova='python3 \$HOME/agova/main.py'" >> ~/.bash_profile
fi

echo ""
echo "Done! Alias added to ~/.bashrc"
echo ""
echo "Run this to apply now:"
echo "  source ~/.bashrc"
echo ""
echo "Then use: agova"
