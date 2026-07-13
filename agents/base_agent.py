"""Base agent class for all specialized agents"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from rich.console import Console
from datetime import datetime
import json

class BaseAgent(ABC):
    def __init__(self, name: str, role: str, console: Console):
        self.name = name
        self.role = role
        self.console = console
        self.context: List[Dict[str, str]] = []
        self.execution_history: List[Dict[str, Any]] = []
        
    def log(self, message: str, style: str = "white"):
        """Log a message with agent name prefix"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.console.print(f"[dim]{timestamp}[/dim] [bold {style}][{self.name}][/bold {style}] {message}")
    
    def add_to_context(self, role: str, content: str):
        """Add message to context memory"""
        self.context.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
    
    def add_to_history(self, action: str, result: Dict[str, Any]):
        """Add action to execution history"""
        self.execution_history.append({
            "action": action,
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
    
    @abstractmethod
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent's task"""
        pass
    
    def get_context_summary(self) -> str:
        """Get summary of current context"""
        if not self.context:
            return "No context available"
        
        summary = {
            "total_messages": len(self.context),
            "last_message": self.context[-1]["content"][:100] + "..." if len(self.context[-1]["content"]) > 100 else self.context[-1]["content"],
            "roles": list(set(msg["role"] for msg in self.context))
        }
        return json.dumps(summary, indent=2)
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """Get summary of execution history"""
        return {
            "total_actions": len(self.execution_history),
            "last_action": self.execution_history[-1]["action"] if self.execution_history else None,
            "success_rate": sum(1 for h in self.execution_history if h["result"].get("status") == "success") / len(self.execution_history) if self.execution_history else 0
        }
