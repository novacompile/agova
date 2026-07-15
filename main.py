#!/usr/bin/env python3
"""
Agova - Multi-Agent AI System for Terminal
Usage: agova [OPTIONS] [PROMPT]
"""

import asyncio
import sys
import os
import argparse
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

install_rich_traceback(show_locals=True)

from agents.orchestrator import OrchestratorAgent
from utils.config_manager import ConfigManager

console = Console()

class Application:
    def __init__(self, args):
        self.args = args
        self.config_manager = ConfigManager()
        self.orchestrator: Optional[OrchestratorAgent] = None
        self.prompt_counter = 0
        self.session_start = datetime.now()
    
    def display_welcome(self):
        welcome = """
# 🤖 Agova - Multi-Agent AI System

[bold cyan]Powered by Groq AI[/bold cyan]
Type [yellow]/help[/yellow] for commands, [yellow]/quit[/yellow] to exit
"""
        console.print(Markdown(welcome))
    
    async def initialize(self):
        try:
            self.config_manager.validate()
        except ValueError as e:
            console.print(f"\n[bold red]⚠️  {str(e)}[/bold red]")
            sys.exit(1)
        
        self.orchestrator = OrchestratorAgent(console)
    
    async def process_prompt(self, query: str):
        self.prompt_counter += 1
        console.print(f"\n[bold blue]🔄 Processing #{self.prompt_counter}[/bold blue]")
        
        task = {
            "query": query,
            "prompt_id": str(self.prompt_counter),
            "timestamp": datetime.now().isoformat()
        }
        
        if self.args.progress:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task_progress = progress.add_task("[cyan]Working...[/cyan]", total=None)
                result = await self.orchestrator.execute(task)
                progress.update(task_progress, completed=True)
        else:
            result = await self.orchestrator.execute(task)
        
        if result.get("status") == "success":
            console.print(f"[bold green]✅ Done![/bold green]")
        else:
            console.print(f"[bold yellow]⚠️  Completed with warnings[/bold yellow]")
    
    async def run_chat(self):
        self.display_welcome()
        await self.initialize()
        
        while True:
            try:
                console.print("\n" + "─" * 60)
                query = Prompt.ask("[bold cyan]💭 Prompt[/bold cyan]")
                
                if query.lower() in ['/quit', '/exit', '/q']:
                    break
                elif query.lower() == '/help':
                    self.show_help()
                    continue
                elif query.lower() == '/config':
                    self.config_manager.display_config()
                    continue
                elif query.lower() == '/clear':
                    os.system('clear')
                    self.display_welcome()
                    continue
                elif not query.strip():
                    continue
                
                await self.process_prompt(query)
                
            except KeyboardInterrupt:
                console.print("\n[yellow]Interrupted[/yellow]")
                if Confirm.ask("Exit?"):
                    break
            except Exception as e:
                console.print(f"[red]Error: {str(e)}[/red]")
        
        console.print("[green]👋 Goodbye![/green]")
    
    def show_help(self):
        help_text = """
[bold cyan]Commands:[/bold cyan]
  [yellow]/help[/yellow]    - Show this help
  [yellow]/config[/yellow]  - Show configuration
  [yellow]/clear[/yellow]   - Clear screen
  [yellow]/quit[/yellow]    - Exit

[bold cyan]CLI Arguments:[/bold cyan]
  [yellow]agova[/yellow]                  - Interactive chat mode
  [yellow]agova "prompt"[/yellow]          - Run single prompt
  [yellow]agova -r "topic"[/yellow]        - Research only
  [yellow]agova -c "task"[/yellow]         - Code generation only
  [yellow]agova --setup[/yellow]           - Run setup wizard
  [yellow]agova --config[/yellow]          - Show configuration
  [yellow]agova -v[/yellow]                - Verbose mode
  [yellow]agova --no-progress[/yellow]     - Disable progress bars
"""
        console.print(Markdown(help_text))
    
    def show_config(self):
        self.config_manager.display_config()


async def main():
    parser = argparse.ArgumentParser(
        description="Agova - Multi-Agent AI System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  agova                              Interactive chat mode
  agova "make a hello world program"  Single prompt mode
  agova -r "quantum computing"        Research only
  agova -c "sorting algorithm"        Code generation only
  agova --setup                       Configure API key and settings
  agova --config                      Show current configuration
  agova -v "prompt"                   Verbose output
        """
    )
    
    # Mode arguments
    parser.add_argument("prompt", nargs="?", help="Prompt to process (single-shot mode)")
    parser.add_argument("-r", "--research", type=str, help="Research a topic")
    parser.add_argument("-c", "--code", type=str, help="Generate code for a task")
    
    # Configuration
    parser.add_argument("--setup", action="store_true", help="Run setup wizard")
    parser.add_argument("--config", action="store_true", help="Show configuration")
    
    # Display options
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("-q", "--quiet", action="store_true", help="Minimal output")
    parser.add_argument("--no-color", action="store_true", help="Disable colors")
    parser.add_argument("--no-progress", action="store_true", help="Disable progress bars")
    
    # Model options
    parser.add_argument("-m", "--model", type=str, help="Model to use")
    parser.add_argument("-t", "--temperature", type=float, help="Temperature (0.0-2.0)")
    
    args = parser.parse_args()
    
    # Handle --setup
    if args.setup:
        import subprocess
        subprocess.run([sys.executable, str(Path(__file__).parent / "setup.py")])
        return
    
    # Handle --config
    if args.config:
        cm = ConfigManager()
        cm.display_config()
        return
    
    # Create app
    app = Application(args)
    
    # Set progress bar preference
    if args.no_progress or args.quiet:
        args.progress = False
    else:
        args.progress = True
    
    try:
        await app.initialize()
    except SystemExit:
        return
    
    # Single prompt mode
    if args.prompt:
        await app.process_prompt(args.prompt)
        return
    
    # Research only mode
    if args.research:
        await app.process_prompt(f"Research: {args.research}")
        return
    
    # Code only mode
    if args.code:
        await app.process_prompt(f"Write code: {args.code}")
        return
    
    # Interactive chat mode (default)
    await app.run_chat()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[green]👋 Goodbye![/green]")
        sys.exit(0)
