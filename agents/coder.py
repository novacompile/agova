"""Coding agent - lightweight version"""
import requests
from typing import Dict, Any
from rich.console import Console
from .base_agent import BaseAgent
from utils.config_manager import ConfigManager

class CoderAgent(BaseAgent):
    def __init__(self, console: Console):
        super().__init__("Coder", "Code Generation", console)
        self.config_manager = ConfigManager()
        self.api_key = self.config_manager.get_api_key()
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        requirements = task.get("requirements", "")
        self.log("💻 Generating code...", "blue")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.config_manager.get("models.coder", "openai/gpt-oss-120b"),
            "messages": [
                {"role": "system", "content": "Write Python code. Output only code in ```python blocks."},
                {"role": "user", "content": f"Write a Python program: {requirements}"}
            ],
            "temperature": 0.5,
            "max_tokens": 2000
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=60)
            if response.status_code == 200:
                data = response.json()
                code = data["choices"][0]["message"]["content"]
                self.log("✅ Code complete", "green")
                return {"status": "success", "code": code, "code_blocks": self._extract_blocks(code), "agent": "coder"}
            else:
                raise Exception(response.json().get("error", {}).get("message", "Unknown error"))
        except Exception as e:
            self.log(f"❌ Failed: {str(e)}", "red")
            return {"status": "error", "message": str(e)}
    
    def _extract_blocks(self, text):
        blocks = []
        lines = text.split('\n')
        in_block = False
        current = []
        lang = ""
        for line in lines:
            if line.strip().startswith('```'):
                if in_block:
                    blocks.append({"language": lang or "text", "code": '\n'.join(current)})
                    current = []
                in_block = not in_block
                if in_block:
                    lang = line.strip()[3:].strip()
            elif in_block:
                current.append(line)
        return blocks
