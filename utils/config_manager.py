"""Configuration manager for JSON-based settings"""
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

class ConfigManager:
    def __init__(self, config_path: str = "config.json"):
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
        self.load_config()
    
    def load_config(self):
        """Load configuration from JSON file"""
        if not self.config_path.exists():
            self.create_default_config()
        
        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
        except json.JSONDecodeError:
            print("⚠️  Invalid config.json, creating default...")
            self.create_default_config()
    
    def create_default_config(self):
        """Create default configuration file"""
        default_config = {
            "api": {
                "groq_api_key": "",
                "provider": "groq"
            },
            "models": {
                "default": "mixtral-8x7b-32768",
                "researcher": "mixtral-8x7b-32768",
                "coder": "llama-3.1-70b-versatile",
                "validator": "llama-3.1-70b-versatile",
                "debugger": "llama-3.1-70b-versatile"
            },
            "workspace": {
                "directory": "workspace",
                "enable_file_tree": True,
                "auto_cleanup": False,
                "max_workspace_age_days": 30
            },
            "agents": {
                "max_retries": 3,
                "temperature": 0.7,
                "max_tokens": 8192,
                "research_depth": "detailed",
                "code_style": "production",
                "auto_debug": True,
                "auto_validate": True
            },
            "display": {
                "show_token_usage": True,
                "show_timestamps": True,
                "show_agent_transitions": True,
                "color_theme": "default",
                "progress_bars": True
            },
            "safety": {
                "require_confirmation_for_execution": True,
                "max_file_size_mb": 10,
                "allowed_file_types": [".py", ".txt", ".json", ".md", ".csv"]
            }
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        self.config = default_config
        print(f"✅ Created default config.json")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value using dot notation"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """Set a configuration value using dot notation"""
        keys = key.split('.')
        target = self.config
        
        for k in keys[:-1]:
            if k not in target:
                target[k] = {}
            target = target[k]
        
        target[keys[-1]] = value
        self.save_config()
    
    def save_config(self):
        """Save current configuration to file"""
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def get_api_key(self) -> Optional[str]:
        """Get the API key from config or environment"""
        # First check environment variable
        env_key = os.getenv("GROQ_API_KEY")
        if env_key:
            return env_key
        
        # Then check config file
        config_key = self.get("api.groq_api_key")
        if config_key and config_key != "":
            return config_key
        
        return None
    
    def validate(self):
        """Validate the configuration"""
        api_key = self.get_api_key()
        if not api_key:
            raise ValueError(
                "Groq API key not found! Set it in config.json or GROQ_API_KEY environment variable.\n"
                "Run 'python setup.py' to configure interactively."
            )
        
        # Create workspace directory
        workspace_dir = Path(self.get("workspace.directory", "workspace"))
        workspace_dir.mkdir(exist_ok=True)
    
    def display_config(self):
        """Display current configuration"""
        print("\n" + "="*50)
        print("🔧 CURRENT CONFIGURATION")
        print("="*50)
        
        api_key = self.get_api_key()
        if api_key:
            masked = api_key[:10] + "..." + api_key[-4:] if len(api_key) > 14 else "***"
            print(f"🔑 API Key: ✅ Set ({masked})")
        else:
            print(f"🔑 API Key: ❌ Not set")
        
        print(f"☁️  Provider: {self.get('api.provider', 'groq')}")
        
        print("\n🤖 Models:")
        for model_type in ['default', 'researcher', 'coder', 'validator', 'debugger']:
            print(f"   • {model_type}: {self.get(f'models.{model_type}')}")
        
        print(f"\n📁 Workspace: {self.get('workspace.directory', 'workspace')}")
        print(f"🌳 File Tree: {'✅ Enabled' if self.get('workspace.enable_file_tree') else '❌ Disabled'}")
        
        print(f"\n⚙️  Agent Settings:")
        print(f"   • Max Retries: {self.get('agents.max_retries')}")
        print(f"   • Temperature: {self.get('agents.temperature')}")
        print(f"   • Max Tokens: {self.get('agents.max_tokens')}")
        print(f"   • Research Depth: {self.get('agents.research_depth')}")
        print(f"   • Code Style: {self.get('agents.code_style')}")
        print(f"   • Auto Validate: {self.get('agents.auto_validate')}")
        print(f"   • Auto Debug: {self.get('agents.auto_debug')}")
        
        print(f"\n🎨 Display:")
        print(f"   • Token Usage: {'✅' if self.get('display.show_token_usage') else '❌'}")
        print(f"   • Timestamps: {'✅' if self.get('display.show_timestamps') else '❌'}")
        print(f"   • Agent Transitions: {'✅' if self.get('display.show_agent_transitions') else '❌'}")
        print("="*50 + "\n")
