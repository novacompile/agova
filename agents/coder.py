"""Coding agent for program generation - Using Groq API via requests"""
import requests
from typing import Dict, Any
from rich.console import Console
from .base_agent import BaseAgent
from utils.config_manager import ConfigManager

class CoderAgent(BaseAgent):
    def __init__(self, console: Console):
        super().__init__("Coder", "Code Generation and Implementation", console)
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
            "model": model or self.config_manager.get("models.coder", "llama-3.3-70b-versatile"),
            "messages": messages,
            "temperature": temperature or 0.5,
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
        """Generate code based on requirements"""
        requirements = task.get("requirements", "")
        research_results = task.get("research_results", "")
        code_style = self.config_manager.get("agents.code_style", "production")
        
        self.log("💻 Generating code...", "blue")
        
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

Important:
- Make sure the code is complete and runnable
- Include error handling
- Follow best practices
- Handle edge cases"""
        
        try:
            data = self._call_api(
                messages=[
                    {"role": "system", "content": "You are an expert Python developer. Write clean, efficient, well-documented code."},
                    {"role": "user", "content": coding_prompt}
                ]
            )
            
            code = data["choices"][0]["message"]["content"]
            usage = data["usage"]
            
            code_blocks = self._extract_code_blocks(code)
            
            self.log("✅ Code generation complete", "green")
            self.log(f"📊 Extracted {len(code_blocks)} code block(s)", "dim")
            
            return {
                "status": "success",
                "code": code,
                "code_blocks": code_blocks,
                "agent": "coder",
                "usage": usage
            }
        except Exception as e:
            self.log(f"❌ Code generation failed: {str(e)}", "red")
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
                    blocks.append({
                        "language": current_lang or "text",
                        "code": '\n'.join(current_block)
                    })
                    current_block = []
                    in_block = False
                else:
                    in_block = True
                    current_lang = line.strip()[3:].strip()
            elif in_block:
                current_block.append(line)
        
        if in_block and current_block:
            blocks.append({
                "language": current_lang or "text",
                "code": '\n'.join(current_block)
            })
        
        return blocks
