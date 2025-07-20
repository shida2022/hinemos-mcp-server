#!/usr/bin/env python3
"""Hinemos MCP Server entry point."""

import asyncio
import os
import sys
from src.hinemos_mcp.server import HinemosMCPServer


def main():
    """Main entry point for Hinemos MCP Server."""
    # Get configuration from environment variables
    base_url = os.environ.get("HINEMOS_BASE_URL", "http://localhost:8080/HinemosWeb/api")
    username = os.environ.get("HINEMOS_USERNAME", "hinemos")
    password = os.environ.get("HINEMOS_PASSWORD", "hinemos")
    verify_ssl = os.environ.get("HINEMOS_VERIFY_SSL", "true").lower() == "true"
    
    # Validate required configuration
    if not all([base_url, username, password]):
        print("Error: Missing required environment variables:", file=sys.stderr)
        print("Required: HINEMOS_BASE_URL, HINEMOS_USERNAME, HINEMOS_PASSWORD", file=sys.stderr)
        print("Optional: HINEMOS_VERIFY_SSL (default: true)", file=sys.stderr)
        sys.exit(1)
    
    # Create and run server
    server = HinemosMCPServer(
        base_url=base_url,
        username=username,
        password=password,
        verify_ssl=verify_ssl
    )
    
    print(f"Starting Hinemos MCP Server...", file=sys.stderr)
    print(f"Hinemos URL: {base_url}", file=sys.stderr)
    print(f"Username: {username}", file=sys.stderr)
    print(f"SSL Verification: {verify_ssl}", file=sys.stderr)
    
    try:
        asyncio.run(server.run())
    except KeyboardInterrupt:
        print("\nServer stopped by user", file=sys.stderr)
    except Exception as e:
        print(f"Server error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()