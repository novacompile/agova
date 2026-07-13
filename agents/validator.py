"""Validator agent for code and solution validation - Using Groq"""
import groq
from typing import Dict, Any
from rich.console import Console
from .base_agent import BaseAgent
from config import Config

class ValidatorAgent(BaseAgent):
    def __init__(self, console: Console):
        super().__init__("Validator", "Solution Validation and Verification", console)
        self.client = groq.Groq(api_key=Config.GROQ_API_KEY)
    
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
1. Accuracy Assessment: Does it correctly answer the query? (Score 1-10)
2. Code Correctness: Is the code syntactically correct and runnable? (Yes/No with explanation)
3. Edge Cases: Are edge cases properly handled? (List missing cases if any)
4. Completeness: Does it fully address all requirements? (Score 1-10)
5. Suggestions: What improvements can be made? (List specific suggestions)
6. Final Verdict: PASS or FAIL (with detailed reason)

Be critical and thorough in your validation."""
        
        try:
            response = self.client.chat.completions.create(
                model=Config.VALIDATION_MODEL,
                messages=[
                    {"role": "system", "content": "You are a thorough validator. Be critical and precise. Provide detailed, actionable feedback."},
                    {"role": "user", "content": validation_prompt}
                ],
                temperature=0.3,
                max_tokens=Config.MAX_TOKENS
            )
            
            validation_results = response.choices[0].message.content
            passed = "FINAL VERDICT: PASS" in validation_results.upper() or "VERDICT: PASS" in validation_results.upper()
            
            status_msg = "✅ Solution validated successfully" if passed else "⚠️ Solution needs improvement"
            self.log(status_msg, "green" if passed else "yellow")
            self.log(f"📊 Tokens used: {response.usage.total_tokens}", "dim")
            
            return {
                "status": "success" if passed else "warning",
                "validation": validation_results,
                "passed": passed,
                "agent": "validator",
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
        except Exception as e:
            self.log(f"❌ Validation failed: {str(e)}", "red")
            return {"status": "error", "message": str(e)}
