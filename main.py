#!/usr/bin/env python3
"""
MCP Cab Search & Book Server
Entry point for the FastMCP server with Google Places API integration.
"""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'mcp-cab-server'))

def main():
    """Start the MCP Cab Server."""
    print("🚕 Starting MCP Cab Search & Book Server...")
    print("📍 Using Google Places API for location autocomplete")
    print("-" * 60)
    
    # Import and run the server
    from server import mcp
    mcp.run()


if __name__ == "__main__":
    main()
