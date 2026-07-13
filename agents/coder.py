"""Coding agent for program generation - Using Groq"""
import groq
from typing import Dict, Any
from rich.console import Console
from .base_agent import BaseAgent
from utils.config_manager import ConfigManager

class CoderAgent(BaseAgent):
    def __init__(self, console: Console):
        super().__init__("Coder", "Code Generation and Implementation", console)
        self.config_manager = ConfigManager()
        self.client = self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Groq client"""
        api_key = self.config_manager.get_api_key()
        if not api_key:
            raise ValueError("Groq API key not configured")
        return groq.Groq(api_key=api_key)
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Generate code based on requirements"""
        requirements = task.get("requirements", "")
        research_results = task.get("research_results", "")
        code_style = self.config_manager.get("agents.code_style", "production")
        
        self.log("💻 Generating code...", "blue")
        self.add_to_context("task", f"Code generation: {requirements}")
        
        style_instructions = {
            "minimal": "Write minimal code that just works. Keep it simple and concise.",
            "production": "Write production-ready code with error handling, logging, and best practices.",
            "educational": "Write heavily commented code with explanations. Focus on teaching concepts."
        }
        
        coding_prompt = f"""You are an expert programmer. {style_instructions.get(code_style, style_instructions['production'])}

Requirements: {requirements}

Research Findings: {research_results}

Please provide:
1. Brief explanation of the solution approach
2. Complete working code in appropriate language (use ```python ``` blocks for Python)
3. Required dependencies with versions
4. Installation and usage instructions
5. Example usage with expected output
6. File structure (if multiple files needed)
7. Testing suggestions

Important:
- Make sure the code is complete and runnable
- Include error handling
- Follow best practices
- Add appropriate comments
- Handle edge cases"""
        
        try:
            model = self.config_manager.get("models.coder", "llama-3.1-70b-versatile")
            temperature = self.config_manager.get("agents.temperature", 0.5)
            max_tokens = self.config_manager.get("agents.max_tokens", 8192)
            
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are an expert Python developer. Write clean, efficient, well-documented code. Always include complete, runnable code in your responses."},
                    {"role": "user", "content": coding_prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            code = response.choices[0].message.content
            self.add_to_context("assistant", code)
            self.add_to_history("code_generation", {"status": "success"})
            
            # Extract code blocks
            code_blocks = self._extract_code_blocks(code)
            
            self.log("✅ Code generation complete", "green")
            self.log(f"📊 Extracted {len(code_blocks)} code block(s)", "dim")
            
            if self.config_manager.get("display.show_token_usage", True):
                self.log(f"📊 Tokens: {response.usage.total_tokens} (P:{response.usage.prompt_tokens} C:{response.usage.completion_tokens})", "dim")
            
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
            self.add_to_history("code_generation", {"status": "error", "message": str(e)})
            return {"status": "error", "message": str(e), "agent": "coder"}
    
    def _extract_code_blocks(self, text: str) -> list:
        """Extract code blocks from response"""
        blocks = []
        lines = text.split('\n')
        in_block = False
        current_block = []
        current_lang = ""
        
        for line in lines:
            if line.strip().startswith('```'):
                if in_block:
                    # End of block
                    blocks.append({
                        "language": current_lang or "text",
                        "code": '\n'.join(current_block)
                    })
                    current_block = []
                    in_block = False
                else:
                    # Start of block
                    in_block = True
                    current_lang = line.strip()[3:].strip()
            elif in_block:
                current_block.append(line)
        
        # Handle unclosed block
        if in_block and current_block:
            blocks.append({
                "language": current_lang or "text",
                "code": '\n'.join(current_block)
            })
        
        return blocks
