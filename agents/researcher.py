"""Research agent - lightweight version"""
import requests
from typing import Dict, Any
from rich.console import Console
from .base_agent import BaseAgent
from utils.config_manager import ConfigManager

class ResearcherAgent(BaseAgent):
    def __init__(self, console: Console):
        super().__init__("Researcher", "Research and Information Gathering", console)
        self.config_manager = ConfigManager()
        self.api_key = self.config_manager.get_api_key()
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        query = task.get("query", "")
        self.log(f"🔍 Researching: {query}", "cyan")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.config_manager.get("models.researcher", "openai/gpt-oss-120b"),
            "messages": [
                {"role": "system", "content": "Research and provide key facts."},
                {"role": "user", "content": f"Research: {query}"}
            ],
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=60)
            if response.status_code == 200:
                data = response.json()
                result = data["choices"][0]["message"]["content"]
                self.log("✅ Research complete", "green")
                return {"status": "success", "results": result, "agent": "researcher"}
            else:
                raise Exception(response.json().get("error", {}).get("message", "Unknown error"))
        except Exception as e:
            self.log(f"❌ Research failed: {str(e)}", "red")
            return {"status": "error", "message": str(e)}
