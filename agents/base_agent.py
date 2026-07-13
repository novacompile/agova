"""Base agent class for all specialized agents"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from rich.console import Console
import json

class BaseAgent(ABC):
    def __init__(self, name: str, role: str, console: Console):
        self.name = name
        self.role = role
        self.console = console
        self.context: List[Dict[str, str]] = []
        
    def log(self, message: str, style: str = "white"):
        """Log a message with agent name prefix"""
        self.console.print(f"[{style}][{self.name}][/{style}] {message}")
    
    def add_to_context(self, role: str, content: str):
        """Add message to context memory"""
        self.context.append({"role": role, "content": content})
    
    @abstractmethod
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent's task"""
        pass
    
    def get_context_summary(self) -> str:
        """Get summary of current context"""
        return json.dumps(self.context[-5:], indent=2)  # Last 5 messages
