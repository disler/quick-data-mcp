"""Test configuration and fixtures."""

import pytest
import sys
import os

# Add src to Python path for tests
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from mcp_server.server import get_server


@pytest.fixture
def mcp_server():
    """Get the MCP server instance for testing."""
    return get_server()