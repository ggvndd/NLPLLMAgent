"""
Configuration management for the Career Coach Agent.

Handles environment variables, API keys, and application settings.
"""

import os
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class Config:
    """Application configuration loaded from environment variables."""
    
    # Discord Bot Configuration
    discord_bot_token: str
    
    # LLM Provider Configuration
    llm_provider: str  # "openai" or "anthropic"
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    # Logging Configuration
    log_level: str = "INFO"
    log_dir: str = "logs"
    
    # Application Settings
    max_resume_length: int = 10000
    max_interview_questions: int = 10
    default_timeout: int = 30
    
    def __init__(self):
        """Initialize configuration from environment variables."""
        self.discord_bot_token = os.getenv("DISCORD_BOT_TOKEN", "")
        self.llm_provider = os.getenv("LLM_PROVIDER", "openai").lower()
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        self.log_dir = os.getenv("LOG_DIR", "logs")
        
        # Validate required configuration
        self._validate_config()
    
    def _validate_config(self):
        """Validate that required configuration is present."""
        errors = []
        warnings = []
        
        # Discord token is only required for Discord bot
        # if not self.discord_bot_token:
        #     warnings.append("DISCORD_BOT_TOKEN not set - Discord bot will not work")
        
        if self.llm_provider == "openai" and not self.openai_api_key:
            warnings.append("OPENAI_API_KEY not set - will run in demo mode")
        
        if self.llm_provider == "anthropic" and not self.anthropic_api_key:
            warnings.append("ANTHROPIC_API_KEY not set - will run in demo mode")
        
        if self.llm_provider not in ["openai", "anthropic", "demo"]:
            errors.append("LLM_PROVIDER must be either 'openai', 'anthropic', or 'demo'")
        
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")
        
        if warnings:
            print(f"⚠️  Configuration warnings: {'; '.join(warnings)}")
    
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return os.getenv("ENVIRONMENT", "development").lower() == "development"
    
    def get_log_file_path(self, component: str) -> str:
        """Get the log file path for a specific component."""
        os.makedirs(self.log_dir, exist_ok=True)
        return os.path.join(self.log_dir, f"{component}.log")
    
    def __repr__(self) -> str:
        """String representation (without sensitive data)."""
        return (
            f"Config(llm_provider='{self.llm_provider}', "
            f"log_level='{self.log_level}', "
            f"discord_configured={bool(self.discord_bot_token)}, "
            f"openai_configured={bool(self.openai_api_key)}, "
            f"anthropic_configured={bool(self.anthropic_api_key)})"
        )