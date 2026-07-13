#!/usr/bin/env python3
"""
Interactive Setup Wizard for AI Agent System
Configures the JSON-based settings for your multi-agent AI application
"""
import json
import sys
import os
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt, Confirm, IntPrompt, FloatPrompt
from rich.panel import Panel
from rich.table import Table
from rich import print as rprint
from typing import Dict, Any

console = Console()

class SetupWizard:
    def __init__(self):
        self.config_path = Path("config.json")
        self.config = self.load_config()
        
    def load_config(self) -> Dict[str, Any]:
        """Load existing config or return default"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        return {
            "api": {
                "groq_api_key": "",
                "provider": "groq"
            },
            "models": {
                "default": "mixtral-8x7b-32768",
                "researcher": "mixtral-8x7b-32768",
                "coder": "llama-3.1-70b-versatile",
                "validator": "llama-3.1-70b-versatile",
                "debugger": "llama-3.1-70b-versatile"
            },
            "workspace": {
                "directory": "workspace",
                "enable_file_tree": True,
                "auto_cleanup": False,
                "max_workspace_age_days": 30
            },
            "agents": {
                "max_retries": 3,
                "temperature": 0.7,
                "max_tokens": 8192,
                "research_depth": "detailed",
                "code_style": "production",
                "auto_debug": True,
                "auto_validate": True
            },
            "display": {
                "show_token_usage": True,
                "show_timestamps": True,
                "show_agent_transitions": True,
                "color_theme": "default",
                "progress_bars": True
            },
            "safety": {
                "require_confirmation_for_execution": True,
                "max_file_size_mb": 10,
                "allowed_file_types": [".py", ".txt", ".json", ".md", ".csv"]
            }
        }
    
    def save_config(self):
        """Save configuration to file"""
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
        console.print(f"[green]✅ Configuration saved to {self.config_path}[/green]")
    
    def run(self):
        """Run the setup wizard"""
        console.print(Panel.fit(
            "[bold cyan]🚀 AI AGENT SYSTEM - SETUP WIZARD[/bold cyan]\n\n"
            "This wizard will help you configure your multi-agent AI system.\n"
            "All settings are stored in config.json",
            title="Welcome"
        ))
        
        while True:
            console.print("\n[bold yellow]What would you like to configure?[/bold yellow]")
            
            table = Table(show_header=False, box=None)
            table.add_column("Option", style="cyan")
            table.add_column("Description", style="white")
            
            table.add_row("1. 🔑", "Set API Key")
            table.add_row("2. 🤖", "Configure AI Models")
            table.add_row("3. 📁", "Workspace Settings")
            table.add_row("4. ⚙️", "Agent Behavior")
            table.add_row("5. 🎨", "Display Preferences")
            table.add_row("6. 📋", "View Current Configuration")
            table.add_row("7. 💾", "Save & Exit")
            table.add_row("8. 🚪", "Exit without Saving")
            
            console.print(table)
            
            choice = Prompt.ask("\nEnter your choice", choices=["1", "2", "3", "4", "5", "6", "7", "8"])
            
            if choice == "1":
                self.setup_api_key()
            elif choice == "2":
                self.setup_models()
            elif choice == "3":
                self.setup_workspace()
            elif choice == "4":
                self.setup_agents()
            elif choice == "5":
                self.setup_display()
            elif choice == "6":
                self.display_config()
            elif choice == "7":
                self.save_config()
                console.print("\n[bold green]✅ Setup complete! Run 'python main.py' to start.[/bold green]")
                break
            elif choice == "8":
                if Confirm.ask("Exit without saving changes?"):
                    console.print("[yellow]Exiting without saving.[/yellow]")
                    break
    
    def setup_api_key(self):
        """Configure API key"""
        console.print("\n[bold cyan]🔑 API KEY SETUP[/bold cyan]")
        console.print("[dim]Get your free API key at: https://console.groq.com/keys[/dim]\n")
        
        current_key = self.config["api"].get("groq_api_key", "")
        if current_key:
            masked_key = current_key[:10] + "..." + current_key[-4:] if len(current_key) > 14 else "***"
            console.print(f"[yellow]Current key: {masked_key}[/yellow]")
        
        api_key = Prompt.ask(
            "Enter your Groq API key",
            password=True,
            default=current_key if current_key else ""
        )
        
        if api_key:
            self.config["api"]["groq_api_key"] = api_key
            console.print("[green]✅ API key updated![/green]")
        
        # Option to set as environment variable
        if Confirm.ask("Also export as environment variable? (Recommended for security)"):
            console.print("[yellow]Add this to your shell:[/yellow]")
            console.print(f"[bold]export GROQ_API_KEY={api_key}[/bold]")
    
    def setup_models(self):
        """Configure AI models"""
        console.print("\n[bold cyan]🤖 MODEL CONFIGURATION[/bold cyan]")
        
        available_models = {
            "mixtral-8x7b-32768": "Fast, good all-rounder (32K context)",
            "llama-3.1-70b-versatile": "Powerful, great for complex tasks (8K context)",
            "llama-3.1-8b-instant": "Fastest, good for simple tasks (8K context)",
            "gemma2-9b-it": "Efficient, good performance (8K context)"
        }
        
        console.print("\n[bold]Available Models:[/bold]")
        for model, desc in available_models.items():
            console.print(f"  • [cyan]{model}[/cyan] - {desc}")
        
        agent_types = [
            ("default", "Default model for general tasks"),
            ("researcher", "Research and information gathering"),
            ("coder", "Code generation and development"),
            ("validator", "Solution validation and verification"),
            ("debugger", "Debug and fix issues")
        ]
        
        console.print("\n[bold]Assign models to agents:[/bold]")
        for agent_key, description in agent_types:
            current = self.config["models"].get(agent_key, "mixtral-8x7b-32768")
            console.print(f"\n[yellow]{description}[/yellow]")
            console.print(f"Current: [cyan]{current}[/cyan]")
            
            if not Confirm.ask(f"Change model for {agent_key}?", default=False):
                continue
            
            model_list = list(available_models.keys())
            console.print("\nSelect model:")
            for i, model in enumerate(model_list, 1):
                console.print(f"  {i}. {model}")
            
            choice = Prompt.ask(
                "Enter number",
                choices=[str(i) for i in range(1, len(model_list) + 1)],
                default="1"
            )
            
            self.config["models"][agent_key] = model_list[int(choice) - 1]
            console.print(f"[green]✅ Set {agent_key} to {model_list[int(choice) - 1]}[/green]")
    
    def setup_workspace(self):
        """Configure workspace settings"""
        console.print("\n[bold cyan]📁 WORKSPACE SETTINGS[/bold cyan]")
        
        current_dir = self.config["workspace"]["directory"]
        new_dir = Prompt.ask("Workspace directory name", default=current_dir)
        self.config["workspace"]["directory"] = new_dir
        
        enable_tree = Confirm.ask(
            "Enable file tree generation?",
            default=self.config["workspace"]["enable_file_tree"]
        )
        self.config["workspace"]["enable_file_tree"] = enable_tree
        
        auto_cleanup = Confirm.ask(
            "Enable auto-cleanup of old workspaces?",
            default=self.config["workspace"].get("auto_cleanup", False)
        )
        self.config["workspace"]["auto_cleanup"] = auto_cleanup
        
        if auto_cleanup:
            max_age = IntPrompt.ask(
                "Max workspace age (days)",
                default=self.config["workspace"].get("max_workspace_age_days", 30)
            )
            self.config["workspace"]["max_workspace_age_days"] = max_age
        
        console.print("[green]✅ Workspace settings updated![/green]")
    
    def setup_agents(self):
        """Configure agent behavior"""
        console.print("\n[bold cyan]⚙️ AGENT BEHAVIOR SETTINGS[/bold cyan]")
        
        max_retries = IntPrompt.ask(
            "Maximum retries for failed API calls",
            default=self.config["agents"]["max_retries"]
        )
        self.config["agents"]["max_retries"] = max_retries
        
        temperature = FloatPrompt.ask(
            "Temperature (0.0-2.0, lower = more focused)",
            default=self.config["agents"]["temperature"]
        )
        self.config["agents"]["temperature"] = min(2.0, max(0.0, temperature))
        
        max_tokens = IntPrompt.ask(
            "Maximum tokens per response",
            default=self.config["agents"]["max_tokens"]
        )
        self.config["agents"]["max_tokens"] = max_tokens
        
        # Research depth
        console.print("\n[bold]Research Depth:[/bold]")
        depths = {
            "basic": "Quick overview, essential facts only",
            "detailed": "Comprehensive research with sources",
            "exhaustive": "In-depth analysis, multiple perspectives"
        }
        for key, desc in depths.items():
            console.print(f"  • [cyan]{key}[/cyan] - {desc}")
        
        research_depth = Prompt.ask(
            "Select research depth",
            choices=list(depths.keys()),
            default=self.config["agents"].get("research_depth", "detailed")
        )
        self.config["agents"]["research_depth"] = research_depth
        
        # Code style
        console.print("\n[bold]Code Style:[/bold]")
        styles = {
            "minimal": "Bare minimum, just works",
            "production": "Production-ready with error handling",
            "educational": "Heavily commented, teaching-focused"
        }
        for key, desc in styles.items():
            console.print(f"  • [cyan]{key}[/cyan] - {desc}")
        
        code_style = Prompt.ask(
            "Select code style",
            choices=list(styles.keys()),
            default=self.config["agents"].get("code_style", "production")
        )
        self.config["agents"]["code_style"] = code_style
        
        auto_validate = Confirm.ask(
            "Automatically validate generated code?",
            default=self.config["agents"]["auto_validate"]
        )
        self.config["agents"]["auto_validate"] = auto_validate
        
        auto_debug = Confirm.ask(
            "Automatically debug if validation fails?",
            default=self.config["agents"]["auto_debug"]
        )
        self.config["agents"]["auto_debug"] = auto_debug
        
        console.print("[green]✅ Agent behavior settings updated![/green]")
    
    def setup_display(self):
        """Configure display preferences"""
        console.print("\n[bold cyan]🎨 DISPLAY PREFERENCES[/bold cyan]")
        
        show_tokens = Confirm.ask(
            "Show token usage statistics?",
            default=self.config["display"]["show_token_usage"]
        )
        self.config["display"]["show_token_usage"] = show_tokens
        
        show_timestamps = Confirm.ask(
            "Show timestamps in logs?",
            default=self.config["display"]["show_timestamps"]
        )
        self.config["display"]["show_timestamps"] = show_timestamps
        
        show_transitions = Confirm.ask(
            "Show agent transitions (when switching between agents)?",
            default=self.config["display"]["show_agent_transitions"]
        )
        self.config["display"]["show_agent_transitions"] = show_transitions
        
        progress_bars = Confirm.ask(
            "Show progress bars?",
            default=self.config["display"]["progress_bars"]
        )
        self.config["display"]["progress_bars"] = progress_bars
        
        console.print("\n[bold]Color Themes:[/bold]")
        themes = ["default", "monokai", "ocean", "forest", "sunset"]
        for theme in themes:
            console.print(f"  • [cyan]{theme}[/cyan]")
        
        theme = Prompt.ask(
            "Select color theme",
            choices=themes,
            default=self.config["display"]["color_theme"]
        )
        self.config["display"]["color_theme"] = theme
        
        console.print("[green]✅ Display preferences updated![/green]")
    
    def display_config(self):
        """Display current configuration"""
        print("\n" + "="*50)
        print("🔧 CURRENT CONFIGURATION")
        print("="*50)
        
        api_key = self.config["api"].get("groq_api_key", "")
        if api_key:
            masked = api_key[:10] + "..." + api_key[-4:] if len(api_key) > 14 else "***"
            print(f"🔑 API Key: ✅ Set ({masked})")
        else:
            print(f"🔑 API Key: ❌ Not set")
        
        print(f"☁️  Provider: {self.config['api']['provider']}")
        
        print("\n🤖 Models:")
        for model_type in ['default', 'researcher', 'coder', 'validator', 'debugger']:
            print(f"   • {model_type}: {self.config['models'][model_type]}")
        
        print(f"\n📁 Workspace: {self.config['workspace']['directory']}")
        print(f"🌳 File Tree: {'✅ Enabled' if self.config['workspace']['enable_file_tree'] else '❌ Disabled'}")
        
        print(f"\n⚙️  Agent Settings:")
        print(f"   • Max Retries: {self.config['agents']['max_retries']}")
        print(f"   • Temperature: {self.config['agents']['temperature']}")
        print(f"   • Max Tokens: {self.config['agents']['max_tokens']}")
        print(f"   • Research Depth: {self.config['agents']['research_depth']}")
        print(f"   • Code Style: {self.config['agents']['code_style']}")
        
        print(f"\n🎨 Display:")
        print(f"   • Token Usage: {'✅' if self.config['display']['show_token_usage'] else '❌'}")
        print(f"   • Timestamps: {'✅' if self.config['display']['show_timestamps'] else '❌'}")
        print("="*50 + "\n")

def main():
    """Main setup function"""
    try:
        wizard = SetupWizard()
        wizard.run()
    except KeyboardInterrupt:
        console.print("\n[yellow]Setup cancelled by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[red]Error during setup: {str(e)}[/red]")
        sys.exit(1)

if __name__ == "__main__":
    main()
