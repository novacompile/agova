"""API integration handler for Groq"""
import groq
from typing import Dict, Any, Optional, List
from config import Config

class APIHandler:
    def __init__(self):
        self.validate_config()
        self.client = self._initialize_client()
    
    def validate_config(self):
        """Validate API configuration"""
        Config.validate()
    
    def _initialize_client(self):
        """Initialize the Groq API client"""
        return groq.Groq(api_key=Config.GROQ_API_KEY)
    
    async def make_request(
        self,
        messages: List[Dict[str, str]],
        model: str = None,
        temperature: float = None,
        max_tokens: int = None,
        retry_count: int = 0
    ) -> Dict[str, Any]:
        """Make an API request with retry logic"""
        model = model or Config.DEFAULT_MODEL
        temperature = temperature or Config.TEMPERATURE
        max_tokens = max_tokens or Config.MAX_TOKENS
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return {
                "status": "success",
                "content": response.choices[0].message.content,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
        except Exception as e:
            if retry_count < Config.MAX_RETRIES:
                return await self.make_request(
                    messages, model, temperature, max_tokens, retry_count + 1
                )
            return {
                "status": "error",
                "message": str(e)
            }
