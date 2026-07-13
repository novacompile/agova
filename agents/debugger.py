"""Debugger agent for fixing issues - Using Groq API via requests"""
import requests
import json
from typing import Dict, Any
from rich.console import Console
from .base_agent import BaseAgent
from utils.config_manager import ConfigManager

class DebuggerAgent(BaseAgent):
    def __init__(self, console: Console):
        super().__init__("Debugger", "Debug and Fix Issues", console)
        self.config_manager = ConfigManager()
        self.api_key = self.config_manager.get_api_key()
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
    
    def _call_api(self, messages: list) -> Dict[str, Any]:
        """Make API call to Groq"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.config_manager.get("models.debugger", "llama-3.1-70b-versatile"),
            "messages": messages,
            "temperature": 0.3,
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
        """Debug and fix identified issues"""
        code = task.get("code", "")
        validation_results = task.get("validation_results", "")
        research_results = task.get("research_results", "")
        original_query = task.get("query", "")
        
        self.log("🐛 Debugging and fixing issues...", "magenta")
        
        debug_prompt = f"""You are an expert debugger. Analyze and fix all issues in the following code.

Original Query: {original_query}

Current Code:
{code}

Validation Results (Issues to Fix):
{validation_results}

Please provide:

1. ISSUES IDENTIFIED
   - Numbered list of all problems with severity

2. FIXED CODE
   - Complete, working code with all fixes applied
   - Use ```python ``` blocks

3. CHANGES MADE
   - Detailed explanation of each fix

4. TESTING SUGGESTIONS

Make sure the fixed code:
- Addresses ALL identified issues
- Is complete and immediately runnable
- Includes proper error handling
- Follows best practices"""
        
        try:
            data = self._call_api(
                messages=[
                    {"role": "system", "content": "You are an expert debugger and code fixer. Find and fix all issues thoroughly."},
                    {"role": "user", "content": debug_prompt}
                ]
            )
            
            fixed_solution = data["choices"][0]["message"]["content"]
            usage = data["usage"]
            
            self.log("✅ Debugging complete - All issues fixed!", "green")
            
            return {
                "status": "success",
                "fixed_solution": fixed_solution,
                "agent": "debugger",
                "usage": usage
            }
        except Exception as e:
            self.log(f"❌ Debugging failed: {str(e)}", "red")
            return {"status": "error", "message": str(e), "agent": "debugger"}
