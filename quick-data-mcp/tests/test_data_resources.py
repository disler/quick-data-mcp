"""Tests for data resources."""

import pytest
from mcp_server.resources import data_resources
from mcp_server.config.settings import settings


@pytest.mark.asyncio
async def test_get_server_config():
    """Test getting server configuration."""
    config = await data_resources.get_server_config()
    
    assert isinstance(config, dict)
    assert config["name"] == settings.server_name
    assert config["version"] == settings.version
    assert config["log_level"] == settings.log_level


@pytest.mark.asyncio
async def test_get_user_profile():
    """Test getting user profile by ID."""
    user_id = "test123"
    profile = await data_resources.get_user_profile(user_id)
    
    assert isinstance(profile, dict)
    assert profile["id"] == user_id
    assert profile["name"] == f"User {user_id}"
    assert profile["email"] == f"user{user_id}@example.com"
    assert profile["status"] == "active"
    assert "preferences" in profile
    assert isinstance(profile["preferences"], dict)
    
    # Test preferences structure
    prefs = profile["preferences"]
    assert "theme" in prefs
    assert "notifications" in prefs
    assert "language" in prefs


@pytest.mark.asyncio
async def test_get_system_status():
    """Test getting system status information."""
    status = await data_resources.get_system_status()
    
    assert isinstance(status, dict)
    assert status["status"] == "healthy"
    assert "uptime" in status
    assert status["version"] == settings.version
    assert "features" in status
    assert isinstance(status["features"], list)
    assert "dependencies" in status
    assert isinstance(status["dependencies"], dict)
    
    # Check expected features
    features = status["features"]
    expected_features = [
        "dataset_loading",
        "schema_discovery",
        "correlation_analysis",
        "segmentation",
        "data_quality_assessment"
    ]
    for feature in expected_features:
        assert feature in features
    
    # Check dependencies
    deps = status["dependencies"]
    assert "mcp" in deps
    assert "pandas" in deps
    assert "plotly" in deps
    assert "pydantic" in deps


@pytest.mark.asyncio
async def test_user_profile_different_ids():
    """Test user profiles with different IDs."""
    user_ids = ["user1", "admin", "test_user_123"]
    
    for user_id in user_ids:
        profile = await data_resources.get_user_profile(user_id)
        assert profile["id"] == user_id
        assert profile["name"] == f"User {user_id}"
        assert profile["email"] == f"user{user_id}@example.com"