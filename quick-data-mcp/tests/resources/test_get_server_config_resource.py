"""Tests for get_server_config resource functionality."""

import pytest
from mcp_server.resources.get_server_config_resource import get_server_config
from mcp_server.config.settings import settings


class TestGetServerConfig:
    """Test get_server_config resource functionality."""
    
    @pytest.mark.asyncio
    async def test_get_server_config(self):
        """Test getting server configuration."""
        config = await get_server_config()
        
        assert isinstance(config, dict)
        assert config["name"] == settings.server_name
        assert config["version"] == settings.version
        assert config["log_level"] == settings.log_level
        assert "analytics_features" in config
        assert isinstance(config["analytics_features"], list)
        assert "dataset_loading" in config["analytics_features"]
        assert "supported_formats" in config
        assert "CSV" in config["supported_formats"]
        assert "JSON" in config["supported_formats"]


if __name__ == '__main__':
    pytest.main([__file__])