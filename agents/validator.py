"""Validator agent for code and solution validation - Using Groq API via requests"""
import requests
import json
from typing import Dict, Any
from rich.console import Console
from .base_agent import BaseAgent
from utils.config_manager import ConfigManager

class ValidatorAgent(BaseAgent):
    def __init__(self, console: Console):
        super().__init__("Validator", "Solution Validation and Verification", console)
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
            "model": self.config_manager.get("models.validator", "llama-3.1-70b-versatile"),
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
        """Validate the generated solution"""
        original_query = task.get("query", "")
        research = task.get("research_results", "")
        code = task.get("code", "")
        
        self.log("🔍 Validating solution...", "yellow")
        
        validation_prompt = f"""You are a validation expert. Verify that the following solution correctly addresses the original query.

Original Query: {original_query}

Research Findings: {research}

Generated Code/Solution: {code}

Provide a detailed validation report with:

1. ACCURACY ASSESSMENT (Score 1-10)
   - Does it correctly answer the query?

2. CODE CORRECTNESS
   - Is the code syntactically correct and runnable?

3. EDGE CASES
   - Are edge cases handled?

4. COMPLETENESS (Score 1-10)
   - Does it fully address all requirements?

5. BEST PRACTICES
   - Does it follow coding standards?

6. SUGGESTIONS FOR IMPROVEMENT

7. FINAL VERDICT
   - PASS or FAIL with detailed reason"""
        
        try:
            data = self._call_api(
                messages=[
                    {"role": "system", "content": "You are a thorough validator and code reviewer. Be critical and precise."},
                    {"role": "user", "content": validation_prompt}
                ]
            )
            
            validation_results = data["choices"][0]["message"]["content"]
            usage = data["usage"]
            
            passed = "FINAL VERDICT: PASS" in validation_results.upper() or "VERDICT: PASS" in validation_results.upper()
            
            if passed:
                self.log("✅ Validation passed - Solution is correct!", "green")
            else:
                self.log("⚠️ Validation failed - Improvements needed", "yellow")
            
            return {
                "status": "success" if passed else "warning",
                "validation": validation_results,
                "passed": passed,
                "agent": "validator",
                "usage": usage
            }
        except Exception as e:
            self.log(f"❌ Validation failed: {str(e)}", "red")
            return {"status": "error", "message": str(e), "agent": "validator"}
