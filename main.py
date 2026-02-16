#!/usr/bin/env python3
"""MCP Cab Search & Book Server Entry Point"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'mcp-cab-server'))

def main():
    print("🚕 Starting MCP Cab Search & Book Server...")
    print("📍 Using Google Places API for location autocomplete")
    print("-" * 60)
    
    from server import mcp
    mcp.run()


if __name__ == "__main__":
    main()
