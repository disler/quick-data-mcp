#!/usr/bin/env python3
"""Entry point for the Recommended MCP Server."""

import sys
import os

# Add src to Python path so we can import our server
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from mcp_server.server import mcp


def main():
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
