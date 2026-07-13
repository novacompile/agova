# Agova Installation Guide

## Quick Install

Install for either Linux/Mac (bash) or Windows (bat).

### Linux / Mac
```bash
# Clone the repository
git clone https://github.com/yourusername/agova.git
cd agova

# Run the installer
chmod +x install/install.sh
./install/install.sh

# Restart your terminal or run:
source ~/.bashrc  # or source ~/.zshrc

# Start Agova
agova
```

### Windows

```
# Clone the repository
git clone https://github.com/novacompile/agova.git
cd agova

# Run the installer
install\install.bat

# Restart your terminal or run:
agova
```

## Manual Installation

If the automatic installer doesn't work, you can install manually:

### Linux / Mac

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Add to your shell configuration (~/.bashrc or ~/.zshrc):

```bash
alias agova='python3 /path/to/agova/main.py'
```

3. Reload your shell:

```bash
source ~/.bashrc
```

### Windows

1. Install dependencies:

```batch
pip install -r requirements.txt
```

2. Create a batch file agova.bat in a directory in your PATH:

```batch
@echo off
python C:\path\to\agova\main.py %*
```
 
##  First-Time Setup

1. Get a free Groq API key at https://console.groq.com/keys
2. Run the configuration wizard:

```bash
agova --setup
```

3. Or manually edit the config file at `~/.config/agova/config.json`

Usage

bash
# Start Agova
agova

# Run setup wizard
agova --setup

# Show help
agova --help
