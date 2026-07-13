"""Configuration settings for the AI Agent System"""
import os
from pathlib import Path
from typing import Optional

class Config:
    # API Keys
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", "your-key-here")
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY", "")
    
    # Model settings
    DEFAULT_MODEL: str = "gpt-4"
    RESEARCH_MODEL: str = "gpt-4"
    CODING_MODEL: str = "gpt-4"
    
    # Workspace settings
    WORKSPACE_DIR: Path = Path("workspace")
    
    # Agent settings
    MAX_RETRIES: int = 3
    TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 4096
    
    # File tree settings
    ENABLE_FILE_TREE: bool = True
    
    @classmethod
    def validate(cls):
        """Validate configuration"""
        if not cls.OPENAI_API_KEY or cls.OPENAI_API_KEY == "your-key-here":
            raise ValueError("Please set OPENAI_API_KEY environment variable")
        cls.WORKSPACE_DIR.mkdir(exist_ok=True)
