"""Validator agent - lightweight version"""
import requests
from typing import Dict, Any
from rich.console import Console
from .base_agent import BaseAgent
from utils.config_manager import ConfigManager

class ValidatorAgent(BaseAgent):
    def __init__(self, console: Console):
        super().__init__("Validator", "Solution Validation", console)
        self.config_manager = ConfigManager()
        self.api_key = self.config_manager.get_api_key()
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        query = task.get("query", "")
        code = task.get("code", "")
        self.log("🔍 Validating...", "yellow")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.config_manager.get("models.validator", "openai/gpt-oss-120b"),
            "messages": [
                {"role": "system", "content": "Validate code. Reply PASS or FAIL with reason."},
                {"role": "user", "content": f"Query: {query}\nCode: {code[:500]}"}
            ],
            "temperature": 0.3,
            "max_tokens": 1000
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=60)
            if response.status_code == 200:
                data = response.json()
                result = data["choices"][0]["message"]["content"]
                passed = "PASS" in result.upper()
                self.log("✅ Passed" if passed else "⚠️ Failed", "green" if passed else "yellow")
                return {"status": "success" if passed else "warning", "validation": result, "passed": passed}
            else:
                raise Exception(response.json().get("error", {}).get("message", "Unknown error"))
        except Exception as e:
            self.log(f"❌ Failed: {str(e)}", "red")
            return {"status": "error", "message": str(e)}
