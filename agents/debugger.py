"""Debugger agent for fixing issues - Using Groq"""
import groq
from typing import Dict, Any
from rich.console import Console
from .base_agent import BaseAgent
from config import Config

class DebuggerAgent(BaseAgent):
    def __init__(self, console: Console):
        super().__init__("Debugger", "Debug and Fix Issues", console)
        self.client = groq.Groq(api_key=Config.GROQ_API_KEY)
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Debug and fix identified issues"""
        code = task.get("code", "")
        validation_results = task.get("validation_results", "")
        research_results = task.get("research_results", "")
        
        self.log("🐛 Debugging and fixing issues...", "magenta")
        
        debug_prompt = f"""You are a debugging expert. Fix the following code/issues based on validation feedback.

Original Code:
{code}

Validation Results (issues to fix):
{validation_results}

Research Context:
{research_results}

Provide:
1. Issues Identified: Numbered list of all problems found
2. Fixed Code: Complete working code in ```python ``` blocks
3. Changes Made: Explanation of each fix
4. Testing Suggestions: How to verify the fixes work

Make sure the fixed code:
- Addresses ALL identified issues
- Is complete and runnable
- Includes error handling
- Has proper documentation
- Follows Python best practices"""
        
        try:
            response = self.client.chat.completions.create(
                model=Config.DEBUG_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert debugger. Find and fix all issues thoroughly. Provide complete, working solutions."},
                    {"role": "user", "content": debug_prompt}
                ],
                temperature=0.3,
                max_tokens=Config.MAX_TOKENS
            )
            
            fixed_solution = response.choices[0].message.content
            self.log("✅ Debugging complete", "green")
            self.log(f"📊 Tokens used: {response.usage.total_tokens}", "dim")
            
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
            return {"status": "error", "message": str(e)}
