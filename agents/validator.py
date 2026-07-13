"""Validator agent for code and solution validation - Using Groq"""
import groq
from typing import Dict, Any
from rich.console import Console
from .base_agent import BaseAgent
from utils.config_manager import ConfigManager

class ValidatorAgent(BaseAgent):
    def __init__(self, console: Console):
        super().__init__("Validator", "Solution Validation and Verification", console)
        self.config_manager = ConfigManager()
        self.client = self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Groq client"""
        api_key = self.config_manager.get_api_key()
        if not api_key:
            raise ValueError("Groq API key not configured")
        return groq.Groq(api_key=api_key)
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the generated solution"""
        original_query = task.get("query", "")
        research = task.get("research_results", "")
        code = task.get("code", "")
        
        self.log("🔍 Validating solution...", "yellow")
        self.add_to_context("task", f"Validation for: {original_query}")
        
        validation_prompt = f"""You are a validation expert. Verify that the following solution correctly addresses the original query.

Original Query: {original_query}

Research Findings: {research}

Generated Code/Solution: {code}

Provide a detailed validation report with:

1. ACCURACY ASSESSMENT (Score 1-10)
   - Does it correctly answer the query?
   - Are the facts accurate?
   - Is the logic sound?

2. CODE CORRECTNESS (if applicable)
   - Is the code syntactically correct?
   - Will it run without errors?
   - Are imports and dependencies correct?

3. EDGE CASES
   - Are edge cases handled?
   - Is error handling present?
   - What could go wrong?

4. COMPLETENESS (Score 1-10)
   - Does it fully address all requirements?
   - Is anything missing?
   - Are there any gaps?

5. BEST PRACTICES
   - Does it follow coding standards?
   - Is it well-documented?
   - Is it maintainable?

6. SUGGESTIONS FOR IMPROVEMENT
   - Specific, actionable improvements
   - Priority (High/Medium/Low)

7. FINAL VERDICT
   - PASS or FAIL
   - Detailed reason for verdict

Be critical, precise, and thorough in your validation."""
        
        try:
            model = self.config_manager.get("models.validator", "llama-3.1-70b-versatile")
            temperature = 0.3  # Lower temperature for more consistent validation
            max_tokens = self.config_manager.get("agents.max_tokens", 8192)
            
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a thorough validator and code reviewer. Be critical and precise. Provide detailed, actionable feedback."},
                    {"role": "user", "content": validation_prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            validation_results = response.choices[0].message.content
            self.add_to_context("assistant", validation_results)
            
            # Determine if passed
            passed = "FINAL VERDICT: PASS" in validation_results.upper() or "VERDICT: PASS" in validation_results.upper()
            
            self.add_to_history("validation", {"status": "success", "passed": passed})
            
            if passed:
                self.log("✅ Validation passed - Solution is correct!", "green")
            else:
                self.log("⚠️ Validation failed - Improvements needed", "yellow")
            
            if self.config_manager.get("display.show_token_usage", True):
                self.log(f"📊 Tokens: {response.usage.total_tokens} (P:{response.usage.prompt_tokens} C:{response.usage.completion_tokens})", "dim")
            
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
            self.add_to_history("validation", {"status": "error", "message": str(e)})
            return {"status": "error", "message": str(e), "agent": "validator"}
