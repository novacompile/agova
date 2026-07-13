"""Research agent for gathering information - Using Groq"""
import groq
from typing import Dict, Any
from rich.console import Console
from .base_agent import BaseAgent
from config import Config

class ResearcherAgent(BaseAgent):
    def __init__(self, console: Console):
        super().__init__("Researcher", "Research and Information Gathering", console)
        self.client = groq.Groq(api_key=Config.GROQ_API_KEY)
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Research the given query"""
        query = task.get("query", "")
        self.log(f"🔍 Researching: {query}", "cyan")
        
        research_prompt = f"""You are a research agent. Thoroughly research the following query and provide:
1. Key facts and information
2. Relevant sources (even if simulated)
3. Important dates, names, and events
4. Any code-relevant information if applicable

Query: {query}

Provide comprehensive research findings. Be detailed and accurate."""
        
        try:
            response = self.client.chat.completions.create(
                model=Config.RESEARCH_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert researcher. Be thorough and accurate. Provide detailed, well-structured research findings."},
                    {"role": "user", "content": research_prompt}
                ],
                temperature=Config.TEMPERATURE,
                max_tokens=Config.MAX_TOKENS
            )
            
            research_results = response.choices[0].message.content
            self.log("✅ Research complete", "green")
            
            # Log token usage
            self.log(f"📊 Tokens used: {response.usage.total_tokens}", "dim")
            
            return {
                "status": "success",
                "results": research_results,
                "agent": "researcher",
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
        except Exception as e:
            self.log(f"❌ Research failed: {str(e)}", "red")
            return {"status": "error", "message": str(e)}
