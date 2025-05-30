"""Server configuration settings."""

import os
from typing import Optional


class Settings:
    """Application settings."""
    
    def __init__(self):
        self.server_name = "Modular MCP Server"
        self.version = "0.1.0"
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.api_key: Optional[str] = os.getenv("API_KEY")
        self.database_url: Optional[str] = os.getenv("DATABASE_URL")
    
    @property
    def server_info(self) -> dict:
        """Get server information."""
        return {
            "name": self.server_name,
            "version": self.version,
            "log_level": self.log_level
        }


settings = Settings()