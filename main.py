#!/usr/bin/env python3
"""
Multi-Agent AI System for Terminal - Powered by Groq
Usage: python main.py
"""
import asyncio
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.panel import Panel
from rich.table import Table
from agents.orchestrator import OrchestratorAgent
from config import Config
import sys

console = Console()

def display_welcome():
    """Display welcome message"""
    welcome_text = """
# 🚀 Multi-Agent AI System (Groq Powered)

This system uses multiple specialized AI agents powered by **Groq's ultra-fast inference**:

### Available Agents:
- **🔍 Researcher** (`mixtral-8x7b-32768`): Gathers information and context
- **💻 Coder** (`llama-3.1-70b-versatile`): Generates code and solutions
- **✅ Validator** (`llama-3.1-70b-versatile`): Verifies correctness
- **🐛 Debugger** (`llama-3.1-70b-versatile`): Fixes issues and improves solutions

### Example Queries:
- "Who was the prime minister in 1928 in America? Make a program to figure this out."
- "Create a weather forecasting app using Python"
- "Research quantum computing and create a simulation"
- "Build a REST API for a todo list application"
- "Write a program to analyze stock market data"

### Benefits:
- ⚡ Ultra-fast responses with Groq
- 🎯 Specialized models for different tasks
- 📁 Automatic file tree generation
- 💾 Saves all outputs in organized workspace
    """
    console.print(Markdown(welcome_text))
    
    # Display model information
    model_table = Table(title="Model Assignment", show_header=True, header_style="bold magenta")
    model_table.add_column("Agent", style="cyan")
    model_table.add_column("Model", style="green")
    model_table.add_column("Purpose", style="white")
    
    model_table.add_row("Researcher", "mixtral-8x7b-32768", "Fast, comprehensive research")
    model_table.add_row("Coder", "llama-3.1-70b-versatile", "Complex code generation")
    model_table.add_row("Validator", "llama-3.1-70b-versatile", "Thorough validation")
    model_table.add_row("Debugger", "llama-3.1-70b-versatile", "Expert debugging")
    
    console.print(model_table)
    
    console.print(Panel.fit(
        "[bold yellow]Type 'quit' or 'exit' to leave[/bold yellow]\n"
        "[bold green]Type 'help' for more information[/bold green]\n"
        "[bold blue]Type 'models' to see available Groq models[/bold blue]",
        title="Commands"
    ))

async def main():
    """Main application loop"""
    display_welcome()
    
    # Initialize orchestrator
    orchestrator = OrchestratorAgent(console)
    
    # Get API key if not set
    if not Config.GROQ_API_KEY or Config.GROQ_API_KEY == "your-key-here":
        console.print("\n[bold red]⚠️  Groq API key not found![/bold red]")
        console.print("[yellow]Get your free API key at: https://console.groq.com/keys[/yellow]")
        api_key = Prompt.ask("Enter your Groq API key", password=True)
        Config.GROQ_API_KEY = api_key
        console.print("[green]✅ API key set![/green]")
    
    prompt_counter = 0
    
    while True:
        try:
            # Get user input
            console.print("\n" + "="*50)
            query = Prompt.ask("\n[bold cyan]Enter your prompt[/bold cyan]")
            
            if query.lower() in ['quit', 'exit', 'q']:
                console.print("\n[bold green]Goodbye! 👋[/bold green]")
                break
            
            if query.lower() == 'help':
                display_welcome()
                continue
            
            if query.lower() == 'models':
                display_available_models()
                continue
            
            if not query.strip():
                continue
            
            prompt_counter += 1
            
            # Show estimated cost (Groq is very affordable)
            console.print("[dim]Processing with Groq... (ultra-fast inference)[/dim]")
            
            # Execute the task
            task = {
                "query": query,
                "prompt_id": str(prompt_counter)
            }
            
            await orchestrator.execute(task)
            
        except KeyboardInterrupt:
            console.print("\n[bold yellow]Interrupted by user[/bold yellow]")
            if Prompt.ask("Do you want to exit?", choices=["y", "n"]) == "y":
                break
        except Exception as e:
            console.print(f"[bold red]Error: {str(e)}[/bold red]")

def display_available_models():
    """Display available Groq models"""
    model_table = Table(title="Available Groq Models", show_header=True, header_style="bold magenta")
    model_table.add_column("Model Name", style="cyan")
    model_table.add_column("Speed", style="yellow")
    model_table.add_column("Best For", style="green")
    model_table.add_column("Context Window", style="white")
    
    model_table.add_row(
        "llama-3.1-70b-versatile", 
        "⚡⚡⚡", 
        "Complex reasoning, coding, validation",
        "8K tokens"
    )
    model_table.add_row(
        "mixtral-8x7b-32768", 
        "⚡⚡⚡⚡", 
        "Fast inference, research, general tasks",
        "32K tokens"
    )
    model_table.add_row(
        "llama-3.1-8b-instant", 
        "⚡⚡⚡⚡⚡", 
        "Simple tasks, quick responses",
        "8K tokens"
    )
    
    console.print(model_table)
    console.print("\n[dim]💡 Tip: You can change models in config.py[/dim]")
    console.print("[dim]🔗 Get API keys: https://console.groq.com/keys[/dim]")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[bold green]Goodbye! 👋[/bold green]")
        sys.exit(0)
