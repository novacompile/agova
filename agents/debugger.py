"""Debugger agent - lightweight version"""
import requests
from typing import Dict, Any
from rich.console import Console
from .base_agent import BaseAgent
from utils.config_manager import ConfigManager

class DebuggerAgent(BaseAgent):
    def __init__(self, console: Console):
        super().__init__("Debugger", "Debug and Fix", console)
        self.config_manager = ConfigManager()
        self.api_key = self.config_manager.get_api_key()
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        code = task.get("code", "")
        issues = task.get("validation_results", "")
        self.log("🐛 Debugging...", "magenta")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.config_manager.get("models.debugger", "openai/gpt-oss-120b"),
            "messages": [
                {"role": "system", "content": "Fix the code. Output fixed code in ```python blocks."},
                {"role": "user", "content": f"Issues: {issues}\nCode: {code[:500]}"}
            ],
            "temperature": 0.3,
            "max_tokens": 2000
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=60)
            if response.status_code == 200:
                data = response.json()
                result = data["choices"][0]["message"]["content"]
                self.log("✅ Fixed!", "green")
                return {"status": "success", "fixed_solution": result}
            else:
                raise Exception(response.json().get("error", {}).get("message", "Unknown error"))
        except Exception as e:
            self.log(f"❌ Failed: {str(e)}", "red")
            return {"status": "error", "message": str(e)}
