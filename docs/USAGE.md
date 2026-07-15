# Usage

Once you have cloned and installed **agova**, you can run it using these commands:

```bash
# Interactive chat mode (default)
agova

# Single prompt - runs and exits
agova "make a python calculator"

# Research only
agova -r "history of quantum computing"

# Code generation only
agova -c "sorting algorithm in python"

# With specific model
agova -m "openai/gpt-oss-120b" "explain recursion"

# With temperature setting
agova -t 0.5 "write a poem about code"

# Verbose mode
agova -v "make a game"

# Quiet mode
agova -q "factorial function"

# Show config
agova --config

# Run setup
agova --setup

# No progress bars
agova --no-progress "create a web scraper"

# Combine flags
agova -v -m "openai/gpt-oss-120b" "build a rest api"
```
