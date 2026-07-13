#!/usr/bin/env python3
"""
Multi-Agent AI System for Terminal
A sophisticated AI application that uses multiple specialized agents
for research, coding, validation, and debugging tasks.

Usage:
    python main.py         # Start the application
    python setup.py        # Configure settings interactively
    
Commands during runtime:
    'quit', 'exit', 'q'   # Exit the application
    'setup'               # Launch configuration wizard
    'config'              # Display current configuration
    'help'                # Show help information
    'stats'               # Show session statistics
    'clear'               # Clear the screen
"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Optional

from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.traceback import install as install_rich_traceback

# Install rich traceback handler for better error display
install_rich_traceback(show_locals=True)

# Import local modules
from agents.orchestrator import OrchestratorAgent
from utils.config_manager import ConfigManager

# Initialize console for rich output
console = Console()

class Application:
    """Main application class for the Multi-Agent AI System"""
    
    def __init__(self):
        """Initialize the application"""
        self.config_manager = ConfigManager()
        self.orchestrator: Optional[OrchestratorAgent] = None
        self.prompt_counter = 0
        self.session_start = datetime.now()
        self.commands = {
            'quit': self.cmd_quit,
            'exit': self.cmd_quit,
            'q': self.cmd_quit,
            'help': self.cmd_help,
            'setup': self.cmd_setup,
            'config': self.cmd_config,
            'clear': self.cmd_clear,
            'stats': self.cmd_stats,
        }
    
    def display_welcome(self):
        """Display welcome message and system information"""
        welcome_text = """
# 🤖 Multi-Agent AI System

A powerful terminal-based AI application that coordinates multiple specialized agents.

## 🎯 Available Agents
"""
        console.print(Markdown(welcome_text))
        
        # Agent information table
        agent_table = Table(title="🧠 Specialized AI Agents", show_header=True, header_style="bold magenta")
        agent_table.add_column("Agent", style="cyan", no_wrap=True)
        agent_table.add_column("Role", style="green")
        agent_table.add_column("Model", style="yellow")
        agent_table.add_column("Capabilities", style="white")
        
        agent_table.add_row(
            "🔍 Researcher",
            "Information Gathering",
            self.config_manager.get("models.researcher", "N/A"),
            "• Web research\n• Fact checking\n• Context gathering"
        )
        agent_table.add_row(
            "💻 Coder",
            "Code Generation",
            self.config_manager.get("models.coder", "N/A"),
            "• Program creation\n• Algorithm design\n• API development"
        )
        agent_table.add_row(
            "✅ Validator",
            "Quality Assurance",
            self.config_manager.get("models.validator", "N/A"),
            "• Code review\n• Accuracy checking\n• Best practices"
        )
        agent_table.add_row(
            "🐛 Debugger",
            "Issue Resolution",
            self.config_manager.get("models.debugger", "N/A"),
            "• Bug fixing\n• Optimization\n• Error handling"
        )
        
        console.print(agent_table)
        
        # Commands panel
        commands_panel = Panel(
            "[bold cyan]Available Commands:[/bold cyan]\n\n"
            "  [yellow]quit / exit / q[/yellow]  - Exit the application\n"
            "  [yellow]help[/yellow]               - Show this help message\n"
            "  [yellow]setup[/yellow]              - Launch configuration wizard\n"
            "  [yellow]config[/yellow]             - Display current configuration\n"
            "  [yellow]clear[/yellow]              - Clear the screen\n"
            "  [yellow]stats[/yellow]              - Show session statistics\n\n"
            "[bold green]Example Prompts:[/bold green]\n\n"
            "  • Who was the prime minister in 1928 in America? Make a program to figure this out.\n"
            "  • Create a REST API for a todo list application\n"
            "  • Research quantum computing and create a simulation\n"
            "  • Build a web scraper for news headlines\n"
            "  • Write a program to analyze stock market data",
            title="📋 Quick Reference",
            border_style="blue"
        )
        console.print(commands_panel)
        
        # System status
        self._display_system_status()
    
    def _display_system_status(self):
        """Display current system status"""
        api_key = self.config_manager.get_api_key()
        status_color = "green" if api_key else "red"
        status_text = "✅ Connected" if api_key else "❌ Not Configured"
        
        status_table = Table(title="System Status", show_header=False, box=None)
        status_table.add_column("Property", style="cyan")
        status_table.add_column("Value", style="white")
        
        status_table.add_row("API Status", f"[{status_color}]{status_text}[/{status_color}]")
        status_table.add_row("Provider", self.config_manager.get("api.provider", "groq"))
        status_table.add_row("Workspace", self.config_manager.get("workspace.directory", "workspace"))
        status_table.add_row("Auto-validate", str(self.config_manager.get("agents.auto_validate", True)))
        status_table.add_row("Auto-debug", str(self.config_manager.get("agents.auto_debug", True)))
        
        console.print(status_table)
    
    async def initialize(self):
        """Initialize the application"""
        # Validate configuration
        try:
            self.config_manager.validate()
        except ValueError as e:
            console.print(f"\n[bold red]⚠️  Configuration Error:[/bold red]")
            console.print(f"[red]{str(e)}[/red]\n")
            
            if Confirm.ask("Would you like to run the setup wizard now?"):
                await self.cmd_setup()
                # Reload configuration
                self.config_manager.load_config()
                try:
                    self.config_manager.validate()
                except ValueError:
                    console.print("[red]Setup incomplete. Please configure your API key.[/red]")
                    sys.exit(1)
            else:
                console.print("[yellow]Run 'python setup.py' to configure manually.[/yellow]")
                sys.exit(1)
        
        # Initialize orchestrator
        self.orchestrator = OrchestratorAgent(console)
        console.print("[green]✅ System initialized successfully![/green]")
    
    async def run(self):
        """Main application loop"""
        self.display_welcome()
        await self.initialize()
        
        while True:
            try:
                # Get user input
                console.print("\n" + "─" * 80)
                query = Prompt.ask("\n[bold cyan]💭 Enter your prompt[/bold cyan]")
                
                # Process commands
                if query.lower() in self.commands:
                    should_exit = await self.commands[query.lower()]()
                    if should_exit:
                        break
                    continue
                
                # Skip empty queries
                if not query.strip():
                    continue
                
                # Process the prompt
                await self.process_prompt(query)
                
            except KeyboardInterrupt:
                console.print("\n[yellow]⚠️  Interrupted by user[/yellow]")
                if Confirm.ask("Do you want to exit?"):
                    break
            except Exception as e:
                console.print(f"[bold red]❌ Error: {str(e)}[/bold red]")
    
    async def process_prompt(self, query: str):
        """Process a user prompt through the agent system"""
        self.prompt_counter += 1
        
        # Show processing start
        console.print(f"\n[bold blue]🔄 Processing prompt #{self.prompt_counter}[/bold blue]")
        
        # Create task
        task = {
            "query": query,
            "prompt_id": str(self.prompt_counter),
            "timestamp": datetime.now().isoformat()
        }
        
        # Execute with optional progress bar
        if self.config_manager.get("display.progress_bars", True):
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task_progress = progress.add_task(
                    "[cyan]Working with AI agents...", 
                    total=None
                )
                result = await self.orchestrator.execute(task)
                progress.update(task_progress, completed=True)
        else:
            result = await self.orchestrator.execute(task)
        
        # Display completion
        if result.get("status") == "success":
            console.print(f"\n[bold green]✅ Task completed successfully![/bold green]")
        else:
            console.print(f"\n[bold yellow]⚠️  Task completed with warnings[/bold yellow]")
    
    async def cmd_quit(self):
        """Handle quit command"""
        console.print("\n[bold yellow]Exiting application...[/bold yellow]")
        await self.cmd_stats()
        console.print("[bold green]👋 Goodbye! Thanks for using Multi-Agent AI System![/bold green]")
        return True
    
    async def cmd_help(self):
        """Handle help command"""
        self.display_welcome()
        return False
    
    async def cmd_setup(self):
        """Handle setup command"""
        console.print("[yellow]Launching configuration wizard...[/yellow]")
        
        try:
            import subprocess
            subprocess.run([sys.executable, "setup.py"])
            self.config_manager.load_config()
            
            if self.orchestrator:
                self.orchestrator = OrchestratorAgent(console)
            
            console.print("[green]✅ Configuration updated successfully![/green]")
        except Exception as e:
            console.print(f"[red]Error launching setup: {str(e)}[/red]")
        
        return False
    
    async def cmd_config(self):
        """Handle config command"""
        self.config_manager.display_config()
        return False
    
    async def cmd_clear(self):
        """Handle clear command"""
        os.system('clear' if os.name != 'nt' else 'cls')
        return False
    
    async def cmd_stats(self):
        """Handle stats command"""
        session_duration = datetime.now() - self.session_start
        
        stats_table = Table(title="📊 Session Statistics", show_header=False, box=None)
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="white")
        
        stats_table.add_row("Session Duration", str(session_duration).split('.')[0])
        stats_table.add_row("Prompts Processed", str(self.prompt_counter))
        stats_table.add_row("Workspace", str(self.config_manager.get("workspace.directory")))
        stats_table.add_row("Default Model", self.config_manager.get("models.default"))
        
        console.print(stats_table)
        return False

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = ['groq', 'rich']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        console.print(f"[bold red]❌ Missing dependencies: {', '.join(missing_packages)}[/bold red]")
        console.print("[yellow]Install with: pip install -r requirements.txt[/yellow]")
        return False
    
    return True

def check_config():
    """Check if configuration file exists"""
    if not Path("config.json").exists():
        console.print("[yellow]⚠️  config.json not found. Running first-time setup...[/yellow]")
        try:
            import subprocess
            subprocess.run([sys.executable, "setup.py"])
            return True
        except Exception as e:
            console.print(f"[red]Error during setup: {str(e)}[/red]")
            return False
    return True

async def main():
    """Main entry point"""
    console.print("[bold cyan]🚀 Starting Multi-Agent AI System...[/bold cyan]\n")
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check configuration
    if not check_config():
        console.print("[red]Setup failed. Please run 'python setup.py' manually.[/red]")
        sys.exit(1)
    
    # Create and run application
    app = Application()
    
    try:
        await app.run()
    except KeyboardInterrupt:
        console.print("\n[bold green]👋 Goodbye![/bold green]")
    except Exception as e:
        console.print(f"[bold red]Fatal error: {str(e)}[/bold red]")
        console.print_exception()
    finally:
        console.print("[dim]Application terminated.[/dim]")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[bold green]👋 Goodbye![/bold green]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[bold red]Failed to start: {str(e)}[/bold red]")
        sys.exit(1)
