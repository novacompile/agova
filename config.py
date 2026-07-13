"""Configuration bridge - loads from JSON config"""
from pathlib import Path
from utils.config_manager import ConfigManager

# Initialize config manager
config_manager = ConfigManager()

class Config:
    """Configuration class that reads from JSON"""
    
    @classmethod
    def get_api_key(cls):
        """Get Groq API key"""
        return config_manager.get_api_key()
    
    @classmethod
    def get_model(cls, agent_type: str = "default") -> str:
        """Get model for specific agent type"""
        return config_manager.get(f"models.{agent_type}", "mixtral-8x7b-32768")
    
    @classmethod
    def get_workspace_dir(cls) -> Path:
        """Get workspace directory"""
        return Path(config_manager.get("workspace.directory", "workspace"))
    
    @classmethod
    def get_agent_setting(cls, key: str, default=None):
        """Get agent setting"""
        return config_manager.get(f"agents.{key}", default)
    
    @classmethod
    def get_display_setting(cls, key: str, default=None):
        """Get display setting"""
        return config_manager.get(f"display.{key}", default)
    
    @classmethod
    def validate(cls):
        """Validate configuration"""
        config_manager.validate()
    
    # Convenience properties
    @property
    def GROQ_API_KEY(self):
        return self.get_api_key()
    
    @property
    def DEFAULT_MODEL(self):
        return self.get_model("default")
    
    @property
    def RESEARCH_MODEL(self):
        return self.get_model("researcher")
    
    @property
    def CODING_MODEL(self):
        return self.get_model("coder")
    
    @property
    def VALIDATION_MODEL(self):
        return self.get_model("validator")
    
    @property
    def DEBUG_MODEL(self):
        return self.get_model("debugger")
    
    @property
    def WORKSPACE_DIR(self):
        return self.get_workspace_dir()
    
    @property
    def MAX_RETRIES(self):
        return self.get_agent_setting("max_retries", 3)
    
    @property
    def TEMPERATURE(self):
        return self.get_agent_setting("temperature", 0.7)
    
    @property
    def MAX_TOKENS(self):
        return self.get_agent_setting("max_tokens", 8192)
    
    @property
    def ENABLE_FILE_TREE(self):
        return config_manager.get("workspace.enable_file_tree", True)

# Create a config instance for easy import
config = Config()
