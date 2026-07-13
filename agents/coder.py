"""Coding agent for program generation - Using Groq"""
import groq
from typing import Dict, Any
from rich.console import Console
from .base_agent import BaseAgent
from config import Config

class CoderAgent(BaseAgent):
    def __init__(self, console: Console):
        super().__init__("Coder", "Code Generation and Implementation", console)
        self.client = groq.Groq(api_key=Config.GROQ_API_KEY)
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Generate code based on requirements"""
        requirements = task.get("requirements", "")
        research_results = task.get("research_results", "")
        
        self.log("💻 Generating code...", "blue")
        
        coding_prompt = f"""You are an expert programmer. Based on the following requirements and research, 
create a complete, working Python program.

Requirements: {requirements}

Research Findings: {research_results}

Provide your response in this format:
1. Brief explanation of the solution
2. The complete code in ```python ``` blocks
3. Required dependencies (if any)
4. Usage instructions
5. File structure if needed

Make sure the code is:
- Well-commented with docstrings
- Production-ready with error handling
- Handles edge cases
- Uses best practices and modern Python features
- Ready to run immediately"""
        
        try:
            response = self.client.chat.completions.create(
                model=Config.CODING_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert Python developer. Write clean, efficient, well-documented code. Always include complete, runnable code in your responses."},
                    {"role": "user", "content": coding_prompt}
                ],
                temperature=0.5,
                max_tokens=Config.MAX_TOKENS
            )
            
            code = response.choices[0].message.content
            self.log("✅ Code generation complete", "green")
            self.log(f"📊 Tokens used: {response.usage.total_tokens}", "dim")
            
            # Extract code blocks
            code_blocks = self._extract_code_blocks(code)
            
            return {
                "status": "success",
                "code": code,
                "code_blocks": code_blocks,
                "agent": "coder",
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
        except Exception as e:
            self.log(f"❌ Code generation failed: {str(e)}", "red")
            return {"status": "error", "message": str(e)}
    
    def _extract_code_blocks(self, text: str) -> list:
        """Extract Python code blocks from response"""
        blocks = []
        lines = text.split('\n')
        in_block = False
        current_block = []
        current_lang = ""
        
        for line in lines:
            if line.startswith('```'):
                if in_block:
                    blocks.append({
                        "language": current_lang,
                        "code": '\n'.join(current_block)
                    })
                    current_block = []
                    in_block = False
                else:
                    in_block = True
                    current_lang = line[3:].strip()
            elif in_block:
                current_block.append(line)
        
        # If there's unclosed code block, capture it
        if in_block and current_block:
            blocks.append({
                "language": current_lang or "python",
                "code": '\n'.join(current_block)
            })
        
        return blocks
