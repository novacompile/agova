"""Debugger agent for fixing issues - Using Groq"""
import groq
from typing import Dict, Any
from rich.console import Console
from .base_agent import BaseAgent
from utils.config_manager import ConfigManager

class DebuggerAgent(BaseAgent):
    def __init__(self, console: Console):
        super().__init__("Debugger", "Debug and Fix Issues", console)
        self.config_manager = ConfigManager()
        self.client = self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Groq client"""
        api_key = self.config_manager.get_api_key()
        if not api_key:
            raise ValueError("Groq API key not configured")
        return groq.Groq(api_key=api_key)
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Debug and fix identified issues"""
        code = task.get("code", "")
        validation_results = task.get("validation_results", "")
        research_results = task.get("research_results", "")
        original_query = task.get("query", "")
        
        self.log("🐛 Debugging and fixing issues...", "magenta")
        self.add_to_context("task", f"Debugging for: {original_query}")
        
        debug_prompt = f"""You are an expert debugger. Analyze and fix all issues in the following code.

Original Query: {original_query}

Current Code:
{code}

Validation Results (Issues to Fix):
{validation_results}

Research Context:
{research_results}

Please provide:

1. ISSUES IDENTIFIED
   - Numbered list of all problems
   - Severity level for each (Critical/High/Medium/Low)
   - Brief explanation of each issue

2. FIXED CODE
   - Complete, working code with all fixes applied
   - Use ```python ``` blocks for Python code
   - Ensure the code is complete and runnable

3. CHANGES MADE
   - Detailed explanation of each fix
   - Why the fix was necessary
   - How it improves the solution

4. TESTING SUGGESTIONS
   - How to verify the fixes work
   - Test cases to run
   - Expected outputs

5. ADDITIONAL IMPROVEMENTS
   - Any optional enhancements
   - Performance optimizations
   - Better practices implemented

Make sure the fixed code:
- Addresses ALL identified issues
- Is complete and immediately runnable
- Includes proper error handling
- Has clear documentation
- Follows best practices
- Passes all edge cases"""
        
        try:
            model = self.config_manager.get("models.debugger", "llama-3.1-70b-versatile")
            temperature = 0.3  # Lower temperature for precise fixes
            max_tokens = self.config_manager.get("agents.max_tokens", 8192)
            
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are an expert debugger and code fixer. Find and fix all issues thoroughly. Provide complete, working solutions with clear explanations."},
                    {"role": "user", "content": debug_prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            fixed_solution = response.choices[0].message.content
            self.add_to_context("assistant", fixed_solution)
            self.add_to_history("debugging", {"status": "success"})
            
            self.log("✅ Debugging complete - All issues fixed!", "green")
            
            if self.config_manager.get("display.show_token_usage", True):
                self.log(f"📊 Tokens: {response.usage.total_tokens} (P:{response.usage.prompt_tokens} C:{response.usage.completion_tokens})", "dim")
            
            return {
                "status": "success",
                "fixed_solution": fixed_solution,
                "agent": "debugger",
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
        except Exception as e:
            self.log(f"❌ Debugging failed: {str(e)}", "red")
            self.add_to_history("debugging", {"status": "error", "message": str(e)})
            return {"status": "error", "message": str(e), "agent": "debugger"}
