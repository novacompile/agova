# AGOVA - COMPLETE DOCUMENTATION
# Multi-Agent AI System for Terminal



########
TABLE OF CONTENTS

1. Installation
2. Configuration  
3. CLI Arguments
4. Interactive Chat Mode
5. In-Chat Commands
6. Research Mode
7. Code Generation Mode
8. Validation & Debugging
9. Workspace Management
10. Model Selection
11. Agent Settings
12. Troubleshooting
13. Examples
########



########
1. INSTALLATION

Prerequisites:
- Python 3.8 or higher
- pip package manager
- Git (optional)
- Groq API key (free at https://console.groq.com/keys)

One-Line Install:
curl -s https://raw.githubusercontent.com/novacompile/agova/main/install/install.sh | bash
source ~/.bashrc

Manual Install:
git clone https://github.com/novacompile/agova.git ~/agova
cd ~/agova
pip install -r requirements.txt
echo "alias agova='python3 ~/agova/main.py'" >> ~/.bashrc
source ~/.bashrc

Verify:
agova --help
agova --config

Uninstall:
cd ~/agova && ./install/uninstall.sh
########



########
2. CONFIGURATION

First-Time Setup:
agova --setup

This interactive wizard guides you through:
- Entering your Groq API key
- Choosing AI models for each agent
- Setting agent behavior (temperature, tokens)
- Configuring display preferences
- Setting up workspace options

View Current Config:
agova --config

Manual Edit:
nano ~/agova/config.json

Config File Location: ~/agova/config.json

Config Structure:
{
  "api": {
    "groq_api_key": "gsk_your_key_here",
    "provider": "groq"
  },
  "models": {
    "default": "openai/gpt-oss-120b",
    "researcher": "openai/gpt-oss-120b",
    "coder": "openai/gpt-oss-120b",
    "validator": "openai/gpt-oss-120b",
    "debugger": "openai/gpt-oss-120b"
  },
  "workspace": {
    "directory": "workspace",
    "enable_file_tree": true,
    "auto_cleanup": false,
    "max_workspace_age_days": 30
  },
  "agents": {
    "max_retries": 3,
    "temperature": 0.7,
    "max_tokens": 2000,
    "research_depth": "detailed",
    "code_style": "production",
    "auto_debug": true,
    "auto_validate": true
  },
  "display": {
    "show_token_usage": true,
    "show_timestamps": true,
    "show_agent_transitions": true,
    "color_theme": "default",
    "progress_bars": true
  }
}

Config Options Explained:

research_depth:
  - "basic"    : Quick overview, essential facts only
  - "detailed" : Comprehensive research with sources
  - "exhaustive": In-depth analysis, multiple perspectives

code_style:
  - "minimal"     : Bare minimum, just works
  - "production"  : Production-ready with error handling
  - "educational" : Heavily commented, teaching-focused

temperature:
  - 0.0 to 0.3 : Very focused, deterministic
  - 0.4 to 0.7 : Balanced (recommended)
  - 0.8 to 2.0 : Creative, more random

max_tokens:
  - Free tier limit: 8000 TPM
  - Recommended: 2000 for most tasks
  - Higher values use more of your rate limit

auto_validate: true/false
  - Automatically validates generated code

auto_debug: true/false
  - Automatically fixes code if validation fails

display settings:
  - show_token_usage: Shows tokens used per request
  - show_timestamps: Shows time for each step
  - show_agent_transitions: Shows when agents switch
  - progress_bars: Shows loading animations
########



########
3. CLI ARGUMENTS

agova [OPTIONS] [PROMPT]

Positional:
  PROMPT    Single prompt to process and exit

Options:
  -r, --research TOPIC     Research only mode
  -c, --code TASK          Code generation only mode
  -v, --verbose            Show detailed output
  -q, --quiet              Minimal output
  -m, --model MODEL        Specify AI model
  -t, --temperature FLOAT  Set temperature (0.0-2.0)
  --setup                  Run configuration wizard
  --config                 Show current configuration
  --no-progress            Disable progress bars
  --no-color               Disable colored output

Examples:
  agova                                    Interactive chat
  agova "make a python calculator"         Single prompt
  agova -r "history of AI"                 Research only
  agova -c "sorting algorithm"             Code only
  agova -v "explain recursion"             Verbose mode
  agova -m "openai/gpt-oss-120b" "test"    Specific model
  agova -t 0.3 "write a function"          Low temperature
  agova --setup                             Run setup
  agova --config                            View config
########



########
4. INTERACTIVE CHAT MODE

Start chat mode:
agova

This opens an interactive session where you can:
- Type prompts and get AI responses
- Use in-chat commands
- Have multi-turn conversations

When you enter a prompt, the system will:
1. Ask for a project name (or press Enter for auto-name)
2. Create a workspace folder
3. Run the prompt through multiple agents
4. Show results in the terminal
5. Save everything to the workspace

Example session:
$ agova

🤖 Agova - Multi-Agent AI System
Type /help for commands, /quit to exit

📁 Project Name
Enter a name for this project: my_calculator

💭 Prompt: make a python calculator

[Orchestrator] 🚀 Starting workflow
[Researcher] 🔍 Researching: make a python calculator
[Researcher] ✅ Research complete
[Coder] 💻 Generating code...
[Coder] ✅ Code generation complete
[Validator] 🔍 Validating...
[Validator] ✅ Passed

✅ Done!

💭 Prompt: add multiplication feature

...continues conversation...
########



########
5. IN-CHAT COMMANDS

Available during interactive chat mode:

/help      Show help information
/config    Display current configuration
/clear     Clear the terminal screen
/quit      Exit Agova (also: /exit, /q)

Example:
💭 Prompt: /help
Shows available commands and usage

💭 Prompt: /config
Shows current API key status, models, settings

💭 Prompt: /clear
Clears the terminal for a fresh start

💭 Prompt: /quit
Exits Agova with goodbye message
########



########
6. RESEARCH MODE

Use when you want to research a topic without generating code.

Command:
agova -r "your research topic"

Or in chat mode, prefix your prompt with "research:" or the agent will auto-detect.

Examples:
agova -r "quantum computing basics"
agova -r "history of the internet"
agova -r "best python libraries for data science"

With options:
agova -v -r "machine learning algorithms"
agova -m "openai/gpt-oss-120b" -r "blockchain technology"

What it does:
1. Researcher agent gathers information
2. Provides key facts, context, and sources
3. Saves findings to workspace/research/findings.txt
4. No code generation phase

Output location: workspace/projectname_uuid/research/findings.txt
########



########
7. CODE GENERATION MODE

Use when you want to generate code for a specific task.

Command:
agova -c "your programming task"

Examples:
agova -c "hello world in python"
agova -c "web scraper using beautifulsoup"
agova -c "rest api with flask"
agova -c "sorting algorithm visualization"
agova -c "discord bot that responds to commands"

With options:
agova -v -c "game using pygame"
agova -c "data analysis script" -t 0.3

What it does:
1. Researcher gathers context
2. Coder generates the program
3. Validator checks the code
4. Debugger fixes issues if needed
5. Saves code to workspace/code/

Output location: workspace/projectname_uuid/code/solution_1.py

Code styles (set in config):
- minimal: Just the working code
- production: Error handling, logging, comments
- educational: Heavy comments, explanations
########



########
8. VALIDATION & DEBUGGING

Automatic (when auto_validate and auto_debug are enabled in config):

1. Coder generates code
2. Validator checks:
   - Accuracy (Score 1-10)
   - Code correctness
   - Edge cases handled
   - Completeness
   - Best practices
   - Final verdict: PASS or FAIL

3. If FAIL and auto_debug enabled:
   - Debugger identifies issues
   - Fixes the code
   - Re-validates after fixes

Manual control:
Set in config.json:
  "auto_validate": false   Skips validation
  "auto_debug": false      Skips debugging

Output files:
workspace/projectname/validation/report.txt       Initial validation
workspace/projectname/validation/final_report.txt  After debugging
workspace/projectname/debug/fixed_solution.txt     Fixed code

Example validation output:
ACCURACY ASSESSMENT: 9/10
CODE CORRECTNESS: Yes, syntactically correct
EDGE CASES: Handles empty input, negative numbers
COMPLETENESS: 8/10 - Missing docstrings
BEST PRACTICES: Follows PEP 8
SUGGESTIONS: Add type hints
FINAL VERDICT: PASS
########



########
9. WORKSPACE MANAGEMENT

When you run a prompt, Agova creates a workspace folder.

Naming format: projectname_shortuuid
Example: my_calculator_a1b2c3d4

Location: ~/agova/workspace/

Structure:
workspace/
└── my_calculator_a1b2c3d4/
    ├── query.txt              Original prompt
    ├── results.json           Full results in JSON
    ├── file_tree.txt          Visual file tree
    ├── README.md              Workspace overview
    ├── research/
    │   └── findings.txt       Research results
    ├── code/
    │   ├── full_response.txt  Complete AI response
    │   └── solution_1.py      Generated Python code
    ├── validation/
    │   ├── report.txt         Initial validation
    │   └── final_report.txt   After debugging
    └── debug/
        └── fixed_solution.txt  Debugged code

View workspace:
ls ~/agova/workspace/
cat ~/agova/workspace/myproject_abc12345/file_tree.txt

Clean old workspaces:
Set in config.json:
  "auto_cleanup": true
  "max_workspace_age_days": 30
########



########
10. MODEL SELECTION

Available Groq Models:

openai/gpt-oss-120b:
  - Best for: Complex reasoning, coding, research
  - Context: Large
  - Speed: Fast

openai/gpt-oss-20b:
  - Best for: Quick responses, simple tasks
  - Context: Medium
  - Speed: Very fast

qwen/qwen3.6-27b:
  - Best for: Alternative to GPT-OSS
  - Context: Medium
  - Speed: Fast

Set default model in config.json:
  "models": {
    "default": "openai/gpt-oss-120b",
    "researcher": "openai/gpt-oss-120b",
    "coder": "openai/gpt-oss-120b",
    "validator": "openai/gpt-oss-120b",
    "debugger": "openai/gpt-oss-120b"
  }

Override model via CLI:
agova -m "openai/gpt-oss-20b" "quick question"

Different models per agent:
You can assign different models to different agents.
Example: Use faster model for researcher, powerful model for coder.
  "researcher": "openai/gpt-oss-20b",
  "coder": "openai/gpt-oss-120b"
########



########
11. AGENT SETTINGS

Each agent has specific behavior settings.

Researcher Agent:
  Setting: research_depth
  Values: basic, detailed, exhaustive
  Effect: How thorough the research phase is
  
  basic: Quick facts only
  detailed: Comprehensive with sources
  exhaustive: Deep analysis, multiple angles

Coder Agent:
  Setting: code_style
  Values: minimal, production, educational
  Effect: How the generated code is structured
  
  minimal: Just works, no extras
  production: Error handling, logging
  educational: Heavy comments, teaches concepts

Validator Agent:
  Always runs with low temperature (0.3)
  Checks: accuracy, correctness, completeness
  Output: PASS or FAIL with detailed report

Debugger Agent:
  Runs when validation fails
  Fixes identified issues
  Re-validates after fixing

Performance Settings:
  max_retries: 3           Retry failed API calls
  temperature: 0.7          Creativity level
  max_tokens: 2000          Max response length
########



########
12. TROUBLESHOOTING

Problem: "agova: command not found"
Fix: source ~/.bashrc
     or re-add alias: echo "alias agova='python3 ~/agova/main.py'" >> ~/.bashrc

Problem: "API key not found"
Fix: agova --setup
     Enter your Groq API key
     Or edit ~/agova/config.json manually

Problem: "Request too large... TPM Limit 8000"
Fix: Reduce max_tokens in config.json to 2000
     Or shorten your prompts
     Or upgrade to Groq Dev Tier

Problem: "Model not found" or "Model decommissioned"
Fix: agova --setup
     Select a current model
     Check https://console.groq.com/docs for available models

Problem: "ModuleNotFoundError: No module named 'requests'"
Fix: pip install requests
     or: pip install -r ~/agova/requirements.txt

Problem: Config resetting on exit
Fix: Check that config.json has valid JSON
     Make sure API key is set
     The config_manager only creates defaults if file is missing

Problem: "No space left on device"
Fix: Clean workspace: rm -rf ~/agova/workspace/*
     Or enable auto_cleanup in config

Problem: Push rejected (API key in git)
Fix: Add config.json to .gitignore
     echo "config.json" >> ~/agova/.gitignore
     git rm --cached config.json
     Revoke exposed API key at console.groq.com/keys

Problem: HTTP 403 or 401 errors
Fix: Your API key may be invalid or expired
     Get a new key at https://console.groq.com/keys
     Run: rm ~/.agova_key && agova --setup
########



########
13. EXAMPLES

Basic Examples:

1. Hello World:
agova "write a hello world program in python"

2. Web Scraper:
agova -c "web scraper that extracts headlines from news websites"

3. Research Topic:
agova -r "how does blockchain technology work"

4. Game Development:
agova "create a snake game using pygame"

5. API Development:
agova -c "build a REST API for a todo app using FastAPI"

Advanced Examples:

6. With specific model and temperature:
agova -m "openai/gpt-oss-120b" -t 0.3 "write a sorting algorithm"

7. Verbose research:
agova -v -r "quantum computing applications in cryptography"

8. Quick code check:
agova -c "validate email address regex" -q

9. Multi-step project:
agova "create a full-stack app with React frontend and Python backend"
(Chat mode allows follow-up prompts)

10. Debug existing code:
agova "fix this code: [paste your code here]"

11. Learn a concept:
agova "explain recursion with examples in python"

12. Data analysis:
agova -c "analyze CSV file and create matplotlib visualizations"

13. Automation script:
agova -c "script to organize files by extension in a directory"

14. Testing:
agova -c "write unit tests for a calculator class"

15. Documentation:
agova "generate docstrings for this Python module: [paste code]"
########



########
FILES AND LOCATIONS

Application:    ~/agova/
Config:         ~/agova/config.json
Workspace:      ~/agova/workspace/
API Key:        ~/.agova_key (or environment variable)
Logs:           Terminal output only
Backups:        Not applicable (use git)

Environment Variables:
GROQ_API_KEY    Your Groq API key (optional, alternative to config)

Shell Alias:
alias agova='python3 ~/agova/main.py'
Added to: ~/.bashrc
########



########
QUICK REFERENCE CARD

Install:        git clone https://github.com/novacompile/agova.git ~/agova && cd ~/agova && pip install -r requirements.txt
Setup:          agova --setup
Chat:           agova
Single prompt:  agova "your prompt"
Research:       agova -r "topic"
Code:           agova -c "task"
Help:           agova --help
Config:         agova --config
Update:         cd ~/agova && git pull
Uninstall:      cd ~/agova && ./install/uninstall.sh

In-Chat Commands:
/help           Show help
/config         Show config
/clear          Clear screen
/quit           Exit

Key Files:
~/.bashrc                   Contains alias
~/agova/config.json         Settings
~/agova/workspace/          Output files
~/agova/main.py             Entry point

Get API Key: https://console.groq.com/keys
Report Issues: https://github.com/novacompile/agova/issues
########
