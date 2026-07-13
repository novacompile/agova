"""API handler for Groq using direct requests"""
import requests
import json
from typing import Dict, Any, Optional, List
from utils.config_manager import ConfigManager

class APIHandler:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.api_key = self.config_manager.get_api_key()
    
    def make_request(
        self,
        messages: List[Dict[str, str]],
        model: str = "mixtral-8x7b-32768",
        temperature: float = 0.7,
        max_tokens: int = 8192,
        retry_count: int = 0
    ) -> Dict[str, Any]:
        """Make an API request to Groq"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "success",
                    "content": data["choices"][0]["message"]["content"],
                    "usage": {
                        "prompt_tokens": data["usage"]["prompt_tokens"],
                        "completion_tokens": data["usage"]["completion_tokens"],
                        "total_tokens": data["usage"]["total_tokens"]
                    }
                }
            else:
                error_data = response.json()
                raise Exception(f"API Error: {error_data.get('error', {}).get('message', 'Unknown error')}")
                
        except Exception as e:
            max_retries = self.config_manager.get("agents.max_retries", 3)
            if retry_count < max_retries:
                print(f"Retrying... ({retry_count + 1}/{max_retries})")
                return self.make_request(
                    messages, model, temperature, max_tokens, retry_count + 1
                )
            return {
                "status": "error",
                "message": str(e)
            }
