"""Configuration settings for the AI Agent System"""
import os
from pathlib import Path
from typing import Optional

class Config:
    # API Keys
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY", "your-key-here")
    
    # Model settings - Groq models
    DEFAULT_MODEL: str = "mixtral-8x7b-32768"  # Fast and capable
    RESEARCH_MODEL: str = "mixtral-8x7b-32768"  # Good for research tasks
    CODING_MODEL: str = "llama-3.1-70b-versatile"  # Better for coding
    VALIDATION_MODEL: str = "llama-3.1-70b-versatile"  # For validation
    DEBUG_MODEL: str = "llama-3.1-70b-versatile"  # For debugging
    
    # Available Groq models: 
    # - mixtral-8x7b-32768 (fast, good all-rounder)
    # - llama-3.1-70b-versatile (powerful, great for complex tasks)
    # - llama-3.1-8b-instant (fastest, good for simple tasks)
    
    # Workspace settings
    WORKSPACE_DIR: Path = Path("workspace")
    
    # Agent settings
    MAX_RETRIES: int = 3
    TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 8192  # Groq supports larger context
    
    # File tree settings
    ENABLE_FILE_TREE: bool = True
    
    @classmethod
    def validate(cls):
        """Validate configuration"""
        if not cls.GROQ_API_KEY or cls.GROQ_API_KEY == "your-key-here":
            raise ValueError("Please set GROQ_API_KEY environment variable")
        cls.WORKSPACE_DIR.mkdir(exist_ok=True)
