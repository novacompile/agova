"""Research agent for gathering information - Using Groq API via requests"""
import requests
import json
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
    
    def _call_api(self, messages: list, model: str = None, temperature: float = None) -> Dict[str, Any]:
        """Make API call to Groq"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model or self.config_manager.get("models.researcher", "mixtral-8x7b-32768"),
            "messages": messages,
            "temperature": temperature or self.config_manager.get("agents.temperature", 0.7),
            "max_tokens": self.config_manager.get("agents.max_tokens", 8192)
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=60)
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"API Error: {response.json().get('error', {}).get('message', 'Unknown error')}")
        except Exception as e:
            raise e
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Research the given query"""
        query = task.get("query", "")
        research_depth = self.config_manager.get("agents.research_depth", "detailed")
        
        self.log(f"🔍 Researching: {query}", "cyan")
        
        depth_instructions = {
            "basic": "Provide a quick overview with essential facts only.",
            "detailed": "Provide comprehensive research with key facts, sources, and detailed information.",
            "exhaustive": "Provide in-depth analysis with multiple perspectives, historical context, and thorough documentation."
        }
        
        research_prompt = f"""You are a research agent. {depth_instructions.get(research_depth, depth_instructions['detailed'])}

Query: {query}

Please provide:
1. Key Facts and Information
2. Important Dates, Names, and Events (if applicable)
3. Relevant Context and Background
4. Code-Relevant Information (if applicable)
5. Sources and References
6. Summary of Findings

Be thorough and accurate in your research."""
        
        try:
            data = self._call_api(
                messages=[
                    {"role": "system", "content": "You are an expert researcher. Be thorough, accurate, and provide well-structured research findings."},
                    {"role": "user", "content": research_prompt}
                ]
            )
            
            research_results = data["choices"][0]["message"]["content"]
            usage = data["usage"]
            
            self.log("✅ Research complete", "green")
            
            if self.config_manager.get("display.show_token_usage", True):
                self.log(f"📊 Tokens: {usage['total_tokens']} (P:{usage['prompt_tokens']} C:{usage['completion_tokens']})", "dim")
            
            return {
                "status": "success",
                "results": research_results,
                "agent": "researcher",
                "usage": usage
            }
        except Exception as e:
            self.log(f"❌ Research failed: {str(e)}", "red")
            return {"status": "error", "message": str(e), "agent": "researcher"}
